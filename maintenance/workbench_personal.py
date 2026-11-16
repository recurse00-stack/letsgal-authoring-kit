"""User-owned personal pages. No package payload replacement or inferred memories."""
import json
import workbench_runtime as w

KEY = 'personal/letsgal-personal'
STATE = 'preferences/package-state.json'
MAX_DOCUMENT_BYTES = 1000000
DOCUMENTS = {
    'requirements': ('我的要求', 'preferences/user.md', '# 我的要求\n\n<!-- 在这里填写希望长期采用的要求与偏好。 -->\n'),
    'memory': ('长期记忆', 'preferences/memory.md', '# 长期记忆\n\n<!-- 在这里记录已经确认、希望长期保留的相关事实。 -->\n'),
    'guide': ('我的指南', 'preferences/guide.md', '# 我的指南\n\n<!-- 在这里编写自己的方法、创作约定或资料索引。 -->\n'),
}
UID = 'ext-' + w.sha(json.dumps(['personal','letsgal-personal','local','1'],ensure_ascii=False).encode())[:16]

def state(area, staged=None):
    path = w.relative(area, STATE)
    raw = staged.get(path) if staged and path in staged else w.read_bytes(path) if path.exists() else None
    if raw is None: return None
    value = json.loads(raw.decode('utf-8-sig'),object_pairs_hook=w.unique)
    if not isinstance(value,dict) or value.get('schema') != 1 or value.get('kind') != 'letsgal-personal-state':
        raise ValueError('Invalid personal package state')
    if set(value) != {'schema','kind','enabled','show_when_paused'} or any(type(value[k]) is not bool for k in ('enabled','show_when_paused')):
        raise ValueError('Invalid personal package settings')
    return value

def document_path(area, key):
    if key not in DOCUMENTS: raise ValueError('Unknown personal document')
    path=w.relative(area,DOCUMENTS[key][1])
    if key == 'requirements':
        legacy=w.relative(area,'user.md')
        if not path.exists() and legacy.exists():path=legacy
    return path

def seed_changes(area):
    changes={}
    if state(area) is None:
        changes[w.relative(area,STATE)]=w.encode({'schema':1,'kind':'letsgal-personal-state','enabled':True,'show_when_paused':False})
    for key,(_,_,initial) in DOCUMENTS.items():
        path=document_path(area,key)
        if not path.exists():changes[path]=initial.encode('utf-8')
    return changes

def document(area, key, staged=None):
    path=document_path(area,key)
    raw=staged.get(path) if staged and path in staged else w.read_bytes(path) if path.exists() else None
    if raw is not None and len(raw)>MAX_DOCUMENT_BYTES:raise ValueError('Personal document exceeds 1 MB')
    relative=path.relative_to(w.ordinary(area)).as_posix()
    fingerprint=w.sha(relative.encode()+b'\0'+(b'MISSING' if raw is None else raw))
    return {'id':key,'title':DOCUMENTS[key][0],'path':relative,'content':'' if raw is None else raw.decode('utf-8-sig'),
            'fingerprint':fingerprint,'exists':raw is not None}

def snapshot(area, key):
    value=state(area)
    if value is None:raise ValueError('Personal package is not initialized; rerun the main installer')
    result=document(area,key)
    canonical=w.relative(area,'preferences/user.md');legacy=w.relative(area,'user.md')
    result['legacy_notice']= bool(key=='requirements' and canonical.exists() and legacy.exists() and w.read_bytes(canonical)!=w.read_bytes(legacy))
    result['enabled']=value['enabled']
    return result

def catalog(area):
    value=state(area)
    if value is None:return None
    return {'key':KEY,'id':'letsgal-personal','title':'我的个人包','package_type':'personal',
        **{k:value[k] for k in ('enabled','show_when_paused')},'selection_mode':'personal','selected_version':None,
        'versions':[],'fingerprint':w.sha(w.read_bytes(w.relative(area,STATE))), 'state_path':STATE,'adapted':False,'editable':True}

def library_item(area, overrides=None, staged=None):
    value=(overrides or {}).get(KEY) or state(area,staged)
    if value is None:return None
    visible=value['enabled'] or value['show_when_paused']
    item={'uid':UID,'id':'letsgal-personal','version':'local','revision':'1','title':'我的个人包',
        'summary':'你的长期要求、已确认记忆和个人指南。','section':'personal','package_key':KEY,
        'status':'available' if value['enabled'] else 'paused','enabled':value['enabled'],'wiki_visible':visible,
        'selection_mode':'personal','selected_version':None,'editable':True,'documents':[]}
    if visible:
        item['documents']=[{'id':key,'title':DOCUMENTS[key][0],'markdown':document(area,key,staged)['content']} for key in DOCUMENTS]
        item['navigation']={'intro':'先写下自己的要求，再按需要积累记忆和指南。','start':'requirements',
            'groups':[{'title':'我的资料','documents':list(DOCUMENTS)}]}
    return item

def change(area, patch, expected):
    from workbench_packages import Conflict
    if not patch or set(patch)-{'enabled','show_when_paused'} or any(type(v) is not bool for v in patch.values()):
        raise ValueError('Personal packages support activation/display only')
    with w.lock(area):
        current=state(area);path=w.relative(area,STATE)
        if current is None:raise ValueError('Personal package is not initialized')
        if expected is not None and expected != w.sha(w.read_bytes(path)):raise Conflict('Personal package changed; refresh before saving')
        value={**current,**patch}
        changes,report=w.refresh_changes(area,overrides={KEY:value})
        changes[path]=w.encode(value)
        result=w.commit_files(area,changes,'personal-state')
    return {'state':result,'wiki':report,'enabled':value['enabled'],'selected_version':None,'show_when_paused':value['show_when_paused']}

def save(area, key, content, expected):
    from workbench_packages import Conflict
    if not isinstance(content,str) or len(content.encode('utf-8'))>MAX_DOCUMENT_BYTES or '\0' in content:
        raise ValueError('Personal content must be UTF-8 text within 1 MB')
    if not isinstance(expected,str):raise ValueError('Document fingerprint is required')
    with w.lock(area):
        if state(area) is None:raise ValueError('Personal package is not initialized')
        current=document(area,key)
        if current['fingerprint'] != expected:raise Conflict('Personal document changed; compare the saved copy before saving again')
        changes={document_path(area,key):content.encode('utf-8')}
        wiki_changes,report=w.refresh_changes(area,staged=changes);changes.update(wiki_changes)
        result=w.commit_files(area,changes,'personal-edit')
        saved=snapshot(area,key)
        if saved['content']!=content:raise ValueError('Personal document readback differs')
    return {'write':result,'wiki':report,'document':saved}

def resolve(area):
    value=state(area)
    if value is None:return {'status':'legacy','key':KEY,'entry':document_path(area,'requirements').relative_to(w.ordinary(area)).as_posix()}
    if not value['enabled']:return {'status':'paused','key':KEY}
    return {'status':'ready','key':KEY,'entry':document_path(area,'requirements').relative_to(w.ordinary(area)).as_posix(),
            'related':{k:v[1] for k,v in DOCUMENTS.items() if k!='requirements'},'state_path':STATE}
