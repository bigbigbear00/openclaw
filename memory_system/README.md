# memory_system (plugin)

A standalone memory/RAG plugin for Clawdbot.

> 生产后端说明（重要）：当前生产数据以后端 Postgres (`clawd_db`) 为准；`memory_system/db/memory.db` 仅用于历史本地测试场景，可能为空文件，不代表生产记忆丢失。

## What it does (V1)
- **Cold memory**: store every user/assistant turn in Postgres (`chat_turns`) — never lose raw text.
- **Warm memory**: retrieve a small set of relevant snippets for prompting.
- **Summary memory**: low-frequency summaries into `chat_summaries`.

Retrieval order (baseline): **FTS → fallback (trgm/ILIKE) → (optional) vectors**.

## DB (Postgres)
Apply migrations (tables/constraints):

- `tmp/migrations_v1.sql` (already used in this repo)

Enable retrieval indexes:

```bash
psql -h localhost -U apple -d clawd_db -f memory_system/sql/fts_postgres.sql
```

## Python env
This plugin expects `psycopg2` and `openai`.

Because Homebrew Python is PEP-668 managed, use a virtualenv:

```bash
cd /Users/apple/clawd
python3 -m venv .venv
source .venv/bin/activate
pip install -r memory_system/requirements.txt
```

## Smoke test
Without OPENAI_API_KEY (DB write + retrieval only):

```bash
source .venv/bin/activate
python -m memory_system.scripts.smoke_test --user_id u1 --session_id s1 --text "中文测试一下记忆系统FTS"
```

With OPENAI_API_KEY set (runs full pipeline):

```bash
export OPENAI_API_KEY="sk-..."
python -m memory_system.scripts.smoke_test --user_id u1 --session_id s1 --text "hello"
```

## Entrypoint
Use `memory_system/app/chat_entry.py:handle(user_id, session_id, user_input)`.
