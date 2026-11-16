"""Isolated personal-package, editor and three-module acceptance checks."""
import argparse, copy, http.client, json, subprocess, sys, threading
from pathlib import Path
from unittest.mock import patch
import workbench_runtime as w
import workbench_packages as packages
import workbench_personal as personal
from workbench_server import Server

ROOT=Path(__file__).resolve().parents[1]

def run(scratch,browser_path=None,contracts_only=False):
    scratch=Path(scratch).resolve();scratch.mkdir(parents=True,exist_ok=False)
    results=[]
    def check(name,condition):
        results.append({'name':name,'passed':bool(condition)})
        (scratch/'results.json').write_bytes(w.encode(results));assert condition,name
    area=scratch/'user';area.mkdir();w.setup(ROOT,area)
    check('default-empty-pages-and-enabled',set(personal.DOCUMENTS)=={'requirements','memory','guide'} and personal.state(area)['enabled'] and not personal.state(area)['show_when_paused'] and all(personal.document(area,k)['exists'] for k in personal.DOCUMENTS))
    check('personal-is-user-data-without-release-selector',personal.catalog(area)['versions']==[] and personal.catalog(area)['selection_mode']=='personal')
    check('repeat-setup-no-change',w.setup(ROOT,area)['write']['status']=='verified-unchanged')
    original=personal.snapshot(area,'requirements');result=personal.save(area,'requirements','# 我的要求\n\n合成偏好甲。\n',original['fingerprint'])
    backup=Path(result['write']['backup'])/'preferences/user.md'
    check('save-backs-up-reads-back-and-refreshes',backup.read_text('utf-8')==original['content'] and result['document']['content']=='# 我的要求\n\n合成偏好甲。\n' and '合成偏好甲' in (area/'workbench/MANUAL.html').read_text('utf-8'))
    check('same-content-save-is-noop',personal.save(area,'requirements',result['document']['content'],result['document']['fingerprint'])['write']['status']=='verified-unchanged')
    before=w.file_map(area)
    try:personal.save(area,'requirements','stale',original['fingerprint'])
    except packages.Conflict:check('stale-document-keeps-all-files',w.file_map(area)==before)
    else:check('stale-document-keeps-all-files',False)
    for key,content in [('../outside','x'),('unknown','x'),('memory','\0'),('memory','x'*1000001)]:
        before=w.file_map(area)
        try:personal.save(area,key,content,'no-fingerprint')
        except (ValueError,packages.Conflict):check('invalid-personal-write-'+str(len(results)),w.file_map(area)==before)
        else:check('invalid-personal-write-'+str(len(results)),False)
    before=w.file_map(area/'preferences');old=personal.catalog(area)['fingerprint']
    packages.change(area,personal.KEY,{'enabled':False},old)
    check('paused-skips-ai-and-hidden-body',packages.resolve(area,personal.KEY)['status']=='paused' and not personal.library_item(area)['documents'])
    packages.change(area,personal.KEY,{'show_when_paused':True})
    check('paused-display-is-independent',len(personal.library_item(area)['documents'])==3 and packages.resolve(area,personal.KEY)['status']=='paused')
    p=personal.snapshot(area,'memory');personal.save(area,'memory','# 长期记忆\n\n合成事实。\n',p['fingerprint'])
    check('editing-does-not-enable',not personal.state(area)['enabled'])
    files=w.file_map(area/'preferences');w.setup(ROOT,area)
    check('setup-preserves-edits-and-state',files==w.file_map(area/'preferences'))
    try:packages.change(area,personal.KEY,{'selected_version':'local'})
    except ValueError:check('no-personal-version-mutation',True)
    else:check('no-personal-version-mutation',False)
    cli=subprocess.run([sys.executable,'-B',str(ROOT/'maintenance/workbench_runtime.py'),'state','--user-area',str(area),'--package-type','personal','--id','letsgal-personal','--enabled','yes'],capture_output=True)
    check('personal-state-cli-compatible-json-exit',cli.returncode==0 and json.loads(cli.stdout)['enabled'] is True)
    legacy=scratch/'legacy';legacy.mkdir();(legacy/'user.md').write_text('合成旧偏好。','utf-8');w.setup(ROOT,legacy)
    check('legacy-path-not-shadowed',not (legacy/'preferences/user.md').exists() and personal.snapshot(legacy,'requirements')['path']=='user.md')
    snap=personal.snapshot(legacy,'requirements');personal.save(legacy,'requirements','合成旧偏好更新。',snap['fingerprint'])
    check('legacy-edit-stays-in-original-file',(legacy/'user.md').read_text('utf-8')=='合成旧偏好更新。' and not (legacy/'preferences/user.md').exists())
    (legacy/'preferences/user.md').write_text('合成新偏好。','utf-8');before=w.file_map(legacy/'preferences');w.setup(ROOT,legacy)
    check('dual-path-notice-preserves-both',personal.snapshot(legacy,'requirements')['legacy_notice'] and before==w.file_map(legacy/'preferences') and (legacy/'user.md').read_text('utf-8')=='合成旧偏好更新。')
    before=w.file_map(area/'preferences');page=(area/'workbench/MANUAL.html').read_bytes();original_replace=w.os.replace;calls=[]
    def fail_second(a,b):
        calls.append(b)
        if len(calls)==2:raise OSError('synthetic transaction failure')
        return original_replace(a,b)
    snap=personal.snapshot(area,'guide')
    with patch.object(w.os,'replace',fail_second):
        try:personal.save(area,'guide','# 合成失败写入',snap['fingerprint'])
        except OSError:check('save-rollback-restores-document-and-wiki',before==w.file_map(area/'preferences') and page==(area/'workbench/MANUAL.html').read_bytes())
        else:check('save-rollback-restores-document-and-wiki',False)
    server=Server(area);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    def request(method,path,body=None,authorized=True):
        connection=http.client.HTTPConnection('127.0.0.1',server.server_port)
        headers={'Content-Type':'application/json','Origin':server.origin}
        if authorized:headers['X-LetsGal-Session']=server.token
        connection.request(method,path,None if body is None else json.dumps(body),headers);response=connection.getresponse();data=json.loads(response.read());status=response.status;connection.close();return status,data
    try:
        check('personal-http-requires-session',request('GET','/api/personal/requirements',authorized=False)[0]==403)
        code,d=request('GET','/api/personal/requirements');check('personal-http-read-fingerprint',code==200 and d['fingerprint'])
        check('personal-http-stale-conflict',request('POST','/api/personal/save',{'document':'requirements','content':'stale','expected':'0'*64})[0]==409)
        check('personal-http-no-arbitrary-path',request('GET','/api/personal/../../outside')[0]==422)
        if not contracts_only:
            check('enable-retains-paused-display-choice',personal.state(area)['show_when_paused'])
            packages.change(area,personal.KEY,{'show_when_paused':False})
            from playwright.sync_api import sync_playwright,expect
            with sync_playwright() as pw:
                options={'headless':True}
                if browser_path:options['executable_path']=str(browser_path)
                browser=pw.chromium.launch(**options);ctx=browser.new_context(viewport={'width':1440,'height':1000});p=ctx.new_page();errors=[];requests=[]
                p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) and not r.url.startswith(server.origin+'/') else None)
                p.goto(server.origin+server.entry);expect(p.locator('#module-grid .module-card')).to_have_count(3)
                check('three-modules-not-flat-spaces',p.locator('#module-directory').is_hidden() and p.locator('.module-card h2').all_text_contents()==['主体','Skill Wiki','个性化'])
                check('no-duplicate-top-package-management',p.locator('.top-actions a[href="#packages"]').count()==0)
                check('history-initial-disabled',p.locator('#nav-back').is_disabled() and p.locator('#nav-forward').is_disabled())
                p.screenshot(path=str(scratch/'home.png'),full_page=True)
                p.locator('[data-module="main"]').click();p.locator('[data-space-key="core"]').click();p.locator('#rail-chapters a[href="#wiki03"]').click();expect(p.locator('#wiki03')).to_be_visible()
                p.locator('#nav-back').click();expect(p.locator('#space-title')).to_have_text('引擎创作指南')
                p.locator('#nav-back').click();expect(p.locator('#module-title')).to_have_text('主体')
                p.locator('#nav-forward').click();expect(p.locator('#space-title')).to_have_text('引擎创作指南')
                check('history-follows-actual-routes',p.locator('#nav-forward').is_enabled())
                p.locator('#space-switcher').select_option('module/personal');expect(p.locator('#module-title')).to_have_text('个性化');check('new-route-discards-forward-branch',p.locator('#nav-forward').is_disabled())
                p.reload();expect(p.locator('#module-title')).to_have_text('个性化');check('history-survives-refresh-within-tab',p.locator('#nav-back').is_enabled())
                p.locator('#module-personal-edit').click();expect(p.locator('#personal-content')).to_be_enabled()
                sample='# 我的要求\n\n**合成清澈标记**\n\n<script>window.BAD_PERSONAL=true</script>\n<img src="https://invalid.example/beacon">\n[危险](javascript:alert(1))\n'
                p.locator('#personal-content').fill(sample);expect(p.locator('#personal-preview strong')).to_have_text('合成清澈标记')
                check('preview-visible-and-sanitized',p.locator('#personal-preview').is_visible() and p.locator('#personal-preview script,#personal-preview img,#personal-preview a[href^="javascript:"]').count()==0 and p.evaluate('window.BAD_PERSONAL!==true'))
                p.once('dialog',lambda dialog:dialog.dismiss());p.locator('#nav-back').click();expect(p.locator('#personal-editor')).to_be_visible();p.wait_for_timeout(80)
                check('cancel-navigation-keeps-draft-and-route',p.url.endswith('#personal-edit/requirements') and p.locator('#personal-content').input_value()==sample)
                p.locator('#personal-save').click();expect(p.locator('#personal-status')).to_contain_text('已保存并读回')
                check('editor-save-preserves-source',personal.snapshot(area,'requirements')['content']==sample)
                p.screenshot(path=str(scratch/'editor.png'),full_page=True)
                # An external edit after the browser's load must not be overwritten.
                p.locator('#personal-content').fill('# 我的要求\n\n浏览器草稿。');(area/'preferences/user.md').write_text('# 我的要求\n\n外部新事实。','utf-8')
                p.locator('#personal-save').click();expect(p.locator('#personal-conflict')).to_be_visible()
                check('conflict-keeps-draft-and-shows-latest','浏览器草稿' in p.locator('#personal-content').input_value() and '外部新事实' in p.locator('#personal-latest').inner_text() and '外部新事实' in (area/'preferences/user.md').read_text('utf-8'))
                p.locator('#personal-merge').click();p.locator('#personal-content').fill('# 我的要求\n\n外部新事实。\n\n浏览器草稿。');p.locator('#personal-save').click();expect(p.locator('#personal-status')).to_contain_text('已保存并读回')
                check('explicit-conflict-merge-retains-both','外部新事实' in personal.snapshot(area,'requirements')['content'] and '浏览器草稿' in personal.snapshot(area,'requirements')['content'])
                p.locator('a[href="#personal-edit/guide"]').first.click();expect(p.locator('#personal-content')).to_have_value(personal.snapshot(area,'guide')['content']);p.locator('#personal-content').fill('# 我的指南\n\n合成指南检索词。');p.locator('#personal-save').click();expect(p.locator('#personal-status')).to_contain_text('已保存并读回')
                p.locator('#rail-home').click();p.locator('#home-tools a[href="#packages"]').click();card=p.locator('[data-package-key="'+personal.KEY+'"]');expect(card).to_be_visible()
                check('personal-manager-no-version-selector',card.locator('select').count()==0)
                card.get_by_role('button',name='暂停 我的个人包',exact=True).click();expect(card.get_by_text('AI 已暂停',exact=True)).to_be_visible()
                check('pause-removes-search-and-ai-body',packages.resolve(area,personal.KEY)['status']=='paused' and not personal.library_item(area)['documents'])
                card.get_by_role('link',name='编辑我的个人包 →').click();expect(p.locator('#personal-content')).to_be_enabled();p.locator('#personal-content').fill('# 我的要求\n\n暂停时编辑保留。');p.locator('#personal-save').click();expect(p.locator('#personal-status')).to_contain_text('已保存并读回');check('paused-editor-does-not-enable',not personal.state(area)['enabled'])
                p.locator('#rail-home').click();p.locator('#home-tools a[href="#packages"]').click();card.get_by_role('checkbox').check();expect(card.get_by_text('Wiki 已显示',exact=True)).to_be_visible();check('paused-show-keeps-ai-paused',packages.resolve(area,personal.KEY)['status']=='paused')
                p.locator('#rail-home').click();p.locator('[data-module="personal"]').click();p.locator('[data-space-key="'+personal.KEY+'"]').click();expect(p.locator('#space-title')).to_have_text('我的个人包');check('personal-read-space-hides-version-selector',p.locator('#rail-version-wrap').is_hidden())
                p.locator('#space-start').click();expect(p.locator('#'+personal.UID+'-requirements')).to_be_visible();p.locator('#search').fill('合成指南检索词');expect(p.locator('#result-list a')).to_have_count(1);p.locator('#result-list a').click();expect(p.locator('#'+personal.UID+'-guide')).to_be_visible();check('saved-personal-index-and-reading-work',True)
                p.emulate_media(media='print');check('personal-page-print',p.locator('#articles .article:visible').count()==1);p.pdf(path=str(scratch/'personal-print.pdf'));p.emulate_media(media='screen')
                memory_path=area/'preferences/memory.md';memory_crlf=memory_path.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n');memory_path.write_bytes(memory_crlf)
                for width in (1440,768,390):
                    p.set_viewport_size({'width':width,'height':900});p.goto(server.origin+server.entry+'#personal-edit/memory');expect(p.locator('#personal-content')).to_be_enabled();check('editor-width-'+str(width),p.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                    check('crlf-not-dirty-'+str(width),p.locator('#personal-save').is_disabled() and p.locator('#personal-cancel').is_disabled())
                    p.screenshot(path=str(scratch/('editor-'+str(width)+'.png')),full_page=True)
                p.locator('#personal-content').fill('# 合成草稿\n\n'+('一段保留草稿。\n\n'*60));draft=p.locator('#personal-content').input_value();p.wait_for_timeout(220)
                p.locator('#editor-show-preview').click();expect(p.locator('#personal-preview')).to_be_visible();check('narrow-preview-keeps-draft',p.locator('#personal-content').input_value()==draft and p.locator('#personal-content').is_hidden())
                p.evaluate('window.scrollTo(0,900)');p.wait_for_timeout(80);check('save-remains-in-view-while-reading-long-preview',p.locator('#personal-save').evaluate('n=>{const r=n.getBoundingClientRect();return r.top>=0&&r.bottom<innerHeight}') and p.locator('#personal-save').is_enabled())
                p.screenshot(path=str(scratch/'editor-sticky-narrow.png'),full_page=False)
                p.locator('#editor-show-source').click();check('narrow-edit-keeps-draft',p.locator('#personal-content').is_visible() and p.locator('#personal-content').input_value()==draft)
                p.once('dialog',lambda d:d.accept());p.locator('#personal-cancel').click();check('cancel-restores-saved-after-view-switch',p.locator('#personal-save').is_disabled())
                check('crlf-original-bytes-retained-after-cancel',memory_path.read_bytes()==memory_crlf)
                check('no-browser-errors-or-external-resource-loads',not errors and not requests)
                p.set_viewport_size({'width':1440,'height':900});p.evaluate("location.hash='#packages'");expect(p.locator('#manager-stop')).to_be_visible()
                p.locator('#manager-stop').click();expect(p.locator('#manager-status')).to_contain_text('管理服务已结束')
                p.evaluate("location.hash='#personal-edit/memory'");expect(p.locator('#personal-mode')).to_contain_text('离线阅读')
                check('shutdown-disables-existing-editor',p.locator('#personal-content').is_disabled() and p.locator('#personal-save').is_disabled() and p.locator('#personal-reload').is_disabled())
                p.locator('a[href="#personal-edit/guide"]').first.click();expect(p.locator('#personal-content')).to_have_value('# 我的指南\n\n合成指南检索词。')
                check('shutdown-retains-latest-reading-snapshot',p.locator('#personal-save').is_disabled() and '合成指南检索词' in p.locator('#personal-preview').inner_text())
                p.goto((area/'workbench/MANUAL.html').as_uri()+'#personal-edit/requirements');expect(p.locator('#personal-mode')).to_contain_text('离线阅读');check('offline-editor-cannot-fake-save',p.locator('#personal-save').is_disabled())
                p.goto((area/'workbench/MANUAL.html').as_uri()+'#'+personal.UID+'-guide');expect(p.locator('#'+personal.UID+'-guide')).to_be_visible();check('offline-personal-content-current','合成指南检索词' in p.locator('#'+personal.UID+'-guide').inner_text())
                ctx.close();browser.close()
    finally:server.shutdown();thread.join(5);server.server_close()
    check('temporary-service-closed',not thread.is_alive())
    return {'status':'passed','checks':len(results),'evidence':str(scratch)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--scratch',type=Path,required=True);parser.add_argument('--browser-path',type=Path);parser.add_argument('--contracts-only',action='store_true');args=parser.parse_args()
    print(json.dumps(run(args.scratch,args.browser_path,args.contracts_only),ensure_ascii=False))
