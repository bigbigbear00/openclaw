#!/usr/bin/env python3
"""
Minimal QA artifact checker
- Checks artifact file for placeholder patterns and basic JSON validity
- Writes QA result to <request_id>-qa.json in same artifacts dir
"""
import sys, json, re
from pathlib import Path

if len(sys.argv)<2:
    print('Usage: qa_artifact.py /path/to/artifact')
    sys.exit(2)

p=Path(sys.argv[1])
if not p.exists():
    print('MISSING')
    sys.exit(3)
text=p.read_text(encoding='utf-8')
qa={'request_id': p.stem.split('-')[0], 'artifact': str(p), 'checked_at': None, 'result': None, 'notes': []}
from datetime import datetime
qa['checked_at']=datetime.now().isoformat()
# detect placeholder
if re.search(r'Artifact for', text) or re.search(r'placeholder', text, re.I):
    qa['result']='FAILED_QA_PLACEHOLDER'
    qa['notes'].append('placeholder text found')
else:
    # attempt JSON parse
    try:
        json.loads(text)
        qa['result']='PASS'
    except Exception:
        # if not json, but non-placeholder, still accept as PASS but note non-json
        qa['result']='PASS'
        qa['notes'].append('non-json artifact but no placeholder detected')
# write qa file
qa_path=p.parent/ (qa['request_id'] + '-qa.json') if False else p.parent.joinpath(qa['request_id'] + '-qa.json')
with open(qa_path,'w',encoding='utf-8') as f:
    json.dump(qa,f,ensure_ascii=False,indent=2)
print('WROTE',qa_path)
print('RESULT',qa['result'])
