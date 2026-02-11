# MEMORY.md health check
Generated: 2026-02-09T11:38:27.757841

Scanned references found in MEMORY.md (heuristic):
- # MEMORY.md
- > 当天流水账写 `memory/YYYY-MM-DD.md`；可复用长文/模板写 `library/`。
- 2. 每次群发必须同时写入该 agent 的 inbox.jsonl（payload_path + timestamp）作为可审计的收悉记录。
- - 记录位置：相关操作与审计均写入 /Users/apple/clawd/memory/YYYY-MM-DD.md 与 /Users/apple/clawd/claw_comm/<agent>/inbox.jsonl ；长期授权写入本文件（MEMORY.md）。
- - request-ctf-post-20260208-002 — 主控在后台请求 ctf-director 在群内发短确认并在 inbox 回执（请求写入 /Users/apple/clawd/claw_comm/ctf-director/inbox.jsonl，memory 写入 2026-02-08.md）。
- - agent_group_map.json — Agent↔群 id 已固化，避免以后发错目标（路径： /Users/apple/clawd/config/agent_group_map.json）。
- - 生效与回滚：本授权立即生效；如需回滚或更改边界，老板可在主对话提出并由主控把变更写入 MEMORY.md（变更同时写入 memory 当日记录）。

Path existence check:
- /Users/apple/clawd/config/agent_group_map.json: EXISTS
- /Users/apple/clawd/claw_comm: EXISTS
- /Users/apple/clawd/memory: EXISTS
- /Users/apple/clawd/cron_logs/job_registry.json: EXISTS

Suggestions:
- Review agent_group_map.json existence and update if moved.
- Ensure inbox paths under claw_comm exist for agents.
