# 记忆运维策略（草案）

生成时间：2026-02-10T01:13:00+08:00

目的
----
定义记忆系统的运维规则：哪些内容存储、冷存到长期记忆的数据流、去重与幂等保障、成本管控以及审计要求。

适用范围
--------
适用于 memory_system 的导入/回填流水线、触及记忆的主控 cron 任务，以及来自导出文件的手动导入流程。

关键策略
--------
1. 冷存（chat_turns）
   - 原始轮次为权威审计日志，除非经明确请求并完成备份，否则不得删除。
   - 写入 chat_turns 的每条记录必须包含说话人、时间戳、session_id 与 turn_index 等元数据。

2. 长期记忆（chat_summaries + MEMORY.md）
   - 仅保存经提炼的高价值条目：事实、偏好、决定、待办、实体等。
   - 管道自动生成的结构化摘要可自动晋升；人工策划的条目仍保留手动晋升通道。

3. 导入 / 回填
   - processed_files 表：每个导入文件必须记录文件名、checksum 与 processed_at；相同 checksum 的再导入会被跳过。
   - 会话切片策略：按轮次滑动窗口分片，默认：7 条轮次/片，重叠 3 条。为每个 chunk 存储元数据：说话人列表、时间范围、session_id、turn_index 范围、source_file、source_checksum。
   - Embeddings 提供者：gemini。默认摘要模型：gpt-4o-mini；关键/升级模型：gpt-5-mini。
   - 插入必须具备幂等性：在写入 chat_turns 或 summaries 前，检查 (user_id, session_id, turn_index) 与 stable_chunk_id 以避免重复写入。

4. 去重
   - 策略：先做精确匹配/checksum 去重；再用向量相似度（cosine > 0.92）识别近似重复。
   - dedupe 作业将标记候选并生成可复核报告；自动删除必须经所有者明确批准。

5. 成本控制与节流
   - 批量导入软预算：每次 bulk import 以 5 美元为软上限。当预计花费达到软上限的 80% 时，暂停任务并通知所有者。
   - 若出现 API 限流（429）或 LLM 重复失败，暂停作业并在 /Users/apple/clawd/reports 下创建 incident 报告。

6. 审计与溯源
   - 所有对 MEMORY.md、chat_summaries 或任何破坏性 DB 操作的自动修改，必须记录到 /Users/apple/clawd/reports，并包含来源文件、chunk_id、时间戳和操作主体（agent id）。
   - 备份：在任何破坏性 dedupe/合并操作前，必须先做数据库备份并存入 /Users/apple/clawd/reports/backups，附带 checksum。

7. 访问与治理
   - 仅允许 main agent 运行计划内的记忆维护作业。agent 层发起的晋升到长期记忆必须保留审计轨迹。

运行手册（简短）
----------------
- 常规批量导入：
  1. 校验文件 checksum 并记录到 processed_files。
  2. 先以 dry_run 模式预览 chunk 与摘要。
  3. 全量导入并监控成本计量；遇到 429 或超过软预算立即中止。
  4. 运行 dedupe（仅标记模式）并生成报告供复核。
  5. 在所有者批准后，执行合并/删除并记录备份信息。

- 紧急回滚：
  1. 从 /Users/apple/clawd/reports/backups 恢复最新数据库备份。
  2. 重新运行 dedupe（仅标记）以验证恢复状态。

注意与待办
----------
- 已实现/进行中：在 backfill 脚本中实现 processed_files 表和幂等插入检查（已完成/进行中）。
- 待办：把成本计量与软预算强制集成到回填脚本与 cron 监督器中；安排定期（夜间）dedupe 标记运行，最终删除操作需人工确认。

批准：待所有者确认签署（Owner 确认）
