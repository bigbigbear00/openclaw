# memory_system × longctx 一体化（A 方案）执行单

时间：2026-02-11 21:26 CST
状态：已启动

## 0. 目标
- 以 LongCtx 为运行时主轴，memory_system 为统一写入与存储主轴，RAG 为统一读取主轴。
- RAG 采用双域：聊天记忆域（Conversation RAG）+ 文件资料域（Document RAG）。
- 取消自动回填，回填改人工触发（已执行：cron disabled）。
- 将“重复写入、重复检索、上下文膨胀”纳入可观测指标。

## 1. 当前基线（已采样）
- overflow 审计条目：902
  - write_path=unknown: 502
  - write_path=none: 400
- 去重历史：
  - exact 删除：152
  - vector 删除：0
  - vector 候选：0
- staging longctx 集成回放：2 次（最新：transcripts/staging_run_1770815659.jsonl）

## 2. A方案落地拆解
### A1（P0）统一写入口与幂等键（本轮）
- 约束：摘要/compaction 仅允许通过 memory_v1_rag 统一接口写入。
- 约束：request_id/chunk_id/checksum 为唯一幂等键体系。
- 验收：不再出现“同一来源多路径写入”的重复条目。

### A2（P0）统一检索优先级（本轮）
- 顺序固定：compaction > periodic summary > raw turns。
- 验收：同query召回中重复语义片段下降。

### A3（P1）重复率可观测（本轮）
- 新增每日指标：
  1) 入库重复率（exact/semantic）
  2) 检索重复命中率
  3) LongCtx compaction 触发率/成功率/回退率
- 输出到 reports/ 下日报。

### A4（P1）回填人工化SOP（本轮）
- 自动回填保持禁用。
- 人工触发脚本统一：scripts/run_backfill_guarded.sh。
- 验收：仅在人工明确触发时运行。

## 3. 风险与防线
- 风险：历史任务/脚本仍绕过统一写入口。
  - 防线：加巡检脚本扫描写入路径与日志。
- 风险：并发运行导致 state 文件交错。
  - 防线：run_id 分片 state/log（下一轮改造）。

## 4. 下一步
1) 实施 A1/A2 代码约束与检查脚本。
2) 产出首份“重复率日报”并建立阈值。
3) 验证 24h 稳定后再考虑优化吞吐。
