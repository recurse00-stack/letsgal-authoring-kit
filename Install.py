"""Preview/install a declared optional LetsGal Skill package; no downloads."""
import argparse
import copy
import json
from pathlib import Path
import re
import shutil
import time
import uuid
import sys
sys.dont_write_bytecode=True
import workbench_runtime as w

def skill_name(path):
    source=w.read_bytes(path).decode('utf-8-sig').replace('\r\n','\n')
    front=re.match(r'\A---\n(.*?)\n---(?:\n|$)',source,re.S)
    names=re.findall(r'^name:\s*([^\n]+)\s*$',front[1],re.M) if front else []
    return names[0].strip().strip('\"\'') if len(names)==1 else None

def package(root):
    meta=w.read_json(root/'addon.json')
    if meta.get('schema')!=1 or meta.get('kind')!='letsgal-skill-addon' or meta.get('entry')!='SKILL.md':raise ValueError('Unsupported addon manifest')
    w.validate_meta(meta)
    payload=w.ordinary(root/'payload')
    files=w.checked_files(payload,meta.get('files'))
    if not {'SKILL.md','wiki-library.json'}<=files.keys() or w.file_map(payload)!=files:raise ValueError('Payload does not match the declared file manifest')
    if skill_name(payload/'SKILL.md')!=meta['id']:raise ValueError('Addon Skill identity differs from manifest')
    manual=meta.get('manual','docs/README.md')
    w.relative(payload,manual)
    if manual not in files:raise ValueError('Declared manual is missing from payload')
    w.validate_library(w.read_json(payload/'wiki-library.json'),meta)
    return meta,payload

def index_text(existing,meta):
    start='<!-- addon:'+meta['id']+':start -->';end='<!-- addon:'+meta['id']+':end -->'
    block=f"{start}\n## {meta['title']}\n\nID：`{meta['id']}`。启用状态、选用版本与文件清单以 [{meta['id']}/state.json]({meta['id']}/state.json) 为准；按相关任务读取所选版本的 `SKILL.md`。\n{end}"
    if start in existing or end in existing:
        if existing.count(start)!=1 or existing.count(end)!=1 or existing.index(end)<existing.index(start):raise ValueError('Malformed existing addon index block')
        a=existing.index(start);b=existing.index(end)+len(end)
        return existing[:a]+block+existing[b:]
    if meta['id'] in existing:raise ValueError('Existing legacy index mentions this addon; review its selection/pause before migrating')
    return existing.rstrip()+'\n\n'+block+'\n'

def install(root,skills_root,area,apply=False,replace=False,select=False,enable=False):
    root=w.ordinary(root);skills_root=w.ordinary(skills_root);area=w.ordinary(area)
    if area.parent==area or area==root or area.is_relative_to(root) or root.is_relative_to(area):raise ValueError('User area and package source must not overlap or use a drive root')
    meta,payload=package(root)
    main_root=w.ordinary(skills_root/'letsgal-authoring')
    main_entry=w.ordinary(main_root/'SKILL.md')
    integrated=False
    if main_root.exists():
        if skill_name(main_entry)!='letsgal-authoring':raise ValueError('Main Skill directory has conflicting identity; no files changed')
        integrated=True
    target=w.relative(area,'addons/'+meta['id']+'/'+meta['version']) if integrated else w.relative(skills_root,meta['id'])
    if target==payload or target.is_relative_to(root) or root.is_relative_to(target):raise ValueError('Install destination overlaps package source')
    current=w.file_map(target) if target.exists() else None
    changed=current!=meta['files']
    if current is not None and changed and not replace:raise ValueError('Existing payload differs; use --replace only after reviewing the backup/replacement scope')
    state_path=w.relative(area,'addons/'+meta['id']+'/state.json')
    index_path=w.relative(area,'addons/INDEX.md')
    state=None;old_index=None;proposed_index=None
    if integrated:
        if state_path.exists():_,state=w.load_state(area,meta['id'])
        else:state={'schema':1,'id':meta['id'],'enabled':True,'selected_version':meta['version'],'versions':{}}
        state=copy.deepcopy(state)
        state['versions'][meta['version']]={key:meta[key] for key in ('revision','title','summary','section','entry','files')}
        if select:state['selected_version']=meta['version']
        if enable:state['enabled']=True
        old_index=w.read_bytes(index_path) if index_path.exists() else None
        proposed_index=index_text(old_index.decode('utf-8-sig') if old_index else '# 可选附属包\n',meta).encode('utf-8')
    report={'status':'preview','mode':'integrated' if integrated else 'standalone','id':meta['id'],'version':meta['version'],'revision':meta['revision'],'target':str(target),'payload':'changed' if changed else 'verified-unchanged','backup_required':current is not None and changed,'wiki':'automatic' if integrated else 'standalone manual','source_modified':False}
    if integrated and (skills_root/meta['id']).exists():report['other_entry']=str(skills_root/meta['id'])
    if not apply:return report
    with w.lock(area):
        if (w.file_map(target) if target.exists() else None)!=current:raise ValueError('Target changed after preview')
        if integrated:
            if (w.read_bytes(index_path) if index_path.exists() else None)!=old_index:raise ValueError('Index changed after preview')
            # Recheck registry under the same operation lock.
            if state_path.exists():
                _,live=w.load_state(area,meta['id'])
                check=copy.deepcopy(state);check['versions']=dict(live['versions']);check['versions'][meta['version']]=state['versions'][meta['version']]
                if not select:check['selected_version']=live['selected_version']
                if not enable:check['enabled']=live['enabled']
                state=check
        stamp=time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:8]
        stage=None;backup=None;placed=False
        try:
            if changed:
                target.parent.mkdir(parents=True,exist_ok=True)
                stage=w.ordinary(target.with_name('.'+target.name+'-stage-'+uuid.uuid4().hex))
                stage.mkdir()
                for name in meta['files']:
                    dest=w.relative(stage,name);dest.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copyfile(w.relative(payload,name),dest)
                if w.file_map(stage)!=meta['files']:raise ValueError('Staged payload verification failed')
                if current is not None:
                    backup=w.relative(area,'backups/'+stamp+'-'+meta['id']+'/payload')
                    backup.parent.mkdir(parents=True)
                    # Cross-volume installs use copy+verification before exact old-tree removal.
                    shutil.copytree(target,backup)
                    if w.file_map(backup)!=current:raise ValueError('Backup verification failed')
                    if w.file_map(target)!=current:raise ValueError('Target changed during backup')
                    shutil.rmtree(target)
                stage.rename(target);stage=None;placed=True
                if w.file_map(target)!=meta['files']:raise ValueError('Installed payload verification failed')
            if integrated:
                changes,wiki=w.refresh_changes(area,overrides={meta['id']:state})
                changes.update({state_path:w.encode(state),index_path:proposed_index})
                report['registration']=w.commit_files(area,changes,'addon-register')
                report['wiki']=wiki
                report['enabled']=state['enabled'];report['selected_version']=state['selected_version']
            else:report['wiki']={'status':'standalone','path':str(target/meta.get('manual','docs/README.md'))}
        except Exception:
            if placed and target.exists():
                if w.file_map(target)!=meta['files']:raise ValueError('Unexpected installed edits; retained target and backup for recovery')
                shutil.rmtree(target)
            if backup and backup.exists() and not target.exists():shutil.copytree(backup,target)
            raise
        finally:
            if stage and stage.exists():
                if not stage.name.startswith('.'+target.name+'-stage-') or stage.parent!=target.parent:raise ValueError('Unexpected staging path')
                shutil.rmtree(stage)
        report.update(status='installed' if changed else 'verified-unchanged',backup=str(backup) if backup else None)
        return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--skills-root',type=Path,default=Path.home()/'.codex/skills')
    parser.add_argument('--user-area',type=Path,default=Path.home()/'.letsgal-authoring')
    for name in ('install','replace','select','enable'):parser.add_argument('--'+name,action='store_true')
    args=parser.parse_args()
    try:
        result=install(args.package,args.skills_root,args.user_area,args.install,args.replace,args.select,args.enable)
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'error','message':str(error)},ensure_ascii=False));return 1

if __name__=='__main__':raise SystemExit(main())
