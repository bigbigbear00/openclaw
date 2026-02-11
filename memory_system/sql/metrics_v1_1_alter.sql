-- metrics_v1_1_alter.sql
-- V1.1 patch: add a few high-value columns recommended by review

BEGIN;

ALTER TABLE memory_request_metrics
  ADD COLUMN IF NOT EXISTS request_id TEXT,
  ADD COLUMN IF NOT EXISTS model_reply TEXT,
  ADD COLUMN IF NOT EXISTS model_summary TEXT,
  ADD COLUMN IF NOT EXISTS memory_token_budget INT,
  ADD COLUMN IF NOT EXISTS max_items_turns INT,
  ADD COLUMN IF NOT EXISTS max_items_summaries INT;

COMMIT;
