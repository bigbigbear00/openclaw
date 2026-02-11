-- migrations_v1.sql
-- V1: ensure chat_turns constraints/indexes + create chat_summaries + create chat_files

BEGIN;

-- -------------------------
-- chat_turns: harden schema
-- -------------------------

-- Normalize NULL session_id (defensive)
UPDATE chat_turns SET session_id='default' WHERE session_id IS NULL;

-- Ensure NOT NULL
ALTER TABLE chat_turns ALTER COLUMN session_id SET NOT NULL;
ALTER TABLE chat_turns ALTER COLUMN meta SET DEFAULT '{}'::jsonb;

-- Ensure role check constraint
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'chat_turns_role_check'
  ) THEN
    ALTER TABLE chat_turns
      ADD CONSTRAINT chat_turns_role_check
      CHECK (role IN ('user','assistant','system','tool'));
  END IF;
END$$;

-- Uniqueness: prevent turn_index conflicts within (user_id, session_id)
CREATE UNIQUE INDEX IF NOT EXISTS uq_turns_user_session_turn
  ON chat_turns(user_id, session_id, turn_index);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_turns_user_session_time
  ON chat_turns(user_id, session_id, created_at);

CREATE INDEX IF NOT EXISTS idx_turns_user_session_role_time
  ON chat_turns(user_id, session_id, role, created_at);

-- -------------------------
-- chat_summaries: V1 asset
-- -------------------------
CREATE TABLE IF NOT EXISTS chat_summaries (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  start_turn BIGINT NOT NULL,
  end_turn BIGINT NOT NULL,
  summary TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  CONSTRAINT chat_summaries_range_check CHECK (end_turn >= start_turn)
);

CREATE INDEX IF NOT EXISTS idx_summaries_user_session_time
  ON chat_summaries(user_id, session_id, created_at);

CREATE INDEX IF NOT EXISTS idx_summaries_user_session_endturn
  ON chat_summaries(user_id, session_id, end_turn DESC);

-- -------------------------
-- chat_files: metadata only
-- -------------------------
CREATE TABLE IF NOT EXISTS chat_files (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  session_id TEXT,
  turn_id BIGINT,
  file_type TEXT,
  mime_type TEXT,
  file_name TEXT,
  local_path TEXT NOT NULL,
  file_size BIGINT,
  checksum TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  meta JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Foreign key (optional): link file to a turn
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_chat_files_turn'
  ) THEN
    ALTER TABLE chat_files
      ADD CONSTRAINT fk_chat_files_turn
      FOREIGN KEY (turn_id) REFERENCES chat_turns(id)
      ON DELETE SET NULL;
  END IF;
END$$;

CREATE INDEX IF NOT EXISTS idx_files_user_time
  ON chat_files(user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_files_user_session_time
  ON chat_files(user_id, session_id, created_at);

COMMIT;
