# 开发指南（给实现与维护 Agent）

## 1) 代码入口

### Memory 侧
- `memory_system/memory_v1_rag.py`
  - `write_summary(...)`：统一摘要写入 API
  - `upsert_compaction_summary(...)`：compaction 幂等写入
  - `retrieve_memory_context(...)`：统一检索

### LongCtx 侧
- `scripts/longctx_runtime.py`
  - 阈值触发 compaction
  - 优先走 Memory API 写 compaction 摘要
  - 灰度开关读取：`config/longctx_rollout.json`

---

## 2) 接入规范

1. 所有 compaction 摘要必须经过 `write_summary(...)`
2. 摘要 meta 必带：
   - `summary_type`（periodic/compaction/manual）
   - `source`（memory/longctx）
   - `request_id`
   - `chunk_id`（稳定 id）
3. 检索默认带 `agent_id + session_id` 过滤

---

## 3) 灰度策略

配置文件：`config/longctx_rollout.json`

```json
{
  "mode": "pilot",
  "pilotAgents": ["main", "news-analyst"],
  "enforceIsolation": true
}
```

- `mode=pilot`：仅白名单 agent 走新链路
- `mode=all`：全 Agent 启用

---

## 4) 本地验证

1. 语法校验：
```bash
python3 -m py_compile memory_system/memory_v1_rag.py scripts/longctx_runtime.py
```

2. 功能检查：
- compaction 时是否只写一条有效 summary（无重复爆发）
- retrieval 是否优先 compaction summary
- 审计日志是否含 `agent_id`、`rollout_mode`

---

## 5) 变更约束

- 不允许直接删历史冷存（除非用户明确授权 + 先备份）
- 不允许绕过统一 API 新建“第三套记忆写入路径”
- 对外动作（消息群发、删除）必须用户确认

---

## 6) 常见问题

Q: 其他 Agent 要不要重做 LongCtx？
A: 不用。核心逻辑复用，只做轻接入和回归。

Q: memory.db 还要不要用？
A: 生产以统一 Memory 主链路为准，legacy sqlite 仅兼容/测试用途。
