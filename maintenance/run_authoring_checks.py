"""Exercise static authoring diagnostics; optionally read native-saved fixtures. Python 3.9+."""
from bundle_layout import payload, manifest_path, with_channel
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path

def run(scratch,native_fixtures=None):
    scratch.mkdir(parents=True,exist_ok=False)
    scripts=payload(Path(__file__).resolve().parents[1])/'scripts'
    checks=[]
    base={'id':'chapter-a','name':'sample','fragments':[{'id':'main-a','name':'main','blocks':[]},
                                                       {'id':'sub-a','name':'sub','blocks':[]}]}
    def hashes(folder):
        return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                for p in folder.rglob('*') if p.is_file()}
    def run_checker(target,profile='auto'):
        p=subprocess.run([sys.executable,'-B',str(scripts/'check_project.py'),str(target),
                          '--format',profile],capture_output=True)
        report=json.loads(p.stdout)
        # Check the structured contract as well as individual diagnostic wording.
        assert report.get('read_only') is True
        assert report.get('engine_compatibility')=='not_verified'
        assert report.get('schema_basis')=='authoring-subset-v0.2.0'
        assert report['errors']==sum(i['level']=='error' for i in report['issues'])
        assert report['warnings']==sum(i['level']=='warning' for i in report['issues'])
        return p.returncode,report
    def case(name,value,code,predicate,profile='auto',project=False,order=None):
        folder=scratch/name;folder.mkdir()
        target=folder/'sample.json'
        if project:
            (folder/'project.json').write_text(json.dumps({'chapterOrder':order or ['sample']}),'utf-8')
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
        exit_code,report=run_checker(folder if project else target,profile)
        ok=exit_code==code and hashes(folder)==before and predicate(report)
        checks.append({'name':name,'passed':bool(ok),'exit':exit_code,'source_bytes_unchanged':hashes(folder)==before,
                       'report':report})
        if not ok: raise AssertionError(name)
        return report
    def warning(report,text):
        return any(i['level']=='warning' and text in i['message'] for i in report['issues'])
    def warning_code_at(report,code,location):
        return any(i['level']=='warning' and i.get('code')==code and i['location']==location
                   for i in report['issues'])
    def supported_chapter(report):
        return report['status']=='partial_static_checks_passed' and report['errors']==0 \
               and report['chapters_checked']==1 and report['unsupported_chapters']==0 \
               and report['unsupported_blocks']==0 and report['unchecked_blocks']==0
    v=copy.deepcopy(base);v['fragments'][1]['blocks']=[{'type':'callFragment','props':{'fragmentId':'main-a'}}]
    case('existing-main-call-is-not-confirmed-corruption',v,0,
         lambda r:supported_chapter(r) and warning_code_at(r,'main_call_version_sensitive','sample.json:fragments[1].blocks[0]')
                  and warning(r,'2.3.0-beta.1'))
    v=copy.deepcopy(base);v['fragments'][1]['blocks']=[{'type':'callFragment','props':{'fragmentId':'sub-a'}}]
    case('conversion-cycle-risk-not-runtime-error',v,0,
         lambda r:supported_chapter(r) and warning_code_at(r,'fragment_cycle','sample.json')
                  and warning(r,'not a runtime recursion guarantee'))
    v['fragments'][1]['blocks'][0]['props']['disabled']=True
    case('disabled-cycle-reachability-is-not-inferred',v,0,
         lambda r:supported_chapter(r) and warning_code_at(r,'fragment_cycle','sample.json')
                  and warning(r,'disabled instructions'))
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
    case('preprocessing-in-ordinary-order-is-warning-without-repair',base,0,
         lambda r:r['status']=='partial_static_checks_passed' and r['errors']==0 and r['chapters_checked']==3
                  and warning_code_at(r,'preprocessing_in_linear_order','pre.json')
                  and not any(i['location']=='pre.json' and i['level']=='error' for i in r['issues']),
         project=True,order=['sample','pre'])
    v={'id':'deep-c','name':'sample','fragments':[{'id':'d'+str(i),'name':'main' if i==0 else 'part'+str(i),
          'blocks':[{'type':'callFragment','props':{'fragmentId':'d'+str(i+1)}}] if i<31 else []} for i in range(32)]}
    case('long-acyclic-expansion-risk',v,0,
         lambda r:supported_chapter(r) and warning_code_at(r,'fragment_depth','sample.json')
                  and warning(r,'not a measured hard limit'))
    v['fragments'].append({'id':'isolated-loop','name':'isolated-loop','blocks':[
        {'type':'callFragment','props':{'fragmentId':'isolated-loop'}}]})
    case('long-chain-and-isolated-cycle-both-diagnosed',v,0,
         lambda r:supported_chapter(r) and warning_code_at(r,'fragment_depth','sample.json')
                  and warning_code_at(r,'fragment_cycle','sample.json')
                  and warning(r,'not a runtime recursion guarantee'))
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'dialogue','props':{},'content':[]},
          {'type':'wait','props':{'duration':'wrong-scalar'}}]
    case('limited-profile-does-not-claim-full-parameters',v,0,
         lambda r:'not full parameter/type/asset/variable' in r['scope'],profile='fragments')
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'narration','props':{},
          'content':[{'type':'future-hyperlink','custom':{'preserve':True}}]}]
    case('unknown-inline-kept-unvalidated',v,0,lambda r:warning(r,'non-text inline'))
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'future-command','props':{}}]
    case('unknown-command-counter-and-warning',v,0,lambda r:r['unchecked_blocks']==1 and warning(r,'supported subset'))
    v=copy.deepcopy(base);v['fragments'][0]['blocks']=[{'type':'narration','props':{'keepDialogue':True}}]
    case('native-empty-narration-auto-compatible',v,0,
         lambda r:warning_code_at(r,'native_empty_narration','sample.json:fragments[0].blocks[0]'))
    case('generated-narration-still-requires-content',v,1,lambda r:r['errors']==1,profile='fragments')
    for bad in [None,'text',{}]:
        v['fragments'][0]['blocks'][0]['content']=bad
        case('malformed-narration-content-'+type(bad).__name__,v,1,lambda r:r['errors']==1)
    v['fragments'][0]['blocks'][0]={'type':'dialogue','props':{}}
    case('missing-dialogue-not-assumed-native-blank',v,1,lambda r:r['errors']==1)
    # These five shapes correspond to the saved 2.3.0-beta.1 native probe cases.
    # They test static readback only; no interpreter here predicts the observed playback order.
    def narration(marker):
        return {'type':'narration','props':{'keepDialogue':False},
                'content':[{'type':'text','text':marker,'styles':{}}]}
    def call(target):
        return {'type':'callFragment','props':{'fragmentId':target}}
    def native_shape(name,main_blocks,other_blocks=None):
        value={'id':'fixture-'+name,'name':'sample',
               'fragments':[{'id':'fixture-main','name':'main','blocks':main_blocks}]}
        if other_blocks is not None:
            value['fragments'].append({'id':'fixture-A','name':'A','blocks':other_blocks})
        return value
    native_cases=[
        ('control-main-to-A','开始',
         native_shape('control',[narration('C0'),call('fixture-A'),narration('C2')],[narration('C1')]),False,False,None),
        ('main-self','MainSelf',
         native_shape('main-self',[narration('M_ENTER'),call('fixture-main'),narration('M_RETURN')]),True,True,0),
        ('main-indirect','MainIndirect',
         native_shape('main-indirect',[narration('X0'),call('fixture-A'),narration('X2')],
                      [narration('X1'),call('fixture-main'),narration('X3')]),True,True,1),
        ('other-self','OtherSelf',
         native_shape('other-self',[narration('S0'),call('fixture-A'),narration('S2')],
                      [narration('A_ENTER'),call('fixture-A'),narration('A_RETURN')]),False,True,None),
        ('main-acyclic','MainAcyclic',
         native_shape('main-acyclic',[narration('T_MAIN')],
                      [narration('T_ENTER'),call('fixture-main'),narration('T_RETURN')]),True,False,1),
    ]
    def shape_signature(value):
        names={f['id']:f['name'] for f in value['fragments']}
        result=[]
        for fragment in value['fragments']:
            blocks=[]
            for block in fragment['blocks']:
                if block['type']=='callFragment':
                    blocks.append(('callFragment',names[block['props']['fragmentId']]))
                elif block['type']=='narration':
                    blocks.append(('narration',''.join(i['text'] for i in block['content'] if i['type']=='text')))
                else:
                    raise AssertionError('unexpected native fixture instruction')
            result.append((fragment['name'],blocks))
        return result
    native_before=hashes(native_fixtures) if native_fixtures is not None else None
    for name,filename,value,has_main,has_cycle,main_origin in native_cases:
        def native_diagnostics(report,chapter_name,has_main=has_main,has_cycle=has_cycle,main_origin=main_origin):
            main_issues=[i for i in report['issues'] if i.get('code')=='main_call_version_sensitive']
            cycle_issues=[i for i in report['issues'] if i.get('code')=='fragment_cycle']
            if not supported_chapter(report) or len(main_issues)!=int(has_main) or len(cycle_issues)!=int(has_cycle):
                return False
            if has_main and not (main_issues[0]['level']=='warning' and '2.3.0-beta.1' in main_issues[0]['message']
                                 and main_issues[0]['location']==chapter_name+':fragments[%d].blocks[1]' % main_origin):
                return False
            return not has_cycle or (cycle_issues[0]['level']=='warning' and cycle_issues[0]['location']==chapter_name
                                     and 'conversion-time' in cycle_issues[0]['message']
                                     and 'not a runtime recursion guarantee' in cycle_issues[0]['message'])
        if native_fixtures is None:
            case('native-shape-'+name,value,0,lambda r:native_diagnostics(r,'sample.json'))
        else:
            target=native_fixtures/(filename+'.json')
            original=target.read_bytes()
            saved=json.loads(original.decode('utf-8-sig'))
            assert saved['name']==filename and shape_signature(saved)==shape_signature(value),name
            exit_code,report=run_checker(target)
            unchanged=target.read_bytes()==original and hashes(native_fixtures)==native_before
            ok=exit_code==0 and unchanged and native_diagnostics(report,target.name)
            checks.append({'name':'native-saved-'+name,'passed':bool(ok),'exit':exit_code,
                           'source_bytes_unchanged':unchanged,'source_sha256':hashlib.sha256(original).hexdigest(),
                           'report':report})
            if not ok: raise AssertionError('native saved fixture: '+name)
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
            'native_fixture_basis':'supplied-native-saved-files' if native_fixtures is not None else 'deidentified-recreated-shapes',
            'scope':'Real CLI static checks on synthetic files and five recreated or supplied native-saved shapes. '
                    'No new Studio conversion/playback/save/export or model-client acceptance.'}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({'passed':len(checks),'failed':0}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',type=Path,required=True)
    p.add_argument('--native-fixtures',type=Path,help='Optional existing chapters directory containing the five native probe JSON files')
    a=p.parse_args()
    if not a.scratch.is_absolute() or a.scratch.exists():p.error('Use a NEW absolute scratch directory')
    if a.native_fixtures is not None and (not a.native_fixtures.is_absolute() or not a.native_fixtures.is_dir()):
        p.error('Native fixtures must be an existing absolute directory; they are read only')
    run(a.scratch,a.native_fixtures)
