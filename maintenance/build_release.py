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
from stage_publication import ordinary, overlaps
from sync_shared_skill import check_shared

def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('--zip',action='store_true')
    args.add_argument('--archive',type=Path,help='NEW archive outside source; used with --zip')
    opts=args.parse_args()
    if opts.archive and not opts.zip: args.error('--archive requires --zip')
    root=Path(__file__).resolve().parents[1]
    shared=check_shared(root)
    assert shared['status']=='identical', 'Merge channel differences, then explicitly sync shared files before building'
    manifest=json.loads((root/'bundle.json').read_text('utf-8'))
    version=manifest['version']
    package_name=manifest['owner']
    assert re.fullmatch(r'[0-9A-Za-z.\-]+',package_name)
    assert re.fullmatch(r'[0-9A-Za-z.\-]+',version)
    assert manifest['schema']==2 and {x['id'] for x in manifest['channels']}=={'stable','beta'}, 'Expected two explicit channel payloads'
    files=release_files(root)
    assert not any(p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) for p in files), 'Linked content is not distributable'
    assert not any('__pycache__' in p.parts or p.suffix=='.pyc' for p in files), 'Remove generated Python caches before release'
    for file in (p for p in files if p.suffix=='.ps1'):
        content=file.read_text('utf-8-sig').replace('\r\n','\n')
        file.write_bytes(b'\xef\xbb\xbf'+content.encode('utf-8'))
    for file in (p for p in files if p.suffix=='.cmd'):
        file.write_bytes(file.read_text('ascii').replace('\r\n','\n').replace('\n','\r\n').encode('ascii'))
    digest=lambda file:hashlib.sha256(file.read_bytes()).hexdigest()
    payload_counts={}
    revisions=set()
    for row in manifest['channels']:
        channel=row['id']
        assert row['bundle']==f'channels/{channel}/bundle.json'
        channel_root=root/'channels'/channel
        skill=channel_root/'skills/letsgal-authoring'
        front=(skill/'SKILL.md').read_text('utf-8')
        assert re.search(r'^  version: '+re.escape(version)+r'$',front,re.M), 'Skill and bundle versions differ'
        assert re.search(r'^  channel: '+channel+r'$',front,re.M), 'Skill channel differs'
        revision=re.search(r'^  revision: ([0-9A-Za-z._-]+)$',front,re.M)
        assert revision, 'Skill revision is required for a new build'
        revisions.add(revision[1])
        payload=[p for p in files if skill in p.parents]
        assert set(payload)=={p for p in skill.rglob('*') if p.is_file()}, 'Unlisted payload file'
        assert (skill/'references/risk-notice.md').read_bytes()==(root/'RISK-NOTICE.md').read_bytes(), 'Risk notice differs'
        selected=json.loads((channel_root/'bundle.json').read_text('utf-8'))
        assert selected['version']==version and selected['channel']==channel and selected['schema']==1
        selected['revision']=revision[1]
        selected['files']=[{'path':p.relative_to(skill).as_posix(),'sha256':digest(p)} for p in payload]
        (channel_root/'bundle.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n','utf-8')
        payload_counts[channel]=len(payload)
    assert len(revisions)==1, 'Channel revisions differ'
    manifest['revision']=revisions.pop()
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
        archive=ordinary(opts.archive or root.parent/(package_name+'-'+version+'.zip'))
        assert not archive.exists() and not overlaps(root,archive), 'Archive must be NEW and outside source'
        assert archive.parent.is_dir(), 'Archive parent must already exist'
        all_files=files
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
            for file in all_files:
                info=zipfile.ZipInfo(package_name+'/'+file.relative_to(root).as_posix(), date_time=(2026,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(info,file.read_bytes())
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert len(z.namelist())==len(all_files)
            for file in all_files:
                assert z.read(package_name+'/'+file.relative_to(root).as_posix())==file.read_bytes()
        print(json.dumps({'archive':str(archive),'files':len(all_files),'bytes':archive.stat().st_size,'sha256':digest(archive),'zip_readback':'all files match'},ensure_ascii=False))
    else:
        print(json.dumps({'version':version,'skill_files':payload_counts,'local_links':'valid','checksums':'refreshed'}))

if __name__=='__main__':
    main()
