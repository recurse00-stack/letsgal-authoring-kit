"""Build the complete offline Wiki from Markdown. Requires Python Markdown."""
import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import markdown

ROOT = Path(__file__).resolve().parents[1]

def slugify(value, separator):
    return re.sub(r'[^\w\-\s]', '', value.lower()).strip().replace(' ', separator)

class Inspect(HTMLParser):
    def __init__(self, value):
        super().__init__(); self.ids=[]; self.links=[]; self.text=[]; self.feed(value)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if 'href' in attrs: self.links.append(attrs['href'])
    def handle_data(self, data): self.text.append(data)

def json_script(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')

def render(root=ROOT, library=None, local=False):
    root=Path(root).resolve()
    layout=json.loads((root/'maintenance/manual-layout.json').read_text('utf-8'))
    bundle=json.loads((root/'bundle.json').read_text('utf-8'))
    names=layout['pages']
    assert names[0]=='MANUAL.md' and len(names)==len(set(names))
    prefixes={name:('guide-home' if i==0 else 'wiki'+str(i).zfill(2)) for i,name in enumerate(names)}
    aliases={key.strip():value for key,value in layout.get('legacy_aliases',{}).items()}
    assert all(target in prefixes for target in aliases.values())
    articles=[]; pages=[]; source_counts={}
    for name in names:
        path=root/name
        assert path.resolve().is_relative_to(root)
        source=path.read_text('utf-8')
        if name=='MANUAL.md': source=re.sub(r'<a id="[^"]+"></a>\s*','',source)
        md=markdown.Markdown(extensions=['tables','fenced_code','toc'],extension_configs={'toc':{'slugify':slugify}})
        body=md.convert(source)
        prefix=prefixes[name]
        def target_link(match):
            href=html.unescape(match[1]); u=urlsplit(href)
            if u.scheme or u.netloc: return match[0]
            destination=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(u.path))) if u.path else name
            fragment=unquote(u.fragment).strip()
            if destination=='MANUAL.html': new='#home'
            elif destination in prefixes:
                if destination=='MANUAL.md' and fragment in aliases: new='#'+fragment
                else: new='#'+prefixes[destination]+('--'+fragment if fragment else '')
            else:
                new=((root/destination).as_uri() if local else destination)+('?' + u.query if u.query else '')+('#'+fragment if fragment else '')
            return 'href="'+html.escape(new,quote=True)+'"'
        body=re.sub(r'id="([^"]+)"',lambda m:'id="'+prefix+'--'+m[1].strip()+'"',body)
        body=re.sub(r'href="([^"]*)"',target_link,body)
        body=body.replace('<table>','<div class="table-scroll"><table>').replace('</table>','</table></div>')
        title=re.search(r'^# (.+)$',source,re.M).group(1).strip()
        page_config=layout.get('details',{}).get(name,{})
        area=page_config.get('area','main')
        assert area in ('main','skills','references','personal')
        chapter_aliases=''.join('<a class="legacy-anchor" id="'+html.escape(alias,quote=True)+'"></a>' for alias,dest in aliases.items() if dest==name)
        articles.append('<article class="article" id="'+prefix+'" data-area="'+area+'" data-source="'+name+'">'+chapter_aliases+body+'</article>')
        pages.append({'id':prefix,'area':area,'title':re.sub(r'^\d+\.\s*','',title),'summary':page_config.get('summary',''),'source':name})
        source_counts[name]={'characters':len(source),'headings':len(Inspect(body).ids)}
    data={'schema':1,'pages':pages,'library':library or {'schema':1,'kind':'letsgal-wiki-library','items':[]},'local':local}
    output=(root/'maintenance/wiki.html').read_text('utf-8')
    substitutions={'CSS':(root/'maintenance/wiki.css').read_text('utf-8'),'SCRIPT':(root/'maintenance/wiki.js').read_text('utf-8'),'ARTICLES':''.join(articles),'DATA':json_script(data),'VERSION':html.escape(bundle['version']),'REVISION':html.escape(bundle['revision'])}
    output=re.sub(r'@@(CSS|SCRIPT|ARTICLES|DATA|VERSION|REVISION)@@',lambda m:substitutions[m[1]],output)
    scan=Inspect(output)
    assert len(scan.ids)==len(set(scan.ids)), 'Duplicate HTML anchor'
    for link in scan.links:
        if link.startswith('#'): assert unquote(link[1:]) in scan.ids or link[1:] in ('home','main','skills','references','personal','all'),link
        elif not urlsplit(link).scheme: assert (root/unquote(link.split('#')[0])).exists(),link
    return output,{'pages':len(names),'anchors':len(scan.ids),'links':len(scan.links),'source_pages':source_counts,'library_items':len(data['library']['items'])}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    output,report=render(); target=ROOT/'MANUAL.html'
    if args.check: assert target.read_bytes()==output.encode('utf-8'),'MANUAL.html is stale; rebuild it from Markdown'
    else: target.write_bytes(output.encode('utf-8'))
    print(json.dumps({'status':'current' if args.check else 'generated',**report},ensure_ascii=False))

if __name__=='__main__': main()
