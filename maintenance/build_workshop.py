"""Build a NEW workshop review package from this source, an official SDK, and a verified core ZIP."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import zipfile
from release_manifest import release_files
from review_release import inspect_text

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def tree_hashes(root):
    return {p.relative_to(root).as_posix(): sha(ordinary(p)) for p in root.rglob('*') if p.is_file()}

def verify_runtime(work):
    mapping = json.loads((work / 'dist/index.mjs.map').read_text('utf-8'))
    expected = ['../src/authoring-guide.tsx', '../src/index.tsx', '../src/risk-notice.ts']
    if sorted(mapping.get('sources', [])) != expected or len(mapping.get('sourcesContent', [])) != len(expected):
        raise ValueError('Source map must contain only the three owned source files')
    for name, source in zip(mapping['sources'], mapping['sourcesContent']):
        if (work / 'dist' / name).read_bytes().decode('utf-8') != source:
            raise ValueError('Source map differs from the actual source')
    module = (work / 'dist/index.mjs').read_text('utf-8')
    imports = re.findall(r'^import\b[^;]*?\bfrom\s*[\"\']([^\"\']+)[\"\']', module, re.M)
    if set(imports) != {'@avg-studio/sdk', 'react', 'react/jsx-runtime'}:
        raise ValueError('Unexpected runtime imports')
    if '__decorateElement' in module or '__decoratorStart' in module:
        raise ValueError('Bundled decorator helpers need a fresh third-party license review')
    return {'runtime_imports': sorted(imports), 'source_map': 'owned sources only'}

def ordinary(path):
    path = Path(path).absolute()
    for part in [path, *path.parents]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Linked build paths are not supported')
    return Path(os.path.abspath(path))

def overlaps(left, right):
    return left == right or left in right.parents or right in left.parents

def build_paths(root, sdk, core, work, out):
    root, sdk, core, work, out = map(ordinary, (root, sdk, core, work, out))
    archive = out.parent / (out.name + '.zip')
    if work.exists() or out.exists() or archive.exists() or overlaps(work, out):
        raise ValueError('Build, output and archive must be separate NEW paths')
    for target in (work, out, archive):
        if any(overlaps(target, source) for source in (root, sdk, core)):
            raise ValueError('Generated paths must not overlap source, SDK or core ZIP')
    return work, out, archive

def source_files(root):
    manifest = json.loads(ordinary(root / 'workshop-source-files.json').read_text('utf-8'))
    if manifest.get('schema') != 1 or not isinstance(manifest.get('files'), list):
        raise ValueError('Unsupported workshop source manifest')
    result = []
    for name in manifest['files']:
        if not isinstance(name, str):
            raise ValueError('Invalid workshop source path')
        parts = PurePosixPath(name).parts
        if not name.startswith('workshop-guide/') or '/'.join(parts) != name or '\\' in name or ':' in name or '..' in parts or any(p.startswith('.') for p in parts):
            raise ValueError('Unsafe workshop source path')
        path = ordinary(root / name)
        if not path.is_file():
            raise ValueError('Missing workshop source file')
        hits = inspect_text(path.read_text('utf-8-sig'), [os.environ.get('USERNAME', '')])
        if hits:
            raise ValueError(f'Workshop source privacy review required: {name}: {hits}')
        result.append(path)
    if len({p.as_posix().lower() for p in result}) != len(result):
        raise ValueError('Duplicate workshop source entry')
    return result

def verify_core(root, archive):
    expected = {p.relative_to(root).as_posix(): p.read_bytes() for p in release_files(root)}
    with zipfile.ZipFile(archive) as z:
        names = z.namelist()
        if len(names) != len(expected):
            raise ValueError('Core ZIP file count does not match current source')
        prefix = root.name + '/'
        if set(names) != {prefix + n for n in expected}:
            raise ValueError('Core ZIP contains unexpected paths')
        if any(stat.S_ISLNK(info.external_attr >> 16) for info in z.infolist()):
            raise ValueError('Core ZIP must not contain links')
        for name, data in expected.items():
            if z.read(prefix + name) != data:
                raise ValueError('Core ZIP differs from current source: ' + name)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', required=True, type=Path)
    parser.add_argument('--core-zip', required=True, type=Path)
    parser.add_argument('--build-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sdk = ordinary(args.sdk)
    try:
        work, out, archive = build_paths(root, sdk, args.core_zip, args.build_dir, args.output)
    except ValueError as error:
        parser.error(str(error))
    if not (sdk / 'index.ts').is_file() or not (sdk / 'constants.ts').is_file():
        parser.error('Provide a complete official SDK directory')
    files = source_files(root)
    verify_core(root, ordinary(args.core_zip))
    version = json.loads((root / 'bundle.json').read_text('utf-8'))['version']
    notice = (root / 'skills/letsgal-authoring/references/risk-notice.md').read_text('utf-8')
    work.mkdir(parents=True)
    for path in files:
        target = work / path.relative_to(root / 'workshop-guide')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    for name in ['extension.json', 'package.json', 'package-lock.json']:
        data = json.loads((work / name).read_text('utf-8'))
        if data['version'] != version:
            raise ValueError('Version mismatch: ' + name)
        if name == 'package-lock.json' and data['packages']['']['version'] != version:
            raise ValueError('Lock root version mismatch')
        if name == 'extension.json' and data.get('entry') != 'dist/index.mjs':
            raise ValueError('Manifest entry must match the build output')
    for path in sdk.rglob('*'):
        ordinary(path)
    sdk_before = tree_hashes(sdk)
    shutil.copytree(sdk, work / 'sdk')
    (work / 'src/risk-notice.ts').write_text('export const riskNotice = ' + json.dumps(notice, ensure_ascii=False) + ';\n', 'utf-8')
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    if not npm:
        raise RuntimeError('Node.js and npm are required for workshop builds')
    for command in [[npm, 'ci', '--include=optional', '--ignore-scripts', '--no-audit', '--no-fund'], [npm, 'run', 'typecheck'], [npm, 'run', 'build']]:
        subprocess.run(command, cwd=work, check=True)
    if sdk_before != tree_hashes(sdk) or sdk_before != tree_hashes(work / 'sdk'):
        raise ValueError('Official SDK changed during the build')
    runtime = verify_runtime(work)
    outputs = [p.relative_to(root / 'workshop-guide').as_posix() for p in files]
    outputs += ['src/risk-notice.ts', 'dist/index.mjs', 'dist/index.mjs.map']
    for name in outputs:
        source = ordinary(work / name)
        hits = inspect_text(source.read_text('utf-8-sig'), [os.environ.get('USERNAME', '')])
        if hits:
            raise ValueError(f'Built output privacy review required: {name}: {hits}')
    out.mkdir(parents=True)
    for name in outputs:
        source = work / name
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    (out / 'assets').mkdir()
    shutil.copy2(args.core_zip, out / 'assets/skill-kit.zip')
    (out / 'assets/risk-notice.md').write_text(notice, 'utf-8')
    outputs += ['assets/skill-kit.zip', 'assets/risk-notice.md']
    (out / 'SHA256SUMS.txt').write_text(''.join(f'{sha(out/name)}  {name}\n' for name in sorted(outputs)), 'utf-8')
    outputs += ['SHA256SUMS.txt']
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(outputs):
            info = zipfile.ZipInfo(out.name + '/' + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, (out / name).read_bytes())
    with zipfile.ZipFile(archive) as z:
        for name in outputs:
            assert z.read(out.name + '/' + name) == (out / name).read_bytes()
    print(json.dumps({'version': version, 'files': len(outputs), 'sha256': sha(archive), 'core_sha256': sha(args.core_zip), 'sdk_unchanged': True, **runtime, 'scope': 'Strict typecheck, build, source map, privacy and ZIP readback. Host runtime tests deferred; workshop submission has a separate receipt.'}))

if __name__ == '__main__':
    main()
