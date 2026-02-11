-- SQLite DDL for Long-Context Memory (S2 storage)

BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS memory_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id TEXT NOT NULL,
  session_id TEXT,
  type TEXT NOT NULL, -- 'pin' | 'summary' | 'fact' | 'doc'
  topic TEXT,
  source_from_msg_id TEXT,
  source_to_msg_id TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  content TEXT NOT NULL,
  meta JSON
);

CREATE INDEX IF NOT EXISTS idx_memory_project ON memory_items(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_items(type);
CREATE INDEX IF NOT EXISTS idx_memory_session ON memory_items(session_id);

-- Embedding cache (optional)
CREATE TABLE IF NOT EXISTS embedding_cache (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  memory_item_id INTEGER,
  vector BLOB,
  dims INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(memory_item_id) REFERENCES memory_items(id)
);

COMMIT;
