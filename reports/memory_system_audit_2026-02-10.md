# 记忆系统审计报告（主控）

- 审计时间：2026-02-10 22:xx (Asia/Shanghai)
- 审计范围：`MEMORY.md`、`memory/*.md`、`memory_system/`、`reports/`、运行状态（`openclaw status`）
- 审计目标：确认当前可用性、数据连续性、治理一致性、风险与整改优先级

---

## 1) 当前结论（TL;DR）

1. **主系统记忆可用且在运行**：OpenClaw 状态显示 memory 插件可用（vector/fts/cache 已就绪）。
2. **治理策略已成文**：长期记忆分层、去重、备份、审计规则已经写入 `reports/ops_memory_policy.md`，方向正确。
3. **存在一个高优先级结构风险**：`memory_system/db/memory.db` 当前为 **0B**，说明本地 sqlite 已被移除/停用，现状与 README 的“可本地 run-once sqlite”描述不完全一致，易造成误判。
4. **目录层面存在轻度可维护性问题**：daily memory 文件命名存在并行样式（如 `2026-02-10.md` 与 `2026-02-10-1235.md`），以及专题文件混放（`ME_Iran_watch_*.md`、`VN_realestate_daily_*.md`）。不影响可用，但会降低检索与回顾效率。
5. **备份链路本次正常**：`MEMORY.md` 已生成 tgz + sha256；未出现 `backup_errors.log`。

---

## 2) 证据快照

### 2.1 运行态
- `openclaw status` 显示：
  - Memory: `13 files · 24 chunks · dirty · plugin memory-core · vector ready · fts ready · cache on`
  - Gateway 正常，主会话活跃。

### 2.2 策略与规则
- `reports/ops_memory_policy.md` 已覆盖：
  - 冷存为权威审计日志，不得无备份删除
  - 长期记忆只保留高价值条目
  - `processed_files + checksum` 防重复导入
  - 7-turn/overlap-3 分片
  - dedupe 阈值与人工确认边界
  - 预算/429 暂停机制（政策层）

### 2.3 文件与数据结构
- `memory/` 文件数：14
- 同日多文件：
  - `2026-01-30.md` 与 `2026-01-30-0427.md`
  - `2026-02-10.md` 与 `2026-02-10-1235.md`
- 非标准命名专题文件：
  - `ME_Iran_watch_2026-02-06.md`
  - `VN_realestate_daily_2026-02-06.md`
- `memory_system/db/memory.db`：0B（对应 wal/shm 残留）

### 2.4 备份
- 已存在：
  - `reports/backups/Memery-Main_2026-02-10.tgz`
  - `reports/backups/Memery-Main_2026-02-10.tgz.sha256`
- `reports/backup_errors.log` 不存在（本次无失败日志）。

---

## 3) 风险矩阵

### P0（立即处理）
1. **存储后端认知漂移风险**
   - 现象：`memory_system/README.md` 说明与当前“sqlite 已移除/0B、主用 Postgres”的现实并存。
   - 风险：后续维护者可能误连 sqlite、误判“数据丢失”。
   - 建议：在 README 首屏加“当前生产后端=Postgres；sqlite 仅历史/测试”红框说明。

### P1（本周处理）
2. **命名与分层不统一**
   - 风险：检索召回不稳定、人工回顾成本上升。
   - 建议：
     - `memory/YYYY-MM-DD.md` 保持“日记流”；
     - 专题迁入 `memory/topics/`（如 `iran_watch/`、`vn_realestate/`）；
     - 同日多文件保留但加索引（避免硬合并导致追溯断裂）。

3. **文档与实际执行状态未完全自动校验**
   - 风险：策略写了但运行偏离（例如 cron 超时不可见）。
   - 建议：加一个只读 `memory_system_healthcheck.sh`，每日输出到 `reports/`。

### P2（持续优化）
4. **长期记忆“宪法层”体积增长**
   - 风险：MEMORY.md 逐渐“流水账化”。
   - 建议：
     - MEMORY.md 仅留“规则/偏好/硬决策”；
     - 事件详情迁移到 `reports/memory_events/`，MEMORY.md 放链接。

---

## 4) 整理方案（A/B/C）

### A. 最小变更（低风险，今天可做）
- 仅做文档纠偏 + 增量索引，不动历史数据。
- 包含：README 生产后端声明、memory 索引文件、命名规则说明。
- 适合：先稳系统，避免误操作。

### B. 标准化整理（推荐）
- 在 A 基础上，新增 `memory/topics/` 分层，给专题文件做迁移（保留软链接或 index 映射）。
- 适合：想提升后续检索质量与人工维护效率。

### C. 深度重构（高投入）
- 做一次全量回填重构：统一 chunk 元数据、重跑 embedding、全链路去重复核。
- 适合：准备进入长期规模化记忆运营，但要专门窗口+预算控制。

**推荐：B**（收益/风险比最佳）。

---

## 5) 建议的立即动作（可执行清单）

1. 更新 `memory_system/README.md` 首段（生产后端声明 + sqlite 状态说明）。
2. 新建 `memory/INDEX.md`：
   - 按日期索引 daily
   - 按主题索引专题文件
   - 约定命名规则
3. 新建 `reports/memory_system_health_YYYY-MM-DD.md` 模板（供每日快检）。
4. 保持现有备份任务；补一条“每次备份后验证 sha256”的自动检查记录模板。

---

## 6) 审计结论

- **总体状态：可用（Good）**
- **治理成熟度：中上（有规则、有备份、有审计）**
- **核心短板：文档-运行态一致性 + 文件分层标准化**
- **建议决策：按方案 B 落地（本周内完成）**
