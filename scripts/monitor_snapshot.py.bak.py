#!/usr/bin/env python3
"""
Monitor snapshot: captures pm2 status, top topics_state entries, recent QA failures into a small report
Writes to /Users/apple/clawd/reports/monitor_snapshot_YYYY-MM-DDTHHMMSS.md
"""
import subprocess, json
from pathlib import Path
from datetime import datetime
BASE=Path('/Users/apple/clawd')
OUT_DIR=BASE/'reports'
OUT_DIR.mkdir(parents=True,exist_ok=True)
now=datetime.utcnow().strftime('%Y-%m-%dT%H%M%SZ')
out=OUT_DIR/f'monitor_snapshot_{now}.md'
# pm2 status
try:
    pm2 = subprocess.check_output(['pm2','status','--no-color']).decode('utf-8')
except Exception as e:
    pm2 = f'pm2 not available or error: {e}'
# topics_state tail
ts=BASE/'metrics'/'topics_state.jsonl'
topics='(none)'
if ts.exists():
    lines=ts.read_text(encoding='utf-8').splitlines()
    topics='\n'.join(lines[-10:])
# qa failures
qa_fail=[]
for p in list((BASE/'claw_comm').glob('*/artifacts/*-qa.json')):
    try:
        q=json.load(open(p,'r',encoding='utf-8'))
        if q.get('result','')!='PASS':
            qa_fail.append(str(p))
    except:
        continue
with open(out,'w',encoding='utf-8') as f:
    f.write('# Monitor snapshot\n')
    f.write('Generated at: '+now+'\n\n')
    f.write('## pm2 status\n')
    f.write('''```
'''+pm2+'''\n```
''')
    f.write('## Recent topics_state entries\n')
    f.write('''```
'''+topics+'''\n```
''')
    f.write('## QA failures (artifacts)\n')
    if qa_fail:
        for a in qa_fail:
            f.write('- '+a+'\n')
    else:
        f.write('- None\n')
print('Wrote',out)
