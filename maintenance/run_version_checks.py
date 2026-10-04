"""Check version routing in a NEW isolated --scratch directory. Python 3.9+."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

def run(scratch):
    scratch.mkdir(parents=True,exist_ok=False)
    scripts=Path(__file__).resolve().parents[1]/'skills/letsgal-authoring/scripts'
    sys.path.insert(0,str(scripts))
    import inspect_version as inspector
    checks=[]
    cases=[({},'UNKNOWN'),({'studio_version':'2.0.0'},'reference_selected'),
           ({'studio_version':'2.0.1'},'reference_selected'),
           ({'studio_version':'2.3.0-beta.1'},'reference_selected'),
           ({'studio_version':'2.3.0-beta.1+build.9'},'reference_selected'),
           ({'studio_version':'2.4.0-beta.1'},'reference_selected'),
           ({'studio_version':'2.4.0-beta.1+build.9'},'reference_selected'),
           ({'studio_version':'2.4.0-beta.2'},'reference_selected'),
           ({'studio_version':'2.4.0-beta.2+build.9'},'reference_selected'),
           ({'studio_version':'2.4.0-beta.3'},'UNKNOWN'),
           ({'studio_version':'2.5.0-beta.1'},'reference_selected'),
           ({'studio_version':'2.5.0-beta.1+build.9'},'reference_selected'),
           ({'studio_version':'2.5.0-beta.2'},'UNKNOWN'),
           ({'studio_version':'2.5.0-beta.1','channel':'stable'},'UNKNOWN'),
           ({'studio_version':'2.5.0-beta.1','project_version':'2.4.0-beta.2'},'UNKNOWN'),
           ({'studio_version':'2.5.0'},'UNKNOWN'),
           ({'studio_version':'2.4.0-beta.2','channel':'stable'},'UNKNOWN'),
           ({'studio_version':'2.4.0-beta.2','project_version':'2.4.0-beta.1'},'UNKNOWN'),
           ({'studio_version':'2.4.0'},'UNKNOWN'),
           ({'studio_version':'2.4.0-beta.1','channel':'stable'},'UNKNOWN'),
           ({'studio_version':'2.4.0-beta.1','project_version':'2.3.0-beta.1'},'UNKNOWN'),
           ({'studio_version':'2.3.0-beta.2'},'UNKNOWN'),
           ({'studio_version':'2.3.0'},'UNKNOWN'),({'studio_version':'1.21.0'},'UNKNOWN'),
           ({'studio_version':'2.3.0-beta.1','channel':'stable'},'UNKNOWN'),
           ({'studio_version':'2.3.0-beta.1','project_version':'2.0.1'},'UNKNOWN'),
           ({'project_version':'2.3.0-beta.1'},'UNKNOWN'),
           ({'studio_version':'2.3.0-rc.1'},'UNKNOWN')]
    for args,status in cases:
        value=inspector.inspect(**args)
        assert value['status']==status and value['read_only'] and value['runtime_compatibility']=='not_verified'
        assert (scripts.parent/value['reference']).is_file()
        if value['status']=='reference_selected':
            expected=inspector.PROFILES[inspector.parse_version(args['studio_version'])[0]]
            assert value['reference']==expected
        checks.append({'case':args,'passed':True,'reference':value['reference']})
    for bad in ['2.3','2.3.0.0','2.3.0-beta.01','02.3.0','v2.3.0','2.3.0-beta.']:
        try: inspector.parse_version(bad)
        except ValueError: checks.append({'invalid_version':bad,'passed':True})
        else: raise AssertionError(bad)
    sdk=scratch/'sdk'
    sdk.mkdir()
    (sdk/'index.ts').write_text('export type Example = number;','utf-8')
    (sdk/'sdk-context.ts').write_text('export interface Example {}','utf-8')
    hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sdk.iterdir()}
    before=hashes()
    value=inspector.inspect(studio_version='2.3.0-beta.1',sdk=sdk)
    assert value['sdk']['files']==before and hashes()==before and value['sdk']['api_compatibility']=='not_verified'
    checks.append({'case':'SDK fingerprint and unchanged bytes','passed':True})
    result=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),
                           '--studio-version','2.3.0-beta.1','--channel','stable'],capture_output=True)
    assert result.returncode==2 and json.loads(result.stdout)['status']=='UNKNOWN'
    checks.append({'case':'CLI conflict fails closed','passed':True})
    result=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),
                           '--studio-version','2.4.0-beta.2','--channel','beta'],capture_output=True)
    value=json.loads(result.stdout)
    assert result.returncode==0 and value['reference']=='references/versions/beta-2.4.md'
    assert value['runtime_compatibility']=='not_verified' and value['sdk']['api_compatibility']=='not_verified'
    checks.append({'case':'CLI beta.2 selects reference without claiming runtime or SDK acceptance','passed':True})
    result=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),
                           '--studio-version','2.5.0-beta.1','--channel','beta'],capture_output=True)
    value=json.loads(result.stdout)
    assert result.returncode==0 and value['reference']=='references/versions/beta-2.5.md'
    assert value['runtime_compatibility']=='not_verified' and value['sdk']['api_compatibility']=='not_verified'
    checks.append({'case':'CLI2.5 selects its own profile without runtime or SDK claim','passed':True})
    report={'passed':len(checks),'failed':0,'checks':checks,
            'scope':'Version routing and read-only SDK fingerprint; no engine runtime acceptance'}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    print(json.dumps({'passed':len(checks),'failed':0}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch',type=Path,required=True)
    args=parser.parse_args()
    if not args.scratch.is_absolute() or args.scratch.exists(): parser.error('Use a NEW absolute scratch directory')
    run(args.scratch)
