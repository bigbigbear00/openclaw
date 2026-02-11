# SYSTEM AUDIT SNAPSHOT
Generated:
2026-02-09T14:26:03.283186

## 1) Repo Tree (top-level under clawd/)
- .DS_Store — file
- .clawdhub/ — inferred purpose: data
- .venv/ — inferred purpose: data
- AFTER_RESTART_CHECKLIST.md — file
- AGENTS.md — file
- BOOTSTRAP.md — file
- HEARTBEAT.md — file
- IDENTITY.md — file
- MEMORY.md — file
- SOUL.md — file
- TOOLS.md — file
- USER.md — file
- V1_C02.md — file
- V1_C03.md — file
- agent_upgrade_plan.md — file
- agents_runtime/ — inferred purpose: core
- archive/ — inferred purpose: reports
- assets/ — inferred purpose: data
- bin/ — inferred purpose: scripts
- canvas/ — inferred purpose: data
- claw_comm/ — inferred purpose: core
- config/ — inferred purpose: data
- cron_logs/ — inferred purpose: data
- ctf_collects/ — inferred purpose: data
- data/ — inferred purpose: data
- generated-images/ — inferred purpose: data
- library/ — inferred purpose: data
- logs/ — inferred purpose: data
- memory/ — inferred purpose: data
- memory_system/ — inferred purpose: data
- metrics/ — inferred purpose: data
- models — file
- plugins/ — inferred purpose: plugin
- reports/ — inferred purpose: reports
- scripts/ — inferred purpose: scripts
- shared/ — inferred purpose: data
- skills/ — inferred purpose: plugin
- tmp/ — inferred purpose: data
- tmp_pdf.txt — file
- tmp_test_msg.json — file
- transcripts/ — inferred purpose: data
- vietnam_re_training/ — inferred purpose: data

## 2) Active Runtime (process summaries)
ps scan:
```
apple            22217  11.0  2.5 444985360 423552   ??  S     2:16PM   0:15.70 openclaw-gateway    
apple            50857   0.0  0.1 411887344  13312   ??  S    Sun12AM   0:04.63 /Users/apple/clawd/skills/xiaohongshu-mcp/bin/xiaohongshu-mcp-darwin-arm64
```

pm2 ls:
```
┌────┬──────────────────────────────┬─────────────┬─────────┬─────────┬──────────┬────────┬──────┬───────────┬──────────┬──────────┬──────────┬──────────┐
│ id │ name                         │ namespace   │ version │ mode    │ pid      │ uptime │ ↺    │ status    │ cpu      │ mem      │ user     │ watching │
├────┼──────────────────────────────┼─────────────┼─────────┼─────────┼──────────┼────────┼──────┼───────────┼──────────┼──────────┼──────────┼──────────┤
│ 11 │ index-reader-ctf-director    │ default     │ N/A     │ fork    │ 22581    │ 0      │ 5408 │ waiting … │ 0%       │ 0b       │ apple    │ disabled │
│ 5  │ worker-ctf                   │ default     │ N/A     │ fork    │ 0        │ 0      │ 0    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 2  │ worker-ctf-director          │ default     │ N/A     │ fork    │ 0        │ 0      │ 0    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 6  │ worker-designer              │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 7  │ worker-library-keeper        │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 8  │ worker-main                  │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 3  │ worker-nba                   │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 0  │ worker-nba-expert            │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 9  │ worker-news-analyst          │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 10 │ worker-vn-realestate         │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 4  │ worker-writer                │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
│ 1  │ worker-writer-editor         │ default     │ N/A     │ fork    │ 0        │ 0      │ 2    │ stopped   │ 0%       │ 0b       │ apple    │ disabled │
└────┴──────────────────────────────┴─────────────┴─────────┴─────────┴──────────┴────────┴──────┴───────────┴──────────┴──────────┴──────────┴──────────┘
```

launchctl list (filtered):
```
PID	Status	Label
68715	0	application.com.tencent.xinWeChat.262172259.262172267
-	0	com.apple.SafariHistoryServiceAgent
-	-9	com.apple.progressd
-	0	com.apple.enhancedloggingd
8953	-9	com.apple.cloudphotod
-	-9	com.apple.MENotificationService
606	0	com.apple.Finder
713	0	com.apple.homed
8596	-9	com.apple.dataaccess.dataaccessd
-	0	com.apple.quicklook
-	0	com.apple.parentalcontrols.check
-	0	us.zoom.updater
739	0	com.apple.mediaremoteagent
647	0	com.apple.FontWorker
50857	0	com.openclaw.xiaohongshu-mcp
1852	-9	com.apple.bird
-	0	com.apple.amp.mediasharingd
-	-9	com.apple.knowledgeconstructiond
18200	-9	com.apple.inputanalyticsd
```

Conclusion: openclaw-gateway is running (ai.openclaw.gateway), pm2 shows index-reader waiting and workers stopped; launchctl contains com.openclaw.xiaohongshu-mcp.

## 3) Agent Registry (digital staff)
- agents_runtime/ exists; agents-full-status.json not present

Main agent: agent:main (哆啦Ai熊) — owner/primary controller

## 4) Memory System (cold memory)
- memory.db exists at /Users/apple/clawd/memory_system/db/memory.db — chat_turns rows = 112
- Recent metrics (last 5):
  - (10, '2026-02-09 05:49:33', 'CTF', 'hybrid', 10)
  - (9, '2026-02-09 05:45:46', '2026', 'hybrid', 10)
  - (8, '2026-02-09 05:42:15', '4A-enhancement', 'hybrid', 2)
  - (7, '2026-02-09 05:37:51', '4A-enhancement', 'text', 2)
  - (6, '2026-02-09 05:34:54', 'STOP-DO', 'text', 0)
- Active retrievals observed: text and hybrid (from recent metrics)

## 5) Automation Status
- job_registry present — most jobs have enabled=false (STOP-DO)
- pm2 workers: status: stopped for worker-*; index-reader present but waiting
- No active watcher/worker python processes detected (per ps scan)

## 6) Key Entry Points
- Gateway executable: openclaw-gateway (running process)
- memory_system module: /Users/apple/clawd/memory_system/
- Backfill script examples: memory_system/scripts/backfill_telegram_html or memory_system/scripts/backfill.py (search required)

## 7) Custom Code (recently modified files)
- /Users/apple/clawd/memory_system/db/memory.db-shm — mtime=2026-02-09T14:26:03.594708
- /Users/apple/clawd/memory_system/db/memory.db-wal — mtime=2026-02-09T14:26:03.594575
- /Users/apple/clawd/.DS_Store — mtime=2026-02-09T13:59:12.951924
- /Users/apple/clawd/memory_system/.DS_Store — mtime=2026-02-09T13:57:24.187161
- /Users/apple/clawd/memory_system/db/.DS_Store — mtime=2026-02-09T13:56:53.653440
- /Users/apple/clawd/memory_system/db/memory.db — mtime=2026-02-09T13:49:33.224994
- /Users/apple/clawd/memory/2026-02-09.md — mtime=2026-02-09T13:49:33.224784
- /Users/apple/clawd/cron_logs/job_registry.json — mtime=2026-02-09T12:54:19.304917
- /Users/apple/clawd/logs/worker-writer.log — mtime=2026-02-09T12:54:00.656810
- /Users/apple/clawd/logs/worker-vn-realestate.log — mtime=2026-02-09T12:54:00.524050

Marking above as Boss-customized assets (recently edited).

## 8) Boss Summary
- System state: STATIC / STOP-DO (no automatic jobs enabled; workers stopped)
- Top 3 risk points:
  1) index-reader waiting process may hold handles to legacy directories (confirm and stop if needed)
  2) openclaw-gateway running — if fully disabled desired, gateway should be stopped gracefully
  3) memory.db contains local data — ensure backup and access controls
- Next step suggestions:
  1) If you want fully static, stop openclaw-gateway process (manual approval required).
  2) Archive memory.db snapshot and store securely.
  3) Reconcile registry vs gateway config (generate diff)