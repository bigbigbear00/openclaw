"""Backfill Telegram HTML export into memory_system.

Strategy: A (summaries) + optional B (key turns).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup
from openai import OpenAI

from memory_system.memory_v1_rag import CFG, get_conn, insert_summary, log_turn


@dataclass
class Msg:
    ts: Optional[str]
    from_name: str
    text: str


def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    return s


def parse_telegram_html(path: str) -> List[Msg]:
    html = open(path, "r", encoding="utf-8", errors="ignore").read()
    soup = BeautifulSoup(html, "html.parser")

    msgs: List[Msg] = []
    for m in soup.select("div.message.default"):
        from_el = m.select_one("div.from_name")
        text_el = m.select_one("div.text")
        date_el = m.select_one("div.pull_right.date.details")

        from_name = _clean_text(from_el.get_text(" ")) if from_el else ""
        text = _clean_text(text_el.get_text(" ")) if text_el else ""
        ts = date_el.get("title") if date_el else None

        if not from_name and not text:
            continue
        if text in {"/start"}:
            continue
        msgs.append(Msg(ts=ts, from_name=from_name or "(unknown)", text=text))

    return msgs


def chunk_messages(msgs: List[Msg], chunk_size: int) -> List[List[Msg]]:
    out: List[List[Msg]] = []
    buf: List[Msg] = []
    for msg in msgs:
        if msg.text:
            buf.append(msg)
        if len(buf) >= chunk_size:
            out.append(buf)
            buf = []
    if buf:
        out.append(buf)
    return out


def messages_to_dialog(chunk: List[Msg], max_chars: int = 12000) -> str:
    lines = []
    for i, m in enumerate(chunk, 1):
        ts = f" ({m.ts})" if m.ts else ""
        lines.append(f"{i}. {m.from_name}{ts}: {m.text}")
    dialog = "\n".join(lines)
    if len(dialog) > max_chars:
        dialog = dialog[:max_chars] + "\n…"
    return dialog


def summarize_chunk(client: OpenAI, dialog: str, model: str, timeout_sec: int = 45) -> Tuple[str, Dict[str, Any]]:
    prompt = (
        "你是一个个人助理的长期记忆摘要器。\n"
        "请基于下面的聊天记录，生成：\n"
        "1) 一段人类可读的中文摘要（100-250字），聚焦：事实/偏好/决定/待办。\n"
        "2) 一个严格 JSON（不要 markdown），结构如下：\n"
        '{"facts":[],"preferences":[],"decisions":[],"todos":[],"entities":[]}\n'
        "要求：\n"
        "- facts/preferences/decisions/todos 里每条尽量短（<=30字）。\n"
        "- todos 如有期限要写出来。\n"
        "- 不要编造，缺失就留空数组。\n\n"
        "聊天记录：\n"
        "---\n"
        f"{dialog}\n"
        "---\n\n"
        "输出格式（两段）：\n"
        "SUMMARY: ...\n"
        "JSON: {...}\n"
    )

    r = client.with_options(timeout=timeout_sec).responses.create(
        model=model,
        input=prompt,
        temperature=0.2,
    )
    text = (r.output_text or "").strip()

    human = ""
    js: Dict[str, Any] = {"facts": [], "preferences": [], "decisions": [], "todos": [], "entities": []}

    m1 = re.search(r"SUMMARY:\s*(.+?)\nJSON:\s*(\{.*\})\s*$", text, re.S)
    if m1:
        human = _clean_text(m1.group(1))
        raw = m1.group(2)
        try:
            js = json.loads(raw)
        except Exception:
            js = {"_raw": raw}
    else:
        human = text[:1000]
        js = {"_raw": text}

    return human, js


KEY_PATTERNS = [r"\bTODO\b", r"待办", r"提醒", r"记住", r"偏好", r"以后", r"决定", r"计划", r"deadline", r"截止"]


def is_key_message(m: Msg) -> bool:
    t = m.text
    if len(t) >= 180:
        return True
    return any(re.search(p, t, re.I) for p in KEY_PATTERNS)


def stable_chunk_id(chunk: List[Msg]) -> str:
    h = hashlib.sha256()
    for m in chunk:
        h.update((m.from_name + "|" + (m.ts or "") + "|" + m.text + "\n").encode("utf-8"))
    return h.hexdigest()[:16]


def check_recent_rate_limit(conn_cfg=CFG, soft_budget_usd: float = 5.0) -> bool:
    """Return True if recent usage looks risky (errors/429-like or estimated cost high)."""
    try:
        with get_conn(conn_cfg) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT count(*) FROM memory_request_metrics WHERE created_at > now() - interval '1 hour' AND (meta->>'error' IS NOT NULL)"
                )
                errs = int(cur.fetchone()[0])
                cur.execute("SELECT count(*) FROM memory_request_metrics WHERE created_at > now() - interval '1 hour'")
                calls = int(cur.fetchone()[0])
                est_cost = calls * 0.05
                return errs > 0 or est_cost > soft_budget_usd
    except Exception:
        return True


def has_unique_index_on_checksum(cur) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = current_schema()
          AND tablename = 'chat_files'
          AND indexdef ILIKE '%UNIQUE%'
          AND indexdef ILIKE '%(checksum%'
        LIMIT 1
        """
    )
    return cur.fetchone() is not None


def insert_chat_file_idempotent(cur, user_id: str, session_id: str, file_type: str, local_path: str, checksum: str, meta: dict):
    payload = (user_id, session_id, file_type, local_path, checksum, json.dumps(meta))
    if has_unique_index_on_checksum(cur):
        cur.execute(
            """
            INSERT INTO chat_files(user_id, session_id, file_type, local_path, checksum, meta)
            VALUES (%s,%s,%s,%s,%s,%s)
            ON CONFLICT (checksum) DO NOTHING
            RETURNING id
            """,
            payload,
        )
        return

    cur.execute(
        """
        INSERT INTO chat_files(user_id, session_id, file_type, local_path, checksum, meta)
        SELECT %s,%s,%s,%s,%s,%s
        WHERE NOT EXISTS (
          SELECT 1 FROM chat_files WHERE checksum=%s
        )
        RETURNING id
        """,
        payload + (checksum,),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--user_id", required=True)
    ap.add_argument("--session_id", required=True)
    ap.add_argument("--chunk_size", type=int, default=120)
    ap.add_argument("--key_turns", type=int, default=30)
    ap.add_argument("--dry_run", action="store_true")
    ap.add_argument("--lock-mode", choices=["internal", "external", "auto"], default="auto")
    ap.add_argument("--max-runtime-sec", type=int, default=900)
    ap.add_argument("--chunk-timeout-sec", type=int, default=45)
    args = ap.parse_args()

    msgs = parse_telegram_html(args.html)
    chunks = chunk_messages(msgs, args.chunk_size)

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required")

    agent_id = args.user_id
    try:
        oc = json.load(open(os.path.expanduser("~/.openclaw/openclaw.json")))
        bindings = oc.get("bindings", [])
    except Exception:
        bindings = []

    html_text = open(args.html, "r", encoding="utf-8", errors="ignore").read()
    for b in bindings:
        try:
            bid = b.get("match", {}).get("peer", {}).get("id")
            if bid and str(bid) in html_text:
                agent_id = b.get("agentId", agent_id)
                break
        except Exception:
            continue

    client = OpenAI()
    model = os.getenv("SUMMARY_MODEL", "gpt-4.1-mini")
    print(f"[backfill] parsed messages={len(msgs)} chunks={len(chunks)} model={model} agent={agent_id}")

    key_candidates = [m for m in msgs if is_key_message(m)][: args.key_turns]

    lock_path = "/tmp/memory_backfill.lock"
    soft_budget_usd = 5.0
    started = time.monotonic()

    env_external = os.getenv("BACKFILL_LOCK_MANAGED_EXTERNALLY", "0") == "1"
    if args.lock_mode == "external":
        external_lock = True
    elif args.lock_mode == "internal":
        external_lock = False
    else:
        external_lock = env_external

    internal_lock_acquired = False

    try:
        if not args.dry_run and not external_lock:
            if os.path.exists(lock_path):
                print(f"[backfill] lock present at {lock_path}, exiting to avoid concurrent backfill")
                return

            if check_recent_rate_limit(CFG, soft_budget_usd):
                try:
                    os.makedirs(os.path.dirname(__file__) + "/../../reports", exist_ok=True)
                    with open(os.path.expanduser("~/clawd/reports/incident_backfill_rate_limit.log"), "a", encoding="utf-8") as fh:
                        fh.write(f"{datetime.utcnow().isoformat()}Z\tbackfill aborted: recent errors or cost high\n")
                except Exception:
                    pass
                print("[backfill] recent errors or estimated cost exceeds soft budget, aborting backfill")
                return

            try:
                with open(lock_path, "w", encoding="utf-8") as f:
                    f.write(str(os.getpid()))
                internal_lock_acquired = True
            except Exception:
                print(f"[backfill] unable to create lock {lock_path}, aborting")
                return

        if args.dry_run:
            print(f"[dry_run] lock_mode={'external' if external_lock else 'internal'} agent={agent_id} key_turn_candidates={len(key_candidates)}")
            for i, m in enumerate(key_candidates[:10], 1):
                print(f"  - {i}. {m.from_name}: {m.text[:120]}")
            return

        if time.monotonic() - started > args.max_runtime_sec:
            print("[backfill] aborted: max runtime exceeded before write phase")
            return

        with get_conn(CFG) as conn:
            with conn.cursor() as cur:
                try:
                    checksum = hashlib.sha256(open(args.html, "rb").read()).hexdigest()
                except Exception:
                    checksum = None

                if checksum:
                    insert_chat_file_idempotent(
                        cur,
                        args.user_id,
                        args.session_id,
                        "telegram_html",
                        args.html,
                        checksum,
                        {"agentId": agent_id},
                    )

                for i, chunk in enumerate(chunks, 1):
                    if time.monotonic() - started > args.max_runtime_sec:
                        print(f"[backfill] aborted: max runtime exceeded at chunk {i}")
                        break

                    cid = stable_chunk_id(chunk)
                    dialog = messages_to_dialog(chunk)
                    try:
                        human, structured = summarize_chunk(client, dialog, model=model, timeout_sec=args.chunk_timeout_sec)
                    except Exception as e:
                        print(f"[backfill] chunk {i} summarize timeout/error: {e}")
                        continue

                    meta = {
                        "backfill": True,
                        "source": "telegram_html",
                        "chunk_index": i,
                        "chunk_id": cid,
                        "structured": structured,
                        "agentId": agent_id,
                    }
                    insert_summary(cur, args.user_id, args.session_id, -1, -1, human, meta=meta)
                    conn.commit()  # chunk-level commit for recoverability

        for m in key_candidates:
            role = "user" if m.from_name.lower().startswith("hua") else "assistant"
            log_turn(
                args.user_id,
                args.session_id,
                role,
                m.text,
                meta={"backfill": True, "source": "telegram_html", "from": m.from_name, "ts": m.ts, "agentId": agent_id},
            )

        print(f"[backfill] done. summaries<= {len(chunks)} key_turns={len(key_candidates)} agent={agent_id}")

    finally:
        if internal_lock_acquired:
            try:
                if os.path.exists(lock_path):
                    os.remove(lock_path)
            except Exception:
                pass


if __name__ == "__main__":
    main()
