# INDEX（常用入口 / 人类式“常用记忆”）

> 目标：把最常用、最稳定、最关键的入口放在一个地方（像人的“常用记忆”）。
> 使用：任何 `/new` 之后先看这里；任何涉及改配置/改流程先从这里跳转。

## 0) 立即入口（/new 后 60 秒恢复）
- `/new` 防断层清单：`/Users/apple/clawd/library/new_aftercare_checklist.md`
- 宪法层（长期规则/SOP）：`/Users/apple/clawd/MEMORY.md`

## 1) 智能体体系（名字/性格/模型/群）
- 全员身份卡汇总（SSOT）：`/Users/apple/clawd/library/agents_identity_roster.md`
- 命名/群绑定对齐表：`/Users/apple/clawd/library/agents_roster.md`
- 各智能体人格设定（权威）：`/Users/apple/clawd-agents/*/IDENTITY.md` + `SOUL.md`

## 2) 讨论与协作（会议室）
- 议题讨论区：`/Users/apple/clawd/shared/meeting_room.md`
- 技术提案汇总（探哥维护）：`/Users/apple/clawd/shared/handoffs/tech-proposals.md`

## 3) 任务可靠性（必须可审计）
- 监控脚本：`/Users/apple/clawd/cron_logs/job_monitor.py`
- 注册表：`/Users/apple/clawd/cron_logs/job_registry.json`
- 当日日志：`/Users/apple/clawd/cron_logs/YYYY-MM-DD.jsonl`
- isolated done-marker：
  - 规则：`/Users/apple/clawd/cron_logs/marker_rules.json`
  - 脚本：`/Users/apple/clawd/cron_logs/job_marker.py`

## 4) 记忆沉淀（日记/可追溯）
- 当日流水账：`/Users/apple/clawd/memory/YYYY-MM-DD.md`
- 每日精炼（23:10 cron）：把 3–7 条长期有效项写回 `MEMORY.md`

## 5) 资料库（可复用工件）
- CTF 4A 数据契约工件：`/Users/apple/clawd/library/ctf_4a_contract/`
- 写作模板库：`/Users/apple/clawd/library/writing/`
- 精华归档：`/Users/apple/clawd/library/highlights/`

## 6) 记忆系统 × LongCtx（开发与运维）
- 总览：`/Users/apple/clawd/library/memory-system/README.md`
- 架构：`/Users/apple/clawd/library/memory-system/ARCHITECTURE.md`
- 开发：`/Users/apple/clawd/library/memory-system/DEVELOPER_GUIDE.md`
- 运维：`/Users/apple/clawd/library/memory-system/OPERATIONS_RUNBOOK.md`

## 7) 主控身份
- 哆啦Ai熊身份卡：`/Users/apple/clawd/IDENTITY.md`
