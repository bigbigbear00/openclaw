"""memory_system.app.chat_entry

Reference entrypoint (non-tmp).

Responsibilities:
- Read env config
- Initialize OpenAI client (SDK 1.x)
- Delegate memory logic to memory_system.memory_v1_rag

This file intentionally keeps business logic minimal so the plugin stays swappable.
"""

from __future__ import annotations

import os

from openai import OpenAI

from memory_system.memory_v1_rag import CFG, handle_user_message


_CLIENT: OpenAI | None = None


def _get_client() -> OpenAI:
    """Lazy singleton client.

    Avoid creating a new client for each request.
    """
    global _CLIENT
    if _CLIENT is None:
        # API key must come from env; never hardcode.
        _CLIENT = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _CLIENT


def llm_summarize_func(prompt: str) -> str:
    client = _get_client()
    model = os.getenv("SUMMARY_MODEL", "gpt-4.1-mini")
    try:
        resp = client.responses.create(model=model, input=prompt)
        return resp.output_text
    except Exception as e:
        # Let caller decide how to record failures.
        raise RuntimeError(f"llm_summarize_func failed: {e}")


def llm_reply_func(user_query: str, memory_context: str) -> str:
    client = _get_client()
    model = os.getenv("REPLY_MODEL", "gpt-4.1")

    prompt = (
        "你是一个会使用记忆的助手。\n"
        "规则：只使用 MEMORY_CONTEXT 中的信息；如果没有相关信息，明确说不知道。\n\n"
        f"MEMORY_CONTEXT:\n{memory_context}\n\n"
        f"USER_QUERY:\n{user_query}"
    )

    try:
        resp = client.responses.create(model=model, input=prompt)
        return resp.output_text
    except Exception as e:
        raise RuntimeError(f"llm_reply_func failed: {e}")


def handle(user_id: str, session_id: str, user_input: str) -> str:
    """Plugin single entrypoint.

    The host app should call ONLY this function.
    """
    return handle_user_message(
        user_id=user_id,
        session_id=session_id,
        user_input=user_input,
        llm_reply_func=llm_reply_func,
        llm_summarize_func=llm_summarize_func,
        cfg=CFG,
        model_reply=os.getenv("REPLY_MODEL", "gpt-4.1"),
        model_summary=os.getenv("SUMMARY_MODEL", "gpt-4.1-mini"),
    )
