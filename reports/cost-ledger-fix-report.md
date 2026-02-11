Cost Ledger Fix — Report

generated_at: 2026-02-08T15:26 (Asia/Shanghai)

Actions:
- Updated pricing_table.json with OpenAI exact values per instruction for gpt-5-mini, gpt-5, gpt-5.2.
- Marked Google / google-antigravity models as internal_free with pricing_status field; cost_usd_external set to null.
- Added pricing_status and cost_usd_external fields for all models.
- Modified comm_validator.py to always write cost records to metrics/topic_costs.jsonl (per new instruction).

Summary of model pricing status:
- exact: openai/gpt-5-mini, openai/gpt-5, openai-codex/gpt-5.2
- unknown: openai/gpt-5-pro, openrouter/auto
- internal_free: google/gemini-2.5-flash, google/gemini-2.5-pro, google-antigravity/gemini-3-pro-low, google-antigravity/gemini-3-flash, google-antigravity/claude-opus-4-6-thinking, openrouter/openrouter/free

Files updated:
- /Users/apple/clawd/library/pricing_table.json
- /Users/apple/clawd/scripts/comm_validator.py
- /Users/apple/clawd/metrics/topic_tokens.jsonl (unchanged)
- /Users/apple/clawd/metrics/topic_costs.jsonl (now will receive entries)

Notes:
- All changes follow instruction to not expand functionality beyond cost governance fixes.

