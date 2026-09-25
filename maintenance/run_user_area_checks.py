"""Verify user-owned bytes survive installs, real upgrades and failures in NEW isolated homes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--scratch',type=Path,required=True)
p.add_argument('--previous-bundle',type=Path,required=True)
args=p.parse_args()
if not args.scratch.is_absolute() or args.scratch.exists():
    p.error('Use a NEW absolute scratch directory')
previous=args.previous_bundle.resolve()
previous_manifest=json.loads((previous/'bundle.json').read_text('utf-8'))
previous_version=previous_manifest['version']
if previous_manifest.get('owner')!='letsgal-authoring-kit':
    p.error('Provide an unmodified previous release of this kit')
bundle=Path(__file__).resolve().parents[1]
version=json.loads((bundle/'bundle.json').read_text('utf-8'))['version']
if version==previous_version: p.error('The upgrade baseline must be a different release')
args.scratch.mkdir()
checks=[]

def snapshot(root):
    return {f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest()
            for f in root.rglob('*') if f.is_file()}

def user_snapshot(root):
    # installer-state.json belongs to the importer and records UI choices; all other files are user-owned.
    return {name:sha for name,sha in snapshot(root).items() if name!='installer-state.json'}

def record(name,ok):
    checks.append({'name':name,'passed':bool(ok)})
    if not ok: raise AssertionError(name)

def fixtures(area):
    for version_name in ['1.0.0','2.0.0-beta.1']:
        folder=area/'plugins/example.plugin'/version_name
        folder.mkdir(parents=True)
        (folder/'SKILL.md').write_bytes(('User-owned plugin Skill '+version_name+'\r\n').encode())
        (folder/'private-notes.bin').write_bytes(bytes(range(256)))
    (area/'plugins/INDEX.md').write_bytes(b'User plugin index; keep custom paragraphs.\r\n')

for shell in filter(None,[shutil.which('powershell.exe'),shutil.which('pwsh.exe')]):
    label=Path(shell).stem
    root=args.scratch/label
    root.mkdir()
    def run(home,action='Install',source=bundle):
        result=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(source/'Install.ps1'),
                               '-Harness','Codex','-Scope','User','-UserHome',str(home),'-Action',action,'-NonInteractive'],capture_output=True)
        rows=result.stdout.decode('utf-8','replace').splitlines()
        parsed=[json.loads(s) for s in rows if s.startswith('{')]
        return result.returncode,parsed[-1] if parsed else {}
    home=root/"new user's home 测试"; home.mkdir()
    area=home/'.letsgal-authoring'; target=home/'.agents/skills/letsgal-authoring'
    code,result=run(home,'Check')
    record(label+' first check is read-only',code==2 and not area.exists() and not (home/'.agents').exists())
    code,result=run(home)
    profile=area/'preferences/user.md'
    record(label+' fresh install separates preference and plugin areas',code==0 and profile.is_file() and (area/'plugins').is_dir() and not (area/'user.md').exists() and Path(result['profile'])==profile and Path(result['plugins'])==area/'plugins')
    profile.write_bytes('个人偏好原文，保留编码与换行。\r\n'.encode('utf-8'))
    fixtures(area)
    (area/'user-notes.txt').write_bytes(b'Unmanaged user file.\n')
    outside=root/'plugin-code'; outside.mkdir(); (outside/'source.ts').write_bytes(b'// User plugin source, do not modify.\n')
    before=user_snapshot(area); source_before=snapshot(outside)
    code,result=run(home)
    record(label+' repeat install preserves every user-owned byte',code==0 and result['action']=='already_current' and user_snapshot(area)==before and snapshot(outside)==source_before)
    code,result=run(home,'Check')
    record(label+' check never rewrites user files',code==0 and user_snapshot(area)==before)
    code,result=run(home,'Uninstall')
    record(label+' uninstall preserves preferences all plugin versions and source',code==0 and not target.exists() and Path(result['backup']).is_dir() and user_snapshot(area)==before and snapshot(outside)==source_before)
    code,result=run(home)
    record(label+' reinstall preserves existing user area',code==0 and user_snapshot(area)==before)

    old_home=root/'upgrading old home'; old_home.mkdir()
    old_area=old_home/'.letsgal-authoring'; old_area.mkdir()
    legacy=old_area/'user.md'; legacy.write_bytes(b'Legacy personal choices remain active.\r\n')
    fixtures(old_area)
    code,result=run(old_home,source=previous)
    old_target=old_home/'.agents/skills/letsgal-authoring'
    old_skill=snapshot(old_target); old_user=user_snapshot(old_area)
    record(label+' real '+previous_version+' baseline installed',code==0 and json.loads((old_target/'.install-receipt.json').read_text('utf-8'))['version']==previous_version)
    code,result=run(old_home)
    record(label+' real version upgrade succeeds with complete old backup',code==0 and json.loads((old_target/'.install-receipt.json').read_text('utf-8'))['version']==version and snapshot(Path(result['backup']))==old_skill)
    record(label+' upgrade preserves legacy preferences and all plugin files',user_snapshot(old_area)==old_user and Path(result['profile'])==legacy)
    record(label+' upgrade cannot shadow legacy preferences with blank defaults',not (old_area/'preferences/user.md').exists() and (old_area/'preferences').is_dir())

    canonical=old_area/'preferences/user.md'; canonical.write_bytes(b'New preferences with a deliberate conflict.\n')
    both=user_snapshot(old_area)
    code,result=run(old_home)
    record(label+' coexisting preferences stay intact and new path is reported',code==0 and Path(result['profile'])==canonical and user_snapshot(old_area)==both)

    # Corrupted source must stop before changing either public Skill or user area.
    bad_bundle=root/'corrupt bundle'; shutil.copytree(bundle,bad_bundle)
    (bad_bundle/'skills/letsgal-authoring/SKILL.md').write_bytes(b'CORRUPTED MANIFEST CONTENT')
    intact_skill=snapshot(old_target); intact_user=user_snapshot(old_area)
    code,result=run(old_home,source=bad_bundle)
    record(label+' failed update preserves existing skill preferences and plugins',code!=0 and snapshot(old_target)==intact_skill and user_snapshot(old_area)==intact_user)
    (old_target/'user-extra.txt').write_bytes(b'User edit inside public Skill.\n')
    edited=snapshot(old_target)
    code,result=run(old_home)
    record(label+' modified public skill stops without backup consent or user changes',code!=0 and result.get('requires_backup') and snapshot(old_target)==edited and user_snapshot(old_area)==intact_user)

    for case in ['preferences-file','profile-directory','plugins-file']:
        h=root/case; a=h/'.letsgal-authoring'; a.mkdir(parents=True)
        if case=='profile-directory': (a/'preferences/user.md').mkdir(parents=True)
        else: (a/('preferences' if case=='preferences-file' else 'plugins')).write_bytes(b'User-owned object; never replace.')
        saved=snapshot(h)
        code,result=run(h)
        record(label+' '+case+' rejects before target mutation',code!=0 and snapshot(h)==saved and not (h/'.agents').exists())

report={'version':version,'checks':checks,'passed':len(checks),'failed':0,
        'previous_version':previous_version,
        'scope':'Isolated real previous-release upgrade and byte-preservation tests; no private homes or plugin code execution.'}
(args.scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'passed':len(checks),'failed':0}))
