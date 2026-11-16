"""Isolated Wiki contract and browser checks. Requires Python Markdown and Playwright; uses a NEW scratch directory."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from build_manual import ROOT, render
from build_workbench import build, collect

def run(scratch, browser_path, contract_only=False):
    scratch=Path(scratch).resolve(); scratch.mkdir(parents=True,exist_ok=False)
    results=[]
    def check(name, condition, detail=None):
        results.append({'name':name,'passed':bool(condition),'detail':detail})
        (scratch/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n','utf-8')
        assert condition,name
    area=scratch/'synthetic-user-area'; area.mkdir()
    def package(version, status='available', kind='plugin'):
        folder=area/'plugins/example.weather'/version if kind=='plugin' else area/'preferences'
        folder.mkdir(parents=True)
        value={'schema':1,'kind':kind,'id':'example.weather' if kind=='plugin' else 'example.preferences','version':version,'revision':'guide.1','title':'合成天气插件' if kind=='plugin' else '合成个人约定','summary':'仅供自动化验证的合成资料。','status':status,'documents':[{'id':'guide','title':'指南','path':'guide.md'},{'id':'reference','title':'参数','path':'reference.md'}]}
        (folder/'wiki.json').write_text(json.dumps(value,ensure_ascii=False),'utf-8')
        if status=='available':
            (folder/'guide.md').write_text('# 合成指南\n\n## 唯一检索词\n\n合成雨幕参照 '+version+'。\n\n[参数页](reference.md#参数说明)\n\n<script>window.BAD_EXECUTED=true</script>\n<img src="https://invalid.example/private-beacon">\n\n[危险地址](javascript:alert(1))\n','utf-8')
            (folder/'reference.md').write_text('# 合成参数\n\n## 参数说明\n\n保持原有设置。\n','utf-8')
        return folder,value
    first,manifest=package('1.0.0'); package('2.0.0'); package('0.5.0','paused'); package('1',kind='personal')
    manifest['navigation']={'intro':'从合成指南开始。','start':'guide','groups':[{'title':'开始使用','documents':['guide']}]}
    (first/'wiki.json').write_text(json.dumps(manifest,ensure_ascii=False),'utf-8')
    hashes=lambda:{p.relative_to(area).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in area.rglob('*') if p.is_file()}
    before=hashes(); library=collect(area)
    check('two-versions-and-personal-collected',len(library['items'])==4)
    check('source-navigation-compiled',next(i for i in library['items'] if i['id']=='example.weather' and i['version']=='1.0.0')['navigation']==manifest['navigation'])
    paused=next(i for i in library['items'] if i['status']=='paused')
    check('paused-missing-documents-not-read',not paused['documents'])
    output=scratch/'local-workbench.html'; data_output=scratch/'library.json'
    receipt=build(area,output,data_output)
    check('local-build-readback',receipt['documents']==6 and output.exists() and json.loads(data_output.read_text('utf-8'))==library)
    check('user-files-unchanged',before==hashes())
    try: build(area,output,data_output)
    except ValueError: check('existing-output-preserved',True)
    else: check('existing-output-preserved',False)
    try: build(area,ROOT/'private-workbench.html')
    except ValueError: check('private-output-rejected-in-public-tree',True)
    else: check('private-output-rejected-in-public-tree',False)
    original=(first/'wiki.json').read_bytes()
    for name,alter in [
        ('id-mismatch',lambda v:v.update(id='different.plugin')),
        ('version-mismatch',lambda v:v.update(version='9.0.0')),
        ('path-traversal',lambda v:v['documents'][0].update(path='../outside.md')),
        ('duplicate-doc-id',lambda v:v['documents'][1].update(id='guide')),
        ('numeric-doc-id',lambda v:v['documents'][0].update(id=5)),
        ('unknown-state',lambda v:v.update(status='enabled')),
    ]:
        changed=copy.deepcopy(manifest); alter(changed)
        (first/'wiki.json').write_text(json.dumps(changed),'utf-8')
        try: collect(area)
        except ValueError: check(name+'-rejected',True)
        else: check(name+'-rejected',False)
        (first/'wiki.json').write_bytes(original)
    command=[sys.executable,'-B',str(ROOT/'maintenance/build_workbench.py'),'--user-area',str(area),'--check']
    cli=subprocess.run(command,capture_output=True)
    check('cli-json-and-success-exit',cli.returncode==0 and json.loads(cli.stdout)['status']=='checked')
    command[command.index(str(area))]=str(scratch/'missing')
    cli=subprocess.run(command,capture_output=True)
    check('cli-json-and-error-exit',cli.returncode==1 and json.loads(cli.stdout)['status']=='error')
    markup,report=render(); check('public-has-no-synthetic-private-data','合成雨幕参照' not in markup and report['library_items']==0)

    if contract_only:
        return {'status':'passed','checks':len(results),'evidence':str(scratch),'scope':'isolated generator contracts only'}

    from playwright.sync_api import sync_playwright,expect
    with sync_playwright() as pw:
        options={'headless':True}
        if browser_path:options['executable_path']=str(browser_path)
        browser=pw.chromium.launch(**options)
        context=browser.new_context(viewport={'width':1440,'height':1000})
        page=context.new_page();errors=[];requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
        markup,report=render();page.set_content(markup)
        def go(hash):
            page.evaluate('(hash)=>location.hash=hash',hash);page.wait_for_timeout(45)
        check('public-three-modules',page.locator('#module-grid .module-card').count()==3);go('module/main');check('main-module-core-guide',page.locator('#space-grid .space-card').count()==1)
        page.locator('#space-grid .space-card').click();expect(page.locator('#space-title')).to_have_text('引擎创作指南')
        check('core-space-owns-rail',page.locator('#rail-chapters a[href="#wiki03"]').count()==1 and page.locator('#rail-chapters a[href="#wiki10"]').count()==0)
        page.locator('#rail-chapters a[href="#wiki03"]').click();expect(page.locator('#wiki03')).to_be_visible()
        check('core-reader-context',page.locator('#space-switcher').input_value()=='core' and page.locator('#toc a').count()>0)
        page.locator('#search').fill('修订');page.locator('#search-scope').select_option('all')
        check('main-text-search',page.locator('.search-item').count()>0)
        page.locator('#clear-search').click();page.keyboard.press('Control+k');check('keyboard-search',page.locator('#search').evaluate('(n)=>n===document.activeElement'))
        page.locator('#search').fill('根本没有的检索词abc123');check('empty-search','没有找到' in page.locator('#search-count').inner_text());page.keyboard.press('Escape')
        go('选择正式版或-beta');check('legacy-anchor',page.locator('#wiki02').is_visible())
        go('help');check('workspace-help',page.locator('#help-view').is_visible());go('wiki10');check('help-not-in-core-sidebar',page.locator('#space-switcher').input_value()=='home' and page.locator('#rail-chapters a[href="#wiki03"]').count()==0)
        go('home');page.locator('#library-file').set_input_files(str(data_output));expect(page.locator('#status')).to_contain_text('已载入 4 份资料')
        go('module/skills');check('same-package-versions-one-space',page.locator('#space-grid .space-card').count()==1)
        go('module/skills');expect(page.locator('#space-grid .space-card')).to_have_count(1)
        check('home-category-filter',page.locator('#home-view').is_visible())
        page.locator('#space-grid .space-card').click();expect(page.locator('#space-title')).to_have_text('合成天气插件')
        check('auto-multiple-no-guessed-version',page.locator('#reading-version').input_value()=='' and page.locator('#version-choice a').count()==2)
        first_index=next(n for n,x in enumerate(library['items']) if x['id']=='example.weather' and x['version']=='1.0.0')
        first_uid=library['items'][first_index]['uid'];page.locator('#reading-version').select_option(first_uid);page.wait_for_timeout(45)
        second_uid=next(x['uid'] for x in library['items'] if x['id']=='example.weather' and x['version']=='2.0.0')
        check('version-specific-sidebar',page.locator('#rail-chapters a[href^="#'+first_uid+'-"]').count()==2 and page.locator('#rail-chapters a[href^="#'+second_uid+'-"]').count()==0)
        page.locator('#space-start').click();page.wait_for_timeout(45)
        check('local-search-default',page.locator('#search-scope').input_value()=='current')
        page.locator('#search').fill('合成雨幕参照');check('one-edition-search',page.locator('.search-item').count()==1)
        page.locator('#search-scope').select_option('all');check('global-search-all-visible-editions',page.locator('.search-item').count()==3)
        page.locator('.search-item').last.click();page.wait_for_timeout(45)
        check('search-result-switches-space',page.locator('#space-switcher').input_value()=='legacy/personal/example.preferences')
        page.locator('#space-switcher').select_option('legacy/skills/example.weather');page.wait_for_timeout(45)
        page.locator('#reading-version').select_option(first_uid);page.wait_for_timeout(45);page.locator('#space-start').click();page.wait_for_timeout(45)
        current=page.locator('.article[data-external]:visible');current.get_by_role('link',name='参数页').click();page.wait_for_timeout(45)
        check('cross-document-link-and-context',page.locator('.article[data-external]:visible').get_by_role('heading',name='参数说明').count()==1 and page.locator('#reading-version').input_value()==first_uid)
        page.go_back();page.wait_for_timeout(45);check('browser-back',page.locator('.article[data-external]:visible').get_by_role('heading',name='合成指南',exact=True).count()==1)
        page.go_forward();page.wait_for_timeout(45);check('browser-forward',page.locator('.article[data-external]:visible').get_by_role('heading',name='参数说明').count()==1)
        page.emulate_media(media='print');check('print-current-document',page.locator('.article:visible').count()==1);page.emulate_media(media='screen')
        page.locator('#reader-back').click();page.wait_for_timeout(45);page.emulate_media(media='print');check('print-current-guide',page.locator('.article:visible').count()==2);page.emulate_media(media='screen')
        page.locator('#reading-version').select_option(second_uid);page.wait_for_timeout(45)
        check('reading-version-switch',page.locator('#rail-chapters a[href^="#'+first_uid+'-"]').count()==0 and page.locator('#rail-chapters a[href^="#'+second_uid+'-"]').count()==2)
        navlib=copy.deepcopy(library);item=next(x for x in navlib['items'] if x['uid']==first_uid)
        item['navigation']={'intro':'合成导览简介','start':'reference','groups':[{'title':'配置查阅','summary':'合成分组说明','documents':['reference']}]}
        page.evaluate('(lib)=>LetsGalWiki.register(lib)',navlib)
        go('space/legacy%2Fskills%2Fexample.weather/'+first_uid)
        check('declared-navigation-and-unlisted-preserved',page.locator('#space-intro').inner_text()=='合成导览简介' and page.locator('#guide-groups h2').all_text_contents()==['配置查阅','其他资料'] and page.locator('#space-start').get_attribute('href')=='#'+first_uid+'-reference')
        page.screenshot(path=str(scratch/'desktop-space.png'),full_page=True)
        for name,mutate in [('missing-navigation-id',lambda v:v['items'][first_index].update(navigation={'start':'absent'})),('duplicate-navigation-member',lambda v:v['items'][first_index].update(navigation={'groups':[{'title':'重复','documents':['guide','guide']}]})),('duplicate-item',lambda v:v['items'].append(copy.deepcopy(v['items'][0])))]:
            bad=copy.deepcopy(navlib);mutate(bad);answer=page.evaluate('(value)=>{try{LetsGalWiki.register(value);return false}catch(e){return true}}',bad)
            check(name+'-atomic',answer and page.locator('.article[data-external]').count()==6 and page.locator('#space-intro').inner_text()=='合成导览简介')
        check('unsafe-import-filtered',page.evaluate('window.BAD_EXECUTED!==true') and page.locator('.article[data-external] img,.article[data-external] script,.article[data-external] a[href^="javascript:"]').count()==0)
        go('packages');page.locator('#package-list details').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=true)');check('hidden-version-still-in-manager','0.5.0' in page.locator('#package-list').inner_text())
        go('space/legacy%2Fskills%2Fexample.weather/'+paused['uid']);check('hidden-edition-not-read',page.locator('#version-choice').is_visible() and page.locator('#rail-chapters a[href^="#'+paused['uid']+'-"]').count()==0)
        go('ext-0000000000000000-absent');check('unavailable-deep-link',page.locator('#unavailable-view').is_visible())
        go('wiki03');check('route-notice-cleared-after-valid-navigation',page.locator('#status').inner_text()=='');page.evaluate('Object.defineProperty(navigator,"clipboard",{value:{writeText:async value=>{window.COPIED=value}},configurable:true})');page.locator('#wiki03 .copy-btn').first.click();page.wait_for_timeout(30)
        check('copy-prompt',page.evaluate('typeof window.COPIED==="string" && window.COPIED.length>10 && !window.COPIED.includes("复制需求")'))
        for width in (1440,1024,768,390):
            page.set_viewport_size({'width':width,'height':900 if width>600 else 844})
            for hash,name in [('home','home'),('space/legacy%2Fskills%2Fexample.weather/'+first_uid,'space'),(first_uid+'-guide','reader')]:
                go(hash);check(name+'-width-'+str(width),page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                if width==390:page.screenshot(path=str(scratch/('mobile-'+name+'.png')),full_page=True)
            if width==390:
                page.locator('#menu-toggle').click();check('mobile-nav-opens',page.locator('#rail').evaluate('n=>n.classList.contains("open")'));page.locator('#space-switcher').select_option('core');page.wait_for_timeout(45);check('mobile-switch-closes-nav',not page.locator('#rail').evaluate('n=>n.classList.contains("open")'))
        page.set_viewport_size({'width':1440,'height':1000});go('home');page.screenshot(path=str(scratch/'desktop-home.png'),full_page=True)
        go('wiki07');headings=page.locator('#wiki07 h2[id],#wiki07 h3[id]');headings.nth(2).scroll_into_view_if_needed();page.evaluate('(id)=>document.getElementById(id).scrollIntoView({block:"start"})',headings.nth(2).get_attribute('id'));page.wait_for_timeout(80)
        check('toc-follows-scroll-without-navigation',page.locator('#toc a[aria-current="location"]').get_attribute('href')=='#'+headings.nth(2).get_attribute('id') and page.evaluate('location.hash')=='#wiki07')
        page.screenshot(path=str(scratch/'desktop-reader.png'),full_page=False)
        go('all');page.emulate_media(media='print');check('print-all-visible-documents',page.locator('.article:visible').count()==report['pages']+receipt['documents']);page.pdf(path=str(scratch/'manual-print.pdf'),prefer_css_page_size=True,print_background=True);page.emulate_media(media='screen')
        check('no-browser-errors',not errors,errors);check('no-automatic-network',not requests,requests)
        context.close()
        local_context=browser.new_context();local_page=local_context.new_page();local_page.set_content(output.read_text('utf-8'));local_page.evaluate('location.hash="module/skills"');local_page.wait_for_timeout(60);check('generated-library-auto-load',local_page.locator('#space-grid .space-card').count()==1);local_context.close()
        fallback=browser.new_context(java_script_enabled=False);fallback_page=fallback.new_page();fallback_page.set_content(markup);check('no-js-complete-reading',fallback_page.locator('.article:visible').count()==report['pages']);fallback.close();browser.close()
    check('final-user-area-unchanged',before==hashes())
    return {'status':'passed','checks':len(results),'evidence':str(scratch),'scope':'isolated synthetic fixtures and generated development markup; no Studio or user browser operation'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch',type=Path,required=True)
    parser.add_argument('--browser-path',type=Path)
    parser.add_argument('--contract-only',action='store_true')
    args=parser.parse_args()
    print(json.dumps(run(args.scratch,args.browser_path,args.contract_only),ensure_ascii=False))

if __name__=='__main__': main()
