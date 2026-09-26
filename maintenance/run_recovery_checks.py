"""Exercise backup restoration and interrupted-install leftovers in a NEW isolated home."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', required=True, type=Path)
    args = parser.parse_args()
    root = args.scratch
    if not root.is_absolute() or root.exists():
        parser.error('Use a NEW absolute scratch directory')
    root.mkdir(parents=True)
    bundle = Path(__file__).resolve().parents[1]
    home = root / 'home'; home.mkdir()
    results = []
    def record(name, ok):
        results.append({'name': name, 'passed': bool(ok)})
        if not ok:
            raise AssertionError(name)
    def invoke(action):
        proc = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(bundle/'Install.ps1'), '-Action', action, '-Harness', 'Codex', '-Scope', 'User', '-UserHome', str(home), '-NonInteractive'], capture_output=True)
        text = proc.stdout.decode('utf-8', errors='replace')
        rows = [json.loads(line) for line in text.splitlines() if line.startswith('{')]
        if not rows:
            # Windows PowerShell may use the platform console encoding for redirected text.
            text = proc.stdout.decode('mbcs', errors='replace')
            rows = [json.loads(line) for line in text.splitlines() if line.startswith('{')]
        return proc.returncode, rows[-1]
    code, receipt = invoke('Install'); record('initial install', code == 0)
    target = Path(receipt['target']); before = snapshot(target)
    area = home/'.letsgal-authoring'
    profile = area/'preferences/user.md'; profile.write_text('Personal recovery note.\n', 'utf-8')
    plugin = area/'plugins/fixture/1.0.0/SKILL.md'; plugin.parent.mkdir(parents=True); plugin.write_text('User plugin knowledge.\n', 'utf-8')
    user_before = snapshot(area)
    code, removed = invoke('Uninstall')
    backup = Path(removed['backup'])
    record('uninstall keeps complete recoverable backup', code == 0 and not target.exists() and snapshot(backup) == before)
    record('uninstall preserves entire user area', snapshot(area) == user_before)
    shutil.copytree(backup, target)
    code, checked = invoke('Check')
    record('restored backup passes installer verification', code == 0 and checked['action'] == 'check' and snapshot(target) == before)
    record('restoration retains original backup', snapshot(backup) == before)
    # Model an interrupted attempt before target publication without killing an unrelated process.
    orphan = backup.parent/'fixture-interrupted-staging'; orphan.mkdir()
    (orphan/'partial.bin').write_bytes(b'incomplete staging bytes\x00\xff')
    orphan_before = snapshot(orphan)
    code, installed = invoke('Install')
    record('leftover staging does not overwrite valid target', code == 0 and snapshot(target) == before)
    record('leftover staging remains available for inspection', snapshot(orphan) == orphan_before)
    user_after = snapshot(area)
    record('reinstall retains preferences and plugin bytes', all(user_after.get(k) == v for k,v in user_before.items() if k != 'installer-state.json'))
    report = {'checks': results, 'passed': len(results), 'failed': 0,
              'scope': 'Real install, uninstall and backup copy restoration; interrupted staging is simulated, not an OS power-loss test.'}
    (root/'results.json').write_text(json.dumps(report, indent=2), 'utf-8')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
