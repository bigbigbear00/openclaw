# 记忆系统与 LongCtx 开发文档总览（给全体 Agent）

更新时间：2026-02-10
适用对象：main / ctf-director / vn-realestate / news-analyst / nba-expert / library-keeper / designer / writer-editor

## 你先看这 3 份

1. `ARCHITECTURE.md`  
   - 系统分层、职责边界、数据流
2. `DEVELOPER_GUIDE.md`  
   - 怎么接入、怎么改、怎么回归测试
3. `OPERATIONS_RUNBOOK.md`  
   - 灰度、监控、故障处理、回滚

---

## 一句话原则

- **Memory 系统 = 数据与治理层**（存储、检索、去重、审计）
- **LongCtx = 运行时编排层**（预算、压缩触发、上下文组装）
- LongCtx 不直接定义另一套存储规范，写入必须走 Memory 标准接口。

---

## 当前实施状态

- Phase A 灰度中：`main + news-analyst`
- 灰度开关：`/Users/apple/clawd/config/longctx_rollout.json`
- 参考报告：`/Users/apple/clawd/reports/longctx_phaseA_rollout_2026-02-10.md`

---

## 相关历史文档（补充）

- `/Users/apple/clawd/library/specs/longctx_prod_implementation_guide_2026-02-10.md`
- `/Users/apple/clawd/library/specs/memory_longctx_deconflict_checklist_2026-02-10.md`
- `/Users/apple/clawd/reports/memory_system_audit_2026-02-10.md`

---

## 面向 Agent 的执行纪律

1. 不允许绕过 Memory 接口直接写“第二套摘要库”。
2. 任何去重删除前必须先备份并可回滚。
3. 检索默认必须带 agent/session 过滤，防串线。
4. 变更前先出 diff 与回滚方案。
