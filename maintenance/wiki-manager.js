(() => {
  'use strict';
  const $=id=>document.getElementById(id), data=JSON.parse($('wiki-data').textContent);
  const context=data.manager;
  let connected=Boolean(context), ready=false, items=[], library=data.library, busy=false, loading=null;
  const node=(tag,content,cls)=>{const n=document.createElement(tag);if(content!==undefined)n.textContent=content;if(cls)n.className=cls;return n;};
  const announce=message=>{$('manager-status').textContent=message;};
  function offlineItems(){
    const groups=new Map();
    for(const i of library.items){
      const key=i.package_key || (i.section==='skills'?'plugin-guide/':'addon/')+i.id;
      if(!groups.has(key))groups.set(key,{key,id:i.id,title:i.title,package_type:key.split('/')[0],enabled:i.package_key?(i.enabled ?? i.status==='available'):null,show_when_paused:i.status==='paused' && i.wiki_visible,selection_mode:'snapshot',selected_version:null,versions:[]});
      const p=groups.get(key);p.versions.push({version:i.version,revision:i.revision,title:i.title});if(i.selected)p.selected_version=i.version;
    }
    return [...groups.values()];
  }
  async function api(path,body){
    const options={cache:'no-store',headers:{'X-LetsGal-Session':context.token}};
    if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
    let response;
    try {response=await fetch(context.api+path,options);} catch {throw Error('本机管理连接已断开。请重新运行 Open-Workbench.cmd；当前仍可阅读。');}
    const result=await response.json();
    if(!response.ok){const error=Error(response.status===409?'状态已被其他页面或工具修改，已刷新，请核对后重新选择。':result.message||'操作未完成。');error.status=response.status;throw error;}
    return result;
  }
  function mode(){
    $('manager-mode').textContent=connected?(ready?'本机管理已连接 · 修改会保存到当前用户区':'正在读取本机包状态…'):'离线阅读模式 · 在本机 workbench 文件夹运行 Open-Workbench.cmd 后管理这些包。';
    $('manager-stop').hidden=!connected;
    $('packages-refresh').disabled=busy||!connected;
  }
  const expanded=new Set();
  function render(){
    mode();
    const focused=document.activeElement?.dataset.control;
    const query=$('package-search').value.trim().toLocaleLowerCase(),kind=$('package-kind').value;
    const shown=items.filter(p=>(kind==='all'||p.package_type===kind)&&(!query||(p.title+' '+p.id).toLocaleLowerCase().includes(query)));
    const cards=shown.map(p=>{
      const card=node('section',undefined,'package-card');card.dataset.packageKey=p.key;
      const heading=node('div',undefined,'package-heading'),identity=node('div');
      identity.append(node('small',p.package_type==='personal'?'个人资料':p.package_type==='plugin-guide'?'插件指南':'附属 Skill','package-type'),node('h3',p.title));heading.append(identity);card.append(heading);
      const matchFor=v=>library.items.find(i=>(i.package_key===p.key||!i.package_key&&i.id===p.id)&&(p.package_type==='personal'||i.version===v?.version));
      const visible=library.items.some(i=>(i.package_key===p.key||!i.package_key&&i.id===p.id)&&i.wiki_visible!==false&&i.documents.length);
      const states=node('div',undefined,'package-states'),usage=node('div',undefined,'package-state'),displayState=node('div',undefined,'package-state');
      usage.append(node('span','AI 使用','package-state-label'),node('span',p.enabled===null?'尚无管理登记':p.enabled?'AI 已启用':'AI 已暂停','badge'+(p.enabled===false?' paused':'')));
      displayState.append(node('span','Wiki 展示','package-state-label'),node('span',visible?'Wiki 已显示':'Wiki 已隐藏','badge'+(!visible?' muted':'')));
      if(connected){
        const controls=node('div',undefined,'package-controls');
        const toggle=node('button',p.enabled?'暂停':'启用','package-toggle');toggle.type='button';toggle.disabled=busy||!ready;toggle.setAttribute('aria-label',(p.enabled?'暂停':'启用')+' '+p.title);toggle.dataset.control=p.key+'/enabled';
        toggle.addEventListener('click',()=>save(p,{enabled:!p.enabled}));controls.append(toggle);
        if(p.package_type!=='personal'){
          const label=node('label','使用版本 '),select=node('select');select.setAttribute('aria-label',p.title+' 使用版本');select.disabled=busy||!ready;select.dataset.control=p.key+'/version';
          if(p.package_type==='plugin-guide'){const option=node('option','自动匹配工程');option.value='@auto';select.append(option);}
          for(const v of p.versions){const option=node('option',v.version);option.value=v.version;select.append(option);}
          if(ready)select.value=p.selection_mode==='auto'?'@auto':p.selected_version;
          else {const option=node('option','正在读取包状态…');option.value='@loading';select.replaceChildren(option);}
          select.addEventListener('change',()=>save(p,select.value==='@auto'?{selection_mode:'auto',selected_version:null}:{selection_mode:'fixed',selected_version:select.value}));label.append(select);controls.append(label);
        }
        usage.append(controls);
        const display=node('label',undefined,'package-display'),checkbox=node('input');checkbox.type='checkbox';checkbox.checked=p.show_when_paused;checkbox.disabled=busy||!ready;checkbox.setAttribute('aria-label',p.title+' 暂停时仍显示 Wiki');checkbox.dataset.control=p.key+'/display';
        checkbox.addEventListener('change',()=>save(p,{show_when_paused:checkbox.checked}));display.append(checkbox,document.createTextNode('暂停时仍显示 Wiki'));displayState.append(display);
      }else usage.append(node('p',p.package_type==='personal'?'由你编写和维护':p.selection_mode==='auto'?'按工程自动匹配':p.selected_version?'使用版本 '+p.selected_version:'使用版本见本机登记','package-state-note'));
      states.append(usage,displayState);card.append(states);
      const links=node('div',undefined,'package-manuals');
      const manual=(v)=>{const match=matchFor(v);if(!match?.documents?.length||match.wiki_visible===false)return null;const a=node('a',p.package_type==='personal'?'阅读个人资料 →':'打开 '+v.version+' 手册 →');a.href='#'+match.uid+'-'+match.documents[0].id;return a;};
      if(p.package_type==='personal'){const a=node('a','编辑我的个人包 →');a.href='#personal-edit/requirements';links.append(a);const read=manual(p.versions[0]);if(read)links.append(read);}
      else if(visible){
        const chosen=p.versions.find(v=>v.version===p.selected_version)||(p.versions.length===1?p.versions[0]:null),primary=chosen&&manual(chosen);
        if(primary)links.append(primary);else {const a=node('a','选择阅读版本 →');a.href='#space/'+encodeURIComponent(p.key);links.append(a);}
      }else links.append(node('span','手册当前隐藏；可开启“暂停时仍显示 Wiki”。'));
      card.append(links);
      const details=node('details',undefined,'package-details');details.open=expanded.has(p.key);
      details.append(node('summary',p.package_type==='personal'?'包信息':p.versions.length+' 个已安装版本 · 查看详情'),node('code',p.id,'package-id'));
      details.addEventListener('toggle',()=>{if(details.isConnected){if(details.open)expanded.add(p.key);else expanded.delete(p.key);}});
      if(p.package_type!=='personal'){
        const list=node('ul',undefined,'package-version-list');
        for(const v of p.versions){const row=node('li');row.append(node('strong',v.version),node('code',v.revision));const a=manual(v);if(a)row.append(a);list.append(row);}details.append(list);
      }
      card.append(details);return card;
    });
    $('package-list').replaceChildren(...cards);
    if(!cards.length)$('package-list').append(node('p',items.length?'没有匹配的包。':'尚未登记可管理的包。安装兼容包或按接入说明登记后，会自动出现在这里。','empty'));
    if(focused){const control=[...$('package-list').querySelectorAll('[data-control]')].find(n=>n.dataset.control===focused);if(control&&!control.disabled)control.focus({preventScroll:true});}
  }
  async function load(){
    if(!connected){items=offlineItems();render();return;}
    if(loading)return loading;
    loading=(async()=>{
      const snapshot=await api('/api/snapshot'),catalog=snapshot.catalog,incoming=snapshot.library;
      window.LetsGalWiki.register(incoming);library=incoming;items=catalog.items;ready=true;render();
    })();
    try {await loading;} finally {loading=null;}
  }
  async function save(p,patch){
    if(busy||!ready)return;busy=true;render();announce('正在保存…');
    try {if(loading)await loading;await api('/api/state',{key:p.key,patch,expected:p.fingerprint});await load();announce('已保存。AI 使用状态和 Wiki 展示已同步。');}
    catch(error){
      try {await load();} catch { /* Keep the last confirmed snapshot. Never replay an uncertain write. */ }
      announce(error.status===409?error.message:'未确认保存完成：'+error.message+' 请核对当前状态。');
    } finally {busy=false;render();}
  }
  async function refresh(){try {await load();}catch(error){announce(error.message);}}
  $('package-search').addEventListener('input',render);$('package-kind').addEventListener('change',render);
  $('packages-refresh').addEventListener('click',refresh);
  $('manager-stop').addEventListener('click',async()=>{
    try {await api('/api/shutdown',{});connected=false;window.dispatchEvent(new Event('letsgal-manager-disconnected'));render();announce('管理服务已结束，当前页面仍可阅读。');}
    catch(error){announce(error.message);}
  });
  window.addEventListener('hashchange',()=>{if(location.hash==='#packages')refresh();});
  window.addEventListener('focus',()=>{if(connected&&location.hash==='#packages'&&!busy)refresh();});
  window.addEventListener('letsgal-library-updated',event=>{library=event.detail;if(!connected){items=offlineItems();render();}});
  items=offlineItems();render();if(connected)refresh();
})();
