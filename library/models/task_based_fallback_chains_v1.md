# 任务类型后备链（v1）

更新时间：2026-02-11
状态：生效（主控调度口径）

## 1) 代码工程类（修复/重构/SQL/脚本）
- 主：`openai-codex/gpt-5.3-codex`
- 后备1：`openai/gpt-5-mini`
- 后备2：`google/gemini-2.5-flash`

## 2) 战略决策类（方案评估/多约束取舍/主控收口）
- 主：`google-antigravity/claude-opus-4-5-thinking`
- 后备1：`openai-codex/gpt-5.3-codex`
- 后备2：`openai/gpt-5-mini`

## 3) 高频情报类（监测/预警/日报）
- 主：`google/gemini-2.5-flash`
- 后备1：`openai/gpt-5-mini`
- 后备2：`google-antigravity/claude-sonnet-4-5`

## 4) 高质量写作类（长文/发布稿/深度编辑）
- 主：`google/gemini-2.5-pro`
- 后备1：`google-antigravity/claude-opus-4-5-thinking`
- 后备2：`openai/gpt-5-mini`

## 5) 创意设计类（视觉创意/风格探索）
- 主：`google/gemini-2.5-pro`
- 后备1：`google/gemini-2.5-flash`
- 后备2：`openai/gpt-5-mini`

---

## 统一触发规则
1. 同任务连续失败 2 次或超时 2 次：切下一后备。
2. 额度低于 25%：非关键任务自动下沉到 mini/flash。
3. 标记“关键任务”：禁止自动降到低阶模型，需先请示用户。

## 执行责任
- 主控（main）：按本矩阵派单。
- 子 Agent：遵循主控指定模型链执行；异常必须上报。
