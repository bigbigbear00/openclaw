# 架构说明：Memory 系统 × LongCtx（统一版）

> 2026-02-11 更新：若与 `library/memory-system/ARCH_V2_longctx_primary_dual_rag_2026-02-11.md` 冲突，以 V2 定版为准。

## 1) 分层架构

### A. Memory（数据/治理层）
职责：
- S0 冷存（原始对话 turns）
- S2 摘要存储（periodic / compaction / manual）
- 统一检索接口（retrieve_context）
- 去重、备份、审计

### B. LongCtx（运行时编排层）
职责：
- 上下文 token 估算
- yellow/red 阈值判断
- compaction 触发
- prompt 预算裁剪与组装

### C. 应用层（Agent 回复流程）
职责：
- 接收消息
- 调用 Memory + LongCtx
- 生成回复并落库

---

## 2) 关键数据层（概念）

- **S0 冷存**：chat_turns（权威原始日志）
- **S1 活跃摘要**：当前会话关键状态（短摘要）
- **S2 压缩记忆**：淘汰窗口的结构化摘要，供 RAG 回填

---

## 3) 统一处理链路（每轮）

1. 写入 user turn（S0）
2. LongCtx 估算 token
3. 超阈值则触发 compaction
4. compaction 结果通过 Memory API 写入 S2（幂等）
5. Memory 统一检索（S1 > S2 > S0）
6. 调用模型生成
7. 写入 assistant turn（S0）
8. 写审计（overflow + request metrics）

---

## 4) 去冲突设计

### 冲突来源
- 双摘要（Memory periodic vs LongCtx compaction）
- 双检索（两套入口）
- 双阈值（行为抖动）

### 解决方案
- LongCtx 只负责“触发和编排”，不单独维护存储体系
- 摘要统一写入 Memory API，带 `summary_type/source/request_id/chunk_id`
- 检索只保留 Memory 统一入口
- 检索排序建议：compaction > periodic > raw turns

---

## 5) 跨 Agent 复用原则

- 核心机制一次开发，全 Agent 共用
- 每个 Agent 仅做 3 件轻接入：
  1) `agent_id` 隔离
  2) 参数继承/覆盖
  3) 回归验收

---

## 6) 当前灰度状态

- Phase A：main + news-analyst
- 配置：`config/longctx_rollout.json`（mode=pilot）
- 目标：验证稳定性后切全量
