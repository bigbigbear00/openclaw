# MEMORY.md Patch Preview (human-readable)

Generated: 2026-02-09T11:41:00+08:00

This document is a non-destructive preview of proposed changes to /Users/apple/clawd/MEMORY.md. It does NOT apply any change. Review and tell me to apply or modify.

---

Summary of proposed edits

1) Add `alias` entries for renamed jobs
   - Rationale: preserve historical searchability for items renamed (e.g., "小档" → "小雅").
   - Proposed text to insert under the existing authorization section:

   "Aliases: (for historical names)
   - 小雅每日知识审阅: alias [\"小档每日知识审阅\"]
   - 小雅知识审阅_done_marker: alias [\"小档知识审阅_done_marker\"]"

2) Update authorization header to reflect current status and effective date
   - Rationale: the authorization block currently lists dates 2026-02-06 to 2026-02-08. Update to show "effective: 2026-02-06 (reviewed 2026-02-09)".
   - Proposed replacement of the top line under "重大授权" with a single sentence noting the effective date and reviewer.

3) Add a short "Core Files & Owners" table
   - Rationale: make it immediately clear where the truth sources live and who to contact.
   - Proposed table (to place near top):

   | File | Purpose | Owner (agent id) |
   |---|---|---|
   | /Users/apple/clawd/cron_logs/job_registry.json | Task registry | agent:main |
   | /Users/apple/.openclaw/openclaw.json | Gateway config (agents & bindings) | agent:main |
   | /Users/apple/claw_comm/<agent>/inbox.jsonl | Agent inboxes | owner = respective agent |

4) Move long historical audit examples into an archive section with cross-reference
   - Rationale: keep MEMORY.md concise; preserve history in /Users/apple/clawd/archive/memory_history_<ts>.md
   - Proposed action: create archive file and replace large example blocks in MEMORY.md with a single link line: "See archive/memory_history_20260209.md for historical examples." (I will not delete current examples; preview shows replacement only.)

5) Add a final "Runbook" note for maintenance
   - Rationale: instruct future upgrades on how to preserve or migrate the memory file during gateway/agent updates.
   - Proposed addition at bottom:

   "Runbook: When upgrading OpenClaw or migrating agents, follow steps: 1) archive MEMORY.md, 2) run cron_guard dry-run, 3) review proposed patches, 4) apply changes and audit."

---

Preview (contextual snippets)

A) Insert alias block (proposed location: below the authorization paragraph):

```
Aliases: (for historical names)
- 小雅每日知识审阅: alias ["小档每日知识审阅"]
- 小雅知识审阅_done_marker: alias ["小档知识审阅_done_marker"]
```

B) Replace header sentence (proposed):

Original header excerpt:
"2026-02-06 至 2026-02-08 — 批注与授权记录："

Proposed replacement:
"生效: 2026-02-06（最近审核: 2026-02-09）。以下为主控代理长期授权记录；如需修改请在本文件顶部署名并写入当日 memory/YYYY-MM-DD.md。"

C) Core files table (proposed insertion near top):

```
| File | Purpose | Owner |
|---|---|---|
| /Users/apple/clawd/cron_logs/job_registry.json | Task registry (source of truth for scheduled jobs) | agent:main |
| /Users/apple/.openclaw/openclaw.json | Gateway runtime config (agents & bindings) | agent:main |
| /Users/apple/clawd/config/agent_group_map.json | Agent ↔ Telegram group map | agent:main |
```

D) Archive placeholder (replace long examples):

Replace the long "审计样例（2026-02-08）" block with:

```
Historical audit examples have been archived to: /Users/apple/clawd/archive/memory_history_20260209.md
```

E) Runbook snippet (append to bottom):

```
Runbook: When upgrading or migrating OpenClaw:
1) Archive MEMORY.md to /Users/apple/clawd/archive
2) Run /Users/apple/clawd/plugins/cron_guard/cron_guard.py scan (dry-run)
3) Review generated report and patch preview
4) Apply authorized changes and write an audit entry to /Users/apple/clawd/reports/
```

---

If you approve this preview, I will:
- Produce a clean patch (human-readable) showing exactly what lines to add/replace.  
- Save the patch preview to /Users/apple/clawd/reports/memory_patch_preview_20260209.diff.md for your review.  

Reply: "Apply patch preview" to generate the preview file (no change to MEMORY.md), or "Modify" with instructions.  
