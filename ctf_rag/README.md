# CTF 市场情报记忆系统（RAG）

目标：让 ctf-director（小钻）从“当日信息响应”升级为“历史趋势+当日信号”的连续判断系统。

## 快速开始
1. 按 `schemas/ctf_rag_schema.sql` 建表
2. 采集任务将结构化事件写入 `ctf_events`
3. 每日运行 `pipelines/daily_trend_rollup.md` 生成趋势快照 `ctf_trends_daily`
4. 查询时先走“今日检索+历史趋势检索”双路，再合并生成观点

## 核心表
- `ctf_events`：原子事件（事实）
- `ctf_claims`：可复用观点（结论）
- `ctf_evidence_links`：观点-证据链映射
- `ctf_trends_daily`：趋势快照
- `ctf_topics`：主题词典（4A / 周大福场景）

## 产物
- 日报模板：`prompts/daily_brief_template.md`
- 周报模板：`prompts/weekly_4a_template.md`

## 版本路线
- 7天：先做事件入库+趋势快照+双路检索
- 30天：加入主题漂移检测、观点稳定性评分、自动反证提醒
