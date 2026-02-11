Long-Context Phase-2 Implementation README

Purpose
- Implement Spec v1: guard-rails, S1/S2 storage, compaction, RAG integration for Telegram.

Files generated
- longctx_v1.md (spec skeleton)
- longctx_guardrails.js (pseudocode)
- longctx_openclaw_config.json (config snippet)
- longctx_ddl.sql (SQLite schema)

Implementation Steps
1. Add longctx config to openclaw.json (merge longctx_openclaw_config.json into config)
2. Implement runtime helpers in agent runtime:
   - estimateTokens(textBlocks)
   - pickWindowTurns(ctxLimit)
   - buildContext / enforceBudget
   - summarizeToS2 and updateS1
   - retrieveMemory (RAG) with project_id filter
3. Add memory DB using longctx_ddl.sql and migrate existing summaries to memory_items
4. Add audit logging: write overflow-audit.json entries per request (see schema below)
5. Add unit tests: simulate heavy sessions and validate compaction behavior
6. Deploy to staging; run synthetic load and validate no model errors / no truncation

Audit log schema (example JSON keys)
{
  "ts": "ISO",
  "project_id": "tg:...",
  "session_id": "...",
  "model": "...",
  "ctx_limit": 400000,
  "reserve": 2000,
  "budget": 398000,
  "est_before": 410000,
  "est_after": 120000,
  "compaction": true,
  "s2_written": 1,
  "rag_chunks": 3,
  "notes": "evicted 120 messages -> s2"
}

Testing / Acceptance
- No provider errors when replaying a 10k-message session
- S1 maintained under configured token target
- RAG retrieval returns relevant S2 items
- Audit logs show compaction events and decisions

Operational notes
- Do NOT store API keys in sqlite meta; use env vars.
- Keep backups before any schema migration.

