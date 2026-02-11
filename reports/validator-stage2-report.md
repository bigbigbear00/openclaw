Validator Stage 2 — Self-check Report

generated_at: 2026-02-08T13:50 (Asia/Shanghai)

Scope:
- Implemented minimal comm_validator (Stage 2 MVP) that checks model provider existence against local model catalog and performs a simple cost estimate using pricing_table.json. It appends topic cost records to metrics/topic_costs.jsonl.

Files created:
- /Users/apple/clawd/library/pricing_table.json
- /Users/apple/clawd/scripts/comm_validator.py
- /Users/apple/clawd/metrics/topic_costs.jsonl

Model alignment check:
- Source catalog: /Users/apple/clawd/library/models/catalog.json
- agents-full-status.json contains agents with model_provider fields; many entries use provider-level names (e.g., "google-antigravity", "openai"). The validator flags any provider that doesn't have a direct model id prefix match in the catalog as needs_resolution.

Resolution notes:
- For full compliance, each agent should include a concrete model id (e.g., "google-antigravity/gemini-3-pro-low") in the roster (model_effective). Current roster has model_provider only for some agents; these are marked for resolution.

Limitations (per Stage 2 constraints):
- The validator does not perform token counting or real model calls (cost is an estimate based on provided meta.input_tokens / meta.output_tokens).
- Does not modify agents or models; does not scan all inbox files.

Next steps (Stage 3 planning):
- Expand comm_validator to verify file existence, checksums, and to perform automated link validation.
- Integrate token counters and real cost accumulation via model usage logs.

