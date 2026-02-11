#!/usr/bin/env python3
"""
USD gating enforcer
- Reads metrics/topic_costs.jsonl and topics_state.jsonl
- If a topic has pricing_status=='exact' and estimated_cost_usd > THRESHOLD_USD -> mark topic in topics_state.jsonl as USD_GATE_BLOCKED and send Telegram notification
- Default threshold: 100 USD (configurable via env var THRESHOLD_USD)
- Writes an audit entry to /Users/apple/clawd/metrics/usd_gating_audit.jsonl
"""
import os, json
from pathlib import Path
from datetime import datetime

def load_jsonl(path):
    out=[]
    if not path.exists():
        return out
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            out.append(json.loads(line))
        except:
            continue
    return out

BASE=Path('/Users/apple/clawd')
COSTS=BASE/'metrics'/'topic_costs.jsonl'
TOPICS=BASE/'metrics'/'topics_state.jsonl'
AUDIT=BASE/'metrics'/'usd_gating_audit.jsonl'
THRESH=float(os.getenv('THRESHOLD_USD','100'))

costs=load_jsonl(COSTS)
# build map by topic id
cost_map={}
for c in costs:
    tid=c.get('id') or c.get('topic_id')
    if not tid: continue
    cost_map[tid]=c

# load topics
topics=load_jsonl(TOPICS)
updated=[]
for t in topics:
    tid=t.get('id')
    if not tid: continue
    c=cost_map.get(tid)
    if not c: continue
    ps=c.get('pricing_status')
    est=float(c.get('cost_usd_external') or c.get('estimated_cost_usd') or 0)
    if ps=='exact' and est>THRESH:
        # block
        t['status']='USD_GATE_BLOCKED'
        t['usd_gate']=True
        t['usd_estimated']=est
        # write audit
        audit={'id':tid,'timestamp':datetime.now().isoformat(),'action':'USD_GATE_BLOCK','estimated_usd':est,'threshold':THRESH,'pricing_status':ps}
        with open(AUDIT,'a',encoding='utf-8') as f:
            f.write(json.dumps(audit,ensure_ascii=False)+'\n')
        updated.append((t,audit))
# rewrite topics_state.jsonl fully (append new entries for changes)
with open(TOPICS,'a',encoding='utf-8') as f:
    for t,audit in updated:
        f.write(json.dumps(t,ensure_ascii=False)+'\n')

# send notifications
from functions import message
for t,audit in updated:
    txt=f"USD_GATE: topic {t.get('id')} agent={t.get('agent')} est_usd={audit['estimated_usd']:.2f} threshold={audit['threshold']}. Status set to USD_GATE_BLOCKED."
    try:
        message({"action":"send","channel":"telegram","to":"8555612162","message":txt})
    except Exception:
        pass

print('USD gating enforcement complete. Updated topics:', len(updated))
