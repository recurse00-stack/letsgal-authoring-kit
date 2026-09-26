"""Verify real notice delivery and receipts in isolated homes, without inferring consent."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scratch', type=Path, required=True)
    args = parser.parse_args()
    scratch = args.scratch
    if not scratch.is_absolute():
        raise SystemExit('Use a NEW absolute scratch directory.')
    scratch.mkdir(parents=True, exist_ok=False)
    kit = Path(__file__).resolve().parents[1]
    relative = Path('skills/letsgal-authoring/references/risk-notice.md')
    notice = kit / relative
    checks = []

    def record(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})

    def run(shell, bundle, home, action='Install'):
        command = '[Console]::OutputEncoding = New-Object Text.UTF8Encoding($false); & ' + "'" + str(bundle/'Install.ps1').replace("'", "''") + "'" + ' -Harness Codex -NonInteractive -Action ' + action + ' -UserHome ' + "'" + str(home).replace("'", "''") + "'"
        result = subprocess.run([shell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-Command', command], capture_output=True)
        stdout = result.stdout.decode('utf-8', errors='replace')
        report = next((json.loads(line) for line in reversed(stdout.splitlines()) if line.startswith('{')), {})
        return result, stdout, report

    for shell in ['powershell.exe', 'pwsh.exe']:
        label = Path(shell).stem
        home = scratch / label / "user's home 测试"
        home.mkdir(parents=True)
        user = home / '.letsgal-authoring'
        prefs = user / 'preferences/user.md'
        plugin = user / 'plugins/example.demo/1.0.0/SKILL.md'
        for path in [prefs, plugin]:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('User-owned sentinel\n', 'utf-8')
        protected = {p: digest(p) for p in [prefs, plugin]}
        result, stdout, report = run(shell, kit, home)
        if result.returncode:
            raise RuntimeError(label + ': installation failed before receipt: ' + stdout + result.stderr.decode('utf-8', errors='replace'))
        target = home / '.agents/skills/letsgal-authoring'
        record(label + ': install succeeds with notice delivered before target output', result.returncode == 0 and stdout.find('使用前请阅读') >= 0 and stdout.find('使用前请阅读') < stdout.find('目标：'))
        record(label + ': installed full notice retains exact bytes', (target/'references/risk-notice.md').exists() and digest(target/'references/risk-notice.md') == digest(notice))
        receipt = json.loads((target/'.install-receipt.json').read_text('utf-8'))
        metadata = receipt.get('risk_notice', {})
        record(label + ': receipt records notice hash and does not assert consent', metadata.get('sha256') == digest(notice) and metadata.get('acknowledgement') == 'not_collected' and metadata.get('channel') == 'installer_console')
        backup = home / '.agents/.letsgal-authoring-backups'
        logs = list(backup.glob('*-install.json'))
        record(label + ': operation log agrees with notice receipt', len(logs) == 1 and json.loads(logs[0].read_text('utf-8')).get('risk_notice') == metadata)
        result, stdout, report = run(shell, kit, home)
        record(label + ': repeat install still emits and reports current notice', result.returncode == 0 and report.get('action') == 'already_current' and report.get('risk_notice') == metadata and '使用前请阅读' in stdout)
        before = {p: digest(p) for p in home.rglob('*') if p.is_file()}
        result, stdout, report = run(shell, kit, home, 'Check')
        record(label + ': check delivers notice without changing any home files', result.returncode == 0 and '使用前请阅读' in stdout and before == {p:digest(p) for p in home.rglob('*') if p.is_file()})
        result, stdout, report = run(shell, kit, home, 'Uninstall')
        uninstall_logs = list(backup.glob('*-uninstall.json'))
        record(label + ': uninstall retains the full notice in backup and records its version', result.returncode == 0 and digest(Path(report['backup'])/'references/risk-notice.md') == digest(notice) and len(uninstall_logs) == 1 and json.loads(uninstall_logs[0].read_text('utf-8')).get('risk_notice') == metadata)
        record(label + ': preferences and plugin notes remain byte-identical', all(digest(p) == h for p,h in protected.items()))
        incomplete = scratch / label / 'incomplete-bundle'
        shutil.copytree(kit, incomplete)
        missing = incomplete / relative
        assert missing.resolve().is_relative_to(incomplete.resolve())
        missing.unlink()
        untouched = scratch / label / 'empty-home'
        untouched.mkdir()
        result, stdout, report = run(shell, incomplete, untouched)
        record(label + ': missing notice stops before creating any user files', result.returncode != 0 and not list(untouched.iterdir()))

    output = {'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'checks':checks,'scope':'Isolated CLI delivery, exact installed notice bytes, receipt provenance and preservation; no human consent or model-behavior claim.'}
    (scratch/'notice-results.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', 'utf-8')
    print(json.dumps(output, ensure_ascii=False, indent=2))
    raise SystemExit(bool(output['failed']))

if __name__ == '__main__':
    main()
