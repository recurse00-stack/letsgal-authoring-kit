(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const data = JSON.parse($('wiki-data').textContent);
  const labels = {main:'主体', skills:'Skill Wiki', personal:'个性化'};
  const descriptions = {
    main:'主 Skill 的完整使用路线：安装与连接、制作与核对、更新与恢复。',
    skills:'插件的 AI 指南与人类用法放在同一入口，按真实 ID、版本和修订分别查阅。',
    personal:'跨作品偏好、单个作品的约定与私人资料，按自己的需要组织。'
  };
  let pages = [...data.pages], library = [], index = [], activeArea = 'main';
  const text = (tag, value, className) => {
    const node=document.createElement(tag); node.textContent=value;
    if (className) node.className=className;
    return node;
  };
  const link = (title, hash, className) => {
    const node=text('a',title,className); node.href='#'+hash; return node;
  };
  const show = (id, yes) => { $(id).hidden=!yes; };
  const report = value => { $('status').textContent=value; };
  const cleanTitle = value => value.replace(/^\d+\.\s*/, '');
  const safeString = (v, max=200) => typeof v==='string' && v.trim().length>0 && v.length<=max;

  function validateLibrary(value) {
    if (!value || value.schema!==1 || value.kind!=='letsgal-wiki-library' || !Array.isArray(value.items) || value.items.length>200) throw Error('资料格式不匹配，请使用接入工具生成的 Wiki JSON。');
    const identities=new Set(), ids=new Set();
    for (const item of value.items) {
      if (!item || !['skills','personal'].includes(item.section) || !['available','paused'].includes(item.status) || !/^ext-[a-f0-9]{16}$/.test(item.uid) || !safeString(item.id) || !safeString(item.version,80) || !safeString(item.revision,100) || !safeString(item.title) || typeof item.summary!=='string' || item.summary.length>1000 || !Array.isArray(item.documents) || item.documents.length>50) throw Error('资料条目缺少有效 ID、版本、修订、状态或正文。');
      const identity=JSON.stringify([item.section,item.id,item.version,item.revision]);
      if (identities.has(identity) || ids.has(item.uid)) throw Error('资料中存在重复身份或重复标识。');
      identities.add(identity); ids.add(item.uid);
      if (item.status==='paused' && item.documents.length) throw Error('暂停条目不应携带正文，请重新生成资料。');
      if (item.status==='available' && !item.documents.length) throw Error('可阅读条目缺少正文。');
      for (const doc of item.documents) {
        if (!doc || !/^[a-z0-9][a-z0-9-]{0,60}$/.test(doc.id) || !safeString(doc.title) || typeof doc.html!=='string' || doc.html.length>1000000) throw Error('资料正文格式不完整或过大。');
        const id=item.uid+'-'+doc.id;
        if (ids.has(id)) throw Error('同一条目中存在重复文档标识。');
        ids.add(id);
      }
    }
    return value.items;
  }

  // Recreate a small document vocabulary. Imported HTML never enters the live
  // DOM directly, and cannot carry scripts, styles, frames or resource loads.
  function readableContent(markup, prefix, itemPrefix) {
    const input=document.createElement('template'); input.innerHTML=markup;
    const fragment=document.createDocumentFragment();
    const allowed=new Set('P H1 H2 H3 H4 H5 H6 UL OL LI PRE CODE STRONG EM BLOCKQUOTE TABLE THEAD TBODY TR TH TD A BR HR DEL'.split(' '));
    const dropped=new Set('SCRIPT STYLE IFRAME OBJECT EMBED SVG MATH FORM INPUT TEXTAREA BUTTON SELECT LINK META IMG AUDIO VIDEO SOURCE'.split(' '));
    const ids=new Set();
    function visit(node, parent) {
      if (node.nodeType===Node.TEXT_NODE) { parent.append(document.createTextNode(node.textContent)); return; }
      if (node.nodeType!==Node.ELEMENT_NODE || dropped.has(node.tagName)) return;
      if (!allowed.has(node.tagName)) { for (const child of node.childNodes) visit(child,parent); return; }
      const out=document.createElement(node.tagName.toLowerCase());
      const originalId=node.getAttribute('id');
      if (originalId && originalId.length<250) {
        const id=prefix+'--'+originalId;
        if (ids.has(id)) throw Error('正文中存在重复章节标识。');
        ids.add(id); out.id=id;
      }
      if (node.tagName==='A') {
        const href=(node.getAttribute('href')||'').trim();
        if (/^https?:\/\//i.test(href)) { out.href=href; out.rel='noreferrer noopener'; }
        else if (href.startsWith('#')) {
          const part=href.slice(1);
          out.href='#'+(part.startsWith(itemPrefix+'-')?part:prefix+'--'+part);
        }
      }
      if (['TD','TH'].includes(node.tagName)) for (const attr of ['colspan','rowspan']) {
        const value=node.getAttribute(attr); if (/^[1-9][0-9]?$/.test(value||'')) out.setAttribute(attr,value);
      }
      for (const child of node.childNodes) visit(child,out);
      if (node.tagName==='TABLE') { const wrap=document.createElement('div'); wrap.className='table-scroll'; wrap.append(out); parent.append(wrap); }
      else parent.append(out);
    }
    for (const child of input.content.childNodes) visit(child,fragment);
    return fragment;
  }

  function registerLibrary(value) {
    const incoming=validateLibrary(value);
    // Validate and render the entire replacement before changing visible data.
    const additions=[], descriptors=[];
    for (const item of incoming) for (const doc of item.documents) {
      const id=item.uid+'-'+doc.id;
      const article=document.createElement('article'); article.className='article'; article.id=id;
      article.dataset.area=item.section; article.dataset.external='true';
      article.append(text('p',item.title+' · '+item.version+' / '+item.revision,'eyebrow'));
      const content=readableContent(doc.html,id,item.uid);
      if (!content.querySelector('h1')) article.append(text('h1',doc.title));
      article.append(content); additions.push(article);
      descriptors.push({id,area:item.section,title:item.title+' '+item.version+' · '+doc.title,summary:item.summary,external:true,owner:item.title});
    }
    for (const old of document.querySelectorAll('.article[data-external]')) old.remove();
    $('articles').append(...additions);
    library=incoming; pages=[...data.pages,...descriptors];
    attachCopyButtons(); rebuildIndex(); updateCounts(); route(false);
    if ($('search').value.trim()) search();
    return {items:library.length,documents:descriptors.length,paused:library.filter(i=>i.status==='paused').length};
  }

  function updateCounts() {
    const count=section=>library.filter(i=>i.section===section).length;
    $('skill-count').textContent=count('skills')?count('skills')+' 份插件资料 · 含各版本':'插件指南与接入';
    $('personal-count').textContent=count('personal')?count('personal')+' 份个人资料':'个人资料与使用方法';
  }

  function fillArea(area) {
    $('area-title').textContent=labels[area]; $('area-description').textContent=descriptions[area];
    $('area-eyebrow').textContent={main:'01 / CORE GUIDE',skills:'02 / PLUGIN KNOWLEDGE',personal:'03 / PERSONAL SPACE'}[area];
    const cards=[];
    for (const page of data.pages.filter(p=>p.area===area && p.id!=='guide-home')) {
      const card=link('',page.id,'chapter-card');
      card.append(text('span',String(cards.length+1).padStart(2,'0'),'num'));
      const body=document.createElement('div'); body.append(text('h3',page.title),text('p',page.summary)); card.append(body); cards.push(card);
    }
    $('chapter-grid').replaceChildren(...cards);
    show('library-area',area!=='main');
    const items=library.filter(i=>i.section===area);
    show('library-empty',!items.length);
    const libraryCards=items.map(item=>{
      const card=document.createElement('section'); card.className='library-card';
      card.append(text('span',item.version,'badge'),text('span',item.status==='paused'?'已暂停':'可阅读','badge'+(item.status==='paused'?' paused':'')),text('h3',item.title),text('p',item.summary));
      if (item.status==='paused') card.append(text('p','保留资料位置与版本；正文不载入、不加入搜索。'));
      else for (const doc of item.documents) { card.append(link(doc.title+' →',item.uid+'-'+doc.id),document.createElement('br')); }
      card.append(text('footer',item.id+' / '+item.revision)); return card;
    });
    $('library-grid').replaceChildren(...libraryCards);
  }

  function rail(area, current, onHome) {
    for (const a of document.querySelectorAll('.areas a')) {
      if (!onHome && a.dataset.area===area) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');
    }
    if(onHome) $('rail-home').setAttribute('aria-current','page'); else $('rail-home').removeAttribute('aria-current');
    const links=pages.filter(p=>p.area===area && p.id!=='guide-home').map(p=>{
      const a=link(p.title,p.id); if(p.id===current) a.setAttribute('aria-current','page'); return a;
    });
    $('rail-chapters').replaceChildren(...links);
  }

  function route(scroll=true) {
    let hash='home'; try { hash=decodeURIComponent(location.hash.slice(1)).trim()||'home'; } catch { report('这个章节链接无法识别，已回到工作台。'); }
    const target=$(hash), article=target?.closest('.article');
    const overview=hash==='home', all=hash==='all';
    const area=article?.dataset.area || (labels[hash]?hash:'main');
    activeArea=area; rail(area,article?.id,overview);
    show('hero',overview); show('home-view',overview); show('area-view',!article && !overview && !all);
    show('reader-view',Boolean(article)||all);
    $('articles').classList.toggle('reading-all',all);
    for (const a of document.querySelectorAll('.article')) a.hidden=!all && a!==article;
    if (!article && !overview && !all) fillArea(area);
    const page=pages.find(p=>p.id===article?.id);
    $('breadcrumb').textContent=overview?'工作台':all?'完整阅读':labels[area]+(page?' / '+page.title:'');
    $('reader-back').href='#'+area; $('reader-back').textContent='← 返回'+labels[area]+'目录';
    $('toc').replaceChildren();
    if (article) {
      $('toc').append(text('b','本页内容'));
      for (const heading of article.querySelectorAll('h2[id],h3[id]')) $('toc').append(link(heading.textContent,heading.id));
    }
    $('rail').classList.remove('open'); $('menu-toggle').setAttribute('aria-expanded','false');
    if (scroll) {
      if (article) {
        requestAnimationFrame(()=>{ target.scrollIntoView({block:'start'}); target.setAttribute('tabindex','-1'); target.focus({preventScroll:true}); });
      } else window.scrollTo(0,0);
    }
    if (!article && !overview && !all && !labels[hash]) report('该章节未找到，已显示主体目录。');
  }

  function rebuildIndex() {
    index=[];
    for (const page of pages) {
      const article=$(page.id); if (!article) continue;
      let chunk={id:page.id,title:page.title,text:'',page:page.title,area:page.area};
      for (const child of article.children) {
        if (/^H[23]$/.test(child.tagName)) {
          if (chunk.text.trim()) index.push(chunk);
          chunk={id:child.id||page.id,title:child.textContent,text:'',page:page.title,area:page.area};
        }
        const copy=child.cloneNode(true); for (const button of copy.querySelectorAll('button')) button.remove();
        chunk.text+=' '+copy.textContent;
      }
      if (chunk.text.trim()) index.push(chunk);
    }
    for (const item of index) { item.text=item.text.replace(/\s+/g,' ').trim(); item.fold=(item.title+' '+item.text).toLocaleLowerCase(); }
  }

  function marked(container, value, terms) {
    const folded=value.toLocaleLowerCase(); let cursor=0;
    while (cursor<value.length) {
      let at=value.length, len=0;
      for (const term of terms) { const found=folded.indexOf(term,cursor); if (found>=0 && found<at) {at=found;len=term.length;} }
      container.append(document.createTextNode(value.slice(cursor,at)));
      if (!len) break;
      container.append(text('mark',value.slice(at,at+len))); cursor=at+len;
    }
  }

  function search() {
    const query=$('search').value.trim().slice(0,120), scope=$('search-scope').value;
    show('clear-search',Boolean(query)); show('search-results',Boolean(query));
    if (!query) { $('result-list').replaceChildren(); return; }
    const terms=[...new Set(query.toLocaleLowerCase().split(/\s+/).filter(Boolean))];
    const found=index.filter(i=>(scope==='all'||i.area===scope)&&terms.every(t=>i.fold.includes(t)))
      .map(i=>({...i,score:terms.reduce((s,t)=>s+(i.title.toLocaleLowerCase().includes(t)?5:0)+(i.page.toLocaleLowerCase().includes(t)?2:0),0)}))
      .sort((a,b)=>b.score-a.score);
    $('search-count').textContent=found.length?`${found.length} 个相关段落${found.length>60?' · 先显示前 60 个':''}`:'没有找到匹配内容';
    const results=found.slice(0,60).map(i=>{
      const a=link('',i.id,'search-item'); a.append(text('small',labels[i.area]+' / '+i.page));
      const title=document.createElement('strong'); marked(title,i.title,terms); a.append(title);
      const first=Math.min(...terms.map(t=>i.text.toLocaleLowerCase().indexOf(t)).filter(n=>n>=0),i.text.length);
      const start=Math.max(0,first-36), excerpt=(start?'…':'')+i.text.slice(start,start+150)+(i.text.length>start+150?'…':'');
      const p=document.createElement('p'); marked(p,excerpt,terms); a.append(p);
      a.addEventListener('click',()=>{ $('search').value=''; search(); if(location.hash==='#'+i.id) route(); }); return a;
    });
    if (!results.length) results.push(text('p','换一个关键词，或将搜索范围切换为“全部内容”。未接入或暂停的资料不参与正文搜索。'));
    $('result-list').replaceChildren(...results);
  }

  function attachCopyButtons() {
    for (const node of document.querySelectorAll('.article blockquote,.article pre')) {
      if (node.querySelector('.copy-btn')) continue;
      const button=text('button',node.tagName==='PRE'?'复制代码':'复制需求','copy-btn'); button.type='button';
      button.addEventListener('click',async()=>{
        const copy=node.cloneNode(true); copy.querySelector('.copy-btn')?.remove();
        const value=copy.textContent.trim();
        try {
          if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(value);
          else {
            const field=document.createElement('textarea'); field.value=value; field.style.position='fixed'; field.style.opacity='0'; document.body.append(field); field.select();
            const ok=document.execCommand('copy'); field.remove(); if(!ok) throw Error('copy');
          }
          button.textContent='已复制'; setTimeout(()=>button.textContent=node.tagName==='PRE'?'复制代码':'复制需求',1600);
        } catch { button.textContent='请选中文字复制'; }
      });
      node.append(button);
    }
  }

  $('search').addEventListener('input',search); $('search-scope').addEventListener('change',search);
  $('clear-search').addEventListener('click',()=>{ $('search').value=''; search(); $('search').focus(); });
  document.addEventListener('keydown',event=>{
    if ((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k') { event.preventDefault(); $('search').focus(); $('search').select(); }
    if (event.key==='Escape') { $('search').value=''; search(); $('rail').classList.remove('open'); $('menu-toggle').setAttribute('aria-expanded','false'); }
  });
  $('menu-toggle').addEventListener('click',()=>{ const open=$('rail').classList.toggle('open'); $('menu-toggle').setAttribute('aria-expanded',String(open)); });
  $('print-manual').addEventListener('click',()=>window.print());
  for(const home of document.querySelectorAll('a[href="#home"]')) home.addEventListener('click',()=>{
    $('search').value=''; search(); report(''); if(location.hash==='#home') route();
  });
  $('load-library').addEventListener('click',()=>$('library-file').click());
  $('library-file').addEventListener('change',async event=>{
    const file=event.target.files[0]; if(!file) return;
    try {
      if(file.size>12000000) throw Error('资料文件超过 12 MB，请拆分后载入。');
      const result=registerLibrary(JSON.parse(await file.text()));
      report(`已载入 ${result.items} 份资料、${result.documents} 篇正文；${result.paused} 份暂停。仅在当前页面展示，未改动原文件。`);
    } catch(error) { report('未载入：'+(error instanceof SyntaxError?'JSON 无法解析。':error.message)); }
    event.target.value='';
  });
  window.addEventListener('hashchange',()=>route());
  window.LetsGalWiki=Object.freeze({schema:1,register:registerLibrary});
  document.body.classList.add('js');
  try { registerLibrary(data.library); if(location.hash) requestAnimationFrame(()=>route()); } catch(error) { report('本地资料未加载：'+error.message); attachCopyButtons(); rebuildIndex(); route(false); }
})();
