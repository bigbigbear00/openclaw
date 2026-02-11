# Suggested clean-up actions for MEMORY.md
Generated: 2026-02-09T11:38:55.763358

1) Add alias field for renamed entries
- Example: keep historical reference to "小档每日知识审阅" as alias for "小雅每日知识审阅".

2) Update timestamps and scope of authorizations
- If authorization timeframe has changed, update the header to reflect current scope and effective date.

3) Prune or move out-of-date examples
- Move old audit examples older than X months into archive with cross-reference.

4) Add definitive mapping section
- Add a short table mapping core files (job_registry, openclaw.json, agent_group_map) and who owns them.

5) After cleanup, run cron_guard plugin to ensure no regressions.
