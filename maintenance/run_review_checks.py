"""Version-safety and release-boundary regression checks in a NEW scratch directory."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
import uuid
from review_release import inspect_text

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch',type=Path,required=True)
    args=parser.parse_args()
    if not args.scratch.is_absolute() or args.scratch.exists(): parser.error('Use a new absolute scratch directory')
    args.scratch.mkdir()
    kit=Path(__file__).resolve().parents[1]
    checker=kit/'skills/letsgal-authoring/scripts/check_project.py'
    checks=[]
    def record(name,ok):
        checks.append({'name':name,'passed':bool(ok)})
        if not ok: raise AssertionError(name)
    def case(name,data,code,status,*extra,project=False):
        folder=args.scratch/name
        folder.mkdir()
        file=folder/('project.json' if project else 'chapter.json')
        file.write_text(json.dumps(data,ensure_ascii=False),'utf-8')
        before=file.read_bytes()
        result=subprocess.run([sys.executable,'-B',str(checker),str(folder if project else file),*extra],capture_output=True)
        report=json.loads(result.stdout)
        record(name,result.returncode==code and report['status']==status and file.read_bytes()==before)
        return report
    legacy={'id':'old-example','name':'chapter','blocks':[],'unknown':{'preserve':'exactly'}}
    case('unknown-chapter-is-not-converted',legacy,2,'unsupported_format')
    case('json-only-accepts-unknown-layout',legacy,0,'json_syntax_passed','--format','json-only')
    case('explicit-profile-reports-shape-problem',legacy,1,'issues_found','--format','fragments')
    case('unknown-project-index-is-not-called-corrupt',{'futureIndex':[]},2,'unsupported_format',project=True)
    case('json-only-unknown-project',{'futureIndex':[]},0,'json_syntax_passed','--format','json-only',project=True)
    known={'id':'c','name':'chapter','fragments':[{'id':'f','name':'main','blocks':[{'type':'futureBetaFeature','props':{'keep':True}}]}]}
    report=case('unknown-instruction-preserved-and-unverified',known,0,'partial_static_checks_passed')
    record('structural-success-is-not-engine-compatibility',report['engine_compatibility']=='not_verified' and report['warnings']>0)
    different_parameters={'id':'c','name':'chapter','fragments':[{'id':'f','name':'main','blocks':[{'type':'branch','props':{'differentVersionParameters':[]}}]}]}
    case('unrecognized-instruction-parameters-need-version-evidence',different_parameters,2,'unsupported_format')
    legacy_choice={'id':'c','name':'chapter','fragments':[{'id':'f','name':'main','blocks':[{'type':'branch','props':{'choices':json.dumps([{'text':'Continue','fragmentId':''}])}}]}]}
    report=case('legacy-choice-mode-default-is-read-only',legacy_choice,0,'partial_static_checks_passed')
    record('legacy-choice-default-is-disclosed',any('legacy choice' in issue['message'] for issue in report['issues']))
    case('explicit-generation-profile-requires-choice-mode',legacy_choice,1,'issues_found','--format','fragments')
    legacy_choice['fragments'][0]['blocks'][0]['props']['choices']=json.dumps([{'text':'Continue','fragmentId':'missing'}])
    case('legacy-default-still-checks-target-reference',legacy_choice,1,'issues_found')
    for name,value in [('path','Q'+':'+chr(92)+'Users'+chr(92)+'private'),('token','ghp_'+'A'*36),('email','person'+'@'+'private.example'),('key','-----BEGIN '+'PRIVATE KEY-----')]:
        record('privacy-detector-'+name,bool(inspect_text(value)))
    record('public-reference-url-not-personal-path',not inspect_text('https://docs.avg-engine.com/reference/script-json'))
    # Prove package selection ignores unlisted local data and Git history.
    copy=args.scratch/'release-fixture'
    shutil.copytree(kit,copy)
    (copy/'.git').mkdir()
    private_marker='private-fixture-'+uuid.uuid4().hex
    (copy/'.git/config').write_text(private_marker,'utf-8')
    (copy/'.env').write_text(private_marker,'utf-8')
    (copy/'private-notes.txt').write_text(private_marker,'utf-8')
    built=subprocess.run([sys.executable,'-B',str(copy/'maintenance/build_release.py'),'--zip'],capture_output=True)
    record('explicit-release-list-builds-with-unlisted-local-files',built.returncode==0)
    archive=next(args.scratch.glob('release-fixture-*.zip'))
    selected=json.loads((copy/'release-files.json').read_text('utf-8'))['files']
    with zipfile.ZipFile(archive) as z:
        actual={name.split('/',1)[1] for name in z.namelist()}
        record('archive-contains-only-approved-files',actual==set(selected))
        record('archive-has-no-private-fixture-bytes',not any(private_marker.encode() in z.read(name) for name in z.namelist()))
    report={'checks':checks,'passed':len(checks),'failed':0,'scope':'Version-format handling, privacy detectors and real ZIP whitelist isolation; no host-version runtime acceptance.'}
    (args.scratch/'review-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
