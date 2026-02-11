"""retrieve_context.py

CLI retrieval helper: given user_id/session_id + query, return packed MEMORY_CONTEXT
according to V1 rules.

Output is JSON so the caller can parse safely.

Usage:
  source /Users/apple/clawd/.venv/bin/activate
  python -m memory_system.scripts.retrieve_context --user_id hua --session_id tg_8555612162_main --query "..." --scope session
"""

import argparse
import json
import time

import psycopg2

from memory_system.memory_v1_rag import CFG, pack_context


def _conn():
    return psycopg2.connect(dbname=CFG.dbname, user=CFG.user, host=CFG.host, port=CFG.port)


def fetch_summaries(cur, user_id: str, session_id: str, limit: int):
    cur.execute(
        """SELECT id, start_turn, end_turn, summary
           FROM chat_summaries
           WHERE user_id=%s AND session_id=%s
           ORDER BY end_turn DESC
           LIMIT %s""",
        (user_id, session_id, limit),
    )
    return cur.fetchall()


def fts_search(cur, user_id: str, session_id: str, query: str, limit: int, scope: str):
    if scope == 'user':
        cur.execute(
            """WITH q AS (SELECT websearch_to_tsquery('simple', %s) AS tsq)
               SELECT session_id, turn_index, role, content,
                      ts_rank_cd(content_tsv, q.tsq) AS rank
               FROM chat_turns, q
               WHERE user_id=%s
                 AND content_tsv @@ q.tsq
               ORDER BY rank DESC, created_at DESC
               LIMIT %s""",
            (query, user_id, limit),
        )
    else:
        cur.execute(
            """WITH q AS (SELECT websearch_to_tsquery('simple', %s) AS tsq)
               SELECT session_id, turn_index, role, content,
                      ts_rank_cd(content_tsv, q.tsq) AS rank
               FROM chat_turns, q
               WHERE user_id=%s AND session_id=%s
                 AND content_tsv @@ q.tsq
               ORDER BY rank DESC, created_at DESC
               LIMIT %s""",
            (query, user_id, session_id, limit),
        )
    return cur.fetchall()


def trgm_search(cur, user_id: str, session_id: str, query: str, limit: int, scope: str):
    # simple ILIKE fallback; pg_trgm index helps
    pat = f"%{query}%"
    if scope == 'user':
        cur.execute(
            """SELECT session_id, turn_index, role, content
               FROM chat_turns
               WHERE user_id=%s AND content ILIKE %s
               ORDER BY created_at DESC
               LIMIT %s""",
            (user_id, pat, limit),
        )
    else:
        cur.execute(
            """SELECT session_id, turn_index, role, content
               FROM chat_turns
               WHERE user_id=%s AND session_id=%s AND content ILIKE %s
               ORDER BY created_at DESC
               LIMIT %s""",
            (user_id, session_id, pat, limit),
        )
    return cur.fetchall()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--user_id', required=True)
    ap.add_argument('--session_id', required=True)
    ap.add_argument('--query', required=True)
    ap.add_argument('--scope', choices=['session', 'user'], default='session')
    ap.add_argument('--max_turns', type=int, default=CFG.max_items_turns)
    ap.add_argument('--max_summaries', type=int, default=CFG.max_items_summaries)
    args = ap.parse_args()

    t0 = time.time()
    fts_hits = trgm_hits = 0
    used_fallback = False
    retrieval_path = None

    items = []
    with _conn() as conn:
        with conn.cursor() as cur:
            # summaries first (session-scoped by design)
            sums = fetch_summaries(cur, args.user_id, args.session_id, args.max_summaries)
            for sid, s0, s1, s in sums:
                items.append((f"[SUMMARY {args.session_id} {s0}-{s1}]", (s or '')[:CFG.max_chars_per_summary]))

            turns = []
            try:
                rows = fts_search(cur, args.user_id, args.session_id, args.query, args.max_turns, args.scope)
                fts_hits = len(rows)
                if fts_hits:
                    retrieval_path = 'fts'
                    turns = rows
                else:
                    used_fallback = True
                    rows2 = trgm_search(cur, args.user_id, args.session_id, args.query, args.max_turns, args.scope)
                    trgm_hits = len(rows2)
                    if trgm_hits:
                        retrieval_path = 'trgm'
                        turns = rows2
                    else:
                        retrieval_path = 'summaries_only'
            except Exception:
                used_fallback = True
                retrieval_path = 'summaries_only'

            for row in turns[: args.max_turns]:
                sess, idx, role, content, *rest = row
                title = f"[TURN {sess} #{idx} {role}]"
                c = (content or '')[:CFG.max_chars_per_turn]
                items.append((title, c))

    memory_text, pack_metrics = pack_context(items)
    latency_ms = int((time.time() - t0) * 1000)

    out = {
        'scope': args.scope,
        'retrieval_path': retrieval_path,
        'fts_hits': fts_hits,
        'trgm_hits': trgm_hits,
        'used_fallback': used_fallback,
        'latency_retrieval_ms': latency_ms,
        'context_items': pack_metrics.get('context_items'),
        'estimated_tokens': pack_metrics.get('estimated_tokens'),
        'truncated': pack_metrics.get('truncated'),
        'memory_context': memory_text,
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == '__main__':
    main()
