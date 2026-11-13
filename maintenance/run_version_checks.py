"""Test release-series routing and operation gates in a NEW isolated --scratch directory."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from bundle_layout import payload

def run(scratch):
    scratch.mkdir(parents=True,exist_ok=False)
    kit=Path(__file__).resolve().parents[1];checks=[]
    def record(name,ok,detail=None):
        checks.append({'name':name,'passed':bool(ok),'detail':detail})
        assert ok,(name,detail)
    versions=['3.0.0','3.0.1','3.0.99+build.9','3.0.0-beta.1','3.1.0','4.0.0',
              '2.9.0-beta.1','2.9.0-beta.2','2.9.17-beta.99+build.1','2.8.0-beta.1','2.8.2-beta.4',
              '2.9.0','2.8.0','2.10.0-beta.1','2.7.0-beta.1','2.5.0','3.0.0-rc.1']
    for ch in ['stable','beta']:
        scripts=payload(kit,ch)/'scripts';sys.path.insert(0,str(scripts))
        spec=importlib.util.spec_from_file_location('inspector_'+ch,scripts/'inspect_version.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        host='3.0.0' if ch=='stable' else '2.9.0-beta.1'
        newer='3.0.17+build.9' if ch=='stable' else '2.9.17-beta.99+build.9'
        for version in versions:
            expected=(version in ['3.0.0','3.0.1','3.0.99+build.9']) if ch=='stable' else (version in ['2.9.0-beta.1','2.9.0-beta.2','2.9.17-beta.99+build.1','2.8.0-beta.1','2.8.2-beta.4'])
            d=module.inspect(studio_version=version)
            record(ch+' route '+version,d['status']==('reference_selected' if expected else 'UNKNOWN') and d['operation_gate']['state']==('matched' if expected else 'confirmation_required') and d['read_only'] and d['runtime_compatibility']=='not_verified')
            record(ch+' reference '+version,(scripts.parent/d['reference']).is_file())
        baseline=module.inspect(studio_version=host)['operation_gate']
        record(ch+' no patch evidence required',baseline['state']=='matched' and baseline['patch']['id']=='UNKNOWN')
        for args in [dict(studio_version=newer),dict(studio_version=host,patch_id='unregistered-r999'),dict(studio_version=host,patch_sha256='f'*64),dict(studio_version=host,patch_id='same-id',patch_sha256='0'*64),dict(studio_version=host,update_channel='beta')]:
            gate=module.inspect(**args)['operation_gate']
            record(ch+' patch-independent admission',gate['state']=='matched' and gate['fingerprint']==baseline['fingerprint'],args)
        for args in [{},{'project_version':host},{'studio_version':host,'channel':'beta' if ch=='stable' else 'stable'}]:
            gate=module.inspect(**args)['operation_gate'];record(ch+' missing or conflicting identity',gate['state']=='identity_required' and gate['decision']=='pause_engine_operations',args)
        d=module.inspect(studio_version=host,project_version=newer)
        record(ch+' project target compares series',d['status']=='reference_selected' and d['operation_gate']['state']=='matched')
        d=module.inspect(studio_version=host,project_version='9.0.0')
        record(ch+' project series mismatch requires confirmation',d['status']=='UNKNOWN' and d['operation_gate']['state']=='confirmation_required')
        with patch.object(module,'file_version',return_value=newer):d=module.inspect(studio_version=host,studio_exe='fixture.exe')
        record(ch+' same-series EXE version is usable',d['operation_gate']['state']=='matched' and d['studio_version']==newer and bool(d['diagnostics']))
        with patch.object(module,'file_version',return_value='9.0.0'):d=module.inspect(studio_version=host,studio_exe='fixture.exe')
        record(ch+' conflicting source series needs identity',d['operation_gate']['state']=='identity_required')
        for invalid in ['2.3','2.3.0.0','2.3.0-beta.01','02.3.0','v2.3.0','2.3.0-beta.']:
            try:module.parse_version(invalid)
            except ValueError:record(ch+' invalid '+invalid,True)
            else:record(ch+' invalid '+invalid,False)
        marker=scratch/(ch+'-renderer.json')
        markers=[{'baseVersion':host,'channel':ch,'rev':1,'sha256':'0'*64},
                 {'baseVersion':host,'channel':ch,'rev':999,'sha256':'f'*64},
                 {'baseVersion':'9.0.0','channel':'stable','rev':1}, {'broken':True}]
        for contents in markers:
            marker.write_text(json.dumps(contents),'utf-8');before=marker.read_bytes()
            d=module.inspect(studio_version=host,renderer_patch=marker)
            record(ch+' optional marker never gates',d['operation_gate']['state']=='matched' and d['operation_gate']['fingerprint']==baseline['fingerprint'] and marker.read_bytes()==before,contents)
        marker.write_text('{','utf-8')
        for args in [{'renderer_patch':marker},{'renderer_patch':scratch/'missing.json'},{'patch_sha256':'bad'},{'patch_id':'bad id'}]:
            d=module.inspect(studio_version=host,**args)
            record(ch+' optional metadata failure is diagnostic',d['operation_gate']['state']=='matched' and bool(d['diagnostics']),{k:str(v) for k,v in args.items()})
        marker.write_text(json.dumps({'baseVersion':host,'channel':ch,'rev':1}),'utf-8')
        d=module.inspect(studio_version=host,renderer_patch=marker,patch_id='conflicting-id')
        record(ch+' conflicting optional patches are diagnostic',d['operation_gate']['state']=='matched' and bool(d['diagnostics']))
        sdk=scratch/(ch+'-sdk');sdk.mkdir();(sdk/'index.ts').write_text('export type Example = number;','utf-8')
        before=hashlib.sha256((sdk/'index.ts').read_bytes()).hexdigest();d=module.inspect(studio_version=host,sdk=sdk)
        record(ch+' SDK fingerprint remains read-only',d['sdk']['files']['index.ts']==before and hashlib.sha256((sdk/'index.ts').read_bytes()).hexdigest()==before and d['sdk']['api_compatibility']=='not_verified')
        for args,want in [(['--studio-version',newer],0),(['--gate','--studio-version',host],0),(['--gate','--studio-version',newer,'--patch-id','arbitrary-r99'],0),(['--gate','--studio-version',host,'--patch-sha256','f'*64],0),(['--gate','--studio-version','9.0.0'],2),(['--gate'],2),(['--studio-version','bad'],2)]:
            p=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),*args],capture_output=True);d=json.loads(p.stdout)
            record(ch+' CLI '+' '.join(args),p.returncode==want and d['read_only'] and d['operation_gate']['approval']=='not_granted_by_script')
    report={'passed':len(checks),'failed':0,'checks':checks,'scope':'routing and admission only; no engine execution'}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--scratch',type=Path,required=True);args=parser.parse_args()
    if not args.scratch.is_absolute() or args.scratch.exists():parser.error('Use a NEW absolute scratch directory')
    report=run(args.scratch);print(json.dumps({'passed':report['passed'],'failed':report['failed'],'scope':report['scope']}))
