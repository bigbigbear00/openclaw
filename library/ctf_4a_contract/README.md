# CTF 周大福情报系统 — 4A 数据契约（工件库）

用途：这是可复用、可落库/可校验的“数据契约”工件。它们来自 Gemini Round 5/6 的共识产出（已记录，暂缓实施），用于未来系统实现时直接落地。

## 文件
- `event_card.schema.v1.1.json`：事件卡（Event Card）JSON Schema
- `weekly_deliverable.schema.v1.0.json`：周交付物（Weekly Deliverable）JSON Schema
- `metrics_threshold.yaml`：阈值与评分下限配置

## 设计原则（简短）
- 可追溯：所有关键结论/洞察必须能追溯到 source_event_ids / evidence_event_ids。
- 可判定：mandatory_review_rules 必须可机器判定。
- 可演进：版本号写入文件名；升级时新建 v1.2/v1.3，不覆盖。
