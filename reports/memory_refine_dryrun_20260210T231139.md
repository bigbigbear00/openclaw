# 每日记忆精炼 Dry-Run

- 执行时间：2026-02-10 23:11 (Asia/Shanghai)
- 任务：记忆精炼_每日
- 锁检查：`/tmp/memory_backfill.lock` 不存在（通过）
- 并发规避：通过 lock 机制确认未与回填并发

## Candidate summaries（dry-run，仅预览）

1. **晋升策略变更（高优先级）**  
   当日用户决策：B 类草稿全部不晋升；3 条敏感条目保留人工复核，不自动入长期记忆。

2. **记忆目录标准化方案 B 已落地（高优先级）**  
   专题记忆迁移到 `memory/topics/`，新增迁移映射 `memory/migrations/2026-02-10_topic_relayout_map.md`，并重建 `memory/INDEX.md` 分层索引。

3. **Memory×LongCtx 统一写入链路首批改造（高优先级）**  
   在 `memory_system/memory_v1_rag.py` 增加统一摘要写入/幂等接口，摘要 metadata 标准化；检索优先级调整为 compaction > periodic。

4. **LongCtx runtime 接入统一接口（中高优先级）**  
   `scripts/longctx_runtime.py` 优先调用 `memory_write_summary`，失败才回退 sqlite，审计时间改为实时 UTC。

5. **灰度范围扩大与治理共识（中高优先级）**  
   LongCtx 灰度已扩展至 `ctf-director`（pilot：main/news-analyst/ctf-director）；7/7 agent 宣贯 ACK 完成，治理口径明确“library-keeper 审计上报，阻断/降级由主控执行”。

## Dry-run 判定

- 结果：通过（候选均为“规则/架构/治理级”长期价值条目）
- 自动策略建议：允许写入 MEMORY.md（非外部动作、非破坏性、符合长期记忆晋升规则）
