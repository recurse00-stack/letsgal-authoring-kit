"""Exercise reference-package import with an isolated, new synthetic user area."""
from pathlib import Path
import argparse, copy, hashlib, json, subprocess, sys
from build_workbench import collect, build
from build_manual import ROOT, render

def run(scratch):
    scratch=Path(scratch).resolve(); scratch.mkdir(parents=True,exist_ok=False)
    area=scratch/'user-area'; area.mkdir()
    results=[]
    def check(name, ok):
        results.append({'name':name,'passed':bool(ok)})
        (scratch/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n','utf-8')
        assert ok,name
    def package(version,status='available'):
        base=area/'addons/example.staging'
        catalog=base/'wiki'; catalog.mkdir(parents=True,exist_ok=True)
        folder=base/version
        m={'schema':1,'kind':'reference','id':'example.staging','version':version,
           'revision':'sample.1','title':'合成场面参考','summary':'独立测试资料。','status':status,
           'documents':[{'id':'entry','title':'使用入口','path':'SKILL.md'},{'id':'method','title':'停顿方法','path':'references/method.md'}]}
        (catalog/(version+'.json')).write_text(json.dumps(m,ensure_ascii=False),'utf-8')
        if status=='available':
            (folder/'references').mkdir(parents=True)
            (folder/'SKILL.md').write_text('---\nname: example-staging\ndescription: Synthetic metadata only\n---\n\n# 合成场面参考\n\n[停顿方法](references/method.md#方法)\n','utf-8')
            (folder/'references/method.md').write_text('# 停顿方法\n\n## 方法\n\n合成停顿节奏 '+version+'。\n','utf-8')
        return catalog/(version+'.json'),m
    p,m=package('1.0.0');package('2.0.0');paused,_=package('0.5.0','paused')
    (area/'addons/INDEX.md').write_text('示例参考包：启用，选用版本 1.0.0；其他版本仅供比较。','utf-8')
    def hashes():return {x.relative_to(area).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in area.rglob('*') if x.is_file()}
    before=hashes();library=collect(area)
    check('reference-versions-kept',len(library['items'])==3 and {x['version'] for x in library['items']}=={'0.5.0','1.0.0','2.0.0'})
    check('reference-section',all(x['section']=='references' for x in library['items']))
    check('paused-missing-payload-not-opened',not next(x for x in library['items'] if x['status']=='paused')['documents'])
    check('version-payload-unchanged-by-adapter',not any('wiki.json' in x for x in before))
    first=next(x for x in library['items'] if x['version']=='1.0.0')
    check('skill-frontmatter-not-in-reading-body','Synthetic metadata only' not in first['documents'][0]['html'] and '合成场面参考' in first['documents'][0]['html'])
    check('cross-document-link',('#'+first['uid']+'-method--方法') in first['documents'][0]['html'])
    receipt=build(area,scratch/'local-workbench.html',scratch/'library.json')
    check('build-matches-library',receipt['documents']==4 and json.loads((scratch/'library.json').read_text('utf-8'))==library)
    check('index-and-payload-readonly',hashes()==before)
    original=p.read_bytes()
    for name,change in [
        ('wrong-kind',lambda v:v.update(kind='plugin')),
        ('wrong-id',lambda v:v.update(id='wrong')),
        ('wrong-version',lambda v:v.update(version='9.0.0')),
        ('traversal',lambda v:v['documents'][0].update(path='../INDEX.md')),
        ('absolute',lambda v:v['documents'][0].update(path='/outside.md')),
        ('missing-active-document',lambda v:v['documents'][0].update(path='missing.md')),
        ('empty-active-docs',lambda v:v.update(documents=[])),
        ('duplicate-doc-id',lambda v:v['documents'][1].update(id='entry')),
        ('unknown-status',lambda v:v.update(status='enabled')),
    ]:
        changed=copy.deepcopy(m);change(changed);p.write_text(json.dumps(changed),'utf-8')
        try: collect(area)
        except ValueError: check(name+'-rejected',True)
        else: check(name+'-rejected',False)
        p.write_bytes(original)
    check('failed-reads-preserve-files',hashes()==before)
    page,info=render()
    check('public-page-empty-library',info['library_items']==0 and '合成停顿节奏' not in page)
    cli=subprocess.run([sys.executable,'-B',str(ROOT/'maintenance/build_workbench.py'),'--user-area',str(area),'--check'],capture_output=True)
    check('cli-contract',cli.returncode==0 and json.loads(cli.stdout)['items']==3)
    # Reference adapter complements existing plugin/personal manifests, whose
    # validation and destination rules are covered by run_wiki_checks.py.
    return {'status':'passed','checks':len(results),'scope':'synthetic reference manifests and payloads; no installation or Studio operation'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--scratch',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(run(args.scratch),ensure_ascii=False))
