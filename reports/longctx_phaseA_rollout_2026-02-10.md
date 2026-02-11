# LongCtx Phase A 灰度启动记录

- 时间：2026-02-10 22:33+ (Asia/Shanghai)
- 策略：A 档灰度（仅 main + news-analyst）

## 已执行

1. 新增灰度配置文件：
   - `config/longctx_rollout.json`
   - mode=`pilot`
   - pilotAgents=`["main","news-analyst"]`

2. 运行时改造：
   - `scripts/longctx_runtime.py`
   - 新增 pilot 开关读取与 agent 过滤
   - 仅 pilot agent 走统一 Memory 写入 API
   - 非 pilot agent 回退 legacy sqlite 路径
   - 审计日志增加 `agent_id`、`rollout_mode`

3. 语法校验：
   - `python3 -m py_compile` 通过

## 观察指标（建议）

- compaction 触发次数
- retrieval 命中质量
- 重复摘要率
- 延迟与成本
- 串线异常（应为 0）

## 升级条件（A -> 全量）

- 连续 24~48h 无异常
- 召回质量稳定
- 无串线、无重复写入爆发

## 全量开关

将 `config/longctx_rollout.json` 的 mode 从 `pilot` 改为 `all`。
