# memory_system Evolution Plan

This is the “engineering owner” evolution plan for the memory system.

## 0) Goal
- Record what “good” looks like.
- Make upgrades **data-driven** (not vibe-driven).
- Define **when** to evolve from V1 → V1.1 → V2.

## 1) Current state (V1)
- **Cold memory**: all turns stored in Postgres `chat_turns` (raw content).
- **Summary memory**: periodic summaries stored in `chat_summaries` (triggered every N *user turns*).
- **Retrieval order**: summaries → Postgres FTS (rank + recency) → `pg_trgm` fallback (similarity threshold + min_query_len) → recent scoring fallback.
- **Guardrails**: memory context budget (≤2000 tokens), ≤6 turns, per-turn length cap.
- **Error handling**: LLM failure returns an error reply (no raise), still logs assistant error turn.
- **Concurrency**: retry on `(user_id, session_id, turn_index)` unique conflict.

## 2) Upgrade principles
1) Keep **cold memory** immutable and complete.
2) Add capability via **derived indexes** (FTS/trgm/embeddings) + **structured summaries**.
3) Upgrades must be triggered by measurable pain: recall failures, context-budget pressure, cost, latency.

## 3) V1.1 — Minimal incremental upgrades (Low risk / High ROI)
### V1.1-1: Runtime retrieval + budget metrics (MOST IMPORTANT)
**Purpose**
- Turn “it forgot” into a diagnosable issue.
- Provide evidence for whether vectors/structured memories are needed.

**Implementation**
Add an append-only table (or JSONB-first version) and write one row per request at the end of `handle_user_message()`.

Suggested schema:
```sql
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

  error_stage TEXT -- null | llm_reply | summary | retrieval
);
```

**Risk**
- Increased writes (but append-only, cheap, does not enter prompts).

**Verification**
- Weekly dashboards (even a simple SQL report):
  - FTS hit-rate, fallback share, truncation share, p95 latency.

---

### V1.1-2: Retrieval scope switch (session → user)
**Purpose**
- Solve “you said it before but in another session.”

**Implementation**
- Add `scope="session"|"user"` option to retrieval.
- Default session scope; expand to user-wide when:
  - `fts_hits < threshold`, or
  - user asks “之前/以前/上次”.

**Risk**
- Pulling stale/contradictory info, more truncation.

**Verification**
- Compare success rate for cross-session queries.
- Track increased truncation rate.

---

### V1.1-3: Structured summaries (store structure in `chat_summaries.meta`)
**Purpose**
- Make summaries computable (facts/preferences/todos/entities), not just readable.

**Implementation**
- Summary LLM outputs:
```json
{
  "facts": [...],
  "preferences": [...],
  "decisions": [...],
  "todos": [...],
  "entities": [...]
}
```
- Store:
  - `chat_summaries.summary` (human-readable)
  - `chat_summaries.meta.structured` (machine-readable)

**Risk**
- JSON instability → require schema + retry.

**Verification**
- structured field non-empty rate.
- Can query `meta->'structured'->'todos'` for simple TODO retrieval.

---

### V1.1-4: Summaries-only vectors (tiny embedding footprint)
**Purpose**
- Fix “semantic” queries where FTS+trgm fail.

**Implementation**
- Add summary embeddings table:
```sql
CREATE TABLE IF NOT EXISTS chat_summary_embeddings (
  summary_id BIGINT PRIMARY KEY REFERENCES chat_summaries(id) ON DELETE CASCADE,
  embedding JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```
- Only use when:
  - `fts_hits < 2` and `trgm_hits == 0`, OR
  - only 1–2 summaries exist.

**Risk**
- Introduces embedding infra (but very small scale).

**Verification**
- Embedding path trigger rate should stay under ~10–20%.

## 4) V2 — Structural upgrades (only after V1.1 metrics prove need)
### V2-1: Structured memories main table
**Purpose**
- Support long-term reasoning: preference evolution, todo lifecycle, factual conflict handling.

**Sketch**
```sql
CREATE TABLE IF NOT EXISTS memories_structured (
  id BIGSERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  type TEXT NOT NULL, -- fact | preference | todo | decision
  content TEXT NOT NULL,
  confidence DOUBLE PRECISION,
  valid_from TIMESTAMPTZ,
  valid_to TIMESTAMPTZ,
  source_summary_id BIGINT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

### V2-2: Vector memory table (DO NOT embed full turns)
**Purpose**
- True semantic recall with controlled cost/noise.

**Rule**
Embed only:
- summaries
- structured memories
- manually marked “high-value” turns

### V2-3: Conflict handling + time evolution
**Purpose**
- Handle: “you said A before, now B” with time-aware reasoning.

**Strategy**
- When writing new memory, detect same-type previous ones;
- mark old valid_to; keep confidence; explain conflicts.

## 5) Upgrade triggers (metrics + suggested thresholds)
| Metric | Suggested threshold | Meaning |
|---|---:|---|
| `fts_hits < 3` rate | >30% of queries/week | lexical retrieval insufficient |
| fallback usage | >50% | FTS no longer main |
| summaries-only context | >20% | summaries not structured enough |
| truncation rate | >40% | context budget pressure |
| embedding “needed” (manual) | >10% | V1.x recall insufficient |
| user “forgot” complaints | >3/week | product signal |
| p95 latency | >3s | need caching/splitting |
| summary cost share | >25% of LLM spend | need lower frequency/compression |

## 6) Decision log
- V1 summary trigger unit: user turns (role='user').
- FTS uses 'simple' dictionary; Chinese recall handled via pg_trgm fallback.
- V2 principle: never embed all turns; embed summaries/structured/high-value only.
