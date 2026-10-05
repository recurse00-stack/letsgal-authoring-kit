"""Boundary cases for read-only operand shape checks; not an engine interpreter."""
import argparse, copy, hashlib, json, subprocess, sys
from pathlib import Path

def run(scratch):
    scratch.mkdir(parents=True, exist_ok=False)
    checker=Path(__file__).resolve().parents[1]/'skills/letsgal-authoring/scripts/check_project.py'
    base={'id':'chapter-probe','name':'sample','fragments':[
        {'id':'main-probe','name':'main','blocks':[]},
        {'id':'true-probe','name':'true','blocks':[]},
        {'id':'false-probe','name':'false','blocks':[]}]}
    valid_assignment={'key':'score','op':'=','aKind':'lit','aLit':'1','bKind':'none'}
    valid_condition={'left':'score','op':'==','rightKind':'literal','rightLiteral':'0'}
    checks=[]
    def case(name, blocks, exit_code, diagnostic=None, extra=None):
        folder=scratch/name;folder.mkdir()
        value=copy.deepcopy(base);value['fragments'][0]['blocks']=blocks
        if extra:value['fragments'].extend(extra)
        file=folder/'sample.json';file.write_text(json.dumps(value,ensure_ascii=False),'utf-8')
        original=file.read_bytes()
        p=subprocess.run([sys.executable,'-X','utf8','-B',str(checker),str(file)],capture_output=True)
        report=json.loads(p.stdout.decode('utf-8'))
        ok=(p.returncode==exit_code and file.read_bytes()==original and
            (not diagnostic or any(i.get('code')==diagnostic for i in report['issues'])))
        checks.append({'name':name,'passed':ok,'exit':p.returncode,'source_unchanged':file.read_bytes()==original,
                       'input_sha256':hashlib.sha256(original).hexdigest(),'report':report})
        return report
    def assignment(props): return {'type':'setver','props':props}
    def condition(value): return {'type':'if','props':{'conditions':json.dumps(value),'logicOp':'and',
                                  'thenFragmentId':'true-probe','elseFragmentId':'false-probe'}}
    case('native-shaped-literal-assignment',[assignment(valid_assignment)],0)
    for name,patch in [('number-not-string',{'aLit':1}),('null-literal',{'aLit':None}),
                       ('variable-reference-missing',{'aKind':'var'}),('operand-kind-object',{'aKind':{}}),
                       ('compound-with-two-operands',{'op':'+=','bKind':'lit','bLit':'2'}),
                       ('unknown-binary-op',{'bKind':'lit','bLit':'2','binOp':'**'})]:
        value=copy.deepcopy(valid_assignment);value.update(patch)
        case(name,[assignment(value)],1,'operand_shape')
    value=copy.deepcopy(valid_assignment);value.update(aKind='var',aVar='other',bKind='var',bVar='third',binOp='+')
    case('two-variable-operands-shape-only',[assignment(value)],0)
    value=copy.deepcopy(valid_assignment);value['future']={'preserve':[1,2]}
    case('unknown-assignment-fields-preserved',[assignment(value)],0)
    case('native-shaped-variable-condition',[condition([valid_condition])],0)
    case('condition-not-object',[condition([True])],1,'condition_shape')
    value=copy.deepcopy(valid_condition);value['rightLiteral']=0
    case('condition-literal-not-string',[condition([value])],1,'operand_shape')
    value=copy.deepcopy(valid_condition);value.update(rightKind='variable');value.pop('rightLiteral')
    case('condition-variable-reference-missing',[condition([value])],1,'operand_shape')
    value=copy.deepcopy(valid_condition);value.update(op='exists');value.pop('rightKind');value.pop('rightLiteral')
    case('unary-condition-needs-no-right-value',[condition([value])],0)
    case('custom-condition-expression-is-not-executed',[condition([{'op':'custom','rightLiteral':'score > 0'}])],0)
    value={'sourceKind':'extension-method','op':'==','extensionMethod':'fixture/check',
           'extensionParams':{},'rightKind':'literal','rightLiteral':'true'}
    case('method-schema-remains-unverified',[condition([value])],0,'condition_method_unverified')
    value['extensionParams']='{}'
    case('method-params-object-not-json-string',[condition([value])],1,'condition_shape')
    future={'sourceKind':'future-provider','custom':{'keep':True}}
    report=case('two-future-conditions-one-uncovered-block',[condition([future,future])],2,'condition_source_unknown')
    checks.append({'name':'uncovered-count-is-block-count','passed':report['unsupported_blocks']==1})
    case('vars-operation-not-object',[{'type':'branch','props':{'choices':json.dumps([
        {'mode':'vars','text':'Change','varOps':[1]}])}}],1,'operand_shape')
    reused={'id':'judge-probe','name':'judge','blocks':[condition([valid_condition])]}
    case('stored-If-reuse-warning',[{'type':'callFragment','props':{'fragmentId':'judge-probe'}},
                                  {'type':'callFragment','props':{'fragmentId':'judge-probe'}}],0,
         'if_reuse_decision_risk',extra=[reused])
    report={'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
            'scope':'Read-only shape, preservation and diagnostics. No expression execution or host acceptance.', 'checks':checks}
    (scratch/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},ensure_ascii=False))
    return bool(report['failed'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch',required=True,type=Path)
    raise SystemExit(run(parser.parse_args().scratch))
