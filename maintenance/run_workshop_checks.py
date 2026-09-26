"""Exercise workshop archive and path guards without executing an engine or npm."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import zipfile
from build_workshop import build_paths, source_files, verify_core
from release_manifest import release_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', type=Path, required=True)
    args = parser.parse_args()
    scratch = args.scratch
    if not scratch.is_absolute() or scratch.exists():
        parser.error('Use a NEW absolute scratch directory')
    scratch.mkdir(parents=True)
    root = Path(__file__).resolve().parents[1]
    checks = []
    files = release_files(root)
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

    def record(name, result):
        checks.append({'name': name, 'passed': bool(result)})
        if not result:
            raise AssertionError(name)

    def rejected(name, operation):
        try:
            operation()
        except ValueError:
            record(name, True)
        else:
            record(name, False)

    def archive(name, prefix=None, linked=False, changed=False, extra=False):
        target = scratch / name
        with zipfile.ZipFile(target, 'x') as z:
            for i, path in enumerate(files):
                info = zipfile.ZipInfo((prefix or root.name) + '/' + path.relative_to(root).as_posix())
                if linked and i == 0:
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                data = path.read_bytes() + (b'changed' if changed and i == 0 else b'')
                z.writestr(info, data)
            if extra:
                z.writestr(root.name + '/unlisted.txt', 'private fixture')
        return target

    good = archive('core.zip')
    verify_core(root, good)
    record('exact-core-snapshot-accepted', True)
    for name, kwargs in [('traversal-root', {'prefix': '..'}), ('absolute-root', {'prefix': '/outside'}),
                         ('linked-entry', {'linked': True}), ('modified-file', {'changed': True}),
                         ('unlisted-file', {'extra': True})]:
        bad = archive(name + '.zip', **kwargs)
        rejected(name + '-rejected', lambda p=bad: verify_core(root, p))
    sdk = scratch / 'official-sdk-path'
    sdk.mkdir()
    work, out = scratch / 'build', scratch / 'package-0.1.0'
    actual = build_paths(root, sdk, good, work, out)
    record('new-sibling-output-accepted', actual == (work, out, scratch / 'package-0.1.0.zip'))
    rejected('same-work-and-output-rejected', lambda: build_paths(root, sdk, good, work, work))
    rejected('output-inside-work-rejected', lambda: build_paths(root, sdk, good, work, work / 'nested'))
    rejected('work-inside-sdk-rejected', lambda: build_paths(root, sdk, good, sdk / 'nested', out))
    rejected('output-inside-source-rejected', lambda: build_paths(root, sdk, good, work, root / 'generated'))
    # This equivalent source path specifically checks that '..' cannot bypass containment.
    disguised = root.parent / 'nonexistent' / '..' / root.name / 'generated'
    rejected('normalized-source-overlap-rejected', lambda: build_paths(root, sdk, good, work, disguised))
    rejected('existing-build-directory-rejected', lambda: build_paths(root, sdk, good, sdk, out))
    collision = scratch / 'occupied.zip'
    collision.write_bytes(b'keep-existing-release')
    rejected('existing-archive-rejected-before-build', lambda: build_paths(root, sdk, good, work, scratch / 'occupied'))
    record('existing-archive-preserved', collision.read_bytes() == b'keep-existing-release')
    selected = source_files(root)
    record('workshop-source-excludes-generated-and-private-files', bool(selected) and all(
        not {'sdk', 'node_modules', 'dist', 'assets', '.git', '.env'} & set(p.relative_to(root).parts) for p in selected))
    record('guard-checks-created-no-build-output', not work.exists() and not out.exists())
    record('source-bytes-unchanged', all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == value for p, value in before.items()))
    result = {'checks': checks, 'passed': len(checks), 'failed': 0,
              'scope': 'Real archive validation and path-guard rejection; no typecheck, engine or workshop submission acceptance.'}
    (scratch / 'results.json').write_text(json.dumps(result, indent=2), 'utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
