#!/usr/bin/env python3
"""
Minimal writer editor handler (updated)
Usage: writer_editor.py <request_id> <artifacts_dir> <output_report_path>
- Reads boxscore.json from artifacts_dir/<request_id>-boxscore.json
- If missing, writes BLOCKED_WAITING_DEP to inbox (handled by caller)
- Else, validates that each claim has source_url; if any missing -> BLOCKED_REQUIRE_SOURCES
- Else, composes final markdown report and writes to output path
"""
import sys, json
from pathlib import Path
from datetime import datetime

if len(sys.argv)<4:
    print('Usage: writer_editor.py <request_id> <artifacts_dir> <output_report_path>')
    sys.exit(2)
req_id=sys.argv[1]
art_dir=Path(sys.argv[2])
out_path=Path(sys.argv[3])
boxfile=art_dir/(req_id+'-boxscore.json')
if not boxfile.exists():
    # signal blocked (print sentinel)
    print('BLOCKED_WAITING_DEP',str(boxfile))
    sys.exit(3)
with open(boxfile,'r',encoding='utf-8') as f:
    box=json.load(f)
# validate sources: each entry must have boxscore_url
missing_sources=[]
for g in box:
    if not g.get('boxscore_url'):
        missing_sources.append(g.get('game','unknown'))
if missing_sources:
    # write a blocked code
    print('BLOCKED_REQUIRE_SOURCES', missing_sources)
    sys.exit(4)
# compose final report
lines=[]
lines.append('# PILOT TOPIC: NBA 報告 (2026-02-08)')
lines.append('\n## 要点')
for i,g in enumerate(box[:5],start=1):
    lines.append(f'{i}. {g.get("game")} — {g.get("score")} (source: {g.get("boxscore_url")})')
lines.append('\n## 详细')
for g in box:
    lines.append(f'### {g.get("game")} — {g.get("score")}')
    for p in g.get('top_players',[]):
        lines.append(f'- {p.get("name")} {p.get("pts")}/{p.get("reb")}/{p.get("ast")}')
    lines.append(f'来源: {g.get("boxscore_url")}')
    lines.append('')
lines.append('## verification_summary')
lines.append('- All claims have at least one source URL and have been minimally verified by boxscore presence.')
lines.append('\n## sources')
for g in box:
    lines.append('- '+g.get('boxscore_url'))
out_path.parent.mkdir(parents=True,exist_ok=True)
with open(out_path,'w',encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('WROTE',out_path)
