-- fts_postgres.sql
-- Postgres Full-Text Search (FTS) for chat_turns.content
--
-- Notes:
-- - We keep original content in chat_turns.content (cold memory)
-- - FTS is used only for retrieval, never as the source of truth
-- - This script is safe to run multiple times.

BEGIN;

-- 0) Optional but strongly recommended: pg_trgm for Chinese/short-string fallback
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1) Add a generated tsvector column (Postgres 12+)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_name='chat_turns' AND column_name='content_tsv'
  ) THEN
    ALTER TABLE chat_turns
      ADD COLUMN content_tsv tsvector
      GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(content, ''))
      ) STORED;
  END IF;
END$$;

-- 2) Indexes
-- FTS index
CREATE INDEX IF NOT EXISTS idx_chat_turns_content_tsv
  ON chat_turns USING GIN (content_tsv);

-- Trigram index for ILIKE/similarity fallback
CREATE INDEX IF NOT EXISTS idx_chat_turns_content_trgm
  ON chat_turns USING GIN (content gin_trgm_ops);

-- Scoped composite index to help (user/session/time) filters
CREATE INDEX IF NOT EXISTS idx_chat_turns_user_session_time
  ON chat_turns(user_id, session_id, created_at);

COMMIT;

-- Example queries:
--
-- Scoped to a session (rank + recency):
--   WITH q AS (SELECT plainto_tsquery('simple', $3) AS tsq)
--   SELECT id, turn_index, role, created_at, content,
--          ts_rank_cd(content_tsv, q.tsq) AS rank
--   FROM chat_turns, q
--   WHERE user_id = $1
--     AND session_id = $2
--     AND content_tsv @@ q.tsq
--   ORDER BY rank DESC, created_at DESC
--   LIMIT 20;
--
-- Cross-session (user-wide) (rank + recency):
--   WITH q AS (SELECT websearch_to_tsquery('simple', $2) AS tsq)
--   SELECT id, session_id, turn_index, role, created_at, content,
--          ts_rank_cd(content_tsv, q.tsq) AS rank
--   FROM chat_turns, q
--   WHERE user_id = $1
--     AND content_tsv @@ q.tsq
--   ORDER BY rank DESC, created_at DESC
--   LIMIT 20;
