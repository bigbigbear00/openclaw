# OpenClaw Discord 社区学习笔记 - 2026-02-06

## 一、架构讨论热点 (#architecture)

### 1. 本地模型配置优化
- **问题**: 本地模型（如 llama.cpp）在 OpenClaw 中表现不佳，必须手动发消息才能推动执行
- **解决方案**: 设置 `api type = anthropic-messages`，模型表现明显改善
- **注意**: 本地模型可能只加载了 tool context，没有吃进 system prompt（SOUL.md 等）
- **排查命令**: 使用 `context` 命令对比实际 token 使用量

### 2. 上下文管理最佳实践
- **核心观点**: `/new` 被认为是反模式 — agent 应该支持持续对话，上下文自动管理
- **Rolling Context 方案** (by samholmes):
  - 把上下文分块（hunks）
  - 让模型在输出时同时输出要保留哪些块
  - 实现"连续压缩"而非一次性 compaction
  - 摘要头部根据 expiry/liveliness 自动过期
- **GitHub 讨论 #9872**: 上下文连续性方案（offload + recompose）

### 3. 多 Agent 协作方案
**方案 A: Gmail 邮件更新**
- 每个 agent 有自己的 Gmail 地址
- 定期发邮件更新到群组

**方案 B: Git 分支共享**
- 不同 agent 检查不同 tag/feature branch 的 .md 文件
- 互相检查对方分支的变更

**局限**: 两种方案都依赖 heartbeat，不是真正的 push

### 4. 模型选择自动化
- 专注型 bot 比通用型更有价值
- 未来方向: 模型选择应该自动化，普通用户不应该有"模型意见"
- 可以建市场卖训练好的记忆（需要脱敏处理）

---

## 二、重启后自动执行问题 (#help - 重点学习)

### 问题描述
- 场景: Gateway 重启后，希望 agent 自动执行健康检查
- 现象: Agent 要么回复 `HEARTBEAT_OK` 忽略指令，要么写一大段解释而不执行

### 核心解决方案

**1. 使用 boot-md hook 而非 heartbeat**
- Heartbeat 设计上允许 no-op (`HEARTBEAT_OK`)
- OpenClaw 会 drop 看起来像 OK-ack 的回复

**启用步骤:**
```bash
openclaw hooks list
openclaw hooks enable boot-md
```

**配置确认:**
```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": { "enabled": true }
      }
    }
  }
}
```

**验证命令:**
```bash
openclaw hooks info boot-md
openclaw config get hooks.internal --json
openclaw logs --follow | grep -i "boot-md\|Registered hook\|gateway:startup"
```

**2. 如果不想依赖 LLM: 用 systemd**
- 创建 oneshot unit，在 OpenClaw 服务启动后运行
- 使用 CLI 发送消息: `openclaw message send --channel telegram --target <chat_id> --message "…"`

**3. 保留 heartbeat 时的优化**
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "ackMaxChars": 0
      }
    }
  }
}
```
- 设置 `ackMaxChars: 0` 后，只有纯 `HEARTBEAT_OK` 被 drop，任何额外文本都会被发送

---

## 三、Skills 频道亮点 (#skills)

### 1. Content Engine 愿景 (by chelsea)
六步自动化内容生产:
1. **FIND** 🔍 - AI 扫描热门话题
2. **WRITE** ✍️ - 用你的风格生成脚本
3. **SPEAK** 🎙️ - 克隆你的声音朗读
4. **CREATE** 🎬 - AI 头像/实拍视频 + 自动剪辑 + B-roll + 字幕
5. **ADAPT** 📱 - 一个视频变 10 个版本
6. **POST** 📤 - 自动排期发布

### 2. 新 Skills 推荐
- **ATL (Agent Touch Layer)**: iOS Simulator 移动浏览器自动化
  - GitHub: https://github.com/JordanCoin/Atl
  - 使用编号标记获取坐标，支持视觉相关操作
  
- **TARDIS**: 计时器 skill，支持可验证的开始/结束时间
  - ClawHub: https://clawhub.ai/skills/tardis
  - 支持 Sendgrid 邮件集成

- **BRAWLNET**: Agent 对战竞技场
  - 100 扇区六边形网格，10 分钟比赛
  - ClawHub: https://clawhub.ai/sikey53/brawlnet

### 3. ClawHub 更新
- 新增 VirusTotal 扫描集成
- 可能会有误报（加密相关代码被标记）

---

## 四、开发频道要点 (#dev)

### 1. Opus 4.6 使用体验
- Token 消耗比 4.5 更高（Teams 模式尤其明显，符合预期）
- 速度快，更能独立完成任务

### 2. 新模型配置方法
在官方更新前手动添加新模型:

```json
{
  "models": {
    "providers": {
      "anthropic": {
        "baseUrl": "https://api.anthropic.com/",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "claude-opus-4-6",
            "name": "Claude Opus 4.6",
            "api": "anthropic-messages",
            "reasoning": true,
            "input": ["text", "image"],
            "contextWindow": 200000,
            "maxTokens": 128000,
            "cost": {
              "input": 5,
              "output": 25,
              "cacheRead": 0.5,
              "cacheWrite": 6.25
            }
          }
        ]
      }
    }
  }
}
```

设置默认模型:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6"
      }
    }
  }
}
```

添加到 allowlist:
```json
{
  "agents": {
    "defaults": {
      "models": {
        "anthropic/claude-opus-4-6": {
          "alias": "opus46"
        }
      }
    }
  }
}
```

### 3. clawdbot vs openclaw 兼容
- 原版 clawdbot 仍可使用上述配置
- 路径改为 `~/.clawdbot/clawdbot.json`
- 命令改为 clawdbot

---

## 五、Security / Users-helping-users / Channels 频道补充（本轮新增）

### 1) Secret 管理与“防提示注入”的纵深防御
- **Vault 管理 secrets（短时 token）**：把 API keys/密码移出 OpenClaw 所在机，降低“被提示注入诱导外泄”的直接风险；但存在生产环境常见问题：token 过期太激进会带来大量人工续期负担。
- **核心矛盾（insider threat）**：OpenClaw 本质是“内鬼式代理”——只要某些 secrets 必须在机器上可用，就很难做到绝对安全。
- **过滤层思路（关键可抄）**：在“非可信输入（邮件/网页/skill 元数据）→ LLM”之间加一层**不可被说服**的分类/过滤器（例如 BERT classifier），先做注入概率检测/截断/清洗，只把“更安全的元数据”回传给主 agent。
- **时间窗/2FA 的工具门控（关键可抄）**：把高危 tools 权限做成**按时间短暂开启**：
  - 创建 cron 时，自动生成一条“权限 cron”：在任务预计时长（+buffer）内临时授予所需权限，结束后回收；并由一次性 HITL 审核背书。

### 2) ClawHub skills 元数据被投毒（Prompt Injection）事件
- 有人报告在浏览 ClawHub skills 元数据时发现疑似 prompt injection 文本（通过 `clawhub inspect` 看到），涉及 skills：`deepresearch` / `nanopdf` / `memory-pipeline-0-1-0`；随后这些条目似乎已被下架（返回“Skill not found”）。
- 结论：**skills 平台需要更强的清理/审核/扫描机制**（社区正推动）。

### 3) Users-helping-users：使用习惯与安全常识
- **何时 /new**：普遍共识是当输出质量下降、上下文膨胀导致“幻觉/遗忘”时才开新会话。
- **新手安全提醒（很现实）**：
  - 不要在 iPhone 上“原生跑 OpenClaw”（不支持）
  - 尽量不要装在主力电脑；更不要直接给主邮箱收件箱权限
  - 更推荐给 bot 单独账号（像给员工一个独立 Gmail/Drive）

### 4) Channels：多频道 persona/identity 的做法
- 有人在 Discord 里做“每频道不同 persona/identity”：每个频道放独立的 `systemPrompt.md` 或 `identity.md`。
- 进一步的工程化方向：不是硬配 channels config，而是**拆 workspace + 绑定 + agent routing**（skills 可共享到 `.openclaw`）。

---

## 六、Golden-path-deployments / Browser-automation 补充（本轮新增）

### 1) browser-automation：现状与替代方案
- **痛点集中**：Browser Relay 连接易断、用起来“笨重/卡顿”；Chrome attached-tab 方式常见“半小时左右后失效，需要重新 attach + 重启”。
- **Headless 被封**：有人反馈 OpenClaw 自带 headless 浏览器在不少站点会被拦。
- **Playwright 改善**：有人直接切到 Playwright 觉得更稳（但生态上仍需处理反爬/验证码）。
- **Extension 安装 bug**：WSL 下执行 `openclaw browser extension install` 报 *Bundled Chrome extension is missing*，被指认为已知 bug：GitHub Issue #9504。
- **第三方替代：smooth.sh**（YC F24）
  - 号称更稳、少验证码、比直接控 Chrome/Playwright MCP 更便宜
  - 计费：**$0.005/step**；免费额度 **$5**，最多 2 并发浏览器
  - 社区关注点：**隐私**（API 是否读取页面内容）

### 2) golden-path-deployments：部署“黄金路径”的共识
- **nix-openclaw**：结论是“看风险偏好/熟悉程度”
  - 熟悉 nix、愿意在前沿折腾 → 推荐
  - 新手/经验不足 → 不推荐
  - nix 优势：能 pin 版本、可回滚
- **成本教训**：不要让 OpenClaw “自我修复”到处试错（会烧大量 tokens），更便宜的方式是用你付费的外部 AI（Claude/Codex 等）帮助排障，再手动改配置。
- **大规模实例/容器持久化**：提到把 bot 的工作目录/存储放到 **EFS** 一类共享文件系统（避免用 S3 处理可变文件）；并给出参考仓库：`openclaw/clawdinators`（声明式 infra + NixOS modules）。

> 注：我尝试进入 #help-中文 继续挖，但 Browser Relay 在频道跳转时出现超时/回退，等下一次稳定附着后我再把 #help-中文 补上。

## 七、待办/跟进

- [ ] 检查我们的 boot-md hook 是否正确启用
- [ ] 考虑为 S 级任务添加 systemd post-start 脚本作为备份
- [ ] 评估 ackMaxChars: 0 配置是否适合我们的场景
- [ ] 关注 GitHub Discussion #9872 的进展（上下文连续性方案）

---

*来源: OpenClaw Discord - Friends of the Crustacean 🦞🤝*
*频道: #architecture, #help, #skills, #dev, #security, #users-helping-users, #channels*
