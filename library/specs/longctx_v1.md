# OpenClaw Long-Context for Telegram (Spec v1)

This document is the engineering spec (phase-1 skeleton). Implement a 3-layer context strategy for Telegram: rolling window, session summary (S1), and incremental summaries in memory (S2). Hard requirements: never exceed model context; never drop current user message; preserve long-term facts via S1/S2.

(Deliverable Phase 1: this skeleton + guard-rails pseudocode. Phase 2 will produce DDL, full config snippet, tests.)

## 0. Scope
Target channel: Telegram Bot API
Goal: handle very long project conversations without context overflow or quality collapse.

## 1. Definitions
- ctx_limit: model context window size (tokens)
- reserve: tokens reserved for system/tools/output
- budget = ctx_limit - reserve

## 2. Project & Session
- project_id attached to session (default: tg:<chat_id>)
- session fields: session_summary (S1), summary_cursor_msg_id, last_compaction_at

## 3. Runtime pipeline (high-level)
1. Ensure session.project_id
2. Ensure S1 exists
3. Load rolling window (pickWindowTurns(ctx_limit))
4. Retrieve bounded RAG chunks
5. Build candidate context (priority: system, user msg, S1, window, RAG)
6. Estimate tokens; if over yellow threshold, shrink window; if over red threshold, evict->S2 summarize and update S1
7. Enforce deterministic budget removal order (never drop system/user/S1)
8. Call model and persist

## 4. Observability & Safety (short)
Log per request: model, ctx_limit, budget, est_tokens_before/after, compaction_performed, s2_written, latencies.

---
Phase-1 complete: skeleton written. Phase-2 will expand pseudocode, provide openclaw.json snippet, SQLite DDL, and tests.
