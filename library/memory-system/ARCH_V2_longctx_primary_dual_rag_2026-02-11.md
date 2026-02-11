# 记忆系统 × LongCtx 架构 V2（主控定版）

日期：2026-02-11
状态：生效（若与当日其他相关文档冲突，以本文为准）

## 1. 定版结论
- LongCtx 为主：唯一运行时上下文编排层。
- 原生记忆为兜底：仅故障回退，不参与主路径竞争。
- RAG 双域拆分：
  1) 聊天记忆域（Conversation RAG）
  2) 文件资料域（Document RAG）
- memory_system 定位收敛为“存储与治理底座”（统一写入、幂等、去重、审计），不再作为第二编排器。

## 2. 目标架构（1主2域1兜底）
### 2.1 主控层（LongCtx）
职责：
- token 预算与阈值（yellow/red）
- compaction 触发与窗口裁剪
- 双域检索编排与注入顺序控制

### 2.2 数据治理层（memory_system）
职责：
- 统一写入口（write_summary / upsert_compaction_summary）
- 幂等键（request_id/chunk_id/checksum）
- 去重（exact + semantic）
- 审计与指标落盘

### 2.3 检索域
A) Conversation RAG：chat_turns/chat_summaries/compaction
- 用于：偏好、决策、待办、历史对话事实

B) Document RAG：library/reports/指定资料库抽取索引
- 用于：证据、规范、报告、外部资料

### 2.4 原生兜底层
- 仅在主链路故障时启用回退。
- 不默认参与主检索，避免双RAG重复召回冲突。

## 3. 注入顺序（强规则）
1) system + 当前用户问题
2) 会话摘要 S1（聊天域）
3) 文档证据片段（文件域）
4) 近窗对话 window
5) 超预算裁剪（先低置信证据，再旧window，最后摘要）

## 4. 冲突消解规则（强规则）
- 偏好/决定/待办冲突：聊天域优先。
- 事实/数据/条款冲突：文档域优先。
- 同类冲突：更新时间新 + 置信度高优先。
- 输出前先做跨域去重，禁止同义重复片段并列注入。

## 5. 文本情报 Agent 专项
适用：news-analyst / nba-expert / ctf-director（及同类）
- 聊天RAG：仅用于“你之前怎么要求/我们已做什么”。
- 文档RAG：仅用于“外部事实与证据来源”。
- 产出模板：新增事实（文档）→ 与既有决策关系（聊天）→ 风险与下一步（融合）。

## 6. 与回填策略关系
- HTML 回填属于人工补救，不纳入自动主链路。
- 自动主链路聚焦：日常 DB 入库 + 双域检索 + LongCtx 编排。

## 7. 验收指标（日报）
- 入库重复率（exact/semantic）
- 检索重复命中率（跨域）
- LongCtx compaction 触发率/成功率/回退率
- 召回冲突率（chat/doc）
- 兜底触发次数（应低）

## 8. 生效范围
- 当日及后续“记忆系统 + LongCtx + RAG”相关开发、配置、文档、巡检，统一以本文件为准。
