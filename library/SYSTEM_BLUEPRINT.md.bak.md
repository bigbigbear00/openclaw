ssot_version: v1.2
generated_at: 2026-02-08T10:18:00+08:00

# OpenClaw 数位公司操作系统（V1.2 FINAL）

## 概要
本文件为 OpenClaw V1.2 的制度蓝图（SSOT），仅用于制度文件落盘与 SSOT 固化阶段（Stage 1）。内容为核心通信总线、工程宪法、工作流骨架、预算分层、断路器、审批 Gates、Reality Sync 与入职/挂起机制。

## Message Bus
- 基本构件：inbox.jsonl（append-only newline-delimited JSON） + artifacts 目录
- 位置范例：/Users/apple/clawd/claw_comm/<agent>/inbox.jsonl 和 /Users/apple/clawd/claw_comm/<agent>/artifacts/
- 语义：所有 agent 间的请求/回复/通知以结构化 JSON 记录到收件者的 inbox.jsonl；artifact 存放在 artifacts/ 并通过 payload_path 引用。

## 工程宪法：Hub-and-spoke
- 架构：main（哆啦Ai熊）为唯一 Hub，有权限拆分与派单；所有其他 Agent 为 Spoke，接收并执行任务。
- 约束：只有 main 可创建/授权新任务、触发 backup；Spoke 只负责执行并在 inbox 写回复/产物路径。

## 固定工作流 S1-S4（简述）
- S1 情报快报：短频次、低延迟、快速验证 → 主要用于时敏摘要（例：每日早报）。
- S2 行业深报：中等深度，需证据链与来源引用（例：周报/行业分析）。
- S3 出版线：面向对外发布的最终稿件，须满足高验证级别与发布审批。
- S4 运营线：内部运维/任务可靠性/审计等。
- 随机工作流：Discovery → Execution（发现 → 执行）的轻量触发链路，按必要嵌入 S1-S4。

## Budget tiers
- 定价分层用于评估任务可用预算：
  - Tier $0.1 — minimal (L3)
  - Tier $0.5 — standard (L2)
  - Tier $1.5+ — heavy compute / deep analysis (L1)
- 在 workflow registry 中每个流程可指定 default_budget_tier。

## 六道铁闸断路器（Circuit Breakers）
- rounds：最大往返轮次（默认 3）
- ttl：话题总时限（默认 2 小时）
- depth：消息深度/嵌套限制（占位 config）
- loop：重复/循环检测与 dedupe（防止重复触发）
- dedupe：对相同 job_id/snapshot 的去重策略
- rework：当验证失败时触发的修订次数与上限

## Gates（A-B-C-D-E） — 审批点
- Gate A：快速发布许可（S1，main 可直接 approve）
- Gate B：中等审查（S2，需 main+subject-matter agent sign-off）
- Gate C：出版批准（S3，需 main + writer-editor + owner）
- Gate D：预算超额审批（任何流程超过 default_budget_tier）
- Gate E：紧急干预（超时/故障/安全事件，直接上报老板）

## Budget & Gates — tokens-first enforcement
- 默认门槛基于 token 使用量：WARN=200k / GATE=500k / BREAKER=1M tokens。Token 阈值永远优先于美元阈值。
- USD（external cost）门槛仅在 pricing_table.json 中 pricing_status == "exact" 时启用；否则 USD 检查被视为不可用，并以 tokens-first 决定流程。
- internal_free 或 unknown 的模型不得通过将成本写为 $0 来规避 token gate；在 ops_board 中应显式标注为 INTERNAL_FREE 并显示 tokens consumed。

## Reality Sync
- ops_board（主控面板）+ Telegram 汇报用于老板（你）日常快速同步与确认，并用于正式汇报通道（只用于老板汇报）。

## Onboarding：新 Agent 入职四步走 + suspended 机制
1) Register identity card（写入 /Users/apple/clawd-agents/<agent>/IDENTITY.md）
2) Create inbox & artifacts（/Users/apple/clawd/claw_comm/<agent>/）
3) Seed policy & ack（主控向 inbox 写 seed notice，Agent 回复 ack）
4) Trial tasks（分配一条 trial request，验证能写 done）
- suspended：若 Agent 连续 2 次超时/未回复且未能给出合理说明，Agent 状态标 suspended，由 main 或老板决定恢复流程。

## 备注
- Stage 1 限制：本阶段仅进行制度文件落盘与 SSOT 固化；禁止新增 Agent、修改模型 provider、实现 validator 脚本或批量扫描 inbox。


