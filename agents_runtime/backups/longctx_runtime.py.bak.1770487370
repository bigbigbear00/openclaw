#!/usr/bin/env python3
"""Runtime implementation for longctx guardrails (staging, simplified).
Provides handle_telegram_message(session, msg) which uses local sqlite memory and simulates model calls.
"""
import json
import sqlite3
from pathlib import Path
from math import floor

DB_PATH = Path('data/longctx_dev.sqlite')
CFG_PATH = Path('library/specs/longctx_openclaw_config.json')

cfg = json.loads(CFG_PATH.read_text())['longctx']

# simple token estimator
def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    cjk = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    if cjk > len(text) * 0.2:
        return max(1, len(text)//2)
    return max(1, len(text)//4)

# pick window turns from config
def pick_window_turns(ctx_limit: int):
    keys = sorted(int(k) for k in cfg['windowTurnsByCtx'].keys())
    chosen = 20
    for k in keys:
        if k <= ctx_limit:
            chosen = cfg['windowTurnsByCtx'][str(k)]
    return chosen

# simple memory retrieve (topK by id desc)
def retrieve_memory(project_id, capTokens=2000, chunkTargetTokens=300):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, type, content, created_at FROM memory_items WHERE project_id=? ORDER BY created_at DESC LIMIT 10", (project_id,))
    rows = cur.fetchall()
    conn.close()
    return [{'id': r[0], 'type': r[1], 'text': r[2]} for r in rows]

# summarization stub
def summarize_to_s2(messages, target_tokens=800):
    text = '\n'.join(m[1] for m in messages)
    approx_chars = target_tokens * 4
    return text[:approx_chars]

# enforceBudget
def enforce_budget(ctx_pieces, budget, longctx):
    # ctx_pieces: dict with keys system,user,s1,window,rag
    # deterministic removal as described
    total = sum(estimate_tokens(v) for v in ctx_pieces.values())
    # ensure system, user, s1 remain
    if total <= budget:
        return ctx_pieces
    # drop lowest rag first
    if ctx_pieces.get('rag'):
        ctx_pieces['rag'] = []
        total = sum(estimate_tokens(v if isinstance(v,str) else json.dumps(v)) for v in ctx_pieces.values())
    # drop oldest window items
    while total > budget and ctx_pieces.get('window'):
        if len(ctx_pieces['window']) == 0:
            break
        ctx_pieces['window'].pop(0)
        total = sum(estimate_tokens(v if isinstance(v,str) else json.dumps(v)) for v in ctx_pieces.values())
    # final truncate s1 if still over
    if total > budget and ctx_pieces.get('s1'):
        s1 = ctx_pieces['s1']
        # truncate
        max_chars = max(100, (budget // 2) * 2)
        ctx_pieces['s1'] = s1[:max_chars]
    return ctx_pieces

# simulate model call
def call_model(model, ctx_text):
    # stub: return echo reply
    return 'ACK: ' + (ctx_text[:200].replace('\n',' '))

# append to session history (DB optional)
def append_to_session_history(session, msg, reply):
    # store in local sqlite as chat_turns? for now just print
    print('Persisted turn', msg['id'])

# main handler
def handle_telegram_message(session, msg):
    model = 'openai/gpt-5-mini'
    ctx_limit = 400000
    reserve = max(cfg['reserveMinTokens'], floor(ctx_limit * cfg['reserveRatio']))
    budget = ctx_limit - reserve

    session['project_id'] = session.get('project_id') or f"tg:{msg['chat_id']}"
    if not session.get('session_summary'):
        session['session_summary'] = 'S1: initialized.'

    window_turns = pick_window_turns(ctx_limit)
    window_msgs = session.get('history', [])[-window_turns:]

    rag = retrieve_memory(session['project_id'], capTokens=cfg['ragCapTokens'], chunkTargetTokens=cfg['chunkTargetTokens'])

    ctx_pieces = {
        'system': 'system prompt',
        'user': msg['text'],
        's1': session['session_summary'],
        'window': [m[1] for m in window_msgs],
        'rag': [r['text'] for r in rag]
    }

    est = sum(estimate_tokens(x if isinstance(x,str) else json.dumps(x)) for x in ctx_pieces.values())
    compaction_flag = False
    if est > budget * cfg['yellowRatio']:
        # shrink window
        window_msgs = window_msgs[-(window_turns//2):]
        ctx_pieces['window'] = [m[1] for m in window_msgs]
        est = sum(estimate_tokens(x if isinstance(x,str) else json.dumps(x)) for x in ctx_pieces.values())
    if est > budget * cfg['redRatio']:
        compaction_flag = True
        evict = session.get('history', [])[:len(session.get('history',[]))//2]
        if evict:
            s2 = summarize_to_s2(evict, target_tokens=cfg['s2TargetTokens'])
            # insert to memory_items
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO memory_items(project_id, session_id, type, topic, source_from_msg_id, source_to_msg_id, content, meta) VALUES(?,?,?,?,?,?,?,?)",
                (session['project_id'], session.get('id'), 'summary', None, evict[0][0], evict[-1][0], s2, json.dumps({'auto':True}))
            )
            conn.commit()
            conn.close()
            session['session_summary'] = (session['session_summary'] + '\n' + s2)[:cfg['s1TargetTokens']*4]
            session['summary_cursor_msg_id'] = evict[-1][0]
            session['history'] = session.get('history',[])[len(evict):]
            # rebuild
            window_msgs = session.get('history', [])[-window_turns:]
            ctx_pieces['window'] = [m[1] for m in window_msgs]
            ctx_pieces['rag'] = [r['text'] for r in retrieve_memory(session['project_id'])]
            ctx_pieces = enforce_budget(ctx_pieces, budget, cfg)
    else:
        ctx_pieces = enforce_budget(ctx_pieces, budget, cfg)

    ctx_text = '\n'.join([ctx_pieces['system'], ctx_pieces['s1'], ctx_pieces['user']] + ctx_pieces['window'][:5])
    reply = call_model(model, ctx_text)
    append_to_session_history(session, msg, reply)
    # write audit
    audit_path = Path('cron_logs/overflow-audit.json')
    audit_entry = {'ts':'2026-02-08T01:30:00Z','project_id':session['project_id'],'session_id':session.get('id'),'model':model,'est':est,'compaction':compaction_flag}
    with open(audit_path,'a',encoding='utf-8') as f:
        f.write(json.dumps(audit_entry,ensure_ascii=False)+'\n')
    return reply

# CLI test
if __name__ == '__main__':
    sess = {'id':'sim-2','project_id':'tg:sim','session_summary':'S1 seed','history':[]}
    for i in range(1,201):
        mid=f'm{i}'
        text=f'Message {i} content. ' + ('x'*200)
        sess['history'].append((mid,text))
        msg={'id':mid,'chat_id':'sim','text':text}
        r = handle_telegram_message(sess,msg)
    print('Done simulation.')
