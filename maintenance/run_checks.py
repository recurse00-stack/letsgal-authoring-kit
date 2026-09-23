"""Run isolated checks. Supply a NEW absolute --scratch directory. Never uses real AI homes."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def run(bundle, scratch):
    scratch.mkdir(parents=True, exist_ok=False)
    results = []
    skill = bundle / 'skills' / 'letsgal-authoring'
    checker = skill / 'scripts' / 'check_project.py'
    example = json.loads((skill / 'examples' / '选择练习.json').read_text('utf-8'))

    def record(name, ok, detail=''):
        results.append({'name': name, 'passed': bool(ok), 'detail': detail})

    def hashes(root):
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*') if p.is_file() and not p.is_symlink()}

    def check_json(name, data, expected, raw=None, project=False):
        fixture = scratch / name
        fixture.mkdir()
        if project:
            chapters = fixture / 'chapters'
            chapters.mkdir()
            (fixture/'project.json').write_text(json.dumps({'chapterOrder':['选择练习']}), 'utf-8')
            file = chapters / '选择练习.json'
            target = fixture
        else:
            file = fixture / '选择练习.json'
            target = file
        file.write_text(raw if raw is not None else json.dumps(data, ensure_ascii=False), encoding='utf-8')
        before = hashes(fixture)
        p = subprocess.run([sys.executable, '-B', str(checker), str(target)], capture_output=True)
        try:
            report = json.loads(p.stdout.decode('utf-8'))
        except Exception:
            report = {}
        record(name, p.returncode == expected and hashes(fixture) == before and 'status' in report,
               'exit=%d; read-only=%s; status=%s' % (p.returncode, before==hashes(fixture), report.get('status')))

    check_json('valid-project', example, 0, project=True)
    check_json('valid-standalone', example, 0)
    value = copy.deepcopy(example)
    value['fragments'][0]['blocks'][1]['props']['choices'] = []
    check_json('array-instead-of-json-string', value, 1)
    value = copy.deepcopy(example)
    value['fragments'][0]['blocks'][1]['props']['choices'] = '[{"mode":"jump","text":"x","fragmentId":"missing"}]'
    check_json('broken-fragment-target', value, 1)
    value = copy.deepcopy(example)
    value['fragments'][1]['blocks'].append({'type':'callFragment','props':{'fragmentId':value['fragments'][1]['id']}})
    check_json('fragment-cycle', value, 1)
    value = copy.deepcopy(example)
    value['fragments'][1]['id'] = value['fragments'][2]['id']
    check_json('duplicate-id', value, 1)
    value = copy.deepcopy(example)
    value['fragments'][0]['blocks'].append({'type':'futureInstruction','props':{'future':True}})
    check_json('unknown-instruction-preserved', value, 0)
    check_json('duplicate-json-keys', {}, 1, raw='{"id":"a","id":"b"}')
    check_json('nonfinite-json', {}, 1, raw='{"x":NaN}')
    value = copy.deepcopy(example)
    value['fragments'][0]['blocks'][0]['props']['disabled'] = 'true'
    check_json('wrong-boolean-type', value, 1)
    value = copy.deepcopy(example)
    value['fragments'][0]['blocks'][0]['type'] = {'unexpected':1}
    check_json('malformed-type-does-not-crash', value, 1)
    value = copy.deepcopy(example)
    value['fragments'][0]['metadata'] = {'future':{'preserve':['yes']}}
    check_json('unknown-metadata-preserved', value, 0)

    # Link integrity without invoking network or reading any author projects.
    missing = []
    for file in bundle.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', file.read_text('utf-8')):
            if '://' in target or target.startswith('#') or '<' in target:
                continue
            if not (file.parent / target.split('#')[0]).exists():
                missing.append(file.name+':'+target)
    record('local-markdown-links', not missing, str(missing))
    private = []
    for file in skill.rglob('*'):
        if file.is_file() and file.suffix in {'.md','.py','.yaml','.json'}:
            if re.search(r'(?i)(?<![A-Z])[A-Z]:[/\\]|/home/[^/< ]+/', file.read_text('utf-8')):
                private.append(str(file.relative_to(skill)))
    record('no-personal-paths-or-private-project-dependencies', not private, str(private))

    shells = [p for p in (shutil.which('powershell.exe'), shutil.which('pwsh.exe')) if p]
    if not shells:
        record('windows-installer-runtime', False, 'Windows PowerShell is unavailable; cannot verify')
    for shell in shells:
        label = Path(shell).stem
        home = scratch / (label + " user's home 测试")
        home.mkdir()
        profile = home / '.letsgal-authoring' / 'user.md'
        profile.parent.mkdir()
        original_profile = '# 我的特调\n请保留字节：文风、Git 与协作偏好。\n'.encode('utf-8')
        profile.write_bytes(original_profile)
        project = scratch / (label+' project')
        project.mkdir()
        project_rules = project/'LETSGAL.md'
        project_rules.write_text('# 作品自己的约定\n', 'utf-8')
        original_project = hashes(project)
        private_skill = home/'.codex'/'skills'/'my-personal-workflow'
        private_skill.mkdir(parents=True)
        (private_skill/'SKILL.md').write_text('PRIVATE SENTINEL', 'utf-8')

        def install(*extra, source=bundle):
            args=[shell,'-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',str(source/'Install.ps1'),
                  '-Harness','Codex','-Scope','User','-UserHome',str(home),'-NonInteractive',*extra]
            p=subprocess.run(args,capture_output=True)
            output=p.stdout.decode('utf-8',errors='replace') + p.stderr.decode('utf-8',errors='replace')
            return p.returncode, output

        code,out=install()
        target=home/'.agents'/'skills'/'letsgal-authoring'
        record(label+' fresh-install',code==0 and (target/'SKILL.md').is_file(),out[-700:] if code else '')
        if code:
            continue
        snapshot=hashes(target)
        code,out=install()
        record(label+' repeat-is-no-op',code==0 and hashes(target)==snapshot and 'already_current' in out)
        code,out=install('-Action','Check')
        record(label+' install-receipt-check',code==0)
        # Direct public edits must prevent an unattended update.
        (target/'SKILL.md').write_text((target/'SKILL.md').read_text('utf-8')+'\nLOCAL EDIT\n','utf-8')
        edited=hashes(target)
        code,out=install()
        record(label+' edited-skill-blocks-overwrite',code!=0 and hashes(target)==edited)
        code,out=install('-ReplaceModified')
        backup_root=target.parent.parent/'.letsgal-authoring-backups'
        previous=list(backup_root.glob('*-previous'))
        record(label+' explicit-replacement-backs-up-edits',code==0 and any(hashes(p)==edited for p in previous))
        record(label+' user-and-project-customizations-preserved',profile.read_bytes()==original_profile and hashes(project)==original_project)
        record(label+' original-private-skill-untouched',(private_skill/'SKILL.md').read_text('utf-8')=='PRIVATE SENTINEL')
        # Tampered distribution must fail before replacing an installed good copy.
        bad=scratch/(label+' bad-bundle')
        shutil.copytree(bundle,bad)
        (bad/'skills'/'letsgal-authoring'/'SKILL.md').write_text('corrupted', 'utf-8')
        good=hashes(target)
        code,out=install(source=bad)
        record(label+' corrupted-bundle-rejected',code!=0 and hashes(target)==good)
        malicious=json.loads((bad/'bundle.json').read_text('utf-8'))
        malicious['files'][0]['path']='../../outside.txt'
        (bad/'bundle.json').write_text(json.dumps(malicious),'utf-8')
        code,out=install(source=bad)
        record(label+' manifest-traversal-rejected',code!=0 and hashes(target)==good)
        code,out=install('-Action','Uninstall')
        record(label+' uninstall-retains-skill-backup-and-profile',code==0 and not target.exists() and profile.read_bytes()==original_profile and any(backup_root.glob('*-uninstalled')))
        # Actual version update (same profile, new bundle hashes).
        code,out=install()
        newer=scratch/(label+' newer-bundle')
        shutil.copytree(bundle,newer)
        new_skill=newer/'skills'/'letsgal-authoring'
        (new_skill/'references'/'production.md').write_text((new_skill/'references'/'production.md').read_text('utf-8')+'\nNew release fixture.\n','utf-8')
        manifest=json.loads((newer/'bundle.json').read_text('utf-8'))
        manifest['version']='0.1.1-test'
        for item in manifest['files']:
            item['sha256']=hashlib.sha256((new_skill/item['path']).read_bytes()).hexdigest()
        (newer/'bundle.json').write_text(json.dumps(manifest,ensure_ascii=False),'utf-8')
        code,out=install(source=newer)
        record(label+' version-upgrade-retains-personal-configuration',code==0 and profile.read_bytes()==original_profile and 'New release fixture.' in (target/'references'/'production.md').read_text('utf-8'))
        # All harness path choices and project installation preserve the project rules.
        for harness in ['Codex','Claude','Cursor','Copilot']:
            args=[shell,'-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-File',str(bundle/'Install.ps1'),
                  '-Harness',harness,'-Scope','Project','-ProjectPath',str(project),'-UserHome',str(home),'-NonInteractive']
            p=subprocess.run(args,capture_output=True)
            directory='.claude' if harness=='Claude' else '.agents'
            record(label+' project-path-'+harness,p.returncode==0 and (project/directory/'skills'/'letsgal-authoring'/'SKILL.md').exists() and project_rules.read_text('utf-8')=='# 作品自己的约定\n')
        # Junction to a separate fixture must be rejected, not written through.
        junction_home=scratch/(label+' linked-home')
        junction_home.mkdir()
        outside=scratch/(label+' outside-fixture')
        outside.mkdir()
        link=junction_home/'.agents'
        command="New-Item -ItemType Junction -Path '%s' -Target '%s' | Out-Null" % (str(link).replace("'","''"),str(outside).replace("'","''"))
        p=subprocess.run([shell,'-NoProfile','-Command',command],capture_output=True)
        if p.returncode==0:
            args=[shell,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(bundle/'Install.ps1'),'-Harness','Codex','-Scope','User','-UserHome',str(junction_home),'-NonInteractive']
            q=subprocess.run(args,capture_output=True)
            record(label+' junction-target-rejected',q.returncode!=0 and not list(outside.iterdir()))
        else:
            record(label+' junction-target-rejected',False,'Could not create test junction')
    report={'checks':results,'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),
            'scope':'Isolated file, installer and static-checker tests only; no real harness/Studio/UI/workshop acceptance.'}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2), 'utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report['failed'] else 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch',type=Path,required=True)
    opts=parser.parse_args()
    if not opts.scratch.is_absolute() or opts.scratch.exists():
        parser.error('--scratch must be an absolute new directory')
    if hasattr(sys.stdout,'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(run(Path(__file__).resolve().parents[1],opts.scratch))
