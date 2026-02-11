"""memory_system.scripts.smoke_test

Smoke test for V1 memory plugin.

Modes:
- Without OPENAI_API_KEY: verifies DB write + retrieval only.
- With OPENAI_API_KEY: runs full handle() including LLM call.

Usage:
  python -m memory_system.scripts.smoke_test --user_id u1 --session_id s1 --text "hello"

Env:
  OPENAI_API_KEY  (optional)
  SUMMARY_MODEL, REPLY_MODEL (optional)
"""

from __future__ import annotations

import argparse
import os

from memory_system.memory_v1_rag import log_turn, retrieve_memory_context


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user_id", required=True)
    ap.add_argument("--session_id", required=True)
    ap.add_argument("--text", required=True)
    args = ap.parse_args()

    user_id = args.user_id
    session_id = args.session_id
    text = args.text

    # Always test cold-memory write
    turn_id = log_turn(user_id, session_id, "user", text)
    print(f"[ok] inserted user turn id={turn_id}")

    # Retrieval should work without any API key
    ctx, metrics = retrieve_memory_context(user_id, session_id, text)
    print("[ok] retrieved MEMORY_CONTEXT (truncated):")
    print(ctx[:800] + ("..." if len(ctx) > 800 else ""))
    print("[metrics]", metrics)

    if "OPENAI_API_KEY" not in os.environ:
        print("[skip] OPENAI_API_KEY not set; skipping LLM generation")
        return 0

    # Full path
    from memory_system.app.chat_entry import handle

    reply = handle(user_id=user_id, session_id=session_id, user_input=text)
    print("[ok] reply:")
    print(reply)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
