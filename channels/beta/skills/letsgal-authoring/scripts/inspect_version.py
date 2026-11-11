"""Read-only Studio evidence and reference selection. Python 3.9+, standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from check_project import safe_path

VERSION = re.compile(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?')
SKILL_CHANNEL = 'beta'
PROFILES = {'2.8.0-beta.1': 'references/current-capabilities.md', '2.9.0-beta.1': 'references/current-capabilities.md'}
# Maintainer-observed identity, not a claim that every operation was retested.
HOST_BASELINES = {'2.8.0-beta.1': {'patch_id': None}, '2.9.0-beta.1': {'patch_id': None}}
GATE_REVISION = '20261111-stable300'
SDK_FILES = ('constants.ts','index.ts','sdk-context.ts','extension-module.ts','extension-method.ts',
             'save-schema.ts','schedule-strategy.ts','internal-system-slots.ts')

def parse_version(value):
    match = VERSION.fullmatch(value or '')
    if not match:
        raise ValueError('Expected full semantic version, including any prerelease suffix')
    prerelease = match.group(4)
    if prerelease and any(p.isdigit() and len(p)>1 and p[0]=='0' for p in prerelease.split('.')):
        raise ValueError('Numeric prerelease identifiers cannot have leading zeros')
    channel = 'stable' if not prerelease else ('beta' if prerelease.split('.')[0]=='beta' else 'UNKNOWN')
    return value.split('+',1)[0], channel

def file_version(exe):
    path = safe_path(Path(exe))
    if not path.is_file() or os.name!='nt':
        raise ValueError('Reading EXE FileVersion requires Windows and a regular existing file')
    env = dict(os.environ, LETSGAL_INSPECT_EXE=str(path))
    command = "[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); (Get-Item -LiteralPath $env:LETSGAL_INSPECT_EXE).VersionInfo.FileVersion"
    result = subprocess.run(['powershell.exe','-NoLogo','-NoProfile','-NonInteractive','-Command',command],
                            env=env, capture_output=True, timeout=15)
    if result.returncode:
        raise ValueError('Could not read EXE FileVersion; no version inferred from filename')
    return result.stdout.decode('utf-8-sig').strip()

def patch_evidence(patch_id=None, patch_sha256=None, renderer_patch=None):
    base = None
    source = 'supplied-current-host' if patch_id else 'UNKNOWN'
    if renderer_patch:
        path = safe_path(Path(renderer_patch))
        if not path.is_file() or path.stat().st_size > 65536:
            raise ValueError('Renderer marker must be a regular JSON file no larger than 64 KiB')
        data = json.loads(path.read_text('utf-8-sig'))
        if not isinstance(data, dict): raise ValueError('Expected renderer marker object')
        base = data.get('baseVersion')
        if not isinstance(base, str): raise ValueError('Renderer base version must be text')
        parse_version(base)
        ch, rev = data.get('channel'), data.get('rev')
        if ch not in ('stable','beta') or type(rev) is not int or rev < 1:
            raise ValueError('Invalid renderer marker channel or revision')
        detected = f'{base}-{ch}-r{rev}'
        if patch_id and patch_id != detected:
            raise ValueError('Reported patch conflicts with installed renderer marker')
        if patch_sha256 and patch_sha256.lower() != str(data.get('sha256','')).lower():
            raise ValueError('Reported patch hash conflicts with installed renderer marker')
        patch_id, patch_sha256 = detected, data.get('sha256')
        source = 'installed-marker; confirm it belongs to the target instance'
    if patch_id is not None and not re.fullmatch(r'[0-9A-Za-z.+_-]{1,160}', patch_id):
        raise ValueError('Invalid patch identifier')
    if patch_sha256 is not None and (not isinstance(patch_sha256,str) or not re.fullmatch(r'[0-9a-fA-F]{64}', patch_sha256)):
        raise ValueError('Invalid patch SHA256')
    return {'id':patch_id or 'UNKNOWN','sha256':patch_sha256.lower() if patch_sha256 else 'UNKNOWN',
            'base_version':base,'source':source}

def operation_gate(actual, project_version, declared_channel, issues, patch):
    baseline = HOST_BASELINES.get(actual)
    reasons = list(issues)
    identity_missing = not actual or any('conflicts with EXE' in x or 'Declared channel conflicts' in x for x in issues)
    if patch['base_version'] and patch['base_version'] != actual:
        identity_missing = True
        reasons.append('Renderer marker base version differs from the target host')
    if not baseline:
        reasons.append('Full host version is not in this payload maintained baseline')
    elif not baseline.get('patch_id'):
        reasons.append('Historical baseline has no recorded renderer identity; confirm the unverified patch scope once')
    elif patch['id'] == 'UNKNOWN':
        reasons.append('Renderer identity is unavailable; identify it or request one scoped confirmation')
    elif patch['id'] != baseline['patch_id']:
        reasons.append('Renderer identity differs from the maintained baseline')
    elif patch['sha256'] != 'UNKNOWN' and baseline.get('patch_sha256') and patch['sha256'] != baseline['patch_sha256']:
        reasons.append('Renderer hash differs despite an identical patch identifier')
    state = 'identity_required' if identity_missing else 'confirmation_required' if reasons else 'matched'
    # A comparison fingerprint only. No approval, network polling or persistent cache.
    identity = [SKILL_CHANNEL,GATE_REVISION,actual,project_version,declared_channel,patch['id'],patch['sha256']]
    return {'state':state,'decision':'continue' if state=='matched' else 'pause_engine_operations',
            'reasons':reasons,'maintained_hosts':HOST_BASELINES,'patch':patch,
            'fingerprint':hashlib.sha256(json.dumps(identity,separators=(',',':')).encode()).hexdigest(),
            'approval':'not_granted_by_script','cache':'reuse in current task for same target instance and project; invalidate on identity or scope change',
            'allowed_while_paused':['discussion','drafts','read-only identification and contract inspection']}

def inspect(studio_version=None, project_version=None, channel='auto', studio_exe=None, sdk=None,
            update_channel=None, patch_id=None, patch_sha256=None, renderer_patch=None):
    issues = []
    actual = studio_version
    basis = 'supplied-host-evidence' if actual else 'UNKNOWN'
    if studio_exe:
        detected = file_version(studio_exe)
        basis = 'exe-file-version'
        if actual and actual!=detected:
            issues.append('Supplied host version conflicts with EXE FileVersion')
        actual = detected
    profile, inferred = None, 'UNKNOWN'
    if actual:
        normalized, inferred = parse_version(actual)
        profile = PROFILES.get(normalized)
        if inferred == SKILL_CHANNEL and not profile:
            issues.append('Host is outside this channel maintained target; pause engine operations pending scoped user confirmation')
        if inferred != SKILL_CHANNEL:
            issues.append('Installed Skill channel differs from host; select the matching installer channel')
    else:
        issues.append('Actual host version is missing; project pin alone is not host evidence')
    if project_version:
        parse_version(project_version)
        if actual and project_version!=actual:
            issues.append('Project version conflicts with actual host version')
    if channel!='auto' and channel!=inferred:
        issues.append('Declared channel conflicts with full host version')
    sdk_report = {'status':'UNKNOWN','files':{},'declared_version':'UNKNOWN',
                  'provenance':'UNKNOWN','api_compatibility':'not_verified',
                  'declared_version_is_host_version':False}
    if sdk:
        sdk_root = safe_path(Path(sdk))
        if not sdk_root.is_dir():
            raise ValueError('SDK path must be an existing directory')
        for name in SDK_FILES:
            path = sdk_root/name
            if path.exists():
                path = safe_path(path)
                if not path.is_file(): raise ValueError('SDK entry must be a regular file')
                sdk_report['files'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
        sdk_report['status']='fingerprinted' if 'index.ts' in sdk_report['files'] else 'UNKNOWN'
        if 'constants.ts' in sdk_report['files']:
            match = re.search(r'\bSDK_VERSION\s*=\s*[\"\']([^\"\'\r\n]+)[\"\']',
                              (sdk_root/'constants.ts').read_text('utf-8-sig'))
            if match: sdk_report['declared_version'] = match.group(1)
    if issues or inferred=='UNKNOWN':
        profile = None
    status = 'reference_selected' if profile else 'UNKNOWN'
    patch = patch_evidence(patch_id, patch_sha256, renderer_patch)
    gate = operation_gate(actual, project_version, channel, issues, patch)
    return {'skill_channel':SKILL_CHANNEL,'status':status,'studio_version':actual or 'UNKNOWN','project_version':project_version or 'UNKNOWN',
            'channel':inferred if not issues else 'UNKNOWN','evidence':basis,
            'reference':profile or 'references/version-compatibility.md','issues':issues,
            'sdk':sdk_report,'read_only':True,'runtime_compatibility':'not_verified',
            'update_channel':update_channel or 'UNKNOWN','operation_gate':gate,
            'version_dependent_writes':('require-target-sample-and-task-api-evidence' if gate['state']=='matched' else 'pause-until-identity-or-scoped-user-confirmation'),
            'scope':'Reference selection only. No installation, migration, SDK update or engine launch.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--studio-version')
    parser.add_argument('--studio-exe',type=Path)
    parser.add_argument('--project-version')
    parser.add_argument('--channel',choices=['auto','stable','beta'],default='auto')
    parser.add_argument('--sdk',type=Path)
    parser.add_argument('--update-channel',choices=['stable','beta','special'],help='Update-feed preference only, not the installed host release channel')
    parser.add_argument('--patch-id',help='Current target renderer patch identifier, not the latest online patch')
    parser.add_argument('--patch-sha256')
    parser.add_argument('--renderer-patch',type=Path,help='Known target local renderer-patch/current.json; never inferred for remote MCP')
    parser.add_argument('--gate',action='store_true',help='Exit 0 only for a matched operation gate; otherwise 2')
    args=parser.parse_args()
    gate_mode = vars(args).pop('gate')
    try:
        result=inspect(**vars(args))
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        result={'status':'UNKNOWN','channel':'UNKNOWN','reference':'references/version-compatibility.md',
                'error':str(exc),'read_only':True,'runtime_compatibility':'not_verified',
                'operation_gate':{'state':'identity_required','decision':'pause_engine_operations','approval':'not_granted_by_script'}}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if (result.get('operation_gate',{}).get('state')=='matched' if gate_mode else result['status']=='reference_selected') else 2

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
