"""Read explicit local Wiki manifests and build a NEW personal workbench outside the public source."""
import argparse
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import markdown
from build_manual import ROOT, render, slugify

MAX_BYTES=1000000

def ordinary(path):
    path=Path(path).absolute()
    for part in (path,*path.parents):
        if part.exists() or part.is_symlink():
            info=part.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                raise ValueError('Linked input/output paths are not supported')
    return path.resolve()

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError('Duplicate JSON key: '+key)
        result[key]=value
    return result

def string(value, field, max_length=200):
    if not isinstance(value,str) or not value.strip() or len(value)>max_length: raise ValueError('Invalid '+field)
    return value

def read_json(path):
    ordinary(path)
    if path.stat().st_size>MAX_BYTES: raise ValueError('Manifest too large')
    return json.loads(path.read_text('utf-8-sig'),object_pairs_hook=unique_object)

def document_path(base, relative):
    if not isinstance(relative,str) or '\\' in relative or ':' in relative: raise ValueError('Invalid document path')
    parts=PurePosixPath(relative).parts
    if not parts or relative.startswith('/') or '..' in parts or '/'.join(parts)!=relative: raise ValueError('Document path must stay within its package')
    path=ordinary(base.joinpath(*parts))
    if not path.is_relative_to(base.resolve()) or not path.is_file() or path.suffix.lower()!='.md': raise ValueError('Expected a Markdown file inside the package')
    if path.stat().st_size>MAX_BYTES: raise ValueError('Document too large')
    return path

def read_item(path, kind, expected_id=None, expected_version=None):
    value=read_json(path)
    if not isinstance(value,dict) or value.get('schema')!=1 or value.get('kind')!=kind: raise ValueError('Manifest schema/kind does not match its location')
    for name,limit in [('id',200),('version',80),('revision',100),('title',200)]: string(value.get(name),name,limit)
    if not isinstance(value.get('summary',''),str) or len(value.get('summary',''))>1000: raise ValueError('Invalid summary')
    if expected_id is not None and value['id']!=expected_id: raise ValueError('Plugin ID differs from its directory')
    if expected_version is not None and value['version']!=expected_version: raise ValueError('Plugin version differs from its directory')
    if value.get('status') not in ('available','paused'): raise ValueError('Explicit available/paused status is required')
    section='skills' if kind=='plugin' else 'personal'
    identity=[section,value['id'],value['version'],value['revision']]
    uid='ext-'+hashlib.sha256(json.dumps(identity,ensure_ascii=False).encode('utf-8')).hexdigest()[:16]
    item={key:value[key] for key in ('id','version','revision','title','status')}
    item.update(uid=uid,section=section,summary=value.get('summary',''),documents=[])
    # Paused packages are metadata-only: do not open, validate or hash their documents.
    if value['status']=='paused': return item
    docs=value.get('documents')
    if not isinstance(docs,list) or not 1<=len(docs)<=50: raise ValueError('Available entries need 1-50 documents')
    paths={}; seen=set()
    for doc in docs:
        if not isinstance(doc,dict) or not isinstance(doc.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,60}',doc['id']): raise ValueError('Invalid document id')
        if doc['id'] in seen: raise ValueError('Duplicate document id')
        seen.add(doc['id']); string(doc.get('title'),'document title')
        file=document_path(path.parent,doc.get('path'))
        if file in paths: raise ValueError('Duplicate document path')
        paths[file]=doc['id']
    for doc in docs:
        file=document_path(path.parent,doc['path'])
        body=markdown.markdown(file.read_text('utf-8-sig'),extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'slugify':slugify}})
        def rewrite(match):
            href=html.unescape(match[1]); u=urlsplit(href)
            if u.scheme or u.netloc or not u.path: return match[0]
            target=(file.parent/unquote(u.path)).resolve()
            if target in paths:
                return 'href="#'+uid+'-'+paths[target]+('--'+html.escape(unquote(u.fragment),quote=True) if u.fragment else '')+'"'
            return ''  # A standalone library includes only its declared documents.
        body=re.sub(r'href="([^"]*)"',rewrite,body)
        item['documents'].append({'id':doc['id'],'title':doc['title'],'html':body})
    return item

def collect(user_area):
    area=ordinary(user_area)
    if not area.is_dir(): raise ValueError('User area does not exist')
    items=[]; identities=set()
    plugins=area/'plugins'
    if plugins.exists():
        ordinary(plugins)
        for plugin in sorted(plugins.iterdir()):
            ordinary(plugin)
            if not plugin.is_dir(): continue
            for version in sorted(plugin.iterdir()):
                ordinary(version)
                if not version.is_dir(): continue
                manifest=version/'wiki.json'
                if manifest.exists(): items.append(read_item(manifest,'plugin',plugin.name,version.name))
    personal=area/'preferences/wiki.json'
    if personal.exists(): items.append(read_item(personal,'personal'))
    if len(items)>200: raise ValueError('Too many Wiki packages')
    for item in items:
        identity=(item['section'],item['id'],item['version'],item['revision'])
        if identity in identities: raise ValueError('Duplicate Wiki identity')
        identities.add(identity)
    return {'schema':1,'kind':'letsgal-wiki-library','items':items}

def build(user_area, output=None, data_output=None, check=False):
    library=collect(user_area)
    report={'status':'checked' if check else 'generated','items':len(library['items']),'documents':sum(len(i['documents']) for i in library['items']),'paused':sum(i['status']=='paused' for i in library['items']),'source_files_modified':False}
    if check: return report
    if output is None: raise ValueError('--output is required unless --check is used')
    destinations=[ordinary(output)]+([ordinary(data_output)] if data_output else [])
    for target in destinations:
        if target.is_relative_to(ROOT.parent.resolve()): raise ValueError('Personal output must stay outside the public release tree')
        if target.exists() or not target.parent.is_dir(): raise ValueError('Output must be a NEW file in an existing directory')
    if len(set(destinations))!=len(destinations): raise ValueError('Output paths must differ')
    page,_=render(library=library,local=True)
    payloads=[page.encode('utf-8')]
    if data_output: payloads.append((json.dumps(library,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    for target,payload in zip(destinations,payloads):
        with target.open('xb') as stream: stream.write(payload)
        assert target.read_bytes()==payload
    report['outputs']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in destinations]
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user-area',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--data-output',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try: result=build(args.user_area,args.output,args.data_output,args.check)
    except (ValueError,OSError,AssertionError) as error:
        print(json.dumps({'status':'error','message':str(error)},ensure_ascii=False)); return 1
    print(json.dumps(result,ensure_ascii=False)); return 0

if __name__=='__main__': raise SystemExit(main())
