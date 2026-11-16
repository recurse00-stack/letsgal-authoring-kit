(() => {
  'use strict';
  const $=id=>document.getElementById(id), data=JSON.parse($('wiki-data').textContent);
  const labels={main:'主 Skill',skills:'Skill Wiki',references:'创作参考',personal:'个人资料'};
  const modules={main:{title:'主体',summary:'主 Skill 的安装、连接与工程制作指南。'},skills:{title:'Skill Wiki',summary:'插件指南与功能型附属资料。'},personal:{title:'个性化',summary:'先写下自己的要求，再选择适合自己的创作参考。'}};
  const moduleOf=section=>section==='references'?'personal':section;
  const personalKey='personal/letsgal-personal';
  const helpIds=new Set(['wiki09','wiki10','wiki11']);
  let pages=[],library=[],spaces=[],index=[],context={},lastScope='';
  const text=(tag,value,cls)=>{const n=document.createElement(tag);if(value!==undefined)n.textContent=value;if(cls)n.className=cls;return n;};
  const link=(title,hash,cls)=>{const a=text('a',title,cls);a.href='#'+hash;return a;};
  const show=(id,yes)=>{$(id).hidden=!yes;};
  const report=value=>{$('status').textContent=value;};
  const safeString=(v,max=200)=>typeof v==='string'&&v.trim().length>0&&v.length<=max;
  const spaceHash=(key,uid)=>'space/'+encodeURIComponent(key)+(uid?'/'+uid:'');
  const itemKey=i=>i.package_key||'legacy/'+i.section+'/'+i.id;
  function validateNavigation(nav,docs){
    if(nav===undefined)return;
    if(!nav||Array.isArray(nav)||typeof nav!=='object'||Object.keys(nav).some(k=>!['intro','start','groups'].includes(k)))throw Error('导览声明格式不正确。');
    const ids=new Set(docs.map(d=>d.id)),seen=new Set();
    if(nav.intro!==undefined&&!safeString(nav.intro,1000))throw Error('导览简介无效。');
    if(nav.start!==undefined&&(!safeString(nav.start,61)||!ids.has(nav.start)))throw Error('导览入口文档不存在。');
    if(nav.groups!==undefined&&(!Array.isArray(nav.groups)||nav.groups.length>20))throw Error('导览分组无效。');
    for(const g of nav.groups||[]){
      if(!g||Array.isArray(g)||Object.keys(g).some(k=>!['title','summary','documents'].includes(k))||!safeString(g.title,120)||g.summary!==undefined&&(typeof g.summary!=='string'||g.summary.length>400)||!Array.isArray(g.documents)||!g.documents.length||g.documents.length>50)throw Error('导览分组格式不正确。');
      for(const id of g.documents){if(typeof id!=='string'||!ids.has(id)||seen.has(id))throw Error('导览文档缺失或重复。');seen.add(id);}
    }
  }
  function validateLibrary(value){
    if(!value||![1,2].includes(value.schema)||value.kind!=='letsgal-wiki-library'||!Array.isArray(value.items)||value.items.length>200)throw Error('资料格式不匹配，请使用接入工具生成的 Wiki JSON。');
    const identities=new Set();
    return value.items.map(i=>{
      if(!i||!['skills','references','personal'].includes(i.section)||!['available','paused'].includes(i.status)||!/^ext-[a-f0-9]{16}$/.test(i.uid)||!safeString(i.id)||!safeString(i.version,80)||!safeString(i.revision,100)||!safeString(i.title)||typeof i.summary!=='string'||i.summary.length>1000||!Array.isArray(i.documents)||i.documents.length>50||identities.has(i.uid))throw Error('资料身份或正文清单无效。');
      if(i.package_key!==undefined&&(typeof i.package_key!=='string'||!new RegExp('^(addon|plugin-guide|personal)/[a-z0-9][a-z0-9._-]{0,199}$').test(i.package_key)||i.package_key.split('/')[1]!==i.id))throw Error('资料空间身份无效。');
      identities.add(i.uid);const visible=value.schema===1?i.status==='available':i.wiki_visible===true;
      if(visible&&!i.documents.length)throw Error('可阅读条目缺少正文。');
      const seen=new Set();
      for(const d of i.documents){if(!d||!/^[a-z0-9][a-z0-9-]{0,60}$/.test(d.id)||!safeString(d.title)||seen.has(d.id))throw Error('资料文档无效或重复。');
        const htmlOK=typeof d.html==='string'&&d.html.length<=1000000&&d.markdown===undefined;
        const mdOK=i.section==='personal'&&typeof d.markdown==='string'&&d.markdown.length<=1000000&&d.html===undefined;
        if(!htmlOK&&!mdOK)throw Error('资料文档正文无效。');seen.add(d.id);}
      if(i.package_key?.startsWith('personal/')&&(i.package_key!==personalKey||i.section!=='personal'))throw Error('个人资料身份无效。');
      validateNavigation(i.navigation,i.documents);
      return {...i,wiki_visible:visible,enabled:value.schema===1?i.status==='available':i.enabled,documents:visible?i.documents:[]};
    });
  }
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


  function markdownBody(source,prefix,itemPrefix){
    const template=document.createElement('template');template.innerHTML=window.marked.parse(source,{async:false});
    const counts=new Map();
    for(const h of template.content.querySelectorAll('h1,h2,h3,h4,h5,h6')){const stem=h.textContent.toLowerCase().replace(/[^\p{L}\p{N}_\s-]/gu,'').trim().replace(/ /g,'-')||'section',count=counts.get(stem)||0;counts.set(stem,count+1);h.id=stem+(count?'_'+count:'');}
    for(const a of template.content.querySelectorAll('a[href]')){const raw=a.getAttribute('href'),parts=raw.split('#'),map={'user.md':'requirements','memory.md':'memory','guide.md':'guide'};if(map[parts[0]])a.setAttribute('href','#'+itemPrefix+'-'+map[parts[0]]+(parts[1]?'--'+parts[1]:''));}
    return readableContent(template.innerHTML,prefix,itemPrefix);
  }
  function groupsFor(edition){
    const nav=edition.navigation||{}, used=new Set();
    const groups=(nav.groups||[]).map(g=>({...g,pages:g.documents.map(id=>{used.add(id);return edition.pages.find(p=>p.docId===id);})}));
    const remaining=edition.pages.filter(p=>!used.has(p.docId));
    if(remaining.length)groups.push({title:groups.length?'其他资料':'文档',summary:'',pages:remaining});
    return groups;
  }
  function registerLibrary(value){
    const incoming=validateLibrary(value),articles=[],descriptors=[];
    for(const i of incoming)for(const d of i.documents){
      const id=i.uid+'-'+d.id,a=text('article',undefined,'article');a.id=id;a.dataset.area=i.section;a.dataset.external='true';
      a.append(text('p',i.title+(i.package_key===personalKey?'':(' · '+i.version)),'eyebrow'));
      if(i.package_key!==personalKey&&i.revision){const details=text('details',undefined,'article-details');details.append(text('summary','资料版本详情'),text('code',i.revision));a.append(details);}
      const body=d.markdown!==undefined?markdownBody(d.markdown,id,i.uid):readableContent(d.html,id,i.uid);if(!body.querySelector('h1'))a.append(text('h1',d.title));a.append(body);
      articles.push(a);descriptors.push({id,docId:d.id,area:i.section,title:d.title,summary:'',external:true,spaceKey:itemKey(i),editionUid:i.uid});
    }
    const builtin=data.pages.map(p=>({...p,docId:p.id,spaceKey:helpIds.has(p.id)?null:'core',editionUid:helpIds.has(p.id)?null:'core',area:helpIds.has(p.id)?p.area:'main'}));
    const corePages=builtin.filter(p=>p.spaceKey==='core');
    validateNavigation(data.core_navigation,corePages.map(p=>({id:p.docId})));
    const core={key:'core',title:'引擎创作指南',summary:'安装与连接、剧情与演出、UI 与扩展。按任务查找实现方法。',section:'main',versions:[{uid:'core',version:data.version||'3.0',revision:'',pages:corePages,navigation:data.core_navigation}]};
    const grouped=new Map();
    for(const i of incoming.filter(i=>i.wiki_visible)){
      const key=itemKey(i);if(!grouped.has(key))grouped.set(key,{key,title:i.title,summary:i.summary,section:i.section,versions:[]});
      grouped.get(key).versions.push({...i,pages:descriptors.filter(p=>p.editionUid===i.uid)});
    }
    // All parsing and navigation checks precede the atomic DOM replacement.
    document.querySelectorAll('.article[data-external]').forEach(n=>n.remove());$('articles').append(...articles);
    library=incoming;pages=[...builtin,...descriptors];spaces=[core,...grouped.values()];
    attachCopyButtons();rebuildIndex();route(false);
    if($('search').value.trim())search();
    window.dispatchEvent(new CustomEvent('letsgal-library-updated',{detail:{schema:2,kind:'letsgal-wiki-library',items:incoming}}));
    return {items:library.length,documents:descriptors.length,paused:library.filter(i=>i.status==='paused').length};
  }
  function preferred(space){
    const pinned=space.versions.find(v=>v.selected_version===v.version&&v.selection_mode==='fixed'||v.selected===true);
    return pinned||(space.versions.length===1?space.versions[0]:null);
  }
  function spaceCard(s){
    const card=link('',spaceHash(s.key),'space-card');card.dataset.spaceKey=s.key;
    const top=text('div',undefined,'space-card-top');top.append(text('span',labels[s.section],'space-kind'),text('span','↗','space-arrow'));card.append(top);
    card.append(text('h2',s.title),text('p',s.summary));
    if(s.key!==personalKey)card.append(text('div',s.versions.map(v=>v.version).join(' · '),'space-versions'));
    const footer=text('div',undefined,'space-card-bottom');footer.append(text('span',s.key===personalKey?'由你编写和维护':s.versions.length>1?s.versions.length+' 个阅读版本':'独立指南空间'),text('strong','进入指南 →'));card.append(footer);return card;
  }
  const moduleIcons=Object.fromEntries(Object.entries({main:'<path d="M4 5h6a3 3 0 0 1 3 3v13a4 4 0 0 0-4-3H4zM13 8a3 3 0 0 1 3-3h5v13h-4a4 4 0 0 0-4 3"/>',skills:'<path d="m12 3 9 5-9 5-9-5zM3 12l9 5 9-5M3 16l9 5 9-5"/>',personal:'<circle cx="12" cy="12" r="9"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5z"/>'}).map(([key,path])=>[key,'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">'+path+'</svg>']));
  function fillHome(category='all'){
    const home=category==='all';show('module-grid',home);show('module-directory',!home);show('home-tools',home);
    $('home-view').querySelector('.home-credit').hidden=!home;
    $('module-grid').replaceChildren(...Object.entries(modules).map(([key,m],n)=>{const a=link('', 'module/'+key,'module-card');a.dataset.module=key;const top=text('div',undefined,'module-card-top'),icon=text('span',undefined,'module-icon');icon.innerHTML=moduleIcons[key];top.append(icon,text('span','0'+(n+1),'module-number'));a.append(top,text('h2',m.title),text('p',m.summary),text('strong','进入模块 →'));return a;}));
    $('workspace-count').textContent='三个模块 · '+spaces.length+' 份可读指南';
    if(home)return;
    const m=modules[category];$('module-title').textContent=m.title;$('module-description').textContent=m.summary;$('module-eyebrow').textContent='WORKSPACE / '+category.toUpperCase();show('module-personal-edit',category==='personal');
    const chosen=spaces.filter(s=>moduleOf(s.section)===category);const grid=$('space-grid');grid.replaceChildren();
    if(category==='personal'){
      for(const [title,filter] of [['我的个人包',s=>s.key===personalKey],['其他个人资料',s=>s.section==='personal'&&s.key!==personalKey],['创作参考',s=>s.section==='references']]){
        const rows=chosen.filter(filter);if(!rows.length)continue;grid.append(text('h2',title,'space-group-title'));grid.append(...rows.map(spaceCard));
      }
    }else grid.append(...chosen.map(spaceCard));
    show('spaces-empty',!chosen.length);
  }
  function fillSpace(space,edition){
    $('space-category').textContent=labels[space.section]+' / GUIDE SPACE';$('space-title').textContent=space.title;
    $('space-intro').textContent=edition?.navigation?.intro||edition?.summary||space.summary;
    $('space-meta').replaceChildren();
    if(edition){
      $('space-meta').append(text('span',space.key===personalKey?'个人资料':'阅读版本 '+edition.version,'badge'));
      if(edition.status==='paused')$('space-meta').append(text('span','AI 已暂停 · 手册可阅读','badge paused'));
      if(space.key==='core')$('space-meta').append(text('span','Stable 与 Beta 双通道','badge'));
    }
    const start=edition?.pages.find(p=>p.docId===edition.navigation?.start)||edition?.pages[0];
    show('space-start',Boolean(start));if(start){$('space-start').href='#'+start.id;$('space-start').textContent='开始阅读：'+start.title+' →';}
    show('version-choice',!edition);$('version-choice').replaceChildren();
    if(!edition){$('version-choice').append(text('h3','选择阅读版本'),text('p','这里的选择只改变阅读内容，AI 使用版本仍由包管理决定。'));
      const versions=text('div',undefined,'version-options');for(const v of space.versions)versions.append(link(v.version+' →',spaceHash(space.key,v.uid),'version-option'));$('version-choice').append(versions);
    }
    const groups=edition?groupsFor(edition):[];
    $('guide-groups').replaceChildren(...groups.map((g,n)=>{
      const box=text('section',undefined,'guide-group');const head=text('div',undefined,'guide-group-heading');
      head.append(text('span',String(n+1).padStart(2,'0'),'group-number'),text('h2',g.title));box.append(head);
      if(g.summary)box.append(text('p',g.summary,'group-summary'));
      const list=text('div',undefined,'guide-docs');
      for(const p of g.pages){const a=link('',p.id,'guide-doc');a.append(text('strong',p.title),text('span','→','doc-arrow'));if(p.summary)a.append(text('small',p.summary));list.append(a);}
      box.append(list);return box;
    }));
  }
  function fillRail(space,edition,article,mode){
    const select=$('space-switcher');const root=text('option','工作台 · 全部资料');root.value='home';select.replaceChildren(root);
    for(const [key,m] of Object.entries(modules)){const group=text('optgroup');group.label=m.title;const module=text('option',m.title+' · 模块首页');module.value='module/'+key;group.append(module);for(const s of spaces.filter(s=>moduleOf(s.section)===key)){const option=text('option',s.title);option.value=s.key;group.append(option);}select.append(group);}select.value=space?.key||(context.category&&context.category!=='all'?'module/'+context.category:'home');
    $('rail-context').textContent=space?'当前指南':'工作台';show('rail-version-wrap',Boolean(space&&space.key!==personalKey));
    if(space){const v=$('reading-version');v.replaceChildren();if(!edition){const hint=text('option','选择阅读版本');hint.value='';v.append(hint);}
      for(const row of space.versions){const opt=text('option',row.version);opt.value=row.uid;v.append(opt);}v.value=edition?.uid||'';
    }
    const nav=$('rail-chapters');nav.replaceChildren();
    const add=(title,hash,current)=>{const a=link(title,hash);if(current)a.setAttribute('aria-current','page');nav.append(a);};
    if(space){add('← '+modules[moduleOf(space.section)].title,'module/'+moduleOf(space.section),false);add('指南首页',spaceHash(space.key,edition?.uid),!article);
      if(edition)for(const group of groupsFor(edition)){nav.append(text('p',group.title,'rail-group'));for(const p of group.pages)add(p.title,p.id,p.id===article?.id);}
      else for(const v of space.versions)add('版本 '+v.version,spaceHash(space.key,v.uid),false);
    }else if(mode==='editor'){
      $('rail-context').textContent='我的个人包';add('← 个性化','module/personal',false);
      for(const [key,title] of Object.entries({requirements:'我的要求',memory:'长期记忆',guide:'我的指南'}))add(title,'personal-edit/'+key,context.editorKey===key);
    }else{
      for(const [key,m] of Object.entries(modules))add(m.title,'module/'+key,context.category===key);
      if(['home','packages','help','all'].includes(mode)){add('包管理','packages',mode==='packages');add('使用与接入','help',mode==='help');add('完整阅读与打印','all',mode==='all');}
      if(mode==='help'||article)for(const p of pages.filter(p=>helpIds.has(p.id)))add(p.title,p.id,p.id===article?.id);
    }
    $('rail-home').toggleAttribute('aria-current',mode==='home');
  }
  let tocHeadings=[],tocPending=false;
  function updateToc(){
    tocPending=false;if(!tocHeadings.length)return;
    const edge=document.querySelector('.topbar').getBoundingClientRect().bottom+28;
    let current=tocHeadings[0];for(const h of tocHeadings){if(h.getBoundingClientRect().top<=edge)current=h;else break;}
    if(window.scrollY>0&&window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-4)current=tocHeadings.at(-1);
    for(const a of $('toc').querySelectorAll('a')){if(a.getAttribute('href')==='#'+current.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');}
  }
  window.addEventListener('scroll',()=>{if(!tocPending){tocPending=true;requestAnimationFrame(updateToc);}},{passive:true});
  new ResizeObserver(entries=>{document.documentElement.style.setProperty('--topbar-height',Math.ceil(entries[0].target.getBoundingClientRect().height)+'px');updateToc();}).observe(document.querySelector('.topbar'));
  $('edition-state').textContent=(data.revision||'').includes('preview')?'· 本地候选':'· 发行版';
  function route(scroll=true){
    report('');
    let raw=location.hash.slice(1)||'home',hash;try{hash=decodeURIComponent(raw);}catch{hash='invalid';}
    let article=$(hash)?.closest('.article'),page=pages.find(p=>p.id===article?.id),space=null,edition=null,missing=false,mode='home',category='all',editorKey=null;
    if(page){space=spaces.find(s=>s.key===page.spaceKey);edition=space?.versions.find(v=>v.uid===page.editionUid);mode='reader';}
    else if(raw.startsWith('space/')){
      const parts=raw.split('/');let key;try{key=decodeURIComponent(parts[1]);}catch{key='';}
      space=spaces.find(s=>s.key===key);if(space){edition=parts[2]?space.versions.find(v=>v.uid===parts[2]):preferred(space);mode='space';if(parts[2]&&!edition)report('该阅读版本当前不可用，请重新选择。');}else missing=true;
    }else if(raw.startsWith('personal-edit/')){editorKey=raw.split('/')[1];if(['requirements','memory','guide'].includes(editorKey)){mode='editor';category='personal';}else missing=true;}
    else if(raw.startsWith('module/')&&modules[raw.split('/')[1]]){mode='module';category=raw.split('/')[1];}
    else if(['main','category/main','skills','references','personal'].includes(hash)){mode='module';category=hash==='category/main'?'main':moduleOf(hash);}
    else if(['packages','help','all','home'].includes(hash))mode=hash;
    else missing=true;
    if(missing){mode='missing';space=null;edition=null;article=null;}
    if(space)category=moduleOf(space.section);
    context={space,edition,article,mode,category,editorKey};
    show('home-view',mode==='home'||mode==='module');show('hero',mode==='home');show('personal-editor',mode==='editor');show('edit-personal',space?.key===personalKey);show('space-view',mode==='space');show('help-view',mode==='help');show('packages',mode==='packages');show('unavailable-view',mode==='missing');show('reader-view',mode==='reader'||mode==='all');
    for(const a of document.querySelectorAll('#articles .article')){a.hidden=mode!=='all'&&a!==article;const include=article?a===article:edition?edition.pages.some(p=>p.id===a.id):mode==='help'?helpIds.has(a.id):mode==='module'?moduleOf(pages.find(p=>p.id===a.id)?.area)===category:['home','all','packages'].includes(mode);a.classList.toggle('print-included',include);}
    $('print-manual').disabled=mode==='editor'||mode==='missing'||mode==='space'&&!edition;
    $('print-manual').textContent=article?'打印本页':mode==='space'?'打印本指南':'打印全部';
    $('articles').classList.toggle('reading-all',mode==='all');
    if(mode==='home'||mode==='module')fillHome(category);if(mode==='space')fillSpace(space,edition);
    fillRail(space,edition,article,mode);
    const crumb=$('breadcrumb');crumb.replaceChildren();
    if(space){crumb.append(link(modules[category].title,'module/'+category),document.createTextNode(' / '),link(space.title,spaceHash(space.key,edition?.uid)));if(page)crumb.append(document.createTextNode(' / '+page.title));}
    else if(mode==='editor')crumb.append(link('个性化','module/personal'),document.createTextNode(' / '),link('我的个人包',spaceHash(personalKey)),document.createTextNode(' / '+({requirements:'我的要求',memory:'长期记忆',guide:'我的指南'}[editorKey])));
    else crumb.textContent=mode==='module'?modules[category].title:mode==='editor'?'个性化 / 编辑我的个人包':page?.title||({home:'主页',packages:'包管理',help:'使用与接入',all:'完整阅读',missing:'资料暂不可读'}[mode]);
    $('reader-back').href='#'+(space?spaceHash(space.key,edition?.uid):'help');$('reader-back').textContent='← 返回'+(space?space.title:'使用与接入');
    $('toc').replaceChildren();tocHeadings=article?[...article.querySelectorAll('h2[id],h3[id]')]:[];if(tocHeadings.length){$('toc').append(text('b','本页内容'));for(const h of tocHeadings){const a=link(h.textContent,h.id);a.dataset.depth=h.tagName==='H3'?'3':'2';$('toc').append(a);}}requestAnimationFrame(updateToc);
    if(mode==='editor')window.dispatchEvent(new CustomEvent('letsgal-editor-route',{detail:{document:editorKey}}));
    const scopeKey=edition?.uid||category;const current=$('search-scope').querySelector('[value="current"]');current.disabled=!edition;current.textContent=edition?'当前指南'+(space.key===personalKey?'':' · '+edition.version):'当前指南';
    if(scopeKey!==lastScope){$('search-scope').value=edition?'current':mode==='module'?category:'all';lastScope=scopeKey;}
    $('search').placeholder=edition?'搜索'+space.title+'…':'搜索全部指南、方法与资料…';$('search').setAttribute('aria-label',edition?'搜索当前指南':'搜索工作台');
    if($('search').value.trim())search();
    $('rail').classList.remove('open');$('menu-toggle').setAttribute('aria-expanded','false');
    if(scroll){if(article)requestAnimationFrame(()=>{const target=$(hash)||article;target.scrollIntoView({block:'start'});target.setAttribute('tabindex','-1');target.focus({preventScroll:true});});else window.scrollTo(0,0);}
  }
  function rebuildIndex(){
    index=[];
    for(const page of pages){const article=$(page.id);if(!article)continue;let chunk={id:page.id,title:page.title,text:'',page:page.title,area:page.area,spaceKey:page.spaceKey,editionUid:page.editionUid};
      for(const child of article.children){if(/^H[23]$/.test(child.tagName)){if(chunk.text.trim())index.push(chunk);chunk={...chunk,id:child.id||page.id,title:child.textContent,text:''};}const copy=child.cloneNode(true);copy.querySelectorAll('button').forEach(n=>n.remove());chunk.text+=' '+copy.textContent;}
      if(chunk.text.trim())index.push(chunk);
    }
    for(const row of index){row.text=row.text.replace(/\s+/g,' ').trim();row.fold=(row.title+' '+row.text).toLocaleLowerCase();}
  }
  function marked(container,value,terms){
    const folded=value.toLocaleLowerCase();let cursor=0;
    while(cursor<value.length){let at=value.length,len=0;for(const t of terms){const found=folded.indexOf(t,cursor);if(found>=0&&found<at){at=found;len=t.length;}}container.append(document.createTextNode(value.slice(cursor,at)));if(!len)break;container.append(text('mark',value.slice(at,at+len)));cursor=at+len;}
  }
  function search(){
    const query=$('search').value.trim().slice(0,120),scope=$('search-scope').value;show('clear-search',!!query);show('search-results',!!query);
    if(!query){$('result-list').replaceChildren();return;}
    const terms=[...new Set(query.toLocaleLowerCase().split(/\s+/).filter(Boolean))];
    const found=index.filter(i=>(scope==='all'||scope==='current'&&i.editionUid===context.edition?.uid||moduleOf(i.area)===scope)&&terms.every(t=>i.fold.includes(t))).map(i=>({...i,score:terms.reduce((n,t)=>n+(i.title.toLocaleLowerCase().includes(t)?5:0),0)})).sort((a,b)=>b.score-a.score);
    $('search-count').textContent=found.length?found.length+' 个相关段落'+(found.length>60?' · 显示前 60 个':''):'没有找到匹配内容';
    const results=found.slice(0,60).map(i=>{const a=link('',i.id,'search-item'),s=spaces.find(s=>s.key===i.spaceKey),v=s?.versions.find(v=>v.uid===i.editionUid);a.append(text('small',(s?s.title+' / '+v.version:'工作台帮助')+' / '+i.page));const title=text('strong');marked(title,i.title,terms);a.append(title);const at=Math.min(...terms.map(t=>i.text.toLocaleLowerCase().indexOf(t)).filter(n=>n>=0),i.text.length),start=Math.max(0,at-36),p=text('p');marked(p,(start?'…':'')+i.text.slice(start,start+150)+(i.text.length>start+150?'…':''),terms);a.append(p);a.addEventListener('click',()=>{$('search').value='';search();if(location.hash==='#'+i.id)route();});return a;});
    if(!results.length)results.push(text('p','试试其他关键词，或将范围切换为全部工作台。'));
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


  $('space-switcher').addEventListener('change',e=>{location.hash=e.target.value==='home'?'home':e.target.value.startsWith('module/')?e.target.value:spaceHash(e.target.value);});
  $('reading-version').addEventListener('change',e=>{if(context.space&&e.target.value)location.hash=spaceHash(context.space.key,e.target.value);});
  for(const b of document.querySelectorAll('[data-category]'))b.addEventListener('click',()=>{const hash=b.dataset.category==='all'?'home':b.dataset.category==='main'?'category/main':b.dataset.category;if(location.hash==='#'+hash)fillHome(b.dataset.category);else location.hash=hash;});
  $('search').addEventListener('input',search);$('search-scope').addEventListener('change',search);
  $('clear-search').addEventListener('click',()=>{$('search').value='';search();$('search').focus();});
  document.addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();$('search').focus();$('search').select();}if(e.key==='Escape'){$('search').value='';search();$('rail').classList.remove('open');$('menu-toggle').setAttribute('aria-expanded','false');}});
  $('menu-toggle').addEventListener('click',()=>{$('menu-toggle').setAttribute('aria-expanded',String($('rail').classList.toggle('open')));});
  $('print-manual').addEventListener('click',()=>window.print());
  document.querySelectorAll('a[href="#home"]').forEach(a=>a.addEventListener('click',()=>{$('search').value='';search();report('');if(location.hash==='#home')route();}));
  $('load-library').addEventListener('click',()=>$('library-file').click());
  $('library-file').addEventListener('change',async e=>{const file=e.target.files[0];if(!file)return;try{if(file.size>12000000)throw Error('资料文件超过 12 MB。');const r=registerLibrary(JSON.parse(await file.text()));report(`已载入 ${r.items} 份资料、${r.documents} 篇正文；仅在当前页面展示，未改动原文件。`);}catch(error){report('未载入：'+error.message);}e.target.value='';});
  window.LetsGalWiki=Object.freeze({schema:2,register:registerLibrary,preview:(source)=>markdownBody(source,'personal-preview','personal-preview')});document.body.classList.add('js');
  // A tab-local ledger bounds the buttons to this workbench's routes.
  const historyKey='letsgal-wiki-history:'+location.pathname;
  let trail,position=0,reverting=false;
  try{trail=JSON.parse(sessionStorage.getItem(historyKey));}catch{}
  const currentHash=()=>location.hash||'#home';
  const hs=history.state?.letsgalWiki;
  if(!trail||!hs||hs.token!==trail.token||trail.entries[hs.index]!==currentHash()){
    trail={token:Date.now().toString(36)+Math.random().toString(36).slice(2),entries:[currentHash()]};
    history.replaceState({...history.state,letsgalWiki:{token:trail.token,index:0}},'',location.href);
  }else position=hs.index;
  function historyButtons(){ $('nav-back').disabled=position===0;$('nav-forward').disabled=position>=trail.entries.length-1;try{sessionStorage.setItem(historyKey,JSON.stringify(trail));}catch{} }
  function navigate(){
    const state=history.state?.letsgalWiki,known=state?.token===trail.token&&trail.entries[state.index]===currentHash();
    if(reverting){reverting=false;historyButtons();route(false);return;}
    if(!window.LetsGalPersonal?.beforeNavigate?.()&&window.LetsGalPersonal?.dirty()){
      reverting=true;history.go(known?position-state.index:-1);return;
    }
    if(known)position=state.index;
    else{trail.entries=trail.entries.slice(0,position+1);trail.entries.push(currentHash());position++;history.replaceState({...history.state,letsgalWiki:{token:trail.token,index:position}},'',location.href);}
    historyButtons();route();
  }
  $('nav-back').addEventListener('click',()=>{if(position>0)history.back();});
  $('nav-forward').addEventListener('click',()=>{if(position<trail.entries.length-1)history.forward();});
  window.addEventListener('hashchange',navigate);historyButtons();
  try{registerLibrary(data.library);if(location.hash)requestAnimationFrame(()=>route());}catch(error){registerLibrary({schema:2,kind:'letsgal-wiki-library',items:[]});report('本地资料未加载：'+error.message);}
})();
