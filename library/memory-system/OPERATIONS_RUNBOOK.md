# 运维手册（Runbook）

## 1) 日常观察项（建议每 24h）

1. compaction 触发次数（是否异常飙升）
2. 重复摘要率（是否双写）
3. 检索命中质量（是否召回错层）
4. 延迟与成本（是否明显恶化）
5. 串线检查（必须为 0）

---

## 2) 灰度 -> 全量条件

满足以下再切全量：
- 连续 24~48h 无严重异常
- 召回质量稳定
- 重复摘要率可接受
- 无跨 Agent 数据串线

切换方式：
- 修改 `config/longctx_rollout.json`：`mode: "all"`

---

## 3) 故障处置

### 症状 A：重复摘要暴增
- 检查是否存在绕过 `write_summary(...)` 的旁路
- 检查 `summary_type/chunk_id` 是否按规范写入
- 临时降级到 pilot 或关闭 compaction 触发

### 症状 B：检索质量下降
- 检查检索排序是否变更
- 检查 agent/session 过滤条件
- 检查是否误把 periodic 覆盖 compaction

### 症状 C：串线
- 立即降级至 pilot
- 开启严格隔离（agent_id/session_id）
- 审计 request_id 链路并复盘

---

## 4) 回滚

回滚触发条件：
- 业务不可接受劣化
- 串线或数据污染
- 成本异常上升

回滚动作：
1. `mode` 从 `all` 改回 `pilot`
2. 必要时关闭 longctx compaction 触发
3. 保留 Memory 原检索路径
4. 导出 incident 报告到 `reports/`

---

## 5) 备份纪律

- 任何破坏性去重/删除前必须备份
- 备份必须附 checksum
- 报告中记录：时间、操作者、路径、回滚点
