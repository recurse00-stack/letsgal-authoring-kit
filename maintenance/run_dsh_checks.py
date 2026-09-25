"""DSH adapter and official provider checks. Uses only a NEW isolated --scratch folder."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--scratch',type=Path,required=True)
p.add_argument('--provider',type=Path,required=True)
args=p.parse_args()
if not args.scratch.is_absolute() or args.scratch.exists() or not args.provider.is_file():
    p.error('Provide a NEW absolute scratch path and an installed provider lib/index.js')
root=args.scratch
root.mkdir()
bundle=Path(__file__).resolve().parents[1]
checks=[]
def record(name,ok):
    checks.append({'name':name,'passed':bool(ok)})
    if not ok:
        raise AssertionError(name)
for shell in filter(None,[shutil.which('powershell.exe'),shutil.which('pwsh.exe')]):
    fixture=root/Path(shell).stem
    fixture.mkdir()
    home=fixture/"user's home 测试"
    home.mkdir()
    data=fixture/'custom dsh data'
    data.mkdir()
    project=fixture/'project'
    nested=project/'chapters'/'nested'
    nested.mkdir(parents=True)
    (project/'.git').write_text('gitdir: fixture-only\n','utf-8')
    rules=project/'LETSGAL.md'
    rules.write_bytes(b'Project preferences.\n')
    env=dict(os.environ)
    env.pop('DSH_HOME',None)
    def run(*extra,environment=env):
        result=subprocess.run([shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(bundle/'Install.ps1'),'-Harness','DSH','-UserHome',str(home),'-NonInteractive',*extra],env=environment,capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stdout.decode('utf-8','replace')+result.stderr.decode('utf-8','replace'))
    run('-Scope','User')
    record(Path(shell).stem+' default DSH home',(home/'.dsh/skills/letsgal-authoring/SKILL.md').exists())
    custom_env=dict(env,DSH_HOME=str(data))
    run('-Scope','User',environment=custom_env)
    record(Path(shell).stem+' DSH_HOME environment',(data/'skills/letsgal-authoring/SKILL.md').exists())
    profile=home/'.letsgal-authoring/preferences/user.md'
    profile.write_bytes(b'Keep my preferences exactly.\n')
    run('-Scope','User','-DshHome',str(data),environment=dict(env,DSH_HOME=str(fixture/'unused-env')))
    record(Path(shell).stem+' explicit home overrides env',not (fixture/'unused-env').exists())
    run('-Scope','Project','-ProjectPath',str(nested))
    record(Path(shell).stem+' Git root and customizations',(project/'.dsh/skills/letsgal-authoring/SKILL.md').exists() and profile.read_bytes()==b'Keep my preferences exactly.\n' and rules.read_bytes()==b'Project preferences.\n')
    def probe(mode):
        result=subprocess.run([shutil.which('node'),str(bundle/'maintenance/check_dsh_provider.mjs'),str(args.provider),str(fixture),mode],capture_output=True)
        if result.returncode:
            raise RuntimeError(result.stderr.decode('utf-8','replace'))
        report=json.loads(result.stdout)
        for entry in report['checks']:
            record(Path(shell).stem+' '+mode+' '+entry['name'],entry['passed'])
    probe('installed')
    run('-Scope','User','-DshHome',str(data),'-Action','Uninstall')
    probe('uninstalled')
    record(Path(shell).stem+' uninstall keeps profile',profile.read_bytes()==b'Keep my preferences exactly.\n')
report={'checks':checks,'passed':len(checks),'failed':0,'scope':'Isolated official DSH filesystem provider; no live session/model/server acceptance.'}
(root/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
