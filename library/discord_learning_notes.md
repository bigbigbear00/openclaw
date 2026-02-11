# OpenClaw Discord 社区完整学习笔记
> 2026-02-06 深度浏览

---

## 📊 社区概览

### 已浏览频道
- ✅ #general（日常讨论）
- ✅ #freshbits（官方更新）
- ✅ #users-helping-users（用户互助）
- ✅ #security（安全讨论）
- ✅ #help-中文（中文求助）

### 社区统计
- 语音频道：~53 人在线
- 活跃用户标签：CLAW、BELU、BRED、TNKR、Hak5 等

---

## 🔥 最有价值的发现

### 1. 安全最佳实践 ⭐⭐⭐⭐⭐

#### 1.1 安全部署配置（来自 bowling_spares）
```
✅ 专用 Mac Mini（不运行其他东西）
✅ 全新 Apple ID + Gmail（无个人数据）
✅ Gateway 绑定 loopback (127.0.0.1)
✅ Auth 模式设为 token
✅ iMessage/WhatsApp 设为 allowlist（只允许自己号码）
✅ Exec approvals 默认 deny + ask-on-miss
✅ 无邮件/银行/社交媒体连接
✅ 只连接必要 API
✅ 不启用破坏性 skills
```

#### 1.2 密钥管理方案
**nono + macOS Keychain**（来自 Luke）：
```bash
security add-generic-password -T /opt/homebrew/bin/nono -s "nono" -a "slack_app_token" -w "xapp-..."
nono run --profile openclaw --secrets slack_app_token,slack_bot_token openclaw gateway
```
- 密钥存储在 macOS Keychain，不暴露给 OpenClaw

**Hashicorp Vault**（来自 sathish316）：
- 时间限制的 token（1小时过期）
- 分层安全：低/中/高敏感度 token
- 但需要人工 SSH 轮换

#### 1.3 Prompt Injection 防护（来自 fielding/Cypherfox）
- **问题**：邮件/日历等外部输入可能包含注入攻击
- **解决思路**：
  - 截断 + 随机化（不完整显示主题行）
  - 检测 unicode 同形字符、base64、url 编码
  - 用 BERT 分类器（非 LLM）预过滤可疑内容
  - 多层防御（但任何回传主 agent 的都可能被注入）

#### 1.4 Skills 安全 ⚠️
- **警告**："Bad actors have put hundreds of skills with malicious code"
- **已发现恶意 skills**（已删除）：deepresearch, nanopdf, memory-pipeline-0-1-0
- **建议**：
  - 下载后让 agent 做安全审查
  - 或让 agent 自己写 skill
  - ClawHub 现在可以举报恶意 skills

#### 1.5 进阶安全方案
**PeterEncrypted 的方案**：
- Zero trust 加固
- 加密所有 env 和敏感数据
- 记忆缓存（节省 90% token）
- 智能路由

**claw-wrap**（来自 dedene）：
- https://github.com/dedene/claw-wrap
- 沙箱化，让 OpenClaw 完全看不到环境变量

**安全自评估 PR**（来自 Hamson）：
- 正在开发让 AI 自评风险的功能
- 需要测试用户帮忙调试 prompt

---

### 2. 本地模型配置 ⭐⭐⭐⭐

#### 2.1 推荐配置（来自 Cypherfox）
```
使用 llama.cpp + anthropic-messages API 类型
配置在 openclaw.json 中
比 Ollama 的表现更好
```

#### 2.2 可用的本地模型
- `ollama/voytas26/openclaw-qwen3vl-8b-opt:latest` — 专门优化过的
- 16GB 统一内存的 Mac 可以跑，但"不是最亮的灯泡"

#### 2.3 模型选择建议
> "Anthropic with Opus is probably the gold standard for high quality agent interaction with OpenClaw, but god is it expensive."
> — Cypherfox

---

### 3. 新功能更新 ⭐⭐⭐

#### 已发布
- **Opus 4.6** 今日发布（但 OpenClaw 还需要更新支持）
- **Gateway 时间戳注入** — 消息自动带 [Wed YYYY-MM-DD HH:MM TZ]
- **MiniMax OAuth 插件** (#4521)
- **System Prompt Safety Guardrails**
- **MEDIA 路径 LFI 安全修复**

#### 文档更新
- Gateway 配置文档大改版
- 扩展 Channel 文档（Discord, Telegram, Slack, MS Teams, GoogleChat）
- Cron jobs & automation 新文档

---

### 4. 常见问题解答 ⭐⭐⭐

| 问题 | 解答 |
|------|------|
| 记忆跨天失效 | Memory 默认只保存最重要内容，需额外配置 |
| Context overflow | 用 /new 重置会话，或换更大上下文模型 |
| Opus 4.6 不可用 | 刚发布，等 OpenClaw 更新支持 |
| memory-core unavailable | 需要安装 node service |
| 输出 system prompt | 检查模型配置，重启 gateway |

---

### 5. 中文社区动态 ⭐⭐⭐

#### 热门帖子
1. **中国用户需求调研**（565 条消息）
   - 寻找最重要的 3-5 件事让工具适配中国
   - 讨论：AI 翻译、聊天平台、中国 AI 服务商

2. **模型省钱讨论**（7 条消息）
   - Kimi 现在是 OpenClaw 全球用量最大的模型！

3. **免费帮忙解决问题**（995 条消息）
   - 用户 Vrusto 下午到凌晨在线帮忙

4. **中国境内可用的 providers**
   - DeepSeek、Qwen 可直接使用（无需 VPN）

---

## 📋 待办事项

### 可立即应用
- [ ] 检查 nono 工具用于密钥管理
- [ ] 考虑 claw-wrap 沙箱化
- [ ] 关注 security-in-the-age-of-agentic-ai 仓库

### 长期关注
- [ ] 安全自评估 PR（Hamson）
- [ ] BERT 预过滤 prompt injection 方案
- [ ] Mac Mini 专用部署

### 已验证我们做对了
✅ Hybrid Search + Embedding Cache（记忆优化）
✅ Pre-compaction Flush（防失忆）
✅ 任务可靠性五层保障
✅ 多 Agent 隔离架构

---

## 🔗 有用资源

- https://github.com/innergclaw/security-in-the-age-of-agentic-ai — 安全指南
- https://github.com/dedene/claw-wrap — 沙箱工具
- https://docs.clawd.bot/security — 官方安全文档
- Vrusto（Discord）— 中文社区热心帮忙者

---

## 💡 关键洞察

### 安全是最大痛点
社区讨论 80% 围绕安全：
1. 密钥暴露风险
2. Prompt injection 攻击
3. 恶意 skills
4. 内部威胁（agent 本身是攻击向量）

### 最佳策略
> "The campers are being chased by a bear... If you make it hard to attack you, attackers will just go after softer targets."
> — Cypherfox

**核心原则：Defense in Depth**
- 不求完美，求比别人难攻击
- 多层防护，每层都增加攻击难度
- 接受风险存在，但要知情同意

---

*更新时间：2026-02-06 13:50 CST*
