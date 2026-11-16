"""Package registry adapters. State changes never modify installed payloads."""
import argparse
import copy
import json
from pathlib import Path
import re
import sys
import workbench_runtime as w
import workbench_personal as personal

KINDS = ('addon', 'plugin-guide')  # External registration types; personal is built in.


class Conflict(ValueError):
    pass


def identity(kind, package_id):
    if kind not in KINDS:
        raise ValueError('Unknown package kind')
    if not isinstance(package_id, str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,199}', package_id):
        raise ValueError('Invalid package ID')
    w.relative(Path.cwd(), package_id)
    return kind + '/' + package_id


def split_key(key):
    if not isinstance(key, str) or key.count('/') != 1:
        raise ValueError('Expected kind/id package key')
    kind, package_id = key.split('/')
    identity(kind, package_id)
    return kind, package_id


def adapter_path(area, key):
    kind, package_id = split_key(key)
    return w.relative(area, 'workbench/packages/' + kind + '/' + package_id + '/state.json')


def check_settings(value, kind):
    if type(value.get('enabled')) is not bool or type(value.get('show_when_paused', False)) is not bool:
        raise ValueError('Package state requires boolean activation/display settings')
    mode = value.get('selection_mode', 'fixed')
    if mode not in ('fixed', 'auto') or (mode == 'auto' and kind != 'plugin-guide'):
        raise ValueError('Automatic version matching is for plugin guides')
    if mode == 'fixed' and value.get('selected_version') not in value.get('versions', {}):
        raise ValueError('Selected version is not installed')
    if mode == 'auto' and value.get('selected_version') is not None:
        raise ValueError('Automatic matching must not pin a version')


def validate_adapter(area, value):
    if not isinstance(value,dict) or value.get('schema') != 1 or value.get('kind') != 'letsgal-package-state':
        raise ValueError('Unsupported package state')
    key = identity(value.get('package_type'), value.get('id'))
    versions = value.get('versions')
    if not isinstance(versions, dict) or not versions:
        raise ValueError('No registered versions')
    check_settings(value, value['package_type'])
    for version, record in versions.items():
        if not isinstance(record,dict):raise ValueError('Invalid version record')
        w.token(version, True)
        prefix = 'plugins' if value['package_type'] == 'plugin-guide' else 'addons'
        expected = prefix + '/' + value['id'] + '/' + version
        if record.get('root') != expected or record.get('entry') != 'SKILL.md':
            raise ValueError('Package root/entry differs from its identity')
        root = w.relative(area, expected)
        if not root.is_dir():
            raise ValueError('Registered payload directory is missing')
        w.validate_meta(dict(record, id=value['id'], version=version), ('references','skills','personal'))
        files = w.checked_files(root, record.get('files'))
        if 'SKILL.md' not in files or not re.fullmatch('[a-f0-9]{64}', record.get('wiki_sha256', '')):
            raise ValueError('Missing package entry/Wiki checksum')
    return key


def records(area, overrides=None):
    """Return one authority per package. Read metadata only, including paused packages."""
    area = w.ordinary(area)
    result = {}
    addons = w.relative(area, 'addons')
    if addons.exists():
        for folder in sorted(addons.iterdir()):
            w.ordinary(folder)
            if not folder.is_dir() or not (folder / 'state.json').exists():
                continue
            path, value = w.load_state(area, folder.name)
            key = identity('addon', folder.name)
            if overrides and key in overrides:
                value = overrides[key]
            check_settings(value, 'addon')
            result[key] = (path, value, False)
    adapters = w.relative(area, 'workbench/packages')
    if adapters.exists():
        for kind_dir in sorted(adapters.iterdir()):
            w.ordinary(kind_dir)
            if not kind_dir.is_dir() or kind_dir.name not in KINDS:
                continue
            for folder in sorted(kind_dir.iterdir()):
                w.ordinary(folder)
                if not folder.is_dir() or not (folder / 'state.json').exists():
                    continue
                key = identity(kind_dir.name, folder.name)
                path = adapter_path(area, key)
                value = overrides[key] if overrides and key in overrides else w.read_json(path)
                if validate_adapter(area, value) != key or key in result:
                    raise ValueError('Duplicate or conflicting package registration: ' + key)
                result[key] = (path, value, True)
    if overrides:
        for key, value in overrides.items():
            if key == personal.KEY:
                continue  # The built-in user-owned package has its own state contract.
            if key not in result:
                if value.get('kind') == 'letsgal-package-state':
                    validate_adapter(area, value)
                    result[key] = (adapter_path(area, key), value, True)
                else:
                    kind, package_id = split_key(key)
                    if kind != 'addon':
                        raise ValueError('Invalid native package')
                    check_settings(value, kind)
                    result[key] = (w.relative(area, 'addons/' + package_id + '/state.json'), value, False)
    return result


def catalog(area):
    items = []
    for key, (path, state, adapted) in records(area).items():
        versions = [{'version':v, **{k:r[k] for k in ('revision','title','summary','section')}} for v,r in state['versions'].items()]
        items.append({'key':key, 'id':state['id'], 'package_type':key.split('/')[0],
            'title':versions[0]['title'], 'enabled':state['enabled'],
            'show_when_paused':state.get('show_when_paused', False),
            'selection_mode':state.get('selection_mode', 'fixed'), 'selected_version':state.get('selected_version'),
            'versions':versions, 'fingerprint':w.sha(w.read_bytes(path)),
            'state_path':path.relative_to(area).as_posix(), 'adapted':adapted})
    own=personal.catalog(area)
    if own is not None:items.append(own)
    return {'schema':1, 'kind':'letsgal-package-catalog', 'items':items}


def library(area, overrides=None, staged=None):
    items = []
    for key, (path, state, adapted) in records(area, overrides).items():
        visible = state['enabled'] or state.get('show_when_paused', False)
        for version, record in state['versions'].items():
            meta = dict(record, id=state['id'], version=version)
            if visible:
                wiki = path.parent / version / 'wiki-library.json' if adapted else path.parent / version / 'wiki-library.json'
                raw = staged[wiki] if staged and wiki in staged else w.read_bytes(wiki)
                digest = record['wiki_sha256'] if adapted else record['files']['wiki-library.json']
                if w.sha(raw) != digest:
                    raise ValueError('Registered Wiki changed: ' + key)
                item = copy.deepcopy(w.validate_library(json.loads(raw.decode('utf-8-sig'), object_pairs_hook=w.unique), meta))
            else:
                item = {k:meta[k] for k in ('id','version','revision','title','summary','section')}
                item.update(uid='ext-'+w.sha(json.dumps([meta[k] for k in ('section','id','version','revision')],ensure_ascii=False).encode())[:16], documents=[])
            item.update(package_key=key, enabled=state['enabled'], wiki_visible=visible,
                selection_mode=state.get('selection_mode','fixed'), selected_version=state.get('selected_version'),
                status='available' if state['enabled'] else 'paused',
                selected=state['enabled'] and state.get('selection_mode','fixed') == 'fixed' and version == state.get('selected_version'))
            items.append(item)
    own=personal.library_item(area,overrides,staged)
    if own is not None:items.append(own)
    if len(items) > 200:
        raise ValueError('Too many registered Wiki versions')
    identities = [x['uid'] for x in items]
    if len(set(identities)) != len(identities):
        raise ValueError('Duplicate Wiki identities')
    return {'schema':2, 'kind':'letsgal-wiki-library', 'items':items}


def change(area, key, patch, expected=None):
    if key==personal.KEY:return personal.change(area,patch,expected)
    if not isinstance(patch,dict) or not patch or set(patch)-{'enabled','show_when_paused','selected_version','selection_mode'}:
        raise ValueError('Unsupported state change')
    with w.lock(area):
        row = records(area).get(key)
        if row is None:
            raise ValueError('Package is not registered')
        path, current, adapted = row
        if expected is not None and expected != w.sha(w.read_bytes(path)):
            raise Conflict('Package changed in another window; refresh before saving')
        value = copy.deepcopy(current)
        value.update(patch)
        check_settings(value, key.split('/')[0])
        if adapted:
            validate_adapter(area, value)
        changes, report = w.refresh_changes(area, overrides={key:value})
        changes[path] = w.encode(value)
        result = w.commit_files(area, changes, 'package-state')
    return {'state':result, 'wiki':report, 'enabled':value['enabled'],
        'selected_version':value.get('selected_version'), 'show_when_paused':value.get('show_when_paused',False)}


def register(area, declaration, apply=False, replace=False):
    """Register an already installed package from explicit precompiled Wiki data."""
    if not isinstance(declaration,dict) or declaration.get('schema') != 1 or declaration.get('kind') != 'letsgal-package-registration':
        raise ValueError('Unsupported registration manifest')
    kind, package_id = declaration.get('package_type'), declaration.get('id')
    key = identity(kind, package_id)
    path = adapter_path(area, key)
    versions = declaration.get('versions')
    if not isinstance(versions, dict) or not versions:
        raise ValueError('No declared versions')
    with w.lock(area) if apply else readonly():
        existing = records(area).get(key)
        if existing and not existing[2]:
            raise ValueError('Package already has native state; use that authority')
        proposed = copy.deepcopy(existing[1]) if existing else {
            'schema':1,'kind':'letsgal-package-state','package_type':kind,'id':package_id,
            'enabled':declaration.get('enabled'), 'show_when_paused':declaration.get('show_when_paused',False),
            'selection_mode':declaration.get('selection_mode', 'auto' if kind=='plugin-guide' else 'fixed'),
            'selected_version':declaration.get('selected_version'), 'versions':{}}
        changes = {}
        for version, supplied in versions.items():
            if not isinstance(supplied,dict):raise ValueError('Invalid version declaration')
            w.token(version, True)
            record = copy.deepcopy(supplied)
            wiki = record.pop('wiki_library',None)
            meta = dict(record,id=package_id,version=version)
            w.validate_library(wiki, meta)
            raw = w.encode(wiki)
            record['wiki_sha256'] = w.sha(raw)
            proposed['versions'][version] = record
            cache = w.relative(area, path.parent.relative_to(area).as_posix()+'/'+version+'/wiki-library.json')
            changes[cache] = raw
        validate_adapter(area, proposed)
        for version, record in proposed['versions'].items():
            root = w.relative(area, record['root'])
            if w.file_map(root) != record['files']:
                raise ValueError('Installed file set differs from registration: '+key+'/'+version)
            front=w.read_bytes(root/'SKILL.md').decode('utf-8-sig')
            match=re.match(r'\A---\r?\n(.*?)\r?\n---',front,re.S)
            if not match or not re.search(r'^name:\s*\S+',match[1],re.M):
                raise ValueError('Missing Skill identity')
        if existing:
            for version in versions:
                old = existing[1]['versions'].get(version)
                if old and old != proposed['versions'][version] and not replace:
                    raise ValueError('Registered version differs; preserve it and register a new version')
        report={'status':'preview','key':key,'versions':list(proposed['versions']),
            'enabled':proposed['enabled'],'selected_version':proposed.get('selected_version'),
            'payload':'verified-unchanged','state_path':path.relative_to(area).as_posix()}
        if not apply:
            return report
        changes[path] = w.encode(proposed)
        index_path=w.relative(area,('plugins' if kind=='plugin-guide' else 'addons')+'/INDEX.md')
        existing_index=w.read_bytes(index_path).decode('utf-8-sig') if index_path.exists() else '# 已登记资料包\n'
        start='<!-- package:'+key+':start -->';end='<!-- package:'+key+':end -->'
        title=' '.join(next(iter(proposed['versions'].values()))['title'].split())
        block=start+'\n## '+title+'\n\nID：`'+package_id+'`。AI 启停、选版和 Wiki 展示以[包管理状态](../'+path.relative_to(area).as_posix()+')为准。\n'+end
        if start in existing_index or end in existing_index:
            if existing_index.count(start)!=1 or existing_index.count(end)!=1 or existing_index.index(start)>existing_index.index(end):
                raise ValueError('Malformed package navigation block')
            a=existing_index.index(start);b=existing_index.index(end)+len(end)
            updated_index=existing_index[:a]+block+existing_index[b:]
        else:updated_index=existing_index.rstrip()+'\n\n'+block+'\n'
        changes[index_path]=updated_index.encode('utf-8')
        wiki_changes, wiki_report = w.refresh_changes(area, overrides={key:proposed}, staged=changes)
        changes.update(wiki_changes)
        result = w.commit_files(area,changes,'package-register')
        return dict(report,status=result['status'],write=result,wiki=wiki_report)


from contextlib import nullcontext as readonly


def resolve(area, key, actual_version=None):
    """Metadata-only lookup for AI. Wiki display settings never enable a Skill."""
    if key==personal.KEY:return personal.resolve(area)
    row=records(area).get(key)
    if row is None:
        return {'status':'unregistered','key':key}
    _,state,adapted=row
    if not state['enabled']:
        return {'status':'paused','key':key}
    kind,package_id=split_key(key)
    version=actual_version if state.get('selection_mode')=='auto' else state.get('selected_version')
    if kind=='plugin-guide' and (not actual_version or version!=actual_version):
        return {'status':'version-mismatch' if actual_version else 'version-required','key':key,'selected_version':version,'actual_version':actual_version}
    if version not in state['versions']:
        return {'status':'no-matching-version','key':key,'actual_version':actual_version}
    record=state['versions'][version]
    root=record['root'] if adapted else 'addons/'+package_id+'/'+version
    return {'status':'ready','key':key,'version':version,'revision':record['revision'],
        'entry':root+'/'+record['entry'],'state_fingerprint':w.sha(w.read_bytes(row[0]))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['list','register','resolve'])
    parser.add_argument('--user-area',type=Path,required=True)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--replace',action='store_true',help='Back up and replace a reviewed registration revision; payloads are never written')
    parser.add_argument('--key');parser.add_argument('--actual-version')
    args=parser.parse_args()
    try:
        area=w.ordinary(args.user_area)
        if args.command=='list':result=catalog(area)
        elif args.command=='register':
            if not args.manifest:raise ValueError('--manifest is required')
            result=register(area,w.read_json(args.manifest),args.apply,args.replace)
        else:result=resolve(area,args.key,args.actual_version)
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'error','message':str(error)},ensure_ascii=False));return 1


if __name__=='__main__':raise SystemExit(main())
