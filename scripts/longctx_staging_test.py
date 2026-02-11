#!/usr/bin/env python3
"""Staging test: create local sqlite DB, apply DDL, insert sample S2 and audit entry."""
import sqlite3
import json
from pathlib import Path

DB_PATH = Path('data/longctx_dev.sqlite')
DDL_PATH = Path('library/specs/longctx_ddl.sql')

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
with open(DDL_PATH, 'r', encoding='utf-8') as f:
    ddl = f.read()
cur.executescript(ddl)
conn.commit()

# Insert sample summary (S2)
sample = {
    'project_id': 'tg:12345',
    'session_id': 'test-session',
    'type': 'summary',
    'topic': 'onboarding',
    'source_from_msg_id': 'm1',
    'source_to_msg_id': 'm20',
    'content': 'This is a sample S2 summary for messages m1..m20',
    'meta': json.dumps({'author':'staging','tokens':520})
}
cur.execute(
    '''INSERT INTO memory_items(project_id, session_id, type, topic, source_from_msg_id, source_to_msg_id, content, meta)
       VALUES(?,?,?,?,?,?,?,?)''',
    (sample['project_id'], sample['session_id'], sample['type'], sample['topic'], sample['source_from_msg_id'], sample['source_to_msg_id'], sample['content'], sample['meta'])
)
conn.commit()

# Create audit log file and write a sample entry
audit_path = Path('cron_logs/overflow-audit.json')
audit_path.parent.mkdir(parents=True, exist_ok=True)
audit_entry = {
    'ts': '2026-02-08T01:27:00Z',
    'project_id': sample['project_id'],
    'session_id': sample['session_id'],
    'model': 'openai/gpt-5-mini',
    'ctx_limit': 400000,
    'reserve': 2000,
    'budget': 398000,
    'est_before': 410000,
    'est_after': 120000,
    'compaction': True,
    's2_written': 1,
    'rag_chunks': 3,
    'notes': 'evicted 120 messages -> s2'
}
with open(audit_path, 'a', encoding='utf-8') as f:
    f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')

print('Staging DB created at', DB_PATH)
print('Inserted sample S2 and audit entry to', audit_path)

cur.close()
conn.close()
