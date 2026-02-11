#!/usr/bin/env python3
"""Global non-destructive dedupe: compare central chat_summaries (Postgres) with per-agent memory_items
and mark memory_items with meta.duplicate_of = <chat_summary_id> when similarity >= threshold.
"""
import sqlite3, json, difflib, os
from pathlib import Path

THRESHOLD = 0.80
AGENT_DB_PATHS = [
    'data/longctx_dev.sqlite',
    '/Users/apple/clawd-agents/writer-editor/memory/writer-editor.sqlite',
    '/Users/apple/clawd-agents/nba-expert/memory/nba-expert.sqlite',
    '/Users/apple/clawd-agents/news-analyst/memory/news-analyst.sqlite',
    '/Users/apple/clawd-agents/designer/memory/designer.sqlite',
    '/Users/apple/clawd-agents/vn-realestate/memory/vn-realestate.sqlite',
    '/Users/apple/clawd-agents/library-keeper/memory/library-keeper.sqlite',
    '/Users/apple/clawd-agents/ctf-director/memory/ctf-director.sqlite'
]

# load chat_summaries from memory_system Postgres via memory_v1_rag.get_conn
try:
    from memory_system.memory_v1_rag import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, summary FROM chat_summaries ORDER BY id ASC")
    summaries = [(str(r[0]), (r[1] or '').strip()) for r in cur.fetchall()]
    cur.close(); conn.close()
except Exception:
    summaries = []

report = {'marked':[], 'skipped':[], 'errors':[]}

for db_path in AGENT_DB_PATHS:
    if not os.path.exists(db_path):
        continue
    try:
        sconn = sqlite3.connect(db_path)
        scur = sconn.cursor()
        scur.execute("CREATE TABLE IF NOT EXISTS memory_items (id INTEGER PRIMARY KEY, project_id TEXT, session_id TEXT, type TEXT, topic TEXT, source_from_msg_id TEXT, source_to_msg_id TEXT, content TEXT, meta TEXT)")
        scur.execute("SELECT id, content, meta FROM memory_items")
        rows = scur.fetchall()
        for r in rows:
            mid = str(r[0])
            mtext = (r[1] or '').strip()
            meta_raw = r[2]
            try:
                meta = json.loads(meta_raw) if meta_raw else {}
            except Exception:
                meta = {}
            # skip if already marked
            if meta.get('duplicate_of'):
                report['skipped'].append({'db':db_path,'memory_id':mid,'reason':'already_marked'})
                continue
            best = None
            best_score = 0.0
            for sid, stext in summaries:
                if not stext or not mtext:
                    continue
                score = difflib.SequenceMatcher(None, stext, mtext).ratio()
                if score > best_score:
                    best_score = score; best = sid
            if best and best_score >= THRESHOLD:
                meta['duplicate_of'] = best
                scur.execute("UPDATE memory_items SET meta=? WHERE id=?", (json.dumps(meta, ensure_ascii=False), mid))
                report['marked'].append({'db':db_path,'memory_id':mid,'duplicate_of':best,'score':best_score})
        sconn.commit()
        scur.close(); sconn.close()
    except Exception as e:
        report['errors'].append({'db':db_path,'error':str(e)})

Path('cron_logs/longctx_dedupe_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print('Dedupe pass complete. Report: cron_logs/longctx_dedupe_report.json')
