"""Check shared channel files; --apply deliberately copies the stable source to Beta."""
import argparse
import json
from pathlib import Path
import shutil

def check_shared(root, apply=False):
    root = root.resolve()
    manifest = json.loads((root/'maintenance/shared-skill-files.json').read_text('utf-8'))
    assert manifest['source_channel']=='stable' and manifest['target_channel']=='beta'
    names = manifest['files']
    assert len(names)==len(set(names)), 'Duplicate shared path'
    pending = []
    # Validate the entire explicit set before writing any file.
    for name in names:
        rel = Path(name)
        assert not rel.is_absolute() and '..' not in rel.parts and ':' not in name
        pair = [root/'channels'/ch/'skills/letsgal-authoring'/rel for ch in ('stable','beta')]
        for path in pair:
            assert path.is_file(), f'Missing shared file: {name}'
            assert path.resolve().is_relative_to(root)
            assert not any(p.is_symlink() or (hasattr(p,'is_junction') and p.is_junction()) for p in [path,*path.parents] if p!=root.parent)
        if pair[0].read_bytes()!=pair[1].read_bytes(): pending.append((name,*pair))
    if apply:
        for name,source,target in pending:
            shutil.copyfile(source,target)
            assert source.read_bytes()==target.read_bytes()
    return {'files':len(names),'different':[row[0] for row in pending],
            'status':'synchronized' if apply and pending else ('different' if pending else 'identical')}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply',action='store_true',help='After merging differences and preserving originals, copy the listed shared files')
    args=p.parse_args()
    result=check_shared(Path(__file__).resolve().parents[1],args.apply)
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(1 if result['status']=='different' else 0)
