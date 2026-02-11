-- metrics_v1_1.sql
-- V1.1: runtime request metrics for observability

BEGIN;

CREATE TABLE IF NOT EXISTS memory_request_metrics (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT,
  session_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),

  query TEXT,

  fts_hits INT,
  trgm_hits INT,
  used_fallback BOOLEAN,
  retrieval_path TEXT, -- fts | trgm | window | summaries_only

  context_items INT,
  estimated_tokens INT,
  truncated BOOLEAN,

  latency_retrieval_ms INT,
  latency_llm_ms INT,

  error_stage TEXT, -- null | llm_reply | summary | retrieval
  meta JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_memory_request_metrics_user_time
  ON memory_request_metrics(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_memory_request_metrics_user_session_time
  ON memory_request_metrics(user_id, session_id, created_at DESC);

COMMIT;
