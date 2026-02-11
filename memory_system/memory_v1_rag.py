"""memory_v1_rag_full.py

V1 目标：
1) 每 20 轮自动生成一次摘要（写入 chat_summaries）
2) 检索时 summaries 优先（再补 turns）
3) MEMORY_CONTEXT token 预算 ≤ 2000（严格裁剪/截断/丢弃）

注意：
- 本模块只负责：DB 写入/读取、摘要触发与 prompt 构造、context 拼装与裁剪。
- 具体调用哪个 LLM 生成摘要/回复，由主程序通过函数注入。

依赖：psycopg2-binary
"""

import re
import hashlib
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

import psycopg2
from psycopg2.extras import Json


# =========================
# Config
# =========================
@dataclass
class MemoryConfig:
    dbname: str = "clawd_db"
    user: str = "apple"
    host: str = "localhost"
    port: str = "5432"

    # V1 预算
    memory_token_budget: int = 2000
    max_items_turns: int = 6
    max_items_summaries: int = 3

    # 摘要触发频率
    summarize_every_n_turns: int = 20

    # 单条裁剪（字符级，配合 token 预算双保险）
    max_chars_per_summary: int = 1200
    max_chars_per_turn: int = 700

    # 检索策略（V1：只看最近 N 条 turns，避免全表扫描）
    turns_search_window: int = 200


CFG = MemoryConfig()


# =========================
# Connection
# =========================
def get_conn(cfg: MemoryConfig = CFG):
    # apple 无密码：不要传 password
    return psycopg2.connect(
        dbname=cfg.dbname,
        user=cfg.user,
        host=cfg.host,
        port=cfg.port,
    )


# =========================
# Token estimation (V1)
# =========================
def estimate_tokens(text: str) -> int:
    """V1 简易 token 估算：
    - 英文约 4 chars/token
    - 中文约 2 chars/token（保守）
    """
    if not text:
        return 0
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    if cjk > len(text) * 0.2:
        return max(1, len(text) // 2)
    return max(1, len(text) // 4)


def truncate_to_budget(items: List[Tuple[str, str]], budget_tokens: int) -> List[Tuple[str, str]]:
    """items: [(title, content), ...] 依顺序保留，超预算则截断/丢弃尾部。"""
    kept: List[Tuple[str, str]] = []
    used = 0
    for title, content in items:
        t = estimate_tokens(title) + estimate_tokens(content) + 8
        if used + t <= budget_tokens:
            kept.append((title, content))
            used += t
            continue

        remaining = budget_tokens - used - estimate_tokens(title) - 8
        if remaining <= 30:
            break

        # 最保守：2 chars/token
        max_chars = remaining * 2
        kept.append((title, content[:max_chars] + "…"))
        break

    return kept


def pack_context(items: List[Tuple[str, str]], cfg: MemoryConfig = CFG) -> Tuple[str, Dict[str, Any]]:
    """Pack items into a single MEMORY_CONTEXT string and return metrics."""
    packed = truncate_to_budget(items, cfg.memory_token_budget)
    blocks = []
    for title, content in packed:
        blocks.append(f"{title}\n{content}")

    text = "\n\n".join(blocks)
    # Estimate tokens for observability (rough)
    estimated = estimate_tokens(text)

    metrics = {
        "context_items": len(packed),
        "estimated_tokens": int(estimated),
        "truncated": len(packed) < len(items) or (estimated > cfg.memory_token_budget),
    }
    return text, metrics


# =========================
# Core DB helpers
# =========================
def next_turn_index(cur, user_id: str, session_id: str) -> int:
    cur.execute(
        """SELECT COALESCE(MAX(turn_index), 0) + 1
           FROM chat_turns
           WHERE user_id=%s AND session_id=%s""",
        (user_id, session_id),
    )
    return int(cur.fetchone()[0])


def log_turn(user_id: str, session_id: str, role: str, content: str, meta: Optional[dict] = None) -> int:
    """Insert a turn.

    Note: turn_index is computed as MAX()+1, which can race under concurrency.
    V1 mitigation: retry on UNIQUE violation a couple times.
    """
    meta = meta or {}
    with get_conn() as conn:
        with conn.cursor() as cur:
            for _ in range(3):
                idx = next_turn_index(cur, user_id, session_id)
                try:
                    cur.execute(
                        """INSERT INTO chat_turns(user_id, session_id, turn_index, role, content, meta)
                           VALUES (%s,%s,%s,%s,%s,%s)
                           RETURNING id""",
                        (user_id, session_id, idx, role, content, Json(meta)),
                    )
                    return int(cur.fetchone()[0])
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    continue
            raise RuntimeError("log_turn failed after retries (turn_index conflict)")


def get_turn_count(cur, user_id: str, session_id: str) -> int:
    cur.execute(
        """SELECT COALESCE(MAX(turn_index), 0)
           FROM chat_turns
           WHERE user_id=%s AND session_id=%s""",
        (user_id, session_id),
    )
    return int(cur.fetchone()[0])


def get_user_turn_count(cur, user_id: str, session_id: str) -> int:
    """Count user turns (preferred unit for 'every N turns' triggers)."""
    cur.execute(
        """SELECT COUNT(*)
           FROM chat_turns
           WHERE user_id=%s AND session_id=%s AND role='user'""",
        (user_id, session_id),
    )
    return int(cur.fetchone()[0])


def last_summary_end_turn(cur, user_id: str, session_id: str) -> int:
    cur.execute(
        """SELECT COALESCE(MAX(end_turn), 0)
           FROM chat_summaries
           WHERE user_id=%s AND session_id=%s""",
        (user_id, session_id),
    )
    return int(cur.fetchone()[0])


def fetch_turns_range(cur, user_id: str, session_id: str, start_turn: int, end_turn: int) -> List[Tuple[int, str, str]]:
    cur.execute(
        """SELECT turn_index, role, content
           FROM chat_turns
           WHERE user_id=%s AND session_id=%s
             AND turn_index BETWEEN %s AND %s
           ORDER BY turn_index ASC""",
        (user_id, session_id, start_turn, end_turn),
    )
    return [(int(r[0]), r[1], r[2]) for r in cur.fetchall()]


def _stable_chunk_id(user_id: str, session_id: str, start_turn: int, end_turn: int, summary_type: str) -> str:
    raw = f"{user_id}|{session_id}|{start_turn}|{end_turn}|{summary_type}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def insert_summary(
    cur,
    user_id: str,
    session_id: str,
    start_turn: int,
    end_turn: int,
    summary: str,
    meta: Optional[dict] = None,
    summary_type: str = "periodic",
    source: str = "memory",
    request_id: Optional[str] = None,
    chunk_id: Optional[str] = None,
) -> int:
    payload = dict(meta or {})
    payload.setdefault("summary_type", summary_type)
    payload.setdefault("source", source)
    if request_id:
        payload.setdefault("request_id", request_id)
    payload.setdefault("chunk_id", chunk_id or _stable_chunk_id(user_id, session_id, start_turn, end_turn, summary_type))

    cur.execute(
        """INSERT INTO chat_summaries(user_id, session_id, start_turn, end_turn, summary, meta)
           VALUES (%s,%s,%s,%s,%s,%s)
           RETURNING id""",
        (user_id, session_id, start_turn, end_turn, summary, Json(payload)),
    )
    return int(cur.fetchone()[0])


def upsert_compaction_summary(
    cur,
    user_id: str,
    session_id: str,
    start_turn: int,
    end_turn: int,
    summary: str,
    meta: Optional[dict] = None,
    request_id: Optional[str] = None,
) -> int:
    """Idempotent write for compaction summaries.

    Reuses an existing compaction summary for the same (user, session, range) when present,
    otherwise inserts a new one.
    """
    cur.execute(
        """
        SELECT id
        FROM chat_summaries
        WHERE user_id=%s
          AND session_id=%s
          AND start_turn=%s
          AND end_turn=%s
          AND COALESCE(meta->>'summary_type', 'periodic')='compaction'
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id, session_id, start_turn, end_turn),
    )
    row = cur.fetchone()
    if row:
        return int(row[0])

    return insert_summary(
        cur,
        user_id,
        session_id,
        start_turn,
        end_turn,
        summary,
        meta=meta,
        summary_type="compaction",
        source="longctx",
        request_id=request_id,
    )


def write_summary(
    user_id: str,
    session_id: str,
    start_turn: int,
    end_turn: int,
    summary: str,
    summary_type: str = "periodic",
    source: str = "memory",
    request_id: Optional[str] = None,
    meta: Optional[dict] = None,
    idempotent: bool = False,
) -> int:
    """Unified summary write API for runtime/longctx integration."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            if idempotent and summary_type == "compaction":
                return upsert_compaction_summary(
                    cur,
                    user_id,
                    session_id,
                    start_turn,
                    end_turn,
                    summary,
                    meta=meta,
                    request_id=request_id,
                )
            return insert_summary(
                cur,
                user_id,
                session_id,
                start_turn,
                end_turn,
                summary,
                meta=meta,
                summary_type=summary_type,
                source=source,
                request_id=request_id,
            )


# =========================
# Summarization trigger (every 20 turns)
# =========================
def should_summarize(cur, user_id: str, session_id: str, cfg: MemoryConfig = CFG) -> Optional[Tuple[int, int]]:
    """返回 (start_turn, end_turn) 或 None。

    规则（V1）：按 *user turn* 计数触发（更符合“每 N 轮用户发言”）。
    - 每累计到 N 个 user turn 的倍数触发一次
    - 摘要范围：上次 summary.end_turn+1 到当前 max(turn_index)
    """
    user_turns = get_user_turn_count(cur, user_id, session_id)
    if user_turns < cfg.summarize_every_n_turns:
        return None
    if user_turns % cfg.summarize_every_n_turns != 0:
        return None

    last_end = last_summary_end_turn(cur, user_id, session_id)
    start = last_end + 1
    end = get_turn_count(cur, user_id, session_id)
    if end < start:
        return None
    return (start, end)


def build_summary_prompt(turns: List[Tuple[int, str, str]]) -> str:
    lines = []
    for idx, role, content in turns:
        role_tag = "U" if role == "user" else "A"
        c = (content or "").strip()
        if len(c) > 500:
            c = c[:500] + "…"
        lines.append(f"[{idx}]{role_tag}: {c}")
    dialog = "\n".join(lines)

    return (
        "你是一个记忆系统的摘要器。请基于以下对话片段生成“长期记忆摘要”，输出为中文，结构严格如下：\n"
        "Facts:\n- ...\n"
        "Preferences:\n- ...\n"
        "Decisions:\n- ...\n"
        "Todos:\n- ...\n"
        "Entities:\n- ...\n\n"
        "要求：只写高价值信息；避免复述；不确定的用‘可能/待确认’。\n"
        f"对话片段：\n{dialog}\n"
    )


def maybe_create_summary(user_id: str, session_id: str, llm_summarize_func, cfg: MemoryConfig = CFG) -> Optional[int]:
    """llm_summarize_func(prompt:str)->str 由主程序注入。"""
    with get_conn(cfg) as conn:
        with conn.cursor() as cur:
            rng = should_summarize(cur, user_id, session_id, cfg)
            if not rng:
                return None

            start_turn, end_turn = rng
            turns = fetch_turns_range(cur, user_id, session_id, start_turn, end_turn)
            prompt = build_summary_prompt(turns)
            summary_text = (llm_summarize_func(prompt) or "").strip()

            if len(summary_text) > cfg.max_chars_per_summary:
                summary_text = summary_text[: cfg.max_chars_per_summary] + "…"

            sid = insert_summary(
                cur,
                user_id,
                session_id,
                start_turn,
                end_turn,
                summary_text,
                meta={"type": "periodic", "turns": [start_turn, end_turn]},
            )
            return sid


# =========================
# Retrieval (summaries first) + context packing
# =========================
def fetch_recent_summaries(cur, user_id: str, session_id: str, limit: int) -> List[Tuple[int, int, str, str]]:
    cur.execute(
        """SELECT start_turn, end_turn, created_at::text, summary
           FROM chat_summaries
           WHERE user_id=%s AND session_id=%s
           ORDER BY
             CASE WHEN COALESCE(meta->>'summary_type', 'periodic')='compaction' THEN 0 ELSE 1 END,
             end_turn DESC
           LIMIT %s""",
        (user_id, session_id, limit),
    )
    out: List[Tuple[int, int, str, str]] = []
    for st, et, ts, summ in cur.fetchall():
        out.append((int(st), int(et), ts, summ))
    return out


def fetch_recent_turns_window(cur, user_id: str, session_id: str, window: int) -> List[Tuple[int, str, str, str]]:
    cur.execute(
        """SELECT turn_index, role, created_at::text, content
           FROM chat_turns
           WHERE user_id=%s AND session_id=%s
           ORDER BY turn_index DESC
           LIMIT %s""",
        (user_id, session_id, window),
    )
    rows = cur.fetchall()
    rows.reverse()  # 回正序
    return [(int(r[0]), r[1], r[2], r[3]) for r in rows]


def _has_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def fts_search_turns(
    cur,
    user_id: str,
    session_id: str,
    query: str,
    limit: int = 20,
) -> List[Tuple[int, str, str, str, float]]:
    """Postgres FTS search on chat_turns.content_tsv.

    Returns: [(turn_index, role, created_at, content, rank)]

    Notes:
    - Dictionary 'simple' is good for English/keywords/code; not great for Chinese.
    - Callers should fallback when results are insufficient.
    """
    # Filter roles: only user/assistant to avoid tool/system noise
    cur.execute(
        """
        WITH q AS (SELECT plainto_tsquery('simple', %s) AS tsq)
        SELECT turn_index, role, created_at::text, content,
               ts_rank_cd(content_tsv, q.tsq) AS rank
        FROM chat_turns, q
        WHERE user_id=%s
          AND session_id=%s
          AND role IN ('user','assistant')
          AND content_tsv @@ q.tsq
        ORDER BY rank DESC, created_at DESC
        LIMIT %s
        """,
        (query, user_id, session_id, limit),
    )
    out: List[Tuple[int, str, str, str, float]] = []
    for idx, role, ts, content, rank in cur.fetchall():
        out.append((int(idx), role, ts, content, float(rank)))
    return out


def trgm_fallback_search_turns(
    cur,
    user_id: str,
    session_id: str,
    query: str,
    limit: int = 20,
    min_score: float = 0.1,
    min_query_len: int = 3,
) -> List[Tuple[int, str, str, str, float]]:
    """Trigram/similarity fallback (requires pg_trgm).

    Note:
    - Use similarity threshold rather than ILIKE, otherwise we lose fuzzy recall.
    - For very short queries, trgm similarity is noisy; callers should skip.
    """
    if len((query or "").strip()) < min_query_len:
        return []

    cur.execute(
        """
        SELECT turn_index, role, created_at::text, content,
               similarity(content, %s) AS score
        FROM chat_turns
        WHERE user_id=%s
          AND session_id=%s
          AND role IN ('user','assistant')
          AND similarity(content, %s) > %s
        ORDER BY score DESC, created_at DESC
        LIMIT %s
        """,
        (query, user_id, session_id, query, min_score, limit),
    )
    out: List[Tuple[int, str, str, str, float]] = []
    for idx, role, ts, content, score in cur.fetchall():
        out.append((int(idx), role, ts, content, float(score)))
    return out


def score_relevance(query: str, text: str) -> int:
    q = (query or "").strip().lower()
    t = (text or "").lower()
    if not q:
        return 0
    parts = [p for p in re.split(r"\s+", q) if p]
    score = 0
    # 中文/无空格场景：整句包含给加权
    if q and q in t:
        score += 5
    for p in parts[:8]:
        score += t.count(p)
    return score


def retrieve_memory_context(user_id: str, session_id: str, user_query: str, cfg: MemoryConfig = CFG) -> Tuple[str, Dict[str, Any]]:
    """规则（按你们基线）：
    1) summaries 优先：最近 N 条
    2) turns：FTS 优先；若命中不足（或中文场景召回差）再 fallback（trgm/ILIKE）；
       再不足才考虑向量检索（V1 此处仅留钩子）
    3) <= token budget：超预算则截断/丢弃

    注意：Postgres FTS (simple) 对中文分词弱，因此中文/短串场景必须有 fallback。
    """
    with get_conn(cfg) as conn:
        with conn.cursor() as cur:
            # 1) summaries
            summaries = fetch_recent_summaries(cur, user_id, session_id, cfg.max_items_summaries)
            summary_items: List[Tuple[str, str]] = []
            summary_ts_list: List[str] = []
            for st, et, ts, summ in summaries:
                s = (summ or "").strip()
                if len(s) > cfg.max_chars_per_summary:
                    s = s[: cfg.max_chars_per_summary] + "…"
                summary_items.append((f"[SUMMARY {st}-{et} @ {ts}]", s))
                if ts:
                    summary_ts_list.append(str(ts))

            # 2) turns via FTS (candidates)
            fts_candidates: List[Tuple[int, str, str, str, float]] = []
            trgm_candidates: List[Tuple[int, str, str, str, float]] = []
            window_candidates: List[Tuple[int, str, str, str, float]] = []

            fts_ok = True
            try:
                fts_candidates = fts_search_turns(cur, user_id, session_id, user_query, limit=max(20, cfg.max_items_turns * 3))
            except Exception:
                fts_ok = False
                fts_candidates = []

            # Decide fallback: Chinese OR too few FTS hits
            need_fallback = _has_cjk(user_query) or len(fts_candidates) < 3

            if need_fallback:
                # Prefer pg_trgm if available; else recent window scoring
                try:
                    trgm_candidates = trgm_fallback_search_turns(
                        cur,
                        user_id,
                        session_id,
                        user_query,
                        limit=max(20, cfg.max_items_turns * 3),
                    )
                except Exception:
                    trgm_candidates = []

                if not trgm_candidates:
                    recent = fetch_recent_turns_window(cur, user_id, session_id, cfg.turns_search_window)
                    scored: List[Tuple[int, int, str, str, str]] = []
                    for idx, role, ts, content in recent:
                        sc = score_relevance(user_query, content)
                        scored.append((sc, idx, role, ts, content))
                    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
                    for sc, idx, role, ts, content in scored[: max(20, cfg.max_items_turns * 3)]:
                        if sc > 0:
                            window_candidates.append((idx, role, ts, content, float(sc)))

            # Merge candidates, de-dup by turn_index
            merged: List[Tuple[int, str, str, str, float, str]] = []
            seen_turns = set()
            for idx, role, ts, content, score in fts_candidates:
                if idx in seen_turns:
                    continue
                seen_turns.add(idx)
                merged.append((idx, role, ts, content, score, "fts"))
            for idx, role, ts, content, score in trgm_candidates:
                if idx in seen_turns:
                    continue
                seen_turns.add(idx)
                merged.append((idx, role, ts, content, score, "trgm"))
            for idx, role, ts, content, score in window_candidates:
                if idx in seen_turns:
                    continue
                seen_turns.add(idx)
                merged.append((idx, role, ts, content, score, "window"))

            # Pick top turns for prompt.
            # Sort: prefer score/rank desc, then recency by turn_index
            merged.sort(key=lambda x: (x[4], x[0]), reverse=True)
            top = merged[: cfg.max_items_turns]

            # Selected time range (for provenance/debugging)
            def _ts_bounds(ts_list: List[str]) -> Tuple[Optional[str], Optional[str]]:
                if not ts_list:
                    return (None, None)
                s = sorted(ts_list)
                return (s[0], s[-1])

            selected_turn_ts = [t[2] for t in top if t[2]]
            selected_turn_ts_min, selected_turn_ts_max = _ts_bounds(selected_turn_ts)

            # Contribution-based path and hit counts (counts refer to *selected top*)
            fts_hits = sum(1 for t in top if t[5] == "fts")
            trgm_hits = sum(1 for t in top if t[5] == "trgm")
            window_hits = sum(1 for t in top if t[5] == "window")

            if fts_hits == 0 and trgm_hits == 0 and window_hits == 0:
                retrieval_path = "summaries_only"
            elif trgm_hits > 0:
                retrieval_path = "trgm"
            elif window_hits > 0:
                retrieval_path = "window"
            else:
                retrieval_path = "fts"

            turn_items: List[Tuple[str, str]] = []
            for idx, role, ts, content, score, src in top:
                c = (content or "").strip()
                if len(c) > cfg.max_chars_per_turn:
                    c = c[: cfg.max_chars_per_turn] + "…"
                if src == "fts" and fts_ok and not _has_cjk(user_query):
                    turn_items.append((f"[TURN {idx} {role} @ {ts} rank={score:.3f}]", c))
                else:
                    turn_items.append((f"[TURN {idx} {role} @ {ts} score={score:.3f}]", c))

            items = summary_items + turn_items
            ctx_text, ctx_metrics = pack_context(items, cfg)

            summary_ts_min, summary_ts_max = _ts_bounds([str(x) for x in summary_ts_list if x])

            ctx_metrics.update(
                {
                    # contribution-based counts (selected top)
                    "fts_hits": int(fts_hits),
                    "trgm_hits": int(trgm_hits),
                    "window_hits": int(window_hits),
                    # whether fallback was actually used to contribute to top
                    "used_fallback": bool(trgm_hits > 0 or window_hits > 0),
                    "retrieval_path": retrieval_path,
                    # candidates for debugging
                    "candidates_summaries_count": int(len(summary_items)),
                    "candidates_fts_count": int(len(fts_candidates) if fts_ok else 0),
                    "candidates_trgm_count": int(len(trgm_candidates)),
                    "candidates_window_count": int(len(window_candidates)),
                    # provenance: selected time range
                    "selected_turn_time_range": {
                        "min": selected_turn_ts_min,
                        "max": selected_turn_ts_max,
                    },
                    "selected_summary_time_range": {
                        "min": summary_ts_min,
                        "max": summary_ts_max,
                    },
                }
            )

            # include explicit drop reason when no turns were added
            if retrieval_path == "summaries_only":
                if not fts_ok:
                    ctx_metrics["drop_reason"] = "fts_missing"
                elif len(fts_candidates) < 1 and len(trgm_candidates) < 1 and len(window_candidates) < 1:
                    ctx_metrics["drop_reason"] = "no_hits"

            return ctx_text, ctx_metrics


# =========================
# Integration hook
# =========================
def log_metrics(
    user_id: str,
    session_id: str,
    query: str,
    metrics: Dict[str, Any],
    error_stage: Optional[str] = None,
    meta: Optional[dict] = None,
    cfg: MemoryConfig = CFG,
    request_id: Optional[str] = None,
    model_reply: Optional[str] = None,
    model_summary: Optional[str] = None,
) -> Optional[int]:
    """Write one row to memory_request_metrics (V1.1).

    Safe: best-effort; failures are swallowed.
    """
    meta = meta or {}
    try:
        with get_conn(cfg) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO memory_request_metrics(
                      user_id, session_id, query,
                      request_id, model_reply, model_summary,
                      memory_token_budget, max_items_turns, max_items_summaries,
                      fts_hits, trgm_hits, used_fallback, retrieval_path,
                      context_items, estimated_tokens, truncated,
                      latency_retrieval_ms, latency_llm_ms,
                      error_stage, meta
                    ) VALUES (
                      %s,%s,%s,
                      %s,%s,%s,
                      %s,%s,%s,
                      %s,%s,%s,%s,
                      %s,%s,%s,
                      %s,%s,
                      %s,%s
                    ) RETURNING id
                    """,
                    (
                        user_id,
                        session_id,
                        query,
                        request_id,
                        model_reply,
                        model_summary,
                        cfg.memory_token_budget,
                        cfg.max_items_turns,
                        cfg.max_items_summaries,
                        metrics.get("fts_hits"),
                        metrics.get("trgm_hits"),
                        metrics.get("used_fallback"),
                        metrics.get("retrieval_path"),
                        metrics.get("context_items"),
                        metrics.get("estimated_tokens"),
                        metrics.get("truncated"),
                        metrics.get("latency_retrieval_ms"),
                        metrics.get("latency_llm_ms"),
                        error_stage,
                        Json(meta),
                    ),
                )
                return int(cur.fetchone()[0])
    except Exception:
        return None


def handle_user_message(
    user_id: str,
    session_id: str,
    user_input: str,
    llm_reply_func,
    llm_summarize_func,
    cfg: MemoryConfig = CFG,
    model_reply: Optional[str] = None,
    model_summary: Optional[str] = None,
) -> str:
    """Single V1 pipeline entry.

    Required order (baseline):
      write user → retrieve (FTS→fallback) → reply (Responses API via injected func) → write assistant → maybe summary

    Notes:
    - We intentionally trigger summary *after* assistant write to avoid half-write and counting ambiguity.
    - On LLM failure, we still write an assistant turn with error meta to keep turn sequence consistent.
    """
    import time
    import uuid

    request_id = str(uuid.uuid4())

    t0 = time.time()
    log_turn(user_id, session_id, "user", user_input, meta={"request_id": request_id})

    memory_context, retrieval_metrics = retrieve_memory_context(user_id, session_id, user_input, cfg)
    retrieval_metrics["latency_retrieval_ms"] = int((time.time() - t0) * 1000)
    retrieval_metrics["request_id"] = request_id
    retrieval_metrics["model_reply"] = model_reply
    retrieval_metrics["model_summary"] = model_summary

    t1 = time.time()
    try:
        reply = (llm_reply_func(user_input, memory_context) or "").strip()
    except Exception as e:
        retrieval_metrics["latency_llm_ms"] = int((time.time() - t1) * 1000)
        # Recommended: do NOT raise after writing an assistant error turn,
        # otherwise UI may show nothing while DB has a reply, and retries may duplicate writes.
        reply = "[ERROR] LLM reply failed."
        meta = {"error": str(e), "stage": "llm_reply"}
        meta.update({"retrieval": retrieval_metrics})
        log_turn(user_id, session_id, "assistant", reply, meta=meta)
        log_metrics(
            user_id,
            session_id,
            user_input,
            retrieval_metrics,
            error_stage="llm_reply",
            meta={"error": str(e), "models": {"reply": retrieval_metrics.get("model_reply"), "summary": retrieval_metrics.get("model_summary")}},
            request_id=request_id,
            model_reply=retrieval_metrics.get("model_reply"),
            model_summary=retrieval_metrics.get("model_summary"),
        )
        try:
            maybe_create_summary(user_id, session_id, llm_summarize_func, cfg)
        except Exception:
            pass
        return reply

    retrieval_metrics["latency_llm_ms"] = int((time.time() - t1) * 1000)

    log_turn(user_id, session_id, "assistant", reply, meta={"retrieval": retrieval_metrics, "request_id": request_id})
    log_metrics(
        user_id,
        session_id,
        user_input,
        retrieval_metrics,
        error_stage=None,
        meta={"models": {"reply": retrieval_metrics.get("model_reply"), "summary": retrieval_metrics.get("model_summary")}},
        request_id=request_id,
        model_reply=retrieval_metrics.get("model_reply"),
        model_summary=retrieval_metrics.get("model_summary"),
    )

    # low-frequency summary (after assistant written)
    try:
        maybe_create_summary(user_id, session_id, llm_summarize_func, cfg)
    except Exception:
        # do not break user-facing reply on summary failure
        pass

    return reply
