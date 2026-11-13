"""Local optional-package registry and offline Wiki. Python 3.10+, standard library."""
import argparse
from contextlib import contextmanager
import copy
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import time
import uuid
from urllib.parse import urlsplit, unquote

SCHEMA = 1
MAX_BYTES = 20000000
ID = re.compile(r'[a-z0-9][a-z0-9-]{0,63}')
VERSION = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}')

def ordinary(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.exists() or part.is_symlink():
            s = part.lstat()
            if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 0x400:
                raise ValueError('Linked paths are not supported: ' + str(part))
    return path

def token(value, version=False):
    if not isinstance(value, str) or not (VERSION if version else ID).fullmatch(value) or value.endswith('.'):
        raise ValueError('Invalid package ID or version')
    if value.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(10)],*[f'LPT{i}' for i in range(10)]}:
        raise ValueError('Reserved path name')
    return value

def relative(root, name):
    if not isinstance(name, str) or ':' in name or '\\' in name:
        raise ValueError('Invalid relative path')
    parts = PurePosixPath(name).parts
    if not parts or name.startswith('/') or '..' in parts or '/'.join(parts) != name:
        raise ValueError('Path must stay inside its package')
    for part in parts:
        if part.endswith(('.', ' ')) or part.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(10)],*[f'LPT{i}' for i in range(10)]}:
            raise ValueError('Invalid Windows path component')
    root = ordinary(root)
    result = ordinary(root.joinpath(*parts))
    if not result.is_relative_to(root): raise ValueError('Path escaped package')
    return result

def sha(data): return hashlib.sha256(data).hexdigest()

def read_bytes(path):
    path = ordinary(path)
    if not path.is_file() or path.stat().st_size > MAX_BYTES: raise ValueError('Missing or oversized file: '+str(path))
    return path.read_bytes()

def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value: raise ValueError('Duplicate JSON key: '+key)
        value[key] = item
    return value

def read_json(path): return json.loads(read_bytes(path).decode('utf-8-sig'), object_pairs_hook=unique)
def encode(value): return (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')

def file_map(root):
    root = ordinary(root)
    if not root.is_dir(): raise ValueError('Missing payload directory')
    result = {}
    for path in sorted(root.rglob('*')):
        ordinary(path)
        if path.is_file(): result[path.relative_to(root).as_posix()] = sha(read_bytes(path))
    return result

def checked_files(root, files):
    if not isinstance(files, dict) or not files: raise ValueError('Missing file manifest')
    folded = set()
    for name, digest in files.items():
        relative(root, name)
        if name.casefold() in folded or not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}',digest):
            raise ValueError('Invalid or duplicate file manifest')
        folded.add(name.casefold())
    return files

def validate_meta(value):
    token(value.get('id')); token(value.get('version'), True)
    for key, limit in [('revision',100),('title',200),('summary',1000)]:
        if not isinstance(value.get(key),str) or not value[key].strip() or len(value[key]) > limit:
            raise ValueError('Invalid '+key)
    if value.get('section') not in ('references','skills'): raise ValueError('Invalid Wiki section')

def validate_library(value, meta):
    if not isinstance(value,dict) or value.get('schema')!=1 or value.get('kind')!='letsgal-wiki-library' or not isinstance(value.get('items'),list) or len(value['items'])!=1:
        raise ValueError('A package must provide exactly one Wiki item')
    item=value['items'][0]
    for key in ('id','version','revision','title','summary','section'):
        if item.get(key)!=meta[key]: raise ValueError('Wiki identity differs: '+key)
    uid='ext-'+sha(json.dumps([item[k] for k in ('section','id','version','revision')],ensure_ascii=False).encode())[:16]
    if item.get('uid')!=uid or item.get('status')!='available': raise ValueError('Invalid Wiki identity/status')
    docs=item.get('documents')
    if not isinstance(docs,list) or not 1<=len(docs)<=50: raise ValueError('Missing Wiki documents')
    seen=set()
    for doc in docs:
        if not isinstance(doc,dict) or not isinstance(doc.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,60}',doc['id']) or doc['id'] in seen:
            raise ValueError('Invalid/duplicate document ID')
        seen.add(doc['id'])
        if not isinstance(doc.get('title'),str) or not 0<len(doc['title'])<=200 or not isinstance(doc.get('html'),str) or len(doc['html'])>1000000:
            raise ValueError('Invalid Wiki document')
    return item

def load_state(area, package_id):
    path=relative(area,'addons/'+token(package_id)+'/state.json')
    value=read_json(path)
    if value.get('schema')!=1 or value.get('id')!=package_id or type(value.get('enabled')) is not bool or not isinstance(value.get('versions'),dict) or not value['versions']:
        raise ValueError('Invalid addon state')
    if value.get('selected_version') not in value['versions']: raise ValueError('Selected version is not installed')
    for version, record in value['versions'].items():
        token(version,True)
        validate_meta(dict(record,id=package_id,version=version))
        if record.get('entry')!='SKILL.md': raise ValueError('Unsupported addon entry')
        files=checked_files(path.parent/version,record.get('files'))
        if not {'SKILL.md','wiki-library.json'}<=files.keys(): raise ValueError('Missing addon payload entries')
    return path,value

def collect(area, overrides=None):
    items=[]
    addons=ordinary(area/'addons')
    if addons.exists():
        for directory in sorted(addons.iterdir()):
            ordinary(directory)
            if not directory.is_dir(): continue
            if overrides and directory.name in overrides:state=overrides[directory.name]
            elif (directory/'state.json').exists():_,state=load_state(area,directory.name)
            else:continue
            for version,record in state['versions'].items():
                meta=dict(record,id=state['id'],version=version)
                if state['enabled']:
                    raw=read_bytes(directory/version/'wiki-library.json')
                    if sha(raw)!=record['files']['wiki-library.json']: raise ValueError('Installed Wiki changed: '+state['id'])
                    item=copy.deepcopy(validate_library(json.loads(raw.decode('utf-8-sig'),object_pairs_hook=unique),meta))
                else:
                    item={k:meta[k] for k in ('id','version','revision','title','summary','section')}
                    item.update(uid='ext-'+sha(json.dumps([meta[k] for k in ('section','id','version','revision')],ensure_ascii=False).encode())[:16],status='paused',documents=[])
                item['selected']=state['enabled'] and version==state['selected_version']
                items.append(item)
    if len(items)>200: raise ValueError('Too many registered Wiki versions')
    return {'schema':1,'kind':'letsgal-wiki-library','items':items}

def inject(base, library):
    pattern=r'(<script id="wiki-data" type="application/json">)(.*?)(</script>)'
    match=re.search(pattern,base,re.S)
    if not match: raise ValueError('Main Wiki data slot not found')
    value=json.loads(match[2]); value['library']=library; value['local']=True
    payload=json.dumps(value,ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    return base[:match.start(2)]+payload+base[match.end(2):]

@contextmanager
def lock(area):
    area=ordinary(area)
    if area.parent==area:raise ValueError('User area cannot be a drive root')
    area.mkdir(parents=True,exist_ok=True)
    path=ordinary(area/'.addon-operation.lock')
    try: stream=path.open('xb')
    except FileExistsError: raise ValueError('Another addon/Wiki operation is active; inspect the existing lock')
    try:
        stream.write(str(os.getpid()).encode());stream.close();yield
    finally:
        stream.close();path.unlink()

def commit_files(area, changes, label):
    """Back up exact prior bytes, replace files atomically, restore all on failure."""
    area=ordinary(area)
    changes={ordinary(p):data for p,data in changes.items()}
    for path in changes:
        if not path.is_relative_to(area): raise ValueError('Managed output escaped user area')
    changed={p:data for p,data in changes.items() if not p.exists() or read_bytes(p)!=data}
    if not changed:return {'status':'verified-unchanged','backup':None,'changed':0}
    before={p:read_bytes(p) if p.exists() else None for p in changed}
    backup=relative(area,'backups/'+time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]+'-'+label)
    backup.mkdir(parents=True)
    for path,data in before.items():
        if data is not None:
            dest=backup/path.relative_to(area);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    (backup/'recovery.json').write_bytes(encode({'previous':{str(p.relative_to(area)):None if d is None else sha(d) for p,d in before.items()}}))
    done=[]
    try:
        for path,data in changed.items():
            if (read_bytes(path) if path.exists() else None)!=before[path]:raise ValueError('File changed during operation')
            path.parent.mkdir(parents=True,exist_ok=True)
            temp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
            try:
                with temp.open('xb') as out:out.write(data)
                os.replace(temp,path);done.append(path)
            finally:
                if temp.exists():temp.unlink()
            if read_bytes(path)!=data:raise ValueError('Output readback failed')
    except Exception:
        for path in reversed(done):
            if before[path] is None:path.unlink()
            else:
                temp=path.with_name('.'+path.name+'.restore-'+uuid.uuid4().hex)
                temp.write_bytes(before[path]);os.replace(temp,path)
        raise
    return {'status':'changed','backup':str(backup),'changed':len(changed)}

def refresh_changes(area, base=None, overrides=None):
    base_path=relative(area,'workbench/MANUAL.base.html')
    if base is None:
        if not base_path.exists():return {},{'status':'pending','reason':'Main workbench is not installed'}
        base=read_bytes(base_path)
    library=collect(area,overrides)
    page=inject(base.decode('utf-8-sig'),library).encode('utf-8')
    return {relative(area,'workbench/MANUAL.html'):page},{'status':'ready','items':len(library['items']),'documents':sum(len(i['documents']) for i in library['items']),'path':str(area/'workbench/MANUAL.html')}

def refresh(area):
    with lock(area):
        changes,report=refresh_changes(area)
        report['write']=commit_files(area,changes,'wiki') if changes else None
        return report

def setup(source,area):
    source=ordinary(source)
    area=ordinary(area)
    if area==source or area.is_relative_to(source) or source.is_relative_to(area):raise ValueError('User area and public source must not overlap')
    base=read_bytes(source/'MANUAL.html')
    def link(match):
        href=html.unescape(match[1]);u=urlsplit(href)
        if u.scheme or u.netloc or not u.path:return match[0]
        destination=relative(source,unquote(u.path)).as_uri()
        return 'href="'+html.escape(destination+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else ''),quote=True)+'"'
    base=re.sub(r'href="([^"]*)"',link,base.decode('utf-8-sig')).encode('utf-8')
    runtime=read_bytes(source/'maintenance/workbench_runtime.py')
    with lock(area):
        changes,report=refresh_changes(area,base)
        changes.update({relative(area,'workbench/MANUAL.base.html'):base,relative(area,'workbench/workbench_runtime.py'):runtime})
        report['write']=commit_files(area,changes,'workbench-setup')
        return report

def change_state(area,package_id,version=None,enabled=None):
    with lock(area):
        path,value=load_state(area,package_id)
        if version is not None:
            if version not in value['versions']:raise ValueError('Requested version is not installed')
            value['selected_version']=version
        if enabled is not None:value['enabled']=enabled
        changes,report=refresh_changes(area,overrides={package_id:value})
        changes[path]=encode(value)
        result=commit_files(area,changes,'addon-state')
        return {'state':result,'wiki':report,'selected_version':value['selected_version'],'enabled':value['enabled']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    for name in ('refresh','setup','state'):
        p=commands.add_parser(name);p.add_argument('--user-area',type=Path,required=True)
        if name=='setup':p.add_argument('--source',type=Path,required=True)
        if name=='state':
            p.add_argument('--id',required=True);p.add_argument('--version');p.add_argument('--enabled',choices=['yes','no'])
    args=parser.parse_args()
    try:
        area=ordinary(args.user_area)
        if args.command=='setup':result=setup(args.source,area)
        elif args.command=='refresh':result=refresh(area)
        else:result=change_state(area,args.id,args.version,None if args.enabled is None else args.enabled=='yes')
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'error','message':str(error)},ensure_ascii=False));return 1

if __name__=='__main__':raise SystemExit(main())
