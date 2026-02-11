-- CTF RAG schema v0.1

CREATE TABLE IF NOT EXISTS ctf_events (
  id TEXT PRIMARY KEY,
  ts TIMESTAMP NOT NULL,
  source TEXT NOT NULL,
  brand TEXT,
  topic TEXT NOT NULL,
  signal_type TEXT NOT NULL, -- price|campaign|product|channel|sentiment|competitor|policy
  region TEXT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  tags TEXT,
  confidence REAL DEFAULT 0.6,
  importance INTEGER DEFAULT 3,
  embedding_ref TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ctf_claims (
  id TEXT PRIMARY KEY,
  claim_date DATE NOT NULL,
  horizon TEXT NOT NULL, -- daily|weekly|monthly
  brand TEXT,
  topic TEXT NOT NULL,
  claim_text TEXT NOT NULL,
  stance TEXT, -- bullish|bearish|neutral|mixed
  confidence REAL DEFAULT 0.6,
  owner_agent TEXT DEFAULT 'ctf-director',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ctf_evidence_links (
  id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  relation TEXT DEFAULT 'supports', -- supports|contradicts|context
  weight REAL DEFAULT 1.0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ctf_trends_daily (
  id TEXT PRIMARY KEY,
  trend_date DATE NOT NULL,
  brand TEXT,
  topic TEXT NOT NULL,
  metric_name TEXT NOT NULL,
  metric_value REAL NOT NULL,
  baseline_7d REAL,
  baseline_30d REAL,
  z_score REAL,
  direction TEXT, -- up|down|flat
  note TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ctf_topics (
  id TEXT PRIMARY KEY,
  topic TEXT UNIQUE NOT NULL,
  taxonomy TEXT, -- 4A/brand/渠道/竞品
  active INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ctf_events_ts ON ctf_events(ts);
CREATE INDEX IF NOT EXISTS idx_ctf_events_topic ON ctf_events(topic);
CREATE INDEX IF NOT EXISTS idx_ctf_trends_date_topic ON ctf_trends_daily(trend_date, topic);
CREATE INDEX IF NOT EXISTS idx_claims_date_topic ON ctf_claims(claim_date, topic);
