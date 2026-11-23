"""Read explicit local Wiki manifests and build a NEW personal workbench outside the public source."""
import argparse
import hashlib
import json
from pathlib import Path
from build_manual import ROOT, render
from workbench_mounts import ordinary
from workbench_packages import library as managed_library


def collect(user_area):
    return managed_library(ordinary(user_area), render_html=True)


def build(user_area, output=None, data_output=None, check=False):
    library=collect(user_area)
    report={'status':'checked' if check else 'generated','items':len(library['items']),'documents':sum(len(i['documents']) for i in library['items']),'paused':sum(i['status']=='paused' for i in library['items']),'source_files_modified':False}
    if check: return report
    if output is None: raise ValueError('--output is required unless --check is used')
    destinations=[ordinary(output)]+([ordinary(data_output)] if data_output else [])
    for target in destinations:
        if target.is_relative_to(ROOT.parent.resolve()): raise ValueError('Personal output must stay outside the public release tree')
        if target.exists() or not target.parent.is_dir(): raise ValueError('Output must be a NEW file in an existing directory')
    if len(set(destinations))!=len(destinations): raise ValueError('Output paths must differ')
    page,_=render(library=library,local=True)
    payloads=[page.encode('utf-8')]
    if data_output: payloads.append((json.dumps(library,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    for target,payload in zip(destinations,payloads):
        with target.open('xb') as stream: stream.write(payload)
        assert target.read_bytes()==payload
    report['outputs']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in destinations]
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user-area',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--data-output',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try: result=build(args.user_area,args.output,args.data_output,args.check)
    except (ValueError,OSError,AssertionError) as error:
        print(json.dumps({'status':'error','message':str(error)},ensure_ascii=False)); return 1
    print(json.dumps(result,ensure_ascii=False)); return 0

if __name__=='__main__': raise SystemExit(main())
