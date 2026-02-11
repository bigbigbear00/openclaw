Long-Context (longctx) v1 — PR / Deployment Description

Purpose
- Integrate longctx guard-rails into agent runtime to prevent context overflow, automatically compact old history into S2 summaries, persist S2 to memory DB, and maintain an always-on S1 session summary.

Files changed/added (review package)
- /library/specs/longctx_v1.md — Spec skeleton
- /library/specs/longctx_guardrails.js — Pseudocode
- /library/specs/longctx_openclaw_config.json — config snippet for openclaw.json
- /library/specs/longctx_ddl.sql — SQLite DDL for memory_items
- /library/specs/longctx_readme.md — Implementation tasks and acceptance criteria
- /library/specs/longctx_ddl.sql — DDL (same)
- /scripts/longctx_staging_test.py — staging DDL & sample S2 insert
- /scripts/longctx_simulate.py — simulator
- /scripts/longctx_runtime.py — runtime handler (staging Python implementation)
- /scripts/longctx_staging_integration.py — integration replay runner

Deployment Steps (for ops)
1. Review files above and approve in PR.
2. On staging host: pull branch, ensure python3 & virtualenv, activate env, `pip install -r requirements.txt`.
3. Run DDL on staging DB (backup first): `sqlite3 /path/to/dev.sqlite < library/specs/longctx_ddl.sql`.
4. Deploy runtime handler into agent runtime (replace message handler with wrapper that calls handle_telegram_message in longctx_runtime.py in staging mode).
5. Run integration replay: `python3 scripts/longctx_staging_integration.py` and validate transcripts & `cron_logs/longctx_staging_report.json`.
6. Review auditing: `cron_logs/overflow-audit.json` entries.
7. If staging tests pass, schedule production window and repeat steps with production DB & agent (ops must have backups and rollback plan).

Rollback Plan
- Stop new handler (revert to previous handler) and restart agent service. Restore DB from backup if necessary.

Notes & Safety
- Do NOT put API keys in SQLite meta; use environment variables.
- This PR contains only staging/test code; production deploy requires ops approval.

Requested approval: merge to staging branch.
