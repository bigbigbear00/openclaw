# LongCtx 生产实现完整开发文档（v1）

> 2026-02-11 冲突优先级说明：若与 `library/memory-system/ARCH_V2_longctx_primary_dual_rag_2026-02-11.md` 冲突，以 V2 定版为准。

- 日期：2026-02-10
- 目标：把“聊天窗口防溢出”从现有能力（compaction + memoryFlush）升级为可审计、可复用、可跨 Agent 的统一长上下文系统。
- 适用范围：OpenClaw 主控与全部子 Agent。

---

## 0. 结论（先看）

1. 这套 LongCtx **可以一次开发，多 Agent 复用**。
2. 其他 Agent **不需要再各自重做一遍核心逻辑**。
3. 但每个 Agent 仍需做 3 件“轻量接入”：
   - Agent 身份隔离（agentId/session 过滤）
   - 路由参数（模型/阈值可继承全局或局部 override）
   - 验收回归（确保不串线、不漏召回）

---

## 1. 现状与升级边界

### 1.1 当前已生效（生产）
- OpenClaw `agents.defaults.compaction.mode = safeguard`
- `memoryFlush.enabled = true`
- `softThresholdTokens = 4000`

### 1.2 当前存在（预研/阶段实现）
- `library/specs/longctx_*.md|json|sql`
- `scripts/longctx_runtime.py`
- `scripts/longctx_simulate.py`
- `scripts/longctx_staging_*`

### 1.3 本文目标
将“预研脚本 + 规范”收敛为**生产可执行标准**，并给出跨 Agent 复用策略。

---

## 2. 架构设计（生产版）

## 2.1 三层记忆

1) S0 冷存（Raw Turns）
- 来源：chat_turns（原始轮次，审计权威）
- 作用：追溯、重建、纠错

2) S1 活跃上下文（Active Summary）
- 保留当前任务关键状态（短摘要）
- 目标：低 token、高信息密度

3) S2 压缩记忆（Compressed Memory）
- 来自窗口淘汰对话的结构化摘要块
- 通过 RAG 检索回填到提示词

---

## 2.2 请求生命周期（每轮）

1. 写入用户 turn（S0）
2. 估算上下文 token（当前会话 + 召回片段）
3. 若超 yellow/red 阈值：
   - 触发 compaction
   - 旧窗口写入 S2
   - 更新 S1
4. 查询构建：S1 > S2（向量/关键词）> S0 回退
5. 生成回复
6. 写入 assistant turn（S0）
7. 写审计事件（overflow/compaction/retrieval）

---

## 3. 配置标准（建议）

```json
{
  "longctx": {
    "enabled": true,
    "reserveRatio": 0.15,
    "reserveMinTokens": 2000,
    "yellowRatio": 0.80,
    "redRatio": 0.95,
    "s1TargetTokens": 600,
    "s2TargetTokens": 800,
    "ragCapTokens": 2000,
    "chunkTargetTokens": 300,
    "windowTurnsByCtx": {
      "128000": 20,
      "400000": 40,
      "1000000": 80
    }
  }
}
```

说明：
- redRatio 触发强压缩；yellowRatio 提前预防。
- reserve 防止末端溢出。
- s1/s2/ragCap 控制成本与质量平衡。

---

## 4. 数据模型（最小生产字段）

## 4.1 必填维度
- user_id
- session_id
- agent_id（关键）
- turn_index
- timestamp
- source_file/source_checksum（回填场景）

## 4.2 S2/摘要建议字段
- chunk_id（稳定 id）
- summary_type（periodic/compaction/manual）
- turn_range_start/end
- tags（facts/preferences/decisions/todos）
- embedding_vector
- created_at/updated_at

## 4.3 幂等与去重
- `(user_id, session_id, turn_index)` 唯一
- `processed_files(checksum)` 防重复回填
- 近似重复阈值：cosine > 0.92 标记，>=0.96 可自动候选合并（删除须人工批准）

---

## 5. 检索策略（统一）

优先级：
1. S1 当前摘要（固定注入）
2. S2 相关片段（Hybrid：vector + text）
3. S0 冷存回退（窗口 + 关键词）

检索隔离规则（必须）：
- 默认按 `agent_id + session_id` 精确过滤
- 仅在“跨 Agent 协作任务”显式授权下，才允许跨 agent 检索

---

## 6. 审计与可观测性

每轮写入审计字段：
- est_before / est_after
- compaction(bool)
- s2_written_count
- rag_chunks
- retrieval_path（s1/s2/s0）
- latency_retrieval_ms / latency_llm_ms
- drop_reason（无命中/阈值裁剪）

建议落地：
- `cron_logs/overflow-audit.json`
- `reports/memory_system_health_YYYY-MM-DD.md`

---

## 7. 跨 Agent 复用策略（回答你的核心问题）

## 7.1 什么是“一次开发”
- LongCtx 核心逻辑（压缩、检索、审计、阈值）写成**公共运行层**。
- 所有 Agent 共享这一套 runtime。

## 7.2 各 Agent 仍需接入的最小项
1. agent_id 注入与过滤（防串线）
2. 模型与阈值是否使用默认值（可选 override）
3. 一次回归测试（10~30 条历史回放）

## 7.3 结论
- **不需要每个 Agent 重写 LongCtx**。
- 只需做“参数化接入 + 验收”。

---

## 8. 实施计划（分三阶段）

### 阶段 A：并轨（低风险）
- 保留当前 compaction/memoryFlush
- 接入 LongCtx 审计与 S2 写入
- 不改激进阈值

### 阶段 B：标准化
- 正式启用 longctx 配置
- 统一 agent_id 过滤
- 增加每日健康报告

### 阶段 C：优化
- 历史回填分层重算 embedding
- 自动建议 / 人工审批去重
- 成本预算联动告警

---

## 9. 验收标准（DoD）

1. 高压会话不再出现上下文溢出错误
2. compaction 可被审计（有日志、有指标）
3. 回答质量在 /new 前后稳定
4. 多 Agent 互不串线
5. 成本在预算线内（可观测）

---

## 10. 运行手册（简版）

1. 先在 staging 启用并回放样本对话
2. 观察 24h：溢出次数、命中率、延迟、成本
3. 小流量灰度到 1~2 个 Agent
4. 全量启用并保留回滚配置

回滚触发条件：
- 召回明显劣化
- 串线风险
- 成本异常激增

---

## 11. 风险清单

- 配置误并轨导致检索范围过宽（串线）
- 去重策略过激导致历史信息误删
- 压缩摘要质量不稳导致事实丢失

控制措施：
- 强制 agent_id 过滤
- 删除动作人工审批 + 先备份
- 抽样对照原文进行质量评估

---

## 12. 与现有文件的关系（索引）

- 规范：`library/specs/longctx_readme.md`
- 配置样例：`library/specs/longctx_openclaw_config.json`
- 运行脚本：`scripts/longctx_runtime.py`
- 模拟：`scripts/longctx_simulate.py`
- 防断层：`library/new_aftercare_checklist.md`
- 自检：`scripts/aftercare_selfcheck.py`

---

## 13. 你接下来只需拍板两件事

1. 是否按“阶段 A（并轨）”开始（推荐）
2. 是否先灰度到 `main + news-analyst` 两个 Agent，再全量

> 若确认，我将基于本文件输出“变更清单 + 回滚清单 + 验收脚本清单”。
