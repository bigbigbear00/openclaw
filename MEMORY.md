# MEMORY.md

> 这是长期稳定的“宪法层”记忆：偏好、硬边界、SOP、关键决策。
> 当天流水账写 `memory/YYYY-MM-DD.md`；可复用长文/模板写 `library/`.



## 多智能体协作社交层规则（19:57+）

- 用户确认采用：系统内协作由主控调度；涉及对外权威/群内观感时，优先由用户在对应群发一句授权/指令，主控后台拆解执行。
- 用户新增要求：内部派单需要在主对话同步“状态卡”（OK回执/ETA/产物路径）。

## 授权实例（20:00+）

- 用户已在主对话下达授权口令：整理今日湖人比赛复盘并写自媒体长稿（球弟供数，简宁写稿）。已转发到对应群并要求 OK 回执。

## 主控可内部派单（20:11+）

- 用户同意改配置：开启 agent-to-agent messaging，避免“主控发群消息不触发子智能体/需要用户复制粘贴”。
- 已在 `/Users/apple/.openclaw/openclaw.json` 启用：`tools.agentToAgent.enabled=true` 并触发 gateway 重启（config-apply ok）。
- 结果：主控可用 `sessions_send` 直接派单到子智能体会话；球弟回执 OK-球弟，简宁回执 OK-简宁-初稿。

## 湖人长稿交付闭环（20:15+）

- 球弟已将比赛要点写入会议室：`/Users/apple/clawd/shared/meeting_room.md`
- 简宁已落盘长稿：`/Users/apple/clawd/library/writing/lakers_2026-02-06_longform.md`
- 主控已用 NBA liveData JSON 核验并回填关键数据（比分/四节/篮板/关键回合/核心数据），避免幻觉，并提交 git：commit `2e5cdd2`。
- 用户反馈：认为“消息准确度验证”很重要，主控做得周到。

## 对外发布稿完成正文规则（20:48+）

- 用户要求：对外发布版正文需去掉元信息与内部标注（如“（自媒体长文｜体育记者风）”、"标题备选" 区块、来源/核验段落等），只保留最终可读标题+正文；核验链接另存到 sources/appendix 文件。

## 2026-02-09 22:12 - Agent roster added

- Action: Added agents roster to /Users/apple/clawd/reports/agents_roster.json and persisted key agent metadata into long-term memory.
- Agents included: main (哆啦Ai熊), ctf-director (小钻), vn-realestate (阿南), news-analyst (探哥), nba-expert (球弟), library-keeper (小雅), designer (画画), writer-editor (简宁).
- For each agent: stored id, name, role summary, workspace path, telegram binding (if any), primary model.
- Source files: /Users/apple/.openclaw/openclaw.json, per-agent AGENTS.md and workspaces under /Users/apple/clawd-agents/.

## 2026-02-10 01:12 - Memory policy draft added

- Action: Added initial memory sedimentation & governance policy to guide what is promoted from cold turns to long-term memory.
- Key points (summary):
  - Cold storage (chat_turns) remains the authoritative raw log; do NOT delete raw turns unless explicitly requested and backed up.
  - Long-term memory (MEMORY.md + chat_summaries) only contains distilled, structured, or high-value items (facts, preferences, decisions, todos).
  - Backfill and ingestion pipeline MUST record processed_files (file checksum + processed_at) to prevent duplicate import.
  - Chunking strategy for conversational data: sliding window by turns (7 turns per chunk, overlap 3), preserving speaker, timestamp, session_id, and turn_index range in metadata.
  - Embeddings provider: gemini; default summary model: gpt-4o-mini; critical chunk upgrade model: gpt-5-mini.
  - Dedupe strategy: exact match/checksum first, then vector similarity (cosine threshold default 0.92) for near-duplicates; dedupe job marks candidates and requires manual confirmation for deletion.
  - Cost control: soft budget per bulk import = $5; on exceed/potential 429 pause and alert owner.
  - Audit & rollback: all automated changes to MEMORY.md or chat_summaries must be logged to /Users/apple/clawd/reports and retain provenance (source file, chunk_id, timestamp).

## 2026-02-10 01:25 - User preference: default report language

- 用户偏好：除非另有说明，所有对外/系统生成的报告、文档与输出默认使用中文（简体）。
- 存放位置：该偏好已写入长期记忆（MEMORY.md），并将被 memory_system 的生成流程优先遵守。

## RAG 可接手的查询类型（已加入规则）

以下类型的查询将优先由 RAG（检索增强生成）处理；当查询触发并被判定为“高价值”时，结果/要点会被写入长期记忆（chat_summaries / MEMORY.md）。默认以中文响应。

1. 事实回溯 / 历史记录
   - 示例："上周我跟你讨论过 X 的结论？" 或 "谁在 2026-02-07 会议负责联系供应商？"
   - 触发条件：查询中包含时间、事件、主题关键词或要求引用来源。
   - 结果处理：优先检索 chat_summaries，再回退到 chat_turns；若包含决定/todo 则晋升为长期记忆条目。

2. 偏好与配置项查询
   - 示例："默认报告用哪种语言？"、"我的写作风格偏好是什么？"
   - 触发条件：包含“偏好/默认/首选”等关键词。
   - 结果处理：返回当前记忆中的偏好；必要时把新偏好写入 MEMORY.md（需用户确认）。

3. 决策与待办（Todos）查询
   - 示例："上次决定谁负责合同？还有哪些未完成的 todo？"
   - 触发条件：包含“决定/todo/待办/deadline”。
   - 结果处理：提取并列出相关 todos 与负责人；写入 chat_summaries 并标注待办状态。

4. 文档与资料检索
   - 示例："把关于 X 的技术要求文档列出来并摘要。"
   - 触发条件：明确指定资料库路径或关键词（library/ reports/）。
   - 结果处理：检索并返回摘要 + 来源路径；高价值摘录可晋升到长期记忆。

5. 项目状态与里程碑查询
   - 示例："VN 项目当前进度和风险？"
   - 触发条件：包含项目名、里程碑或周报关键词。
   - 结果处理：汇总最近 summaries 与相关 turns，输出状态与风险。

6. 引用与证据类查询
   - 示例："上次给我的数据来源是什么？把原始来源列出来。"
   - 触发条件：要求来源或证据时。
   - 结果处理：返回可核验的来源与引用片段。

7. SOP / 运维手册查询
   - 示例："重启 Gateway 的步骤"、"遇到 429 的应对流程是什么？"
   - 触发条件：运维/流程相关关键词。
   - 结果处理：优先返回已存的运维文档或 MEMORY.md 中的 SOP 节点。

不由 RAG 自动决定的场景（需人工）
- 涉及法律/财务承诺、密钥/权限变更、或大规模破坏性删除（必须人工审批）。

## 2026-02-10 23:11 - 每日记忆精炼（自动策略）

- 晋升门槛更新：用户当日明确“B 类草稿全部不晋升”，且有 3 条敏感条目保留人工复核；后续精炼默认遵循该门槛。
- 记忆结构标准化已落地：专题记忆迁移到 `memory/topics/`，配套迁移映射与分层索引（`memory/INDEX.md`）已完成。
- Memory × LongCtx 首批统一：摘要写入改为统一接口并补齐幂等语义（`write_summary / upsert_compaction_summary`），摘要 metadata 标准化，检索优先 compaction 再 periodic。
- LongCtx runtime 已接入统一写入链路：优先 `memory_write_summary`，失败才回退 sqlite；审计时间统一为实时 UTC。
- 灰度与治理：LongCtx pilot 扩展到 `ctf-director`（pilot：main/news-analyst/ctf-director）；7/7 agent 宣贯 ACK 完成，执行口径为“小雅审计上报、主控负责阻断/降级”。


