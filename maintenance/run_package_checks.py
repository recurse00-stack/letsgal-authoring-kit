"""Isolated package-state, registry, HTTP and real-browser checks. No Studio calls."""
import argparse
import copy
import hashlib
import http.client
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
import workbench_runtime as w
import workbench_packages as p
from workbench_server import Server

ROOT=Path(__file__).resolve().parents[1]
SCRATCH=None


def wiki(package_id,version,section='skills',word='合成云杉标记'):
    meta={'id':package_id,'version':version,'revision':'test.1','title':'合成资料 '+package_id,'summary':'仅用于隔离测试。','section':section}
    uid='ext-'+w.sha(json.dumps([meta[k] for k in ('section','id','version','revision')],ensure_ascii=False).encode())[:16]
    return {'schema':1,'kind':'letsgal-wiki-library','items':[dict(meta,uid=uid,status='available',documents=[
        {'id':'guide','title':'使用指南','html':'<h1>合成指南</h1><p>'+word+'</p><a href="#'+uid+'-details">参数</a><script>window.INJECTED=true</script><img src="https://invalid.example/beacon">'},
        {'id':'details','title':'参数说明','html':'<h1>参数说明</h1><p>合成参数终点</p>'}]) ]}


def declaration(area,kind='plugin-guide',package_id='example.weather',versions=('1.0.0','2.0.0'),enabled=True):
    result={'schema':1,'kind':'letsgal-package-registration','package_type':kind,'id':package_id,'enabled':enabled,'show_when_paused':False,
        'selection_mode':'auto' if kind=='plugin-guide' else 'fixed','selected_version':None if kind=='plugin-guide' else versions[-1],'versions':{}}
    for version in versions:
        root=area/('plugins' if kind=='plugin-guide' else 'addons')/package_id/version
        root.mkdir(parents=True)
        (root/'SKILL.md').write_text('---\nname: example-weather\ndescription: Synthetic fixture.\n---\n# 合成资料\n','utf-8')
        lib=wiki(package_id,version)
        result['versions'][version]={'root':root.relative_to(area).as_posix(),'entry':'SKILL.md','revision':'test.1','title':lib['items'][0]['title'],
            'summary':'仅用于隔离测试。','section':'skills','files':w.file_map(root),'wiki_library':lib}
    return result


def native(area):
    root=area/'addons/example-reference/1.0.0';root.mkdir(parents=True)
    (root/'SKILL.md').write_text('---\nname: example-reference\ndescription: Synthetic reference.\n---\n# 合成参考\n','utf-8')
    lib=wiki('example-reference','1.0.0','references','合成海潮标记')
    (root/'wiki-library.json').write_bytes(w.encode(lib))
    meta=lib['items'][0]
    state={'schema':1,'id':'example-reference','enabled':False,'selected_version':'1.0.0','versions':{'1.0.0':{k:meta[k] for k in ('revision','title','summary','section')}}}
    state['versions']['1.0.0'].update(entry='SKILL.md',files=w.file_map(root))
    (root.parent/'state.json').write_bytes(w.encode(state))
    return state


class Contracts(unittest.TestCase):
    count=0
    def setUp(self):
        type(self).count+=1
        self.area=SCRATCH/str(self.count);self.area.mkdir()
        w.setup(ROOT,self.area)
        native(self.area)
        self.manifest=declaration(self.area)
        self.key='plugin-guide/example.weather'
    def register(self):return p.register(self.area,self.manifest,True)
    def state(self):return next(x for x in p.catalog(self.area)['items'] if x['key']==self.key)
    def test_navigation_roundtrip_and_registration(self):
        area=self.area;d=self.manifest
        item=d['versions']['1.0.0']['wiki_library']['items'][0]
        item['navigation']={'intro':'合成入口','start':'guide','groups':[{'title':'起步','documents':['guide']}]}
        p.register(area,d,True)
        self.assertEqual(next(i for i in p.library(area)['items'] if i['id']=='example.weather' and i['version']=='1.0.0')['navigation'],item['navigation'])
        self.assertIsNone(next(i for i in p.library(area)['items'] if i['id']=='example.weather')['selected_version'])
        self.assertEqual(p.resolve(area,'plugin-guide/example.weather','1.0.0')['status'],'ready')

    def test_bad_navigation_retains_registration(self):
        area=self.area;d=self.manifest;p.register(area,d,True)
        before=w.read_bytes(p.adapter_path(area,'plugin-guide/example.weather'))
        for nav in ({'start':'absent'},{'groups':[{'title':'重复','documents':['guide','guide']}]},{'groups':[{'title':'缺少','documents':['absent']}]}):
            bad=copy.deepcopy(d);bad['versions']['1.0.0']['wiki_library']['items'][0]['navigation']=nav
            with self.assertRaises(ValueError):p.register(area,bad,True,True)
            self.assertEqual(w.read_bytes(p.adapter_path(area,'plugin-guide/example.weather')),before)

    def test_paused_fixed_reading_hint_preserves_ai_pause(self):
        area=self.area;d=self.manifest;d['enabled']=False;p.register(area,d,True)
        p.change(area,'plugin-guide/example.weather',{'selection_mode':'fixed','selected_version':'1.0.0','show_when_paused':True})
        self.assertEqual(next(i for i in p.library(area)['items'] if i['id']=='example.weather')['selected_version'],'1.0.0')
        self.assertEqual(p.resolve(area,'plugin-guide/example.weather','1.0.0')['status'],'paused')

    def test_preview_writes_nothing(self):
        before=w.file_map(self.area);self.assertEqual(p.register(self.area,self.manifest)['status'],'preview');self.assertEqual(before,w.file_map(self.area))
    def test_register_retains_payload_and_repeat(self):
        before=w.file_map(self.area/'plugins/example.weather');self.register();self.assertEqual(before,w.file_map(self.area/'plugins/example.weather'));self.assertEqual(self.register()['status'],'verified-unchanged')
        self.assertIn('workbench/packages/plugin-guide/example.weather/state.json',(self.area/'plugins/INDEX.md').read_text('utf-8'))
    def test_pause_show_does_not_resolve(self):
        self.register();p.change(self.area,self.key,{'enabled':False,'show_when_paused':True})
        items=[x for x in p.library(self.area)['items'] if x['package_key']==self.key]
        self.assertTrue(all(x['documents'] and not x['enabled'] and x['wiki_visible'] for x in items))
        self.assertEqual(p.resolve(self.area,self.key,'1.0.0')['status'],'paused')
    def test_hidden_has_no_body(self):
        self.register();p.change(self.area,self.key,{'enabled':False})
        self.assertTrue(all(not x['documents'] for x in p.library(self.area)['items'] if x['package_key']==self.key))
    def test_switch_preserves_pause_and_display(self):
        self.register();p.change(self.area,self.key,{'enabled':False,'show_when_paused':True})
        p.change(self.area,self.key,{'selection_mode':'fixed','selected_version':'1.0.0'})
        s=self.state();self.assertFalse(s['enabled']);self.assertTrue(s['show_when_paused']);self.assertEqual(s['selected_version'],'1.0.0')
    def test_auto_and_fixed_plugin_matching(self):
        self.register();self.assertEqual(p.resolve(self.area,self.key,'1.0.0')['version'],'1.0.0')
        p.change(self.area,self.key,{'selection_mode':'fixed','selected_version':'2.0.0'})
        self.assertEqual(p.resolve(self.area,self.key,'1.0.0')['status'],'version-mismatch')
        self.assertEqual(p.resolve(self.area,self.key)['status'],'version-required')
        p.change(self.area,self.key,{'selection_mode':'auto','selected_version':None})
        self.assertEqual(p.resolve(self.area,self.key,'3.0.0')['status'],'no-matching-version')
    def test_native_state_compatibility(self):
        w.change_state(self.area,'example-reference',show_when_paused=True)
        self.assertEqual(p.resolve(self.area,'addon/example-reference')['status'],'paused')
        self.assertEqual(len(next(i for i in p.library(self.area)['items'] if i['id']=='example-reference')['documents']),2)
    def test_stale_fingerprint_rejected(self):
        self.register();old=self.state()['fingerprint'];p.change(self.area,self.key,{'enabled':False},old)
        before=w.file_map(self.area)
        with self.assertRaises(p.Conflict):p.change(self.area,self.key,{'enabled':True},old)
        self.assertEqual(before,w.file_map(self.area))
    def test_invalid_version_and_boolean(self):
        self.register()
        for patch in [{'selected_version':'9.0.0','selection_mode':'fixed'},{'enabled':1},{'show_when_paused':'yes'},{'unknown':False}]:
            with self.assertRaises(ValueError):p.change(self.area,self.key,patch)
    def test_registered_version_not_overwritten(self):
        self.register();self.manifest['versions']['1.0.0']['summary']='Changed'
        with self.assertRaises(ValueError):self.register()
    def test_register_preserves_choices(self):
        self.register();p.change(self.area,self.key,{'enabled':False,'show_when_paused':True,'selection_mode':'fixed','selected_version':'1.0.0'})
        self.register();s=self.state();self.assertFalse(s['enabled']);self.assertTrue(s['show_when_paused']);self.assertEqual(s['selected_version'],'1.0.0')
    def test_reviewed_revision_replacement_preserves_settings(self):
        self.register();p.change(self.area,self.key,{'enabled':False,'show_when_paused':True})
        record=self.manifest['versions']['1.0.0'];record['revision']='test.2'
        item=record['wiki_library']['items'][0];item['revision']='test.2'
        item['uid']='ext-'+w.sha(json.dumps([item[k] for k in ('section','id','version','revision')],ensure_ascii=False).encode())[:16]
        result=p.register(self.area,self.manifest,True,True)
        self.assertTrue(result['write']['backup']);self.assertFalse(self.state()['enabled']);self.assertTrue(self.state()['show_when_paused'])
    def test_path_identity_hash_and_duplicate_authority(self):
        for mutation in ['root','hash','id']:
            bad=copy.deepcopy(self.manifest)
            if mutation=='root':bad['versions']['1.0.0']['root']='plugins/../outside'
            elif mutation=='hash':bad['versions']['1.0.0']['files']['SKILL.md']='0'*64
            else:bad['id']='../escape'
            with self.assertRaises(ValueError):p.register(self.area,bad,True)
        other=declaration(self.area,'addon','example-reference',('2.0.0',),False)
        with self.assertRaises(ValueError):p.register(self.area,other,True)
    def test_broken_wiki_rolls_back_state(self):
        self.register();before=(self.area/'workbench/packages/plugin-guide/example.weather/state.json').read_bytes()
        (self.area/'workbench/packages/plugin-guide/example.weather/1.0.0/wiki-library.json').write_text('{}','utf-8')
        with self.assertRaises(ValueError):p.change(self.area,self.key,{'selected_version':'2.0.0','selection_mode':'fixed'})
        self.assertEqual(before,(self.area/'workbench/packages/plugin-guide/example.weather/state.json').read_bytes())
    def test_file_transaction_rollback(self):
        from unittest.mock import patch
        first=self.area/'first.txt';second=self.area/'second.txt';first.write_bytes(b'old');second.write_bytes(b'old2')
        original=w.os.replace;calls=[]
        def failing(a,b):
            calls.append(b)
            if len(calls)==2:raise OSError('synthetic write failure')
            return original(a,b)
        with patch.object(w.os,'replace',failing):
            with self.assertRaises(OSError):w.commit_files(self.area,{first:b'new',second:b'new2'},'fixture')
        self.assertEqual(first.read_bytes(),b'old');self.assertEqual(second.read_bytes(),b'old2')
    def test_legacy_collaboration_adapter_four_versions(self):
        old=declaration(self.area,'addon','example-collaboration',('0.1.0','0.1.1','0.1.2','0.1.3'),False)
        before=w.file_map(self.area/'addons/example-collaboration');p.register(self.area,old,True)
        self.assertEqual(before,w.file_map(self.area/'addons/example-collaboration'));self.assertEqual(p.resolve(self.area,'addon/example-collaboration')['status'],'paused')
    def test_legacy_snapshot_refresh_recovers_all_registrations(self):
        self.register();old=w.collect_legacy(self.area)
        path=self.area/'workbench/MANUAL.html';path.write_text(w.inject((self.area/'workbench/MANUAL.base.html').read_text('utf-8'),old),'utf-8')
        w.refresh(self.area);self.assertIn('example.weather',path.read_text('utf-8'))
    def test_update_rebuilds_old_manifests_and_mounted_reading_editions(self):
        from workbench_mounts import mount
        self.register()
        p.change(self.area,self.key,{'enabled':False,'show_when_paused':False})
        legacy=self.area/'plugins/example.legacy/1'
        legacy.mkdir(parents=True)
        (legacy/'guide.md').write_text('# Old guide','utf-8')
        manifest={'schema':1,'kind':'plugin','id':'example.legacy','version':'1','revision':'v1',
                  'title':'Legacy','status':'available','documents':[{'id':'guide','title':'Guide','path':'guide.md'}]}
        (legacy/'wiki.json').write_bytes(w.encode(manifest))
        imported=wiki('example.notes','1')
        self.assertEqual(mount(self.area,imported)['added'],1)
        self.assertEqual(mount(self.area,imported)['added'],0)
        self.assertEqual(mount(self.area,wiki('example.weather','1.0.0'))['added'],0)
        before=w.file_map(self.area/'workbench/packages')
        snapshot=p.library(self.area)
        w.setup(ROOT,self.area)
        self.assertEqual(p.library(self.area),snapshot)
        self.assertEqual(w.file_map(self.area/'workbench/packages'),before)
        ready={i['id']:i for i in snapshot['items'] if i['wiki_visible']}
        self.assertEqual(ready['example.legacy']['documents'][0]['markdown'],'# Old guide')
        self.assertEqual(ready['example.notes']['uid'],imported['items'][0]['uid'])
        self.assertNotIn('example.weather',ready)
        self.assertEqual(p.resolve(self.area,'plugin-guide/example.notes')['status'],'unregistered')

    def test_setup_preserves_embedded_markdown_renderer(self):
        source=(ROOT/'MANUAL.html').read_text('utf-8-sig')
        installed=(self.area/'workbench/MANUAL.base.html').read_text('utf-8')
        script='<script id="wiki-data"'
        self.assertEqual(installed[installed.index(script):],source[source.index(script):])

    def test_invalid_mount_keeps_last_readable_wiki(self):
        from workbench_mounts import mount
        original=wiki('example.notes','1')
        mount(self.area,original)
        output=self.area/'workbench/MANUAL.html'
        before=output.read_bytes()
        different=copy.deepcopy(original)
        different['items'][0]['documents'][0]['title']='Changed edition'
        with self.assertRaises(ValueError):mount(self.area,different)
        self.assertEqual(output.read_bytes(),before)
        broken=self.area/'workbench/libraries/broken.json'
        broken.write_bytes(b'{}')
        with self.assertRaises(ValueError):w.setup(ROOT,self.area)
        self.assertEqual(output.read_bytes(),before)

    def test_main_setup_preserves_package_choices(self):
        self.register();p.change(self.area,self.key,{'enabled':False,'show_when_paused':True});before=self.state()
        w.setup(ROOT,self.area);self.assertEqual(before,self.state())
    def test_pending_without_main(self):
        area=SCRATCH/'no-main';area.mkdir();decl=declaration(area);result=p.register(area,decl,True)
        self.assertEqual(result['wiki']['status'],'pending');w.setup(ROOT,area);self.assertEqual(len(p.library(area)['items']),3)
    def test_declared_personal_skill_package(self):
        decl=declaration(self.area,'addon','example-personal',('1.0.0',),False)
        record=decl['versions']['1.0.0'];record['section']='personal';record['wiki_library']=wiki('example-personal','1.0.0','personal')
        p.register(self.area,decl,True);p.change(self.area,'addon/example-personal',{'show_when_paused':True})
        item=next(x for x in p.library(self.area)['items'] if x['id']=='example-personal')
        self.assertEqual(item['section'],'personal');self.assertTrue(item['documents']);self.assertEqual(p.resolve(self.area,'addon/example-personal')['status'],'paused')
    def test_service_idle_exit(self):
        with Server(self.area,idle_seconds=0.1) as server:
            worker=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':0.02},daemon=True);worker.start()
            watcher=threading.Thread(target=server.watch_idle,daemon=True);watcher.start()
            worker.join(timeout=3);server.stopped.set();self.assertFalse(worker.is_alive())
    def test_http_authority_and_conflict(self):
        self.register()
        with Server(self.area) as s:
            thread=threading.Thread(target=s.serve_forever,daemon=True);thread.start()
            def request(path,body=None,headers=None):
                conn=http.client.HTTPConnection('127.0.0.1',s.server_port,timeout=5)
                h={'X-LetsGal-Session':s.token,'Origin':s.origin,'Content-Type':'application/json'};h.update(headers or {})
                conn.request('GET' if body is None else 'POST',path,None if body is None else json.dumps(body),h)
                r=conn.getresponse();raw=r.read();conn.close();return r.status,raw
            try:
                self.assertEqual(request('/api/packages',headers={'X-LetsGal-Session':'wrong'})[0],403)
                self.assertEqual(request('/api/packages',headers={'Host':'evil.invalid'})[0],403)
                self.assertEqual(request('/api/packages',headers={'Origin':'https://evil.invalid'})[0],403)
                self.assertEqual(request('/api/packages',headers={'Sec-Fetch-Site':'cross-site'})[0],403)
                self.assertEqual(request('/../../private.txt')[0],404)
                links=w.read_json(self.area/'workbench/document-links.json');doc=next(iter(links.values()))
                self.assertEqual(request(s.entry+'docs/'+doc)[0],200)
                self.assertEqual(request(s.entry+'docs/../../state.json')[0],404)
                old=self.state()['fingerprint'];self.assertEqual(request('/api/state',{'key':self.key,'expected':old,'patch':{'enabled':False}})[0],200)
                self.assertEqual(request('/api/state',{'key':self.key,'expected':old,'patch':{'enabled':True}})[0],409)
                status,raw=request('/api/snapshot');self.assertEqual(status,200);self.assertEqual(json.loads(raw)['library']['schema'],2)
                self.assertEqual(request('/api/shutdown',{})[0],200);thread.join(timeout=5);self.assertFalse(thread.is_alive())
            finally:
                if thread.is_alive():s.shutdown();thread.join()


def browser_checks(scratch,browser_path=None):
    from playwright.sync_api import sync_playwright,expect
    area=scratch/'browser';area.mkdir();w.setup(ROOT,area);native(area)
    p.register(area,declaration(area,enabled=False),True)
    key='plugin-guide/example.weather';checks=[]
    def check(name,condition):
        checks.append({'name':name,'passed':bool(condition)})
        (scratch/'browser-results.json').write_bytes(w.encode({'checks':checks}));assert condition,name
    with Server(area) as server,sync_playwright() as playwright:
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        options={'headless':True}
        if browser_path:options['executable_path']=str(browser_path)
        browser=playwright.chromium.launch(**options)
        context=browser.new_context(viewport={'width':1440,'height':1050})
        page=context.new_page();errors=[];remote=[]
        page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:remote.append(r.url) if not r.url.startswith(server.origin) else None)
        try:
            page.goto(server.origin+server.entry+'#packages');card=page.locator('[data-package-key="'+key+'"]');card.wait_for()
            expect(card.get_by_role('combobox')).to_have_value('@auto')
            check('initial-version-loaded',not card.get_by_role('combobox').is_disabled())
            check('paused-start-hidden',card.get_by_text('AI 已暂停',exact=True).is_visible() and card.get_by_text('Wiki 已隐藏',exact=True).is_visible())
            card.get_by_role('checkbox').check();page.get_by_text('已保存。AI 使用状态和 Wiki 展示已同步。',exact=True).wait_for()
            check('paused-show-still-paused',p.resolve(area,key,'1.0.0')['status']=='paused' and len(p.library(area)['items'][1]['documents'])>0)
            page.locator('#search').fill('合成云杉标记');page.locator('#result-list a').first.wait_for();check('paused-visible-search',page.locator('#result-list a').count()>0)
            page.locator('#search').fill('');page.evaluate('location.hash="packages"');page.wait_for_timeout(60)
            card.get_by_role('combobox').select_option('1.0.0');page.get_by_text('已保存。AI 使用状态和 Wiki 展示已同步。',exact=True).wait_for()
            check('switch-does-not-enable',p.resolve(area,key,'1.0.0')['status']=='paused')
            card.get_by_role('button',name='启用 合成资料 example.weather',exact=True).click();page.get_by_text('已保存。AI 使用状态和 Wiki 展示已同步。',exact=True).wait_for()
            check('enable-selected-version',p.resolve(area,key,'1.0.0')['status']=='ready')
            card.get_by_role('link',name='打开 1.0.0 手册 →').click();page.get_by_role('link',name='参数',exact=True).click()
            check('cross-document-link',page.locator('.article:not([hidden])').get_by_role('heading',name='参数说明').count()==1)
            page.evaluate('location.hash="packages"');page.wait_for_timeout(60);card.get_by_role('button',name='暂停 合成资料 example.weather',exact=True).click();page.get_by_text('已保存。AI 使用状态和 Wiki 展示已同步。',exact=True).wait_for()
            card.get_by_role('checkbox').uncheck();page.get_by_text('已保存。AI 使用状态和 Wiki 展示已同步。',exact=True).wait_for()
            page.locator('#search').fill('合成云杉标记');check('hidden-search-removed',page.locator('#result-list a').count()==0);page.locator('#search').fill('')
            page.reload();card.wait_for();check('reload-preserves-state',card.get_by_text('AI 已暂停',exact=True).is_visible() and not card.get_by_role('checkbox').is_checked())
            page.keyboard.press('Control+k');check('keyboard-search-shortcut',page.locator('#search').evaluate('(n)=>n===document.activeElement'))
            page.locator('#package-search').fill('example.weather');check('package-filter',page.locator('[data-package-key]').count()==1);page.locator('#package-search').fill('')
            second=context.new_page();second.goto(server.origin+server.entry+'#packages');second.locator('[data-package-key="'+key+'"] button').wait_for()
            p.change(area,key,{'enabled':True})
            second.locator('[data-package-key="'+key+'"] button').dispatch_event('click')
            second.get_by_text('状态已被其他页面或工具修改，已刷新，请核对后重新选择。',exact=True).wait_for()
            check('stale-page-refreshes-without-overwrite',p.resolve(area,key,'1.0.0')['status']=='ready')
            second.close();p.change(area,key,{'enabled':False});page.locator('#packages-refresh').click();page.get_by_text('AI 已暂停',exact=True).first.wait_for()
            page.screenshot(path=str(scratch/'packages-desktop.png'),full_page=True)
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(scratch/'packages-narrow.png'),full_page=True)
            check('narrow-no-overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            page.set_viewport_size({'width':1440,'height':1050});page.emulate_media(media='print');check('manager-not-printed',not page.locator('#packages').is_visible());page.emulate_media(media='screen')
            check('sanitized-no-executable-or-remote',page.evaluate('window.INJECTED !== true') and not remote)
            check('no-browser-errors',not errors)
            page.locator('#manager-stop').click();page.get_by_text('管理服务已结束，当前页面仍可阅读。',exact=True).wait_for();thread.join(timeout=5);check('explicit-shutdown',not thread.is_alive())
            page.goto((area/'workbench/MANUAL.html').as_uri()+'#packages');check('offline-read-only',page.locator('[data-package-key] button').count()==0 and page.get_by_text('离线阅读模式',exact=False).count()>0)
        except Exception:
            page.screenshot(path=str(scratch/'failure.png'),full_page=True)
            (scratch/'failure-details.json').write_bytes(w.encode({'manager_status':page.locator('#manager-status').inner_text(),'errors':errors,'remote_requests':remote}))
            raise
        finally:
            browser.close()
            if thread.is_alive():server.shutdown();thread.join()
    return checks


def main():
    global SCRATCH
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--scratch',type=Path,required=True);parser.add_argument('--browser',action='store_true');parser.add_argument('--browser-path',type=Path)
    args=parser.parse_args();SCRATCH=args.scratch.resolve();SCRATCH.mkdir(parents=True,exist_ok=False)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    report={'contracts':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)}
    if result.wasSuccessful() and args.browser:report['browser']=browser_checks(SCRATCH,args.browser_path)
    (SCRATCH/'results.json').write_bytes(w.encode(report));print(json.dumps(report,ensure_ascii=False));return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
