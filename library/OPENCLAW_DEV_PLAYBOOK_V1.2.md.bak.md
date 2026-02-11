OPENCLAW DEV PLAYBOOK — V1.2 (Final)

Generated: 2026-02-08T15:42 (Asia/Shanghai)
ssot_version: v1.2

1) 项目定位（1页）

OpenClaw 是一个面向组织的“数位公司操作系统”，它并非单纯的聊天机器人，而是把多种 Agent（数字员工）、调度器、审计与记账机制、消息总线以及运维监控结合，构成公司级的信息生产、处理与发布平台。

核心理念：
- Hub-and-spoke 架构（主控 main 负责统筹与派单；各专责 agent 执行与产出）；
- 文件总线（Message Bus）为首要通信机制：每个 agent 使用 append-only inbox.jsonl + artifacts 目录交换结构化消息与产物；
- 工作流分层（S1–S4）保证既能极速交付（S1）又能产出可发布成品（S3）；
- 在 Telegram 限制下，通信走文件总线与 ops_board 汇报，Telegram 仅作老板汇报 / Gate 通告通道。

2) Stage 1–3 已完成里程碑

Stage 1 — 制度落盘（完成项）
- SYSTEM_BLUEPRINT.md：系统宪法蓝图（Message Bus、工程宪法、S1–S4、Budget tiers、六道断路器、Gates、Reality Sync、Onboarding）
- agents-full-status.json / agents-full-status.md：团队 SSOT roster（按 priority、包含 identity_path、inbox/ artifact 路径等）
- workflow_registry.yaml：固定流程骨架（S1–S4，占位 dag_handoff_order 与 default_limits）

Stage 2 — 最小成本治理（完成项）
- library/pricing_table.json：初步价格表（OpenAI exact 值写入；其他 provider 标注 internal_free/unknown）
- scripts/comm_validator.py：最小验证器（记录 token usage；基于 pricing 写 cost records；校验 model provider 在 catalog）
- metrics/topic_tokens.jsonl and metrics/topic_costs.jsonl：账本/记账位置（tokens 永远记账；costs 写入策略按 pricing）

Stage 3 — 运营化最小闭环（完成项）
- scripts/watch_inboxes.py：minimal watcher（offset、ack、dedupe，写 topics_state.json）
- metrics/ops_board.md：ops board snapshot（Active/Blocked/Frozen/Done）
- metrics/topics_state.json：topic 状态机（最小字段）
- model alignment：agents-full-status.json 中 model_effective 已对齐 catalog 中具体 id；agent_count 校正为 8

3) 系统宪法（Engineering Constitution）

Hub-and-spoke：
- main（哆啦Ai熊）为唯一 Hub，拥有拆分、派单、升级与触发 backup 的权限；Spoke（各 agent）只接受任务、执行并把产物与状态写回其 inbox。

固定 SOP（S1–S4） vs 随机 Mesh（暂未启用）
- S1 情报快报：短频次、低延迟、轻量验证。
- S2 行业深报：中等深度，来源验证齐备。
- S3 出版线：对外发布，需 Gate 审批。
- S4 运营线：任务可靠性/审计/记录。
- 随机 Mesh（Discovery→Execution）为轻量触发流，暂作为占位，不在 Stage 3 自动化。

六道铁闸断路器（rounds/ttl/depth/loop/dedupe/rework）
- rounds：默认 3 往返；ttl：默认 2 小时；depth/loop/dedupe/rework 为策略参数并记录在 policy 文件。

Gates（A–E）与老板审批点
- Gate A（S1 快速）: main 直接 approve
- Gate B（S2）: main + subject-matter sign-off
- Gate C（S3 出版）: main + writer-editor + owner
- Gate D（预算超额）: 需老板批准
- Gate E（紧急）: 直接上报老板（Telegram）

4) SSOT 文件清单（唯一真源）

以下文件为本次 V1.2 的单一真源（SSOT），请在变更时更新并经 main 批准：
- /Users/apple/clawd/library/SYSTEM_BLUEPRINT.md
- /Users/apple/clawd/reports/agents-full-status.json
- /Users/apple/clawd/library/workflow_registry.yaml
- /Users/apple/clawd/library/pricing_table.json
- /Users/apple/clawd/scripts/comm_validator.py
- /Users/apple/clawd/scripts/watch_inboxes.py
- /Users/apple/clawd/metrics/ops_board.md
- /Users/apple/clawd/metrics/topic_tokens.jsonl
- /Users/apple/clawd/metrics/topic_costs.jsonl

5) 成本治理（Cost Governance）

分类与字段：pricing_table.json 中每个 model 有字段 pricing_status（exact/unknown/internal_free）和 cost_usd_external（exact 有值；unknown/internal_free 为 null）
记账规则：
- tokens 永远记账（metrics/topic_tokens.jsonl）
- cost 也必须写入 ledger（metrics/topic_costs.jsonl），但当 cost 为 unknown/null 表示外部成本不可应用；仍写入一条记录并标注 pricing_status
- Gates/Breaker：token 阈值触发（默认 warn 200k / gate 500k / breaker 1M tokens）；美元阈值在 pricing 生效后启用

6) 当前模型状态（2026-02-08）

引用 cost-ledger-fix-report.md：
- exact：openai/gpt-5-mini, openai/gpt-5, openai-codex/gpt-5.2
- internal_free：google/gemini-2.5-flash, google/gemini-2.5-pro, google-antigravity/gemini-3-pro-low, google-antigravity/gemini-3-flash, google-antigravity/claude-opus-4-6-thinking
- unknown：openai/gpt-5-pro, openrouter/auto

策略：internal_free 模型暂视为内部执行免费；external cost 需在 pricing 表填定后启用美元阈值报警

7) Pilot Week 试运营规则（7天）

目的：验证 S1–S3 的闭环、Gate 运转与成本计账
- 只运行固定 SOP（S1–S3），每天 20:00 生成日报并通过 Telegram 向老板发布 ops_board 小结（Active/Blocked/Needs User）
- 老板关注点仅限 ops_board + Blocked / Needs User

8) 下一次升级路线（Stage 4+）

- Stage 4：Publishing Gates（sources/risk/verified）
- Stage 5：Dynamic Mesh（需人工批准为策略性变更）
- Stage 6：自动 on-boarding 扩编（仅在治理与审计完备后）

9) 恢复与迁移指南（Disaster Recovery）

必备备份目录（最低）：
- /Users/apple/clawd/library/
- /Users/apple/clawd/reports/
- /Users/apple/clawd/memory/
- /Users/apple/clawd/cron_logs/
- /Users/apple/clawd/claw_comm/
- /Users/apple/clawd/metrics/

恢复步骤（简要）：
1) 从备份还原 library/ 与 reports/、cron_logs/、claw_comm/ 与 metrics/
2) 启动 main agent，运行 sync_model_catalog.py 并验证 catalog.json
3) 依次运行 scripts/watch_inboxes.py 与 scripts/comm_validator.py 的自检（不对外调用）
4) 检查 ops_board.md 与 topics_state.json 的最新状态；若有 missing/blocked，人工介入

附录：重要文件列表与路径（SSOT 重复）

---- end of playbook ----
