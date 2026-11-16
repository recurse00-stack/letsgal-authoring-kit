"""On-demand, loopback-only Wiki management. Python standard library; no package execution."""
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
from pathlib import Path
import re
import secrets
import threading
import time
from urllib.parse import urlsplit
import webbrowser
import workbench_runtime as w
import workbench_packages as packages
import workbench_personal as personal


class Server(ThreadingHTTPServer):
    daemon_threads=True
    allow_reuse_address=False

    def __init__(self,area,port=0,idle_seconds=1800):
        self.area=w.ordinary(area)
        self.token=secrets.token_urlsafe(32)
        self.last_activity=time.monotonic()
        self.idle_seconds=idle_seconds
        self.stopped=threading.Event()
        self.transaction=threading.RLock()
        super().__init__(('127.0.0.1',port),Handler)
        self.origin='http://127.0.0.1:'+str(self.server_port)
        self.entry='/session/'+self.token+'/'

    def watch_idle(self):
        while not self.stopped.wait(min(10,self.idle_seconds)):
            if time.monotonic()-self.last_activity>self.idle_seconds:
                self.shutdown();return


class Handler(BaseHTTPRequestHandler):
    server_version='LetsGalWiki/1'

    def log_message(self,*args):
        pass # Tokens and local document paths must not enter request logs.

    def send(self,status,payload,kind='application/json; charset=utf-8'):
        raw=w.encode(payload) if isinstance(payload,dict) else payload
        self.send_response(status)
        self.send_header('Content-Type',kind)
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; img-src data:; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        try:self.wfile.write(raw)
        except ConnectionError:pass

    def authorize(self,api=True):
        s=self.server
        if self.headers.get('Host')!='127.0.0.1:'+str(s.server_port):return False
        origin=self.headers.get('Origin')
        if origin is not None and origin!=s.origin:return False
        if self.headers.get('Sec-Fetch-Site') in ('cross-site','same-site'):return False
        if api and not hmac.compare_digest(self.headers.get('X-LetsGal-Session',''),s.token):return False
        return True

    def do_GET(self):
        s=self.server
        document=self.path.startswith(s.entry+'docs/')
        if not self.authorize(api=self.path!=s.entry and not document):
            self.send(403,{'status':'forbidden'});return
        try:
            if self.path==s.entry:
                with s.transaction:w.refresh(s.area)
                page=w.read_bytes(s.area/'workbench/MANUAL.html').decode('utf-8')
                pattern=r'(<script id="wiki-data" type="application/json">)(.*?)(</script>)'
                m=re.search(pattern,page,re.S)
                data=json.loads(m[2]);data['manager']={'api':s.origin,'token':s.token}
                encoded=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
                page=page[:m.start(2)]+encoded+page[m.end(2):]
                links=w.read_json(s.area/'workbench/document-links.json') if (s.area/'workbench/document-links.json').exists() else {}
                def rewrite(match):
                    href=html.unescape(match[1]);url=urlsplit(href);source=url._replace(fragment='',query='').geturl()
                    if source not in links:return match[0]
                    return 'href="'+s.entry+'docs/'+links[source]+'"'
                page=re.sub(r'href="([^"]*)"',rewrite,page)
                self.send(200,page.encode('utf-8'),'text/html; charset=utf-8')
            elif document:
                key=self.path[len(s.entry+'docs/'):]
                links=w.read_json(s.area/'workbench/document-links.json')
                if not re.fullmatch('[a-f0-9]{24}',key) or key not in links.values():
                    self.send(404,{'status':'not-found'});return
                self.send(200,w.read_bytes(s.area/'workbench/documents'/(key+'.txt')),'text/plain; charset=utf-8')
            elif self.path=='/api/snapshot':
                with s.transaction,w.lock(s.area):result={'catalog':packages.catalog(s.area),'library':packages.library(s.area)}
                self.send(200,result)
            elif self.path.startswith('/api/personal/'):
                key=self.path[len('/api/personal/'):]
                with s.transaction,w.lock(s.area):result=personal.snapshot(s.area,key)
                self.send(200,result)
            elif self.path=='/api/packages':self.send(200,packages.catalog(s.area))
            elif self.path=='/api/library':self.send(200,packages.library(s.area))
            else:self.send(404,{'status':'not-found'});return
            s.last_activity=time.monotonic()
        except ConnectionError:return
        except (ValueError,OSError,KeyError,TypeError) as error:
            self.send(422,{'status':'error','message':str(error)})

    def do_POST(self):
        s=self.server
        if not self.authorize() or self.headers.get('Origin')!=s.origin:
            self.send(403,{'status':'forbidden'});return
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':
            self.send(415,{'status':'json-required'});return
        try:
            if self.headers.get('Transfer-Encoding'):raise ValueError('Chunked requests are not accepted')
            length=int(self.headers.get('Content-Length','0'))
            limit=6500000 if self.path=='/api/personal/save' else 8192
            if not 0<length<=limit:raise ValueError('Invalid request size')
            value=json.loads(self.rfile.read(length).decode('utf-8'),object_pairs_hook=w.unique)
            if not isinstance(value,dict):raise ValueError('Expected an object')
            if self.path=='/api/state':
                if set(value)!={'key','patch','expected'} or not isinstance(value['expected'],str):raise ValueError('State fingerprint is required')
                with s.transaction:result=packages.change(s.area,value['key'],value['patch'],value['expected'])
                self.send(200,result)
            elif self.path=='/api/personal/save':
                if set(value)!={'document','content','expected'}:raise ValueError('Expected document, content and fingerprint')
                with s.transaction:result=personal.save(s.area,value['document'],value['content'],value['expected'])
                self.send(200,result)
            elif self.path=='/api/shutdown' and not value:
                self.send(200,{'status':'stopping'})
                threading.Thread(target=s.shutdown,daemon=True).start()
            else:self.send(404,{'status':'not-found'});return
            s.last_activity=time.monotonic()
        except ConnectionError:return
        except packages.Conflict as error:self.send(409,{'status':'conflict','message':str(error)})
        except (ValueError,OSError,KeyError,TypeError) as error:self.send(422,{'status':'error','message':str(error)})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user-area',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    try:
        w.refresh(args.user_area)
        with Server(args.user_area) as server:
            threading.Thread(target=server.watch_idle,daemon=True).start()
            if args.no_browser:print(json.dumps({'url':server.origin+server.entry}),flush=True)
            else:webbrowser.open(server.origin+server.entry)
            try:server.serve_forever(poll_interval=0.5)
            finally:server.stopped.set()
        return 0
    except (ValueError,OSError,KeyboardInterrupt) as error:
        print(json.dumps({'status':'stopped','message':str(error)},ensure_ascii=False));return 1


if __name__=='__main__':raise SystemExit(main())
