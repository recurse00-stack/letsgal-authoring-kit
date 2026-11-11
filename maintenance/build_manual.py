"""Build the complete offline manual from its Markdown sources. Requires Python Markdown."""
import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import markdown

ROOT=Path(__file__).resolve().parents[1]
def slugify(value, separator):
    return re.sub(r'[^\w\-\s]', '', value.lower()).replace(' ', separator)

class Inspect(HTMLParser):
    def __init__(self, value):
        super().__init__();self.ids=[];self.links=[];self.feed(value)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if 'href' in attrs:self.links.append(attrs['href'])

def render(root=ROOT):
    layout=json.loads((root/'maintenance/manual-layout.json').read_text('utf-8'))
    bundle=json.loads((root/'bundle.json').read_text('utf-8'))
    version_label=html.escape(bundle['version']+' · '+bundle['revision'])
    names=layout['pages']; assert names[0]=='MANUAL.md' and len(names)==len(set(names))
    prefixes={name:('home' if i==0 else 'wiki'+str(i).zfill(2)) for i,name in enumerate(names)}
    aliases=layout.get('legacy_aliases',{})
    assert all(target in prefixes for target in aliases.values())
    articles=[];nav=[];source_counts={}
    for name in names:
        path=root/name
        assert path.resolve().is_relative_to(root.resolve())
        source=path.read_text('utf-8')
        # HTML aliases belong at the destination chapter, while Markdown retains
        # its small navigation aliases for repositories that render that file.
        if name=='MANUAL.md':source=re.sub(r'<a id="[^"]+"></a>\s*','',source)
        md=markdown.Markdown(extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'slugify':slugify}})
        body=md.convert(source)
        prefix=prefixes[name]
        def target_link(match):
            href=html.unescape(match[1]);u=urlsplit(href)
            if u.scheme or u.netloc:return match[0]
            destination=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(u.path))) if u.path else name
            fragment=unquote(u.fragment)
            if destination=='MANUAL.html':new='#home'
            elif destination in prefixes:
                if destination=='MANUAL.md' and fragment in aliases:
                    new='#'+fragment
                else:new='#'+prefixes[destination]+('--'+fragment if fragment else '')
            else:
                new=destination+('?' + u.query if u.query else '')+('#'+fragment if fragment else '')
            return 'href="'+html.escape(new,quote=True)+'"'
        body=re.sub(r'id="([^"]+)"',lambda m:'id="'+prefix+'--'+m[1]+'"',body)
        body=re.sub(r'href="([^"]*)"',target_link,body)
        # Make wide tables independently scrollable without horizontal page overflow.
        body=body.replace('<table>','<div class="table-scroll"><table>').replace('</table>','</table></div>')
        title=re.search(r'^# (.+)$',source,re.M).group(1)
        nav.append('<li><a href="#'+prefix+'">'+html.escape(title)+'</a></li>')
        chapter_aliases=''.join('<a class="legacy-anchor" id="'+html.escape(alias,quote=True)+'"></a>' for alias,dest in aliases.items() if dest==name)
        subnav=''.join('<a href="#'+prefix+'--'+html.escape(item['id'],quote=True)+'">'+html.escape(item['name'])+'</a>' for top in md.toc_tokens for item in top.get('children',[]))
        articles.append(chapter_aliases+'<section id="'+prefix+'" data-source="'+name+'">'+('<nav class="chapter-nav" aria-label="本章目录">'+subnav+'</nav>' if subnav else '')+body+'</section>')
        source_counts[name]={'characters':len(source),'headings':len(Inspect(body).ids)}
    css='''
:root { color-scheme: light; --ink:#183040; --accent:#176b65; --line:#d9e3e6; }
* { box-sizing:border-box; }
html { scroll-padding-top:1rem; }
body { margin:0; color:var(--ink); background:#f3f6f6; font:16px/1.8 "Segoe UI","Microsoft YaHei",sans-serif; }
a { color:var(--accent); text-underline-offset:.18em; overflow-wrap:anywhere; }
a:focus-visible { outline:3px solid #df9c3a; outline-offset:3px; }
.layout { display:grid; grid-template-columns:270px minmax(0,1fr); max-width:1440px; margin:auto; }
.sidebar { padding:30px 22px; position:sticky; top:0; max-height:100vh; overflow:auto; align-self:start; }
.brand { font-size:21px; font-weight:750; line-height:1.4; }
.sidebar ol { list-style:none; padding:0; }
.sidebar li { margin:.8rem 0; line-height:1.5; }
.sidebar small { display:block; color:#526772; overflow-wrap:anywhere; }
main { min-width:0; padding:24px 32px 64px; }
section { background:white; border:1px solid var(--line); border-radius:12px; padding:32px 40px; margin-bottom:28px; }
h1 { font-size:1.85rem; line-height:1.4; margin:.4em 0 1em; }
h2 { font-size:1.35rem; margin-top:1.8em; border-bottom:1px solid var(--line); padding-bottom:.3em; }
p,li,td { overflow-wrap:anywhere; }
blockquote { margin:1em 0; padding:12px 18px; border-left:4px solid var(--accent); background:#eff7f4; }
blockquote p { margin:.4em 0; }
pre { background:#172c37; color:#eef6f4; padding:18px; border-radius:7px; overflow:auto; white-space:pre-wrap; overflow-wrap:anywhere; }
code { font-size:.91em; font-family:Consolas,"Microsoft YaHei",monospace; }
td code,p code,li code { background:#eef2f3; padding:1px 4px; border-radius:3px; }
.table-scroll { overflow:auto; margin:1em 0; }
table { border-collapse:collapse; width:100%; font-size:.94em; }
th,td { border:1px solid var(--line); padding:10px 12px; vertical-align:top; text-align:left; }
th { background:#edf4f3; }
.chapter-nav { display:flex; flex-wrap:wrap; gap:8px 16px; font-size:.88em; padding-bottom:15px; border-bottom:1px solid var(--line); margin-bottom:24px; }
.legacy-anchor { display:block; height:0; }
.skip { position:absolute; left:-9999px; } .skip:focus { position:static; }
@media(max-width:800px) { .layout { display:block; } .sidebar { position:static; max-height:none; padding:22px; } .sidebar ol { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:4px 16px; } main { padding:0 12px 30px; } section { padding:22px 18px; } h1 { font-size:1.5rem; } th,td { padding:7px; } }
@media(max-width:430px) { .sidebar ol { display:block; } }
@page { size:A4; margin:18mm 16mm; }
@media print { body { background:white; color:#111; font-size:10pt; line-height:1.55; } .layout { display:block; } .sidebar,.chapter-nav,.skip { display:none; } main { padding:0; } section { border:0; border-radius:0; padding:0; margin:0; break-before:page; } section:first-of-type { break-before:auto; } h1,h2,h3 { break-after:avoid; } p,li { orphans:3; widows:3; } table { font-size:9pt; } tr,blockquote,pre { break-inside:avoid; } .table-scroll { overflow:visible; } a { color:#111; } pre { color:#111; background:#f3f3f3; } }
'''
    output='<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>LetsGal Authoring Kit · 完整使用 Wiki</title><style>'+css+'</style></head><body><a class="skip" href="#home">跳到正文</a><div class="layout"><aside class="sidebar"><div class="brand">LetsGal<br>Authoring Kit</div><small>完整离线使用 Wiki<br>'+version_label+'<br>浏览器查找：Ctrl+F · 打印：Ctrl+P</small><nav aria-label="全书目录"><ol>'+''.join(nav)+'</ol></nav></aside><main>'+''.join(articles)+'</main></div></body></html>\n'
    scan=Inspect(output);assert len(scan.ids)==len(set(scan.ids)),'Duplicate HTML anchor'
    for link in scan.links:
        if link.startswith('#'):assert link[1:] in scan.ids,link
        elif not urlsplit(link).scheme:assert (root/unquote(link.split('#')[0])).exists(),link
    return output,{'pages':len(names),'anchors':len(scan.ids),'links':len(scan.links),'source_pages':source_counts}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args()
    output,report=render();target=ROOT/'MANUAL.html'
    if args.check:
        assert target.read_bytes()==output.encode('utf-8'),'MANUAL.html is stale; rebuild it from Markdown'
    else:target.write_bytes(output.encode('utf-8'))
    print(json.dumps({'status':'current' if args.check else 'generated',**report},ensure_ascii=False))
if __name__=='__main__':main()
