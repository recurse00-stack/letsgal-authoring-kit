(() => {
  'use strict';
  const $=id=>document.getElementById(id),data=JSON.parse($('wiki-data').textContent);
  let manager=data.manager;
  let key=null,saved=null,latest=null,loading=false,saving=false,sequence=0,timer;
  const editorText=value=>value.replace(/\r\n?/g,'\n');
  const dirty=()=>saving||Boolean(saved&&$('personal-content').value!==editorText(saved.content));
  const status=message=>{$('personal-status').textContent=message;};
  function controls(){
    $('personal-content').disabled=!saved||!manager||saving;
    $('personal-save').disabled=!manager||!saved||saving||!dirty();
    $('personal-cancel').disabled=!saved||saving||!dirty();
    $('personal-reload').disabled=!manager||saving||loading;
    $('personal-merge').disabled=saving;
    $('personal-dirty').textContent=saving?'正在保存…':dirty()?'有未保存修改':saved?'与已保存内容一致':'';
  }
  function preview(){
    clearTimeout(timer);
    const container=$('personal-preview');
    try{container.replaceChildren(window.LetsGalWiki.preview($('personal-content').value));}
    catch{container.replaceChildren(document.createTextNode('这段 Markdown 暂时无法预览；正文草稿仍保留。'));}
    controls();
  }
  async function api(path,body){
    const options={cache:'no-store',headers:{'X-LetsGal-Session':manager.token}};
    if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
    const response=await fetch(manager.api+path,options),value=await response.json();
    if(!response.ok){const error=Error(value.message||'操作未完成');error.status=response.status;throw error;}
    return value;
  }
  function accept(document){
    saved=document;latest=null;$('personal-content').value=document.content;
    $('personal-conflict').hidden=true;$('personal-merge').hidden=true;preview();
    $('personal-path').textContent=document.path||'本页来自离线资料快照';$('personal-mode').textContent=(manager?'本机编辑':'离线阅读')+(document.enabled===false?' · AI 读取已暂停':'');
    if(document.legacy_notice)status('新旧偏好文件同时存在。本页编辑 preferences/user.md，旧 user.md 保留；请核对尚未整合的内容。');
  }
  async function open(document,force=false){
    if(key===document&&(loading||saved)&&!force)return;
    key=document;const request=++sequence;loading=true;saved=null;latest=null;status('');
    $('personal-content').value='';$('personal-path').textContent='读取后显示实际文件位置';$('personal-preview').replaceChildren();$('personal-conflict').hidden=true;
    for(const a of documentLinks())a.toggleAttribute('aria-current',a.hash==='#personal-edit/'+key);
    controls();
    if(!manager){
      const item=data.library.items.find(i=>i.package_key==='personal/letsgal-personal'),doc=item?.documents.find(d=>d.id===key);
      if(doc?.markdown!==undefined)accept({content:doc.markdown,path:null,enabled:item.enabled});
      $('personal-mode').textContent='离线阅读 · 在本机 workbench 文件夹运行 Open-Workbench.cmd 后编辑和保存。';
      loading=false;controls();return;
    }
    try{const value=await api('/api/personal/'+key);if(request!==sequence)return;accept(value);}
    catch(error){if(request===sequence)status('未能读取个人资料。请核对本机连接后重新载入。'+(error.message?' '+error.message:''));}
    finally{if(request===sequence){loading=false;controls();}}
  }
  function documentLinks(){return $('personal-editor').querySelectorAll('.personal-tabs a');}
  function beforeNavigate(message='这页有未保存修改。放弃草稿并离开？'){
    if(saving){status('正在保存，请稍候。');return false;}
    if(!dirty())return true;
    if(!window.confirm(message))return false;
    $('personal-content').value=saved.content;preview();return true;
  }
  for(const view of ['source','preview'])$('editor-show-'+view).addEventListener('click',()=>{
    document.querySelector('.personal-editor-grid').dataset.view=view;
    for(const tab of ['source','preview'])$('editor-show-'+tab).setAttribute('aria-pressed',String(tab===view));
    if(view==='preview')preview();
  });
  $('personal-content').addEventListener('input',()=>{controls();clearTimeout(timer);timer=setTimeout(preview,180);});
  $('personal-cancel').addEventListener('click',()=>{if(beforeNavigate('放弃未保存修改，恢复已载入的正文？')){status('已取消未保存修改。');preview();}});
  $('personal-reload').addEventListener('click',()=>{if(beforeNavigate('放弃未保存修改，载入当前文件内容？'))open(key,true);});
  $('personal-merge').addEventListener('click',()=>{
    if(!latest)return;saved=latest;latest=null;$('personal-merge').hidden=true;
    status('已核对最新保存内容。请完成草稿中的合并后再保存。');controls();
  });
  $('personal-save').addEventListener('click',async()=>{
    if(!manager||!saved||saving)return;
    const content=$('personal-content').value;
    if(new TextEncoder().encode(content).length>1000000){status('正文超过 1 MB，请缩小本页内容后保存。');return;}
    saving=true;controls();status('正在保存并核对…');
    try{
      const result=await api('/api/personal/save',{document:key,content,expected:saved.fingerprint});
      if(result.document.content!==content)throw Error('保存读回与草稿不同');
      accept(result.document);status(result.write.status==='verified-unchanged'?'内容未变，已核对。':'已保存并读回。');
      try{const incoming=await api('/api/library');window.LetsGalWiki.register(incoming);}catch{status('正文已保存并读回。页面索引尚未刷新，可稍后重新打开工作台。');}
    }catch(error){
      try{
        const current=await api('/api/personal/'+key);
        if(error.status!==409&&current.content===content){accept(current);status('已重新读取并确认保存内容。');}
        else{latest=current;$('personal-latest').textContent=current.content;$('personal-conflict').hidden=false;$('personal-merge').hidden=false;status(error.status===409?'文件已被其他位置修改，草稿保留。':'保存结果需要核对，草稿保留；下方为当前文件内容。');}
      }catch{status('未确认保存完成，草稿保留。请恢复本机连接后载入已保存内容核对。');}
    }finally{saving=false;controls();}
  });
  window.addEventListener('beforeunload',event=>{if(dirty()){event.preventDefault();event.returnValue='';}});
  window.addEventListener('letsgal-library-updated',event=>{data.library=event.detail;});
  window.addEventListener('letsgal-manager-disconnected',()=>{
    manager=null;++sequence;loading=false;
    $('personal-mode').textContent='离线阅读 · 在本机 workbench 文件夹运行 Open-Workbench.cmd 后编辑和保存。';
    status('管理服务已结束，当前内容保留供阅读。');controls();
  });
  window.addEventListener('letsgal-editor-route',event=>open(event.detail.document));
  window.LetsGalPersonal=Object.freeze({dirty,beforeNavigate});
  if(location.hash.startsWith('#personal-edit/'))open(location.hash.slice('#personal-edit/'.length));
})();
