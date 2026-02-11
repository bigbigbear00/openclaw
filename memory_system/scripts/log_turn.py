"""log_turn.py

Tiny CLI helper to append one chat turn into Postgres (cold memory).

Usage:
  source /Users/apple/clawd/.venv/bin/activate
  python -m memory_system.scripts.log_turn \
    --user_id hua --session_id tg_8555612162_main --role user --content "hi" \
    --meta '{"channel":"telegram","message_id":"123"}'

This is intentionally simple so the main agent can call it via exec.
"""

import argparse
import json

from memory_system.memory_v1_rag import log_turn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user_id", required=True)
    ap.add_argument("--session_id", required=True)
    ap.add_argument("--role", required=True, choices=["user", "assistant", "system"])
    ap.add_argument("--content", required=True)
    ap.add_argument("--meta", default="{}")
    args = ap.parse_args()

    try:
        meta = json.loads(args.meta) if args.meta else {}
    except Exception:
        meta = {"_meta_raw": args.meta}

    turn_id = log_turn(
        user_id=args.user_id,
        session_id=args.session_id,
        role=args.role,
        content=args.content,
        meta=meta,
    )

    print(turn_id)


if __name__ == "__main__":
    main()
