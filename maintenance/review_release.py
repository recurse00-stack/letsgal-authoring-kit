"""Audit only the explicitly selected publication files; never print matched private values."""
import argparse
import ast
import json
import os
from pathlib import Path
import re
from release_manifest import release_files

PATTERNS={
    'absolute-windows-path':r'(?<![A-Za-z0-9])[A-Za-z]:[\\/](?!/)',
    'personal-home-path':r'/(?:home|Users)/[A-Za-z0-9_.-]+/',
    'private-key':r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'github-token':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b',
    'api-token':r'\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b',
    'email-address':r'\b[A-Za-z0-9._%+-]+@(?!users\.noreply\.github\.com\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'credential-url':r'https?://[^\s/:]+:[^\s/@]+@',
}

def inspect_text(text, deny_values=()):
    hits=[name for name,pattern in PATTERNS.items() if re.search(pattern,text)]
    for value in deny_values:
        if value and re.search(r'(?<![\w])'+re.escape(value)+r'(?![\w])',text,re.I):
            hits.append('local-identity-marker')
            break
    return hits

def audit(root, deny_values=()):
    files=release_files(root)
    findings=[]
    for file in files:
        name=file.relative_to(root).as_posix()
        try:
            value=file.read_text('utf-8-sig')
        except UnicodeDecodeError:
            findings.append({'file':name,'rule':'unreviewed-binary'})
            continue
        for hit in inspect_text(value,deny_values):
            findings.append({'file':name,'rule':hit})
        if file.suffix=='.py':
            try: ast.parse(value,filename=name)
            except SyntaxError: findings.append({'file':name,'rule':'python-syntax'})
    return {'status':'passed' if not findings else 'review_required','files_checked':len(files),
            'findings':findings,'scope':'Selected source and documentation text. No screenshots, logs, personal configuration or workspace history selected.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deny-value',action='append',default=[])
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    result=audit(root,[os.environ.get('USERNAME',''),*args.deny_value])
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status']=='passed' else 1

if __name__=='__main__':
    raise SystemExit(main())
