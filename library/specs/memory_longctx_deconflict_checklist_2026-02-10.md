# 记忆系统 × LongCtx 去冲突改造清单（可执行）

日期：2026-02-10
状态：Draft v1

## 目标
- 消除重叠触发与双写冲突
- 保持“Memory 数据层、LongCtx 编排层”单一职责
- 对所有 Agent 一次改造、统一复用

---

## 一、职责边界（先固化）

1) Memory（数据/治理层）
- 负责：S0 冷存、S2 存储、统一检索接口、去重、备份、审计
- 不负责：会话内何时压缩

2) LongCtx（运行时编排层）
- 负责：预算估算、yellow/red 判定、触发 compaction、上下文组装
- 不直接维护独立存储规范，写入必须走 Memory 标准接口

---

## 二、统一触发顺序（必须一致）

每轮请求执行顺序：
1. 写入 chat_turns（user）
2. LongCtx 估算 token
3. 若触发压缩：调用 Memory API 写 compaction-summary（S2）
4. 用 Memory 检索接口构建上下文（S1/S2/S0）
5. 生成回复
6. 写入 chat_turns（assistant）
7. 写审计事件（overflow-audit + request_metrics）

禁止：
- LongCtx 与 Memory 各自独立再做一次摘要写入
- 两套检索器并行注入 prompt

---

## 三、字段与接口统一（最小必做）

新增/统一字段：
- `agent_id`（必须）
- `summary_type`：`periodic|compaction|manual`
- `source`：`memory|longctx`
- `chunk_id`：稳定 id（幂等写入）
- `request_id`：单轮全链路追踪

统一接口约定：
- `memory.write_summary(...)`：LongCtx 只调用它，不直写库
- `memory.retrieve_context(...)`：唯一上下文检索入口

---

## 四、去重与防冲突规则

1. 周期摘要（periodic）与压缩摘要（compaction）可共存，但需类型标识。
2. 相同 turn_range + agent_id + session_id 的 compaction-summary 幂等覆盖（不重复插入）。
3. periodic 不覆盖 compaction；由检索阶段按权重选择。

检索权重建议：
- S1（当前摘要）> compaction-summary > periodic-summary > raw-turns

---

## 五、阈值协同（避免“双触发抖动”）

- 保留 OpenClaw `memoryFlush` 作为兜底
- LongCtx yellow/red 为主触发
- 设“抖动冷却窗口”：同一 session 60 秒内不重复 compaction

---

## 六、灰度计划（一次改造，多 Agent 复用）

阶段 A（2 agents）
- main + news-analyst
- 观察：溢出率、召回质量、延迟、重复摘要率

阶段 B（全量）
- 所有 agent 启用统一运行层
- 每个 agent 仅配置：agent_id / 阈值继承 / 回归样本

---

## 七、验收标准（DoD）

1. 无上下文溢出报错
2. 每轮仅一条有效检索链路
3. 重复摘要率显著下降
4. agent 间 0 串线
5. 审计可追踪（request_id 贯通）

---

## 八、回滚

触发条件：
- 召回明显劣化
- 成本异常上升
- 串线或数据污染

动作：
1) 关闭 LongCtx compaction 触发
2) 保留 Memory 原检索路径
3) 保留审计日志用于复盘

---

## 九、产物索引

- `library/specs/longctx_prod_implementation_guide_2026-02-10.md`
- `library/specs/memory_longctx_deconflict_checklist_2026-02-10.md`（本文件）
