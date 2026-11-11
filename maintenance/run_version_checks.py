"""Check both channels in a NEW isolated --scratch directory. Python 3.9+."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from bundle_layout import payload

def run(scratch):
    scratch.mkdir(parents=True, exist_ok=False)
    kit=Path(__file__).resolve().parents[1]
    checks=[]
    known={'stable':['3.0.0'], 'beta':['2.8.0-beta.1','2.9.0-beta.1']}
    for ch in ['stable','beta']:
        scripts=payload(kit,ch)/'scripts'
        sys.path.insert(0,str(scripts))
        spec=importlib.util.spec_from_file_location('inspector_'+ch,scripts/'inspect_version.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cases=[({},'UNKNOWN'),({'project_version':'2.5.0'},'UNKNOWN')]
        for host in known['stable']+known['beta']:
            cases.append(({'studio_version':host},'reference_selected' if host in known[ch] else 'UNKNOWN'))
        for host in ['2.5.0','3.0.1','3.0.0-beta.1','2.9.0','2.9.0-beta.2','2.10.0-beta.1','2.7.1-beta.1','2.8.0','2.8.0-beta.2','2.7.0-beta.1','2.7.1','2.7.1-beta.2','2.0.0','2.0.1','2.3.0-beta.1','2.4.0-beta.1','2.4.0-beta.2','2.5.0-beta.1','2.6.0','2.6.0-beta.1','2.6.0-beta.2','2.7.0','2.7.0-beta.2','1.21.0','2.3.0-rc.1']:
            cases.append(({'studio_version':host},'UNKNOWN'))
        host=known[ch][-1]
        cases.extend([({'studio_version':host+'+build.9'},'reference_selected'),({'studio_version':host,'channel':'beta' if ch=='stable' else 'stable'},'UNKNOWN'),({'studio_version':host,'project_version':'9.0.0'},'UNKNOWN')])
        for args,status in cases:
            d=module.inspect(**args)
            assert d['status']==status and d['skill_channel']==ch and d['read_only'] and d['runtime_compatibility']=='not_verified',(ch,args,d)
            assert (scripts.parent/d['reference']).is_file()
            checks.append({'channel':ch,'case':args,'passed':True})
        for invalid in ['2.3','2.3.0.0','2.3.0-beta.01','02.3.0','v2.3.0','2.3.0-beta.']:
            try: module.parse_version(invalid)
            except ValueError: checks.append({'channel':ch,'invalid':invalid,'passed':True})
            else: raise AssertionError(invalid)
        sdk=scratch/ch
        sdk.mkdir()
        (sdk/'index.ts').write_text('export type Example = number;','utf-8')
        before=hashlib.sha256((sdk/'index.ts').read_bytes()).hexdigest()
        d=module.inspect(studio_version=host,sdk=sdk)
        assert d['sdk']['files']['index.ts']==before and hashlib.sha256((sdk/'index.ts').read_bytes()).hexdigest()==before and d['sdk']['api_compatibility']=='not_verified'
        checks.append({'channel':ch,'case':'SDK fingerprint is read-only, not acceptance','passed':True})
        p=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),'--studio-version',known['beta' if ch=='stable' else 'stable'][-1]],capture_output=True)
        assert p.returncode==2 and json.loads(p.stdout)['status']=='UNKNOWN'
        checks.append({'channel':ch,'case':'opposite-channel CLI returns UNKNOWN','passed':True})
        # Operation admission is separate from legacy reference routing.
        gate_cases=[({},'identity_required'),
            ({'studio_version':'3.0.0'},'confirmation_required'),
            ({'studio_version':'3.0.1','patch_id':'3.0.1-stable-r1'},'confirmation_required'),
            ({'studio_version':'3.0.0','patch_id':'3.0.0-stable-r3'},'confirmation_required'),
            ({'studio_version':'3.0.0+build.9','patch_id':'3.0.0-stable-r2'},'confirmation_required'),
            ({'studio_version':'3.0.0','patch_id':'3.0.0-stable-r2','channel':'beta'},'identity_required'),
            ({'studio_version':'3.0.0','patch_id':'3.0.0-stable-r2','patch_sha256':'f'*64},'confirmation_required'),
            ({'studio_version':'2.9.0-beta.1'},'confirmation_required'),
            ({'studio_version':'2.8.0-beta.1'},'confirmation_required')]
        for args,want in gate_cases:
            gate=module.inspect(**args)['operation_gate']
            assert gate['state']==want and gate['decision']=='pause_engine_operations' and gate['approval']=='not_granted_by_script'
            checks.append({'channel':ch,'case':{'gate':args},'passed':True})
        args={'studio_version':'3.0.0','patch_id':'3.0.0-stable-r2'}
        first=module.inspect(**args)['operation_gate']
        second=module.inspect(**args,update_channel='beta')['operation_gate']
        assert first==second and first['state']==('matched' if ch=='stable' else 'confirmation_required')
        checks.append({'channel':ch,'case':'feed preference does not change current host identity or cache key','passed':True})
        for patch,code in [('3.0.0-stable-r2',0 if ch=='stable' else 2),('3.0.0-stable-r3',2)]:
            p=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),'--gate','--studio-version','3.0.0','--patch-id',patch],capture_output=True)
            assert p.returncode==code and json.loads(p.stdout)['read_only']
            checks.append({'channel':ch,'case':'gate CLI '+patch,'passed':True})
    report={'passed':len(checks),'failed':0,'checks':checks,'scope':'routing only, no engine or SDK compatibility acceptance'}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scratch',type=Path,required=True)
    a=p.parse_args()
    if not a.scratch.is_absolute() or a.scratch.exists(): p.error('Use a NEW absolute scratch directory')
    r=run(a.scratch)
    print(json.dumps({'passed':r['passed'],'failed':r['failed'],'scope':r['scope']},ensure_ascii=False))
