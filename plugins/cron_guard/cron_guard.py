#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

ROOT = Path('/Users/apple/clawd')
REG = ROOT / 'cron_logs' / 'job_registry.json'
LOGS_DIR = ROOT / 'cron_logs'
OUT_DIR = ROOT / 'reports'
OUT_DIR.mkdir(exist_ok=True)

def load_registry():
    return json.loads(REG.read_text(encoding='utf-8'))


def scan(reg):
    now = datetime.now().isoformat()
    findings = []
    for section, jobs in reg.get('jobs', {}).items():
        for j in jobs:
            jid = j.get('id') or j.get('job_id')
            name = j.get('name') or j.get('title')
            owner = j.get('owner')
            # check presence in logs
            found = False
            for p in LOGS_DIR.glob('*.jsonl'):
                for line in p.read_text(encoding='utf-8').splitlines():
                    if jid and jid in line:
                        found = True
                        break
                if found:
                    break
            if not found:
                findings.append((jid, name, section, owner, 'no recent done log'))
    return findings


def generate_report(findings):
    ts = datetime.now().strftime('%Y%m%dT%H%M%S')
    out = OUT_DIR / f'cron_guard_{ts}.md'
    with out.open('w', encoding='utf-8') as f:
        f.write('# cron_guard dry-run report\n')
        f.write(f'Generated: {datetime.now().isoformat()}\n\n')
        if not findings:
            f.write('No missing jobs detected in registry scan.\n')
            return out
        f.write('## Findings (jobs with no recent done logs)\n\n')
        f.write('| job_id | name | section | owner | issue |\n')
        f.write('|---|---|---|---|---|\n')
        for jid, name, section, owner, issue in findings:
            f.write(f'| {jid} | {name} | {section} | {owner} | {issue} |\n')
    return out


def main():
    reg = load_registry()
    findings = scan(reg)
    report = generate_report(findings)
    print('Dry-run complete. Report written to', report)

if __name__ == '__main__':
    main()
