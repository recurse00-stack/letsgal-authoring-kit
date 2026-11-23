"""User-owned Wiki manifests and persistent reading libraries."""
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import unquote, urlsplit
import workbench_runtime as w

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

def read_item(path, kind, expected_id=None, expected_version=None, document_base=None, render_html=False):
    value=read_json(path)
    if not isinstance(value,dict) or value.get('schema')!=1 or value.get('kind')!=kind: raise ValueError('Manifest schema/kind does not match its location')
    for name,limit in [('id',200),('version',80),('revision',100),('title',200)]: string(value.get(name),name,limit)
    if not isinstance(value.get('summary',''),str) or len(value.get('summary',''))>1000: raise ValueError('Invalid summary')
    if expected_id is not None and value['id']!=expected_id: raise ValueError('Package ID differs from its directory')
    if expected_version is not None and value['version']!=expected_version: raise ValueError('Package version differs from its directory')
    if value.get('status') not in ('available','paused'): raise ValueError('Explicit available/paused status is required')
    section={'plugin':'skills','reference':'references','personal':'personal'}[kind]
    identity=[section,value['id'],value['version'],value['revision']]
    uid='ext-'+hashlib.sha256(json.dumps(identity,ensure_ascii=False).encode('utf-8')).hexdigest()[:16]
    item={key:value[key] for key in ('id','version','revision','title','status')}
    item.update(uid=uid,section=section,summary=value.get('summary',''),documents=[])
    # Paused packages are metadata-only: do not open, validate or hash their documents.
    if value['status']=='paused': return item
    base=ordinary(document_base or path.parent)
    docs=value.get('documents')
    if not isinstance(docs,list) or not 1<=len(docs)<=50: raise ValueError('Available entries need 1-50 documents')
    paths={}; seen=set()
    for doc in docs:
        if not isinstance(doc,dict) or not isinstance(doc.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,60}',doc['id']): raise ValueError('Invalid document id')
        if doc['id'] in seen: raise ValueError('Duplicate document id')
        seen.add(doc['id']); string(doc.get('title'),'document title')
        file=document_path(base,doc.get('path'))
        if file in paths: raise ValueError('Duplicate document path')
        paths[file]=doc['id']
    for doc in docs:
        file=document_path(base,doc['path'])
        source=file.read_text('utf-8-sig')
        if file.name=='SKILL.md' and source.startswith('---\n'):
            parts=source.split('\n---\n',1)
            if len(parts)==2 and re.search(r'^name:\s',parts[0],re.M): source=parts[1].lstrip('\n')
        if not render_html:
            item['documents'].append({'id':doc['id'],'title':doc['title'],'path':doc['path'],'markdown':source})
            continue
        import markdown
        from build_manual import slugify
        body=markdown.markdown(source,extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'slugify':slugify}})
        def rewrite(match):
            href=html.unescape(match[1]); u=urlsplit(href)
            if u.scheme or u.netloc or not u.path: return match[0]
            target=(file.parent/unquote(u.path)).resolve()
            if target in paths:
                return 'href="#'+uid+'-'+paths[target]+('--'+html.escape(unquote(u.fragment),quote=True) if u.fragment else '')+'"'
            return ''  # A standalone library includes only its declared documents.
        body=re.sub(r'href="([^"]*)"',rewrite,body)
        item['documents'].append({'id':doc['id'],'title':doc['title'],'html':body})
    if 'navigation' in value:
        from workbench_runtime import validate_navigation
        validate_navigation(value['navigation'],item['documents'])
        item['navigation']=value['navigation']
    return item

def legacy_items(user_area, registered, render_html):
    area=ordinary(user_area)
    if not area.is_dir(): raise ValueError('User area does not exist')
    items=[]
    plugins=area/'plugins'
    if plugins.exists():
        ordinary(plugins)
        for plugin in sorted(plugins.iterdir()):
            ordinary(plugin)
            if not plugin.is_dir() or ('plugin-guide',plugin.name) in registered: continue
            for version in sorted(plugin.iterdir()):
                ordinary(version)
                if not version.is_dir(): continue
                manifest=version/'wiki.json'
                if manifest.exists(): items.append(read_item(manifest,'plugin',plugin.name,version.name,render_html=render_html))
    addons=area/'addons'
    if addons.exists():
        ordinary(addons)
        for addon in sorted(addons.iterdir()):
            ordinary(addon)
            if not addon.is_dir() or ('addon',addon.name) in registered: continue
            if (addon/'state.json').exists(): continue
            catalog=addon/'wiki'
            if not catalog.exists(): continue
            ordinary(catalog)
            if not catalog.is_dir(): raise ValueError('Expected an addon Wiki directory')
            for manifest in sorted(catalog.glob('*.json')):
                # Adapter lives outside the checked version payload. It reads only
                # the selected package's declared Markdown; no install or activation.
                version=manifest.stem
                if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}',version) or version.endswith('.'):
                    raise ValueError('Invalid addon version directory')
                items.append(read_item(manifest,'reference',addon.name,version,addon/version,render_html))
    personal=area/'preferences/wiki.json'
    if personal.exists(): items.append(read_item(personal,'personal',render_html=render_html))
    return items

def portable_items(value):
    """A saved reading library never supplies the state of an installed package."""
    if (not isinstance(value, dict) or value.get('schema') not in (1, 2)
            or value.get('kind') != 'letsgal-wiki-library' or not isinstance(value.get('items'), list)
            or len(value['items']) > 200):
        raise ValueError('Expected a Wiki library with at most 200 editions')
    items = []
    seen = set()
    for row in value['items']:
        if not isinstance(row, dict):
            raise ValueError('Invalid Wiki item')
        if row.get('package_key') == 'personal/letsgal-personal':
            continue  # The editable personal space always belongs to this user area.
        item = {k:row[k] for k in ('uid','id','version','revision','section','title','summary','status')}
        for key,limit in [('id',200),('version',80),('revision',100),('title',200)]:
            string(item[key], key, limit)
        expected_uid = 'ext-' + w.sha(json.dumps([item[k] for k in ('section','id','version','revision')],ensure_ascii=False).encode())[:16]
        if (item['uid'] != expected_uid or item['uid'] in seen or item['section'] not in ('skills','references','personal')
                or item['status'] not in ('available','paused') or not isinstance(item['summary'],str) or len(item['summary'])>1000):
            raise ValueError('Invalid or duplicate Wiki identity')
        seen.add(item['uid'])
        visible = item['status']=='available' if value['schema']==1 else row.get('wiki_visible')
        if type(visible) is not bool:
            raise ValueError('Missing Wiki visibility')
        docs=row.get('documents')
        if not isinstance(docs,list) or len(docs)>50 or (visible and not docs):
            raise ValueError('Invalid Wiki document list')
        item.update(enabled=False,wiki_visible=visible,documents=[])
        ids=set()
        for doc in docs if visible else []:
            if not isinstance(doc,dict) or not isinstance(doc.get('id'),str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,60}',doc['id']) or doc['id'] in ids:
                raise ValueError('Invalid or duplicate document ID')
            ids.add(doc['id'])
            string(doc.get('title'),'document title',200)
            keys=[k for k in ('html','markdown') if k in doc]
            if len(keys)!=1 or not isinstance(doc[keys[0]],str) or len(doc[keys[0]])>1000000:
                raise ValueError('Invalid document body')
            clean={k:doc[k] for k in ('id','title',keys[0])}
            if 'path' in doc:
                path=doc['path']
                if not isinstance(path,str) or len(path)>1000 or not path or '\\' in path or ':' in path or PurePosixPath(path).is_absolute() or '..' in PurePosixPath(path).parts:
                    raise ValueError('Invalid document reference')
                clean['path']=path
            item['documents'].append(clean)
        if visible and 'navigation' in row:
            w.validate_navigation(row['navigation'],item['documents'])
            item['navigation']=row['navigation']
        items.append(item)
    return items


def complete(area, items, staged=None, render_html=False):
    registered={tuple(row['package_key'].split('/',1)) for row in items}
    legacy=legacy_items(area,registered,render_html)
    for row in legacy:
        row.update(enabled=row['status']=='available',wiki_visible=row['status']=='available')
    items.extend(legacy)
    authoritative={(row['section'],row['id']) for row in items if row.get('package_key')}
    identities={row['uid'] for row in items}
    if len(identities)!=len(items):
        raise ValueError('Duplicate Wiki identity in package manifests')
    directory=w.relative(area,'workbench/libraries')
    staged=staged or {}
    paths=set(directory.glob('*.json'))
    paths.update(p for p in staged if p.parent==directory and p.suffix=='.json')
    imported={}
    for path in sorted(paths):
        value=json.loads(staged[path].decode('utf-8-sig'),object_pairs_hook=w.unique) if path in staged else w.read_json(path)
        for row in portable_items(value):
            uid=row['uid']
            if (row['section'],row['id']) in authoritative or uid in identities:
                continue
            if uid in imported and imported[uid]!=row:
                raise ValueError('Reading libraries disagree on edition '+uid)
            imported[uid]=row
    items.extend(imported.values())
    if len(items)>200:
        raise ValueError('Too many Wiki editions')
    return {'schema':2,'kind':'letsgal-wiki-library','items':items}


def mount(area, value):
    rows=portable_items(value)
    with w.lock(area):
        staged={}
        current={r['uid']:r for r in w.collect(area)['items']}
        registered={(r['section'],r['id']) for r in current.values() if r.get('package_key')}
        for row in rows:
            uid=row['uid']
            if (row['section'],row['id']) in registered:
                continue
            path=w.relative(area,'workbench/libraries/'+uid+'.json')
            wrapped={'schema':2,'kind':'letsgal-wiki-library','items':[row]}
            if uid in current:
                old=portable_items({'schema':2,'kind':'letsgal-wiki-library','items':[current[uid]]})[0]
                if old!=row:
                    raise ValueError('A different copy of this edition is already mounted: '+uid)
                continue
            staged[path]=w.encode(wrapped)
        changes,report=w.refresh_changes(area,staged=staged)
        changes.update(staged)
        report['write']=w.commit_files(area,changes,'wiki-mount')
        report['added']=len(staged)
        return report

