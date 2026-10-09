"""Isolated installation, channel switching and recovery checks; no Studio access."""
import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def run(bundle,scratch,previous=None):
    scratch.mkdir(parents=True,exist_ok=False)
    home=scratch/"user's home 测试";home.mkdir()
    area=home/'.letsgal-authoring';(area/'preferences').mkdir(parents=True);(area/'plugins/demo/1.0').mkdir(parents=True)
    (area/'preferences/user.md').write_text('Preserve personal preferences.\n','utf-8')
    (area/'plugins/demo/1.0/SKILL.md').write_text('Preserve plugin knowledge.\n','utf-8')
    personal=hashes(area);target=home/'.agents/skills/letsgal-authoring';results=[]
    def record(name,ok,detail=''):
        results.append({'name':name,'passed':bool(ok),'detail':detail})
        (scratch/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n','utf-8')
        if not ok:raise AssertionError(name+': '+str(detail))
    def call(channel=None,action='Install',src=bundle,user=home,*extra):
        args=['powershell.exe','-NoLogo','-NoProfile','-ExecutionPolicy','Bypass','-NonInteractive','-File',str(src/'Install.ps1'),'-Harness','Codex','-Scope','User','-UserHome',str(user),'-Action',action,'-NonInteractive']
        if channel:args+=['-Channel',channel]
        p=subprocess.run(args+list(extra),capture_output=True,timeout=45)
        output=p.stdout.decode('utf-8-sig',errors='replace');data={}
        for line in output.splitlines():
            if line.startswith('{'):
                try:data=json.loads(line)
                except json.JSONDecodeError:pass
        return p.returncode,data,p.stderr.decode('utf-8-sig',errors='replace')[-1500:]
    expected={ch:{r['path']:r['sha256'] for r in json.loads((bundle/f'channels/{ch}/bundle.json').read_text('utf-8'))['files']} for ch in ['stable','beta']}
    def installed(ch,t=target):
        h=hashes(t);h.pop('.install-receipt.json',None)
        receipt=json.loads((t/'.install-receipt.json').read_text('utf-8')) if t.exists() else {}
        return h==expected[ch] and receipt.get('channel')==ch
    before=hashes(home);code,data,err=call()
    record('missing channel rejects without changing user area',code!=0 and hashes(home)==before,data)
    code,data,err=call('stable');record('fresh Stable install has only Stable payload',code==0 and installed('stable'),(data,err))
    first=hashes(target);code,data,err=call('stable');record('Stable repeat is no-op',code==0 and data.get('action')=='already_current' and hashes(target)==first,data)
    state=(area/'installer-state.json').read_bytes();code,data,err=call('stable','Check')
    record('matching check is read-only and channel-aware',code==0 and data.get('matches_bundle') and data.get('installed_channel')=='stable' and hashes(target)==first and (area/'installer-state.json').read_bytes()==state,data)
    code,data,err=call('STABLE','Check');record('case-insensitive Stable parameter uses canonical channel',code==0 and data.get('channel')=='stable' and data.get('matches_bundle') and hashes(target)==first,data)
    code,data,err=call('beta','Check');record('same version opposite channel is not reported current',code==0 and data.get('status')=='channel_change' and not data.get('matches_bundle') and hashes(target)==first,data)
    code,data,err=call('beta');record('Stable to Beta preserves complete old directory',code==0 and installed('beta') and hashes(Path(data['backup']))==first,data)
    second=hashes(target);code,data,err=call('beta');record('Beta repeat is no-op',code==0 and hashes(target)==second,data)
    code,data,err=call('Beta');record('case-insensitive Beta parameter remains a no-op',code==0 and data.get('channel')=='beta' and data.get('action')=='already_current' and hashes(target)==second,data)
    code,data,err=call('stable');record('Beta to Stable removes obsolete active payload via full backup',code==0 and installed('stable') and hashes(Path(data['backup']))==second,data)
    record('personal preferences and plugin knowledge preserved',all(hashes(area).get(p)==h for p,h in personal.items()))
    (target/'SKILL.md').write_text((target/'SKILL.md').read_text('utf-8')+'\nLOCAL EDIT\n','utf-8');edited=hashes(target)
    code,data,err=call('beta');record('modified installed content blocks unattended switch',code!=0 and hashes(target)==edited,data)
    code,data,err=call('beta','Install',bundle,home,'-ReplaceModified');record('explicit replacement retains edited original',code==0 and installed('beta') and hashes(Path(data['backup']))==edited,data)
    good=hashes(target);bad=scratch/'bad-bundle';shutil.copytree(bundle,bad)
    p=bad/'channels/beta/skills/letsgal-authoring/SKILL.md';p.write_text('Corrupted selected payload','utf-8')
    code,data,err=call('beta',src=bad);record('tampered selected payload rejects before overwrite',code!=0 and hashes(target)==good,data)
    d=json.loads((bad/'bundle.json').read_text('utf-8'));d['channels'][1]['bundle']='../outside/bundle.json';(bad/'bundle.json').write_text(json.dumps(d),'utf-8')
    code,data,err=call('beta',src=bad);record('channel manifest traversal rejected',code!=0 and hashes(target)==good,data)
    d=json.loads((bundle/'bundle.json').read_text('utf-8'));(bad/'bundle.json').write_text(json.dumps(d),'utf-8')
    d=json.loads((bad/'channels/beta/bundle.json').read_text('utf-8'));d['channel']='stable';(bad/'channels/beta/bundle.json').write_text(json.dumps(d),'utf-8')
    code,data,err=call('beta',src=bad);record('channel manifest mismatch rejected',code!=0 and hashes(target)==good,data)
    saved=json.loads((area/'installer-state.json').read_text('utf-8'));record('saved installation choice includes selected channel',saved.get('Channel')=='beta')
    code,data,err=call('beta','Uninstall');record('uninstall retains last payload and personal data',code==0 and not target.exists() and hashes(Path(data['backup']))==good and all(hashes(area).get(p)==h for p,h in personal.items()),data)
    if previous:
        oldhome=scratch/'old-combined-home';oldhome.mkdir();code,data,err=call(src=previous,user=oldhome)
        oldtarget=oldhome/'.agents/skills/letsgal-authoring';old=hashes(oldtarget)
        record('old combined fixture installed through its original installer',code==0 and bool(old),data)
        code,data,err=call('beta',user=oldhome);record('old combined to selected Beta backs up original',code==0 and installed('beta',oldtarget) and hashes(Path(data['backup']))==old,data)
    for ch,correct,wrong in [('stable','2.5.0','2.6.0-beta.1'),('beta','2.6.0-beta.1','2.5.0')]:
        inspector=bundle/f'channels/{ch}/skills/letsgal-authoring/scripts/inspect_version.py'
        for version,want in [(correct,0),(wrong,2)]:
            p=subprocess.run([sys.executable,'-B',str(inspector),'--studio-version',version],capture_output=True)
            d=json.loads(p.stdout.decode('utf-8'));record(ch+' host '+version,p.returncode==want and d.get('skill_channel')==ch and d.get('read_only') is True,d)
    return {'status':'passed','checks':len(results),'scope':'isolated CLI installation and channel routing; no Studio or live Agent acceptance','results':results}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--scratch',type=Path,required=True);p.add_argument('--previous',type=Path);args=p.parse_args()
    print(json.dumps(run(args.bundle,args.scratch,args.previous),ensure_ascii=False,indent=2))
