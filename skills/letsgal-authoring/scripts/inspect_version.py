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
PROFILES = {'2.0.0':'references/versions/stable-2.0.md',
            '2.0.1':'references/versions/stable-2.0.md',
            '2.5.0':'references/versions/stable-2.5.md',
            '2.3.0-beta.1':'references/versions/beta-2.3.md',
            '2.4.0-beta.1':'references/versions/beta-2.4.md',
            '2.4.0-beta.2':'references/versions/beta-2.4.md',
            '2.5.0-beta.1':'references/versions/beta-2.5.md'}
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

def inspect(studio_version=None, project_version=None, channel='auto', studio_exe=None, sdk=None):
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
    return {'status':status,'studio_version':actual or 'UNKNOWN','project_version':project_version or 'UNKNOWN',
            'channel':inferred if not issues else 'UNKNOWN','evidence':basis,
            'reference':profile or 'references/version-compatibility.md','issues':issues,
            'sdk':sdk_report,'read_only':True,'runtime_compatibility':'not_verified',
            'version_dependent_writes':'require-target-sample-and-task-api-evidence',
            'scope':'Reference selection only. No installation, migration, SDK update or engine launch.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--studio-version')
    parser.add_argument('--studio-exe',type=Path)
    parser.add_argument('--project-version')
    parser.add_argument('--channel',choices=['auto','stable','beta'],default='auto')
    parser.add_argument('--sdk',type=Path)
    args=parser.parse_args()
    try:
        result=inspect(**vars(args))
    except (OSError,ValueError,subprocess.SubprocessError) as exc:
        result={'status':'UNKNOWN','channel':'UNKNOWN','reference':'references/version-compatibility.md',
                'error':str(exc),'read_only':True,'runtime_compatibility':'not_verified'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='reference_selected' else 2

if __name__=='__main__':
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
