"""Exercise authoring diagnostics on NEW isolated synthetic files. Python 3.9+."""
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path

def run(scratch):
    scratch.mkdir(parents=True,exist_ok=False)
    scripts=Path(__file__).resolve().parents[1]/'skills/letsgal-authoring/scripts'
    checks=[]
    base={'id':'chapter-a','name':'sample','fragments':[{'id':'main-a','name':'main','blocks':[]},
                                                       {'id':'sub-a','name':'sub','blocks':[]}]}
    def hashes(folder):
        return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in folder.rglob('*') if p.is_file()}
    def case(name,value,code,predicate,profile='auto',project=False):
        folder=scratch/name;folder.mkdir()
        target=folder/'sample.json'
        if project:
            (folder/'project.json').write_text(json.dumps({'chapterOrder':['sample']}),'utf-8')
            (folder/'chapters').mkdir();target=folder/'chapters/sample.json'
        target.write_text(json.dumps(value,ensure_ascii=False),'utf-8')
        if project:
            special=copy.deepcopy(base);special.update(id='pre-c',name='pre',kind='schedule-preprocessing')
            special['fragments']=[{'id':'pre-f','name':'main','blocks':[]}]
            (folder/'chapters/pre.json').write_text(json.dumps(special),'utf-8')
            ordinary=copy.deepcopy(special);ordinary.pop('kind');ordinary.update(id='or-c',name='ordinary')
            ordinary['fragments'][0]['id']='or-f'
            (folder/'chapters/ordinary.json').write_text(json.dumps(ordinary),'utf-8')
        before=hashes(folder)
        p=subprocess.run([sys.executable,'-B',str(scripts/'check_project.py'),str(folder if project else target),
                          '--format',profile],capture_output=True)
        report=json.loads(p.stdout)
        ok=p.returncode==code and hashes(folder)==before and report.get('read_only') and predicate(report)
        checks.append({'name':name,'passed':bool(ok),'exit':p.returncode,'report':report})
        if not ok: raise AssertionError(name)
        return report
    def warning(report,text):
        return any(i['level']=='warning' and text in i['message'] for i in report['issues'])
    v=copy.deepcopy(base);v['fragments'][1]['blocks']=[{'type':'callFragment','props':{'fragmentId':'main-a'}}]
    case('existing-main-call-is-not-confirmed-corruption',v,0,lambda r:warning(r,'official JSON reference'))
    v=copy.deepcopy(base);v['fragments'][1]['blocks']=[{'type':'callFragment','props':{'fragmentId':'sub-a'}}]
    case('conversion-cycle-risk-not-runtime-error',v,0,lambda r:warning(r,'conversion-time'))
    v['fragments'][1]['blocks'][0]['props']['disabled']=True
    case('disabled-cycle-reachability-is-not-inferred',v,0,lambda r:warning(r,'disabled instructions'))
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'callFragment','props':{'fragmentId':''}}]
    case('empty-editor-target-auto-compatible',v,0,lambda r:warning(r,'editor no-op'))
    case('empty-target-not-valid-generated-call',v,1,lambda r:r['errors']>0,profile='fragments')
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'callFragment','props':{'fragmentId':'missing'}}]
    case('broken-target-still-reported',v,1,lambda r:r['errors']>0)
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'branch','props':{}},{'type':'branch','props':{}}]
    case('uncovered-blocks-not-counted-as-chapters',v,2,
         lambda r:r['chapters_checked']==1 and r['unsupported_chapters']==0 and r['unsupported_blocks']==2)
    case('preprocessing-excluded-ordinary-unlisted-retained',base,0,
         lambda r:not any(i['location']=='pre.json' and 'chapterOrder' in i['message'] for i in r['issues'])
                  and any(i['location']=='ordinary.json' and 'chapterOrder' in i['message'] for i in r['issues']),project=True)
    v={'id':'deep-c','name':'sample','fragments':[{'id':'d'+str(i),'name':'main' if i==0 else 'part'+str(i),
          'blocks':[{'type':'callFragment','props':{'fragmentId':'d'+str(i+1)}}] if i<31 else []} for i in range(32)]}
    case('long-acyclic-expansion-risk',v,0,lambda r:warning(r,'30-level'))
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'dialogue','props':{},'content':[]},
          {'type':'wait','props':{'duration':'wrong-scalar'}}]
    case('limited-profile-does-not-claim-full-parameters',v,0,
         lambda r:'not full parameter/type/asset/variable' in r['scope'],profile='fragments')
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'narration','props':{},
          'content':[{'type':'future-hyperlink','custom':{'preserve':True}}]}]
    case('unknown-inline-kept-unvalidated',v,0,lambda r:warning(r,'non-text inline'))
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'future-command','props':{}}]
    case('unknown-command-counter-and-warning',v,0,lambda r:r['unchecked_blocks']==1 and warning(r,'supported subset'))
    sdk=scratch/'sdk';sdk.mkdir()
    (sdk/'index.ts').write_text('export type Marker = number;','utf-8')
    (sdk/'constants.ts').write_text('export const SDK_VERSION = "1.21.0";','utf-8')
    before=hashes(sdk)
    p=subprocess.run([sys.executable,'-B',str(scripts/'inspect_version.py'),'--studio-version','2.3.0-beta.1',
                      '--sdk',str(sdk)],capture_output=True)
    r=json.loads(p.stdout)
    ok=p.returncode==0 and hashes(sdk)==before and r['sdk']['declared_version']=='1.21.0' \
       and r['sdk']['provenance']=='UNKNOWN' and r['sdk']['api_compatibility']=='not_verified' \
       and r['sdk']['declared_version_is_host_version'] is False
    checks.append({'name':'SDK-declaration-distinct-from-host-and-provenance','passed':ok,'report':r})
    if not ok: raise AssertionError('SDK evidence')
    report={'passed':len(checks),'failed':0,'checks':checks,
            'scope':'Real CLI execution on synthetic files. No Studio conversion/playback/save/export or model-client acceptance.'}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({'passed':len(checks),'failed':0}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',type=Path,required=True);a=p.parse_args()
    if not a.scratch.is_absolute() or a.scratch.exists():p.error('Use a NEW absolute scratch directory')
    run(a.scratch)
