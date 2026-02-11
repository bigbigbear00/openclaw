# 主控→代码机交接包（memory_system × longctx 一体化）

时间：2026-02-11 11:26 CST
目标：把“记忆系统 + longctx”合并成单一稳定链路，优先稳定/可恢复。

## 1) 当前症状（已观测）

### 症状A：回填链路双锁冲突
- 外部调度先创建 `/tmp/memory_backfill.lock`，随后脚本内再次检查同一路径，导致“看见锁即退出”。
- 证据：`reports/backfill_3af5e243-a47c-41c7-8453-496fa479713e.log`
  - `state: lock_created`
  - `[backfill] lock present ... exiting`
  - 后续尝试 `BACKFILL_LOCK_MANAGED_EXTERNALLY=1` 才能进入。

### 症状B：进入回填后阻塞超时
- 启用外部托管锁后可进入回填，但出现长时间阻塞，最终被安全中止。
- 证据同上日志：
  - `state: running_backfill_v2`
  - `state: aborted_timeout_v2`
  - `state: lock_removed_manual_after_kill`

### 症状C：历史数据库约束不一致风险
- 曾出现 `ON CONFLICT (checksum)` 失败（缺少对应唯一约束）。
- 代码中虽加了 except fallback 插入，但仍有语义漂移和幂等风险。
- 证据：同日志早期 traceback（InvalidColumnReference）。

## 2) 关键文件与位置
- 回填脚本：`memory_system/scripts/backfill_telegram_html.py`
  - 锁逻辑：约 224 行后（`LOCK_PATH` + `external_lock`）
  - DB写入：`chat_files` 的 `ON CONFLICT(checksum)` 分支
- 运行日志：`reports/backfill_3af5e243-a47c-41c7-8453-496fa479713e.log`
- 状态文件：`reports/backfill_3af5e243-a47c-41c7-8453-496fa479713e.state`
- 规则说明：`reports/cron_memory_guards.md`
- longctx相关脚本：
  - `scripts/longctx_runtime.py`
  - `scripts/longctx_dedupe_mark.py`
  - `scripts/longctx_staging_integration.py`

## 3) 统一架构目标（用户已确认）
1. 控制面统一：锁/超时/重试/并发窗口统一，不再双层互咬。
2. 数据面统一：memory_system 与 longctx 写入链路一致（幂等键、processed_files、summary upsert语义一致）。
3. 验证面统一：同一健康指标与验收脚本（成功率、重复率、阻塞率、回填产出率）。

## 4) 请代码机输出（必须）
A. 根因树（控制面/数据面/运行时）
B. 方案A/B/C（最小改动优先）+取舍
C. 改动清单（路径+函数级）
D. 验收脚本与回滚方案
E. 工时评估（30/60/120分钟）

## 5) 约束
- 默认中文、结论先行。
- 不做外部不可逆动作。
- 优先“可恢复性与稳定性”高于“吞吐优化”。

## 6) 主控建议基线（供参考）
- 只保留一层锁：
  - 要么完全脚本内锁；
  - 要么完全外部调度锁 + 脚本显式跳过内部锁（强制参数，不允许隐式环境漂移）。
- 全路径 finally 清锁 + 心跳更新（避免僵尸锁）。
- 回填分批提交（chunk级事务）+ 总超时/子任务超时双阈值。
- `chat_files.checksum` 统一幂等：补唯一约束迁移，清理 fallback 分支的不可预测行为。
- longctx 与 memory 写入统一调用接口（既有 write_summary/upsert_compaction_summary 语义保持一致）。

---
请先回 ACK + ETA，再给完整方案。