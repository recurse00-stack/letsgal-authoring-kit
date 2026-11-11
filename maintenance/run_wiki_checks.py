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

def run(scratch, browser_path):
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
    hashes=lambda:{p.relative_to(area).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in area.rglob('*') if p.is_file()}
    before=hashes(); library=collect(area)
    check('two-versions-and-personal-collected',len(library['items'])==4)
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

    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        options={'headless':True}
        if browser_path: options['executable_path']=str(browser_path)
        browser=playwright.chromium.launch(**options)
        context=browser.new_context(viewport={'width':1440,'height':1000})
        page=context.new_page(); errors=[]; requests=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('request',lambda request:requests.append(request.url))
        # Render generated development markup in an isolated blank document.
        # No file URL, user browser, localhost server or production UI is used.
        page.set_content(markup,wait_until='load')
        page.screenshot(path=str(scratch/'desktop-home.png'),full_page=True)
        check('three-main-regions',page.locator('.areas a').count()==3)
        check('public-home-visible',page.locator('#home-view').is_visible() and not page.locator('#reader-view').is_visible())
        page.locator('#search').fill('调度'); check('chinese-fulltext-search',page.locator('.search-item').count()>0)
        page.locator('.search-item').first.click(); page.wait_for_timeout(80)
        check('search-opens-matching-article',page.locator('#wiki07').is_visible() and not page.locator('#search-results').is_visible())
        page.screenshot(path=str(scratch/'desktop-reader.png'),full_page=False)
        page.locator('#search').fill('WINDOW_HIDDEN'); check('case-insensitive-search',page.locator('.search-item').count()>0)
        page.locator('#search-scope').select_option('personal'); check('scope-filter-empty-state',page.locator('.search-item').count()==0 and '没有找到' in page.locator('#search-count').inner_text())
        page.locator('#search-scope').select_option('all'); page.locator('#clear-search').click()
        page.keyboard.press('Control+k'); check('keyboard-search-shortcut',page.locator('#search').evaluate('(node)=>node===document.activeElement'))
        page.locator('#search').fill('根本没有的检索词abc123'); check('empty-search-state','没有找到' in page.locator('#search-count').inner_text())
        page.keyboard.press('Escape'); check('escape-clears-search',page.locator('#search').input_value()=='')
        for area_name in ['skills','personal','main']:
            page.locator('.areas a[data-area="'+area_name+'"]').click()
            check('area-'+area_name,page.locator('#area-view').is_visible() and page.locator('#chapter-grid .chapter-card').count()>0)
        page.evaluate("location.hash='选择正式版或-beta'"); page.wait_for_timeout(40)
        check('legacy-anchor-routes-to-connection',page.locator('#wiki02').is_visible())
        page.evaluate("location.hash='home'"); page.wait_for_timeout(40)
        page.locator('#library-file').set_input_files(str(data_output)); page.wait_for_timeout(80)
        check('file-picker-loads-library','已载入 4 份资料' in page.locator('#status').inner_text())
        page.locator('.areas a[data-area="skills"]').click()
        check('versions-and-pause-visible',page.locator('.library-card').count()==3 and page.locator('.badge.paused').count()==1)
        page.screenshot(path=str(scratch/'desktop-library.png'),full_page=False)
        check('imported-active-content-removed',page.evaluate('window.BAD_EXECUTED!==true') and page.locator('.article[data-external] img,.article[data-external] script,.article[data-external] a[href^="javascript:"]').count()==0)
        page.locator('#search').fill('合成雨幕参照'); check('imported-searchable',page.locator('.search-item').count()==3)
        page.locator('.search-item').first.click(); page.wait_for_timeout(50)
        current=page.locator('.article[data-external]:visible')
        check('imported-document-opens',current.count()==1)
        current.get_by_role('link',name='参数页').click(); page.wait_for_timeout(50)
        check('cross-document-link',page.locator('.article[data-external]:visible').get_by_role('heading',name='参数说明').is_visible())
        bad=copy.deepcopy(library); bad['items'].append(copy.deepcopy(bad['items'][0]))
        answer=page.evaluate('(value)=>{try{LetsGalWiki.register(value);return false}catch(e){return true}}',bad)
        check('invalid-import-atomic',answer and page.locator('.article[data-external]').count()==6)
        page.evaluate("location.hash='wiki03'"); page.wait_for_timeout(50)
        page.evaluate('Object.defineProperty(navigator,"clipboard",{value:{writeText:async value=>{window.COPIED=value}},configurable:true})')
        page.locator('#wiki03 .copy-btn').first.click(); page.wait_for_timeout(30)
        check('copy-prompt-simulated-clipboard',page.evaluate('typeof window.COPIED==="string" && window.COPIED.length>10 && !window.COPIED.includes("复制需求")'))
        for width in (1440,1024,768,390):
            page.set_viewport_size({'width':width,'height':900 if width>600 else 844})
            page.evaluate("location.hash='home'"); page.wait_for_timeout(50)
            check('home-width-'+str(width),page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            if width==390:
                page.screenshot(path=str(scratch/'mobile-home.png'),full_page=True)
                page.locator('#menu-toggle').click(); check('mobile-navigation',page.locator('#rail').evaluate('node=>node.classList.contains("open")'))
                page.locator('.areas a[data-area="personal"]').click(); check('mobile-navigation-closes',not page.locator('#rail').evaluate('node=>node.classList.contains("open")'))
            page.evaluate("location.hash='wiki07'"); page.wait_for_timeout(50)
            check('reader-width-'+str(width),page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            if width==390: page.screenshot(path=str(scratch/'mobile-reader.png'),full_page=True)
        page.emulate_media(media='print')
        check('print-includes-all-articles',page.locator('.article:visible').count()==17)
        page.pdf(path=str(scratch/'manual-print.pdf'),prefer_css_page_size=True,print_background=True)
        check('runtime-no-errors',not errors,errors)
        check('no-automatic-network',not requests,requests)
        context.close()
        local_context=browser.new_context(viewport={'width':1440,'height':1000})
        local_page=local_context.new_page(); local_page.set_content(output.read_text('utf-8'))
        check('generated-local-library-auto-appears',local_page.locator('.article[data-external]').count()==6)
        local_context.close()
        public_context=browser.new_context(viewport={'width':1440,'height':1000})
        public_page=public_context.new_page(); public_page.set_content(markup)
        public_page.emulate_media(media='print')
        check('public-print-all-chapters',public_page.locator('.article:visible').count()==11)
        public_page.pdf(path=str(scratch/'public-manual-print.pdf'),prefer_css_page_size=True,print_background=True)
        public_context.close()
        fallback=browser.new_context(java_script_enabled=False)
        page=fallback.new_page(); page.set_content(markup)
        check('no-javascript-complete-reading',page.locator('.article:visible').count()==11)
        fallback.close(); browser.close()
    check('final-user-area-unchanged',before==hashes())
    return {'status':'passed','checks':len(results),'evidence':str(scratch),'scope':'isolated synthetic fixtures and generated development markup; no Studio or user browser operation'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch',type=Path,required=True)
    parser.add_argument('--browser-path',type=Path)
    args=parser.parse_args()
    print(json.dumps(run(args.scratch,args.browser_path),ensure_ascii=False))

if __name__=='__main__': main()
