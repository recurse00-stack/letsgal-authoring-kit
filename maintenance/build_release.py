"""Refresh encodings/manifests. Add --zip to build a NEW verified archive beside the bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import zipfile
from release_manifest import release_files
from review_release import audit

def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('--zip',action='store_true')
    opts=args.parse_args()
    root=Path(__file__).resolve().parents[1]
    skill=root/'skills/letsgal-authoring'
    manifest=json.loads((root/'bundle.json').read_text('utf-8'))
    version=manifest['version']
    assert re.fullmatch(r'[0-9A-Za-z.\-]+',version)
    assert re.search(r'^  version: '+re.escape(version)+r'$',(skill/'SKILL.md').read_text('utf-8'),re.M), 'Skill and bundle versions differ'
    files=release_files(root)
    assert not any(p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) for p in files), 'Linked content is not distributable'
    assert not any('__pycache__' in p.parts or p.suffix=='.pyc' for p in files), 'Remove generated Python caches before release'
    for file in (p for p in files if p.suffix=='.ps1'):
        content=file.read_text('utf-8-sig').replace('\r\n','\n')
        file.write_bytes(b'\xef\xbb\xbf'+content.encode('utf-8'))
    for file in (p for p in files if p.suffix=='.cmd'):
        file.write_bytes(file.read_text('ascii').replace('\r\n','\n').replace('\n','\r\n').encode('ascii'))
    digest=lambda file:hashlib.sha256(file.read_bytes()).hexdigest()
    skill_files=[p for p in files if skill in p.parents]
    manifest['files']=[{'path':p.relative_to(skill).as_posix(),'sha256':digest(p)} for p in skill_files]
    (root/'bundle.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
    for file in (p for p in files if p.suffix=='.md'):
        for link in re.findall(r'\]\(([^)]+)\)',file.read_text('utf-8')):
            if '://' not in link and not link.startswith('#') and '<' not in link:
                assert (file.parent/link.split('#')[0]).exists(), f'Broken link: {file}: {link}'
    checksums=''.join(f'{digest(p)}  {p.relative_to(root).as_posix()}\n' for p in files if p.name!='SHA256SUMS.txt')
    (root/'SHA256SUMS.txt').write_text(checksums,'utf-8')
    privacy=audit(root,[os.environ.get('USERNAME','')])
    if privacy['status']!='passed':
        raise ValueError('Publication audit requires review: '+json.dumps(privacy['findings']))
    if opts.zip:
        archive=root.parent/(root.name+'-'+version+'.zip')
        all_files=files
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
            for file in all_files:
                z.write(file,root.name+'/'+file.relative_to(root).as_posix())
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert len(z.namelist())==len(all_files)
            for file in all_files:
                assert z.read(root.name+'/'+file.relative_to(root).as_posix())==file.read_bytes()
        print(json.dumps({'archive':str(archive),'files':len(all_files),'bytes':archive.stat().st_size,'sha256':digest(archive),'zip_readback':'all files match'},ensure_ascii=False))
    else:
        print(json.dumps({'version':version,'skill_files':len(manifest['files']),'local_links':'valid','checksums':'refreshed'}))

if __name__=='__main__':
    main()
