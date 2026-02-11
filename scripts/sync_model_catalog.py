#!/usr/bin/env python3
"""
Sync model catalog from OpenClaw runtime config (openclaw.json) to local catalog.json
Writes: /Users/apple/clawd/library/models/catalog.json
Backups previous catalog, generates diff summary and audit.
"""
import json
from pathlib import Path
from datetime import datetime
BASE=Path('/Users/apple/clawd')
OPENCLAW=Path('/Users/apple/.openclaw/openclaw.json')
OUT=BASE/'library'/'models'/'catalog.json'

conf=json.loads(OPENCLAW.read_text(encoding='utf-8'))
models=set()
for k in conf.get('agents',{}).get('defaults',{}).get('models',{}).keys():
    models.add(k)
for a in conf.get('agents',{}).get('list',[]):
    prim=a.get('model',{}).get('primary')
    if prim:
        models.add(prim)

out={'generated_at':datetime.now().isoformat(),'source':'openclaw.json','models':[]}
for m in sorted(models):
    provider=m.split('/')[0] if '/' in m else None
    out['models'].append({'id':m,'provider':provider})

OUT.parent.mkdir(parents=True,exist_ok=True)
# backup old
bak=None
if OUT.exists():
    ts=datetime.now().strftime('%Y%m%dT%H%M%S')
    bak=OUT.with_name('catalog.json.bak-'+ts)
    OUT.replace(bak)

# write new
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')

# diff summary
old_ids=set()
if bak and bak.exists():
    try:
        oldj=json.loads(bak.read_text(encoding='utf-8'))
        old_ids=set([m.get('id') for m in oldj.get('models',[])])
    except Exception:
        old_ids=set()
new_ids=set([m['id'] for m in out['models']])
added=sorted(list(new_ids - old_ids))
removed=sorted(list(old_ids - new_ids))

# write diff report
date=datetime.now().strftime('%Y-%m-%d')
rep=BASE/f'reports/catalog-sync-diff-{date}.md'
rep_content = (
    '# Catalog sync diff\n\n'
    f'generated_at: {datetime.now().isoformat()}\n\n'
    'Added:\n' + ('\n'.join(added) if added else 'None') + '\n\n'
    'Removed:\n' + ('\n'.join(removed) if removed else 'None') + '\n'
)
rep.write_text(rep_content,encoding='utf-8')

# write memory audit
mem=BASE/'memory'
memfile=mem.joinpath(date + '.md')
with open(memfile,'a',encoding='utf-8') as mf:
    mf.write('\nCatalog sync audit: '+datetime.now().isoformat()+"\n")
    mf.write('catalog_changed: '+str(bool(added or removed))+"\n")
    mf.write('added: '+json.dumps(added,ensure_ascii=False)+"\n")
    mf.write('removed: '+json.dumps(removed,ensure_ascii=False)+"\n")

print('sync complete, added:',len(added),'removed:',len(removed))
