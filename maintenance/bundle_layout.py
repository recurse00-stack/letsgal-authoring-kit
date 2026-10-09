"""Channel-aware paths for isolated maintenance checks, including old flat bundles."""
import json
from pathlib import Path

def manifest_path(root,channel='beta'):
    root=Path(root)
    data=json.loads((root/'bundle.json').read_text('utf-8'))
    return root/f'channels/{channel}/bundle.json' if data['schema']==2 else root/'bundle.json'

def payload(root,channel='beta'):
    return manifest_path(root,channel).parent/'skills/letsgal-authoring'

def with_channel(command,channel='beta'):
    args=list(command)
    if '-Channel' in args or '-File' not in args:return args
    path=Path(args[args.index('-File')+1])
    if path.name=='Install.ps1' and json.loads((path.parent/'bundle.json').read_text('utf-8'))['schema']==2:args+=['-Channel',channel]
    return args
