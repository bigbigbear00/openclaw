# 团队作战手册（Team Playbook）

更新时间：2026-02-07

## 1) 总览
- 主控：哆啦Ai熊（主控助手｜总控/调度/可靠性与记忆系统维护）
- 目标：任务拆分与派单、模型路由与成本控制、可靠性审计闭环、长期记忆沉淀
- 安全边界：不做未经确认的对外不可逆动作（公开发布/删除/支付）

## 2) 成员与职责
- 简宁｜writer-editor（文案总编）
  - 模型：openai/gpt-5（Primary）
  - 用途：长文结构化、语气统一、终稿润色
- 小钻｜ctf-director（4A 市场情报总监）
  - 模型：google-antigravity/gemini-3-pro-low
  - 用途：CTF/行业情报抽取与编排
- 阿南｜vn-realestate（越南房地产专家）
  - 模型：google-antigravity/gemini-3-pro-low
  - 用途：越南地产情报与解读
- 探哥｜news-analyst（新闻跟踪分析）
  - 模型：google-antigravity/gemini-3-pro-low
  - 用途：新闻监测与要点凝练
- 球弟｜nba-expert（NBA 篮球专员）
  - 模型：google-antigravity/gemini-3-pro-low
  - 用途：NBA 情报/赛季分析
- 小雅｜library-keeper（资料管理+知识审阅）
  - 模型：google-antigravity/gemini-3-pro-low
  - 用途：daily highlights、知识精炼、sources 归档
- 画画｜designer（平面设计师）
  - 模型：google-antigravity/gemini-3-flash
  - 用途：轻量视觉草稿/排版建议

## 3) 模型路由与成本（简则）
- 旗舰推理/长文：openai/gpt-5
- 多模态/性价比：google/gemini-2.5-pro
- 大量轻任务：openai/gpt-4o-mini 或 google/gemini-2.5-flash
- 代码/工具生成：openai-codex/gpt-5.2（已测：并发10、~60 RPM 稳定）
- 暂禁路由（未授权/硬性封顶）：gpt-5-pro、gemini-3-pro-preview、claude-*、gpt-oss-120b-medium

参考价格（Standard，USD/百万tokens，账号以控制台为准）：
- gpt-5：输入≈$1.25 / 输出≈$10
- gpt-4o-mini：输入≈$0.15 / 输出≈$0.60
- Gemini 2.5 Pro：输入$1.25–$2.5 / 输出$10–$15
- Gemini 2.5 Flash：输入$0.30 / 输出$2.50

## 4) 通信与绑定
- 内部协作：主控用 sessions_send 派单，成员在各自工作区产出并回传
- Telegram 绑定（允许群）：
  - nba-expert → -4995447684
  - vn-realestate → -5151557628
  - news-analyst → -5261774282
  - library-keeper → -5137214022
  - ctf-director → -5231717830
  - designer → -5175626021
  - writer-editor → -5260834117
- 规则：群内不越权发声；需要用户授权的动作由主控先征询

## 5) 可靠性与审计（S/A/B）
- 小时级审计：`python3 cron_logs/job_monitor.py check 2`
- 网络恢复补执行；备用触发覆盖主任务
- isolated 任务 done-marker：`python3 cron_logs/job_marker.py`（以产物存在性补记 done）
- 日志：`cron_logs/*.jsonl`；必要时告警到 Telegram

## 6) 记忆系统（分层＋RAG）
- 宪法层：`MEMORY.md`（长期规则/偏好/SOP，冲突时以此为准）
- 当日层：`memory/YYYY-MM-DD.md`（事实流水，每日晚精炼）
- 复用库：`library/`（模板/方案/长笔记）
- DB+RAG：chat_turns/chat_summaries，Hybrid 检索（向量0.7+关键词0.3）；与宪法层冲突→忽略RAG
- /new 断层恢复：先读 MEMORY.md + 近两日 memory，再用 RAG 补细节

## 7) SLA 与升级
- 正常响应：< 2 分钟
- 紧急（S级）：即时告警并补执行（< 15 分钟闭环）
- 升级路径：异常→主控判定→必要时人工确认→补救/回滚→落审计日志

## 8) 变更管理
- 路由或权限变更：由主控提交配置补丁（config.patch），自动重载
- 价格/配额变化：每周检查一次价表与健康状态，更新本手册

## 9) 写作章节（简宁｜writer-editor）
- 流水线：/Users/apple/clawd/library/writing/pipelines/writer_editor_pipeline.md
- 模板：
  - 长文（Longform）：/Users/apple/clawd/library/writing/templates/longform.md
  - 新闻速递（News Brief）：/Users/apple/clawd/library/writing/templates/news_brief.md
  - 评论稿（Op-Ed）：/Users/apple/clawd/library/writing/templates/op_ed.md
- 路由与成本配置：/Users/apple/clawd/library/writing/config/writer_editor.routing.json
- 运行要点：
  1) 必有 sources.md（正文不放链接）
  2) 大纲→分段（每段≤700 tokens）→合并润色→终稿检查
  3) 预算：soft $0.80 → 降级到 2.5-pro；hard $1.20 → 2.5-flash/4o-mini 并停止扩写
  4) 质量门槛：3点小结、导语≤60字、术语与时间线一致

## 10) 学习与知识沉淀
- 社区学习渠道：OpenClaw Docs、GitHub Discussions、Discord
- 每周学习纪要：周末生成一页总结，重要配置/经验沉淀到 library/
- 记忆精炼：每日从 memory/YYYY-MM-DD.md 精炼 3–7 条入 MEMORY.md

（完）
