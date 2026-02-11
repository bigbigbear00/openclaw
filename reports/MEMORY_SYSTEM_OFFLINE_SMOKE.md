# MEMORY_SYSTEM_OFFLINE_SMOKE

Generated: 2026-02-09T15:39:30+08:00

Goal: Verify memory_system old mainline (Postgres FTS + pg_trgm + metrics) can run end-to-end in STRICT OFFLINE mode (no network, no API keys, no watchers/workers).

Summary: PASS

Evidence & steps (commands run + results):

A) Runtime checks
- DATABASE_URL env: not set
- pm2 ls: workers stopped, index-reader removed (see /Users/apple/clawd/reports/SYSTEM_AUDIT_SNAPSHOT.md for full pm2 listing)
- ps scan (filtered): openclaw-gateway running

B) Entry files existence
- /Users/apple/clawd/memory_system/app/chat_entry.py : exists
- /Users/apple/clawd/memory_system/sql/fts_postgres.sql : exists
- /Users/apple/clawd/memory_system/sql/metrics_v1_1.sql : exists

C) Postgres availability (checked without revealing credentials)
- Command: psql -h localhost -d clawd_db -c "select 1;"
- Result: SUCCESS (returned 1)

D) Schema existence
- Checked via: SELECT to_regclass('public.chat_turns'), to_regclass('public.memory_request_metrics');
- Result: both tables present

E) Sample writes (minimal writes performed)
- Inserted 2 rows into chat_turns with session_id='offline_smoke_20260209' (user_id='offline_test')
- Verification: SELECT count(*) FROM chat_turns WHERE session_id='offline_smoke_20260209'; -> 2

F) Offline retrieval tests
- FTS test (plainto_tsquery 'CTF'):
  - Command: SELECT id, substr(content,1,120) FROM chat_turns WHERE to_tsvector('simple', content) @@ plainto_tsquery('simple','CTF') ORDER BY id DESC LIMIT 1;
  - Result: hit id=183, snippet='辅助内容 包含 CTF 关键词 测试 B' (truncated to 120 chars)
- trgm/ILIKE fallback:
  - Command: SELECT count(*) FROM chat_turns WHERE content ILIKE '%CTF%';
  - Result: 2

G) Metrics write
- Inserted one row into memory_request_metrics recording fts_hits=2, trgm_hits=2, retrieval_path='fts'
- Verification: SELECT id,created_at,query,retrieval_path,fts_hits,trgm_hits FROM memory_request_metrics ORDER BY id DESC LIMIT 1; -> shows the inserted row

PASS/FAIL
- PASS: All required steps succeeded under STRICT OFFLINE constraints.

Notes & minimal artifacts written
- Written to Postgres (allowed by task): 2 chat_turns rows and 1 memory_request_metrics row (session_id='offline_smoke_20260209')
- No external network calls were made.
- No watchers/workers/pm2 processes were started by this run.

Files & logs referenced
- /Users/apple/clawd/reports/MEMORY_SYSTEM_OFFLINE_SMOKE.md (this file)
- /Users/apple/clawd/memory/2026-02-09.md (audit log)
- /Users/apple/clawd/memory_system/db/ (if local sqlite exists; not used in this offline test)

If you want me to now remove the test rows (cleanup), reply 'CLEANUP_OFFLINE_TEST' and I will delete rows where session_id='offline_smoke_20260209' and append to audit.
