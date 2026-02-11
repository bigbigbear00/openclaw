# After Restart Checklist (Mac) — Clawd

> 目标：机器重启后，让 Clawd（OpenClaw）+ 采集管线（CTF 婚嫁金钻情报中心）+ 小红书 MCP（xiaohongshu-mcp）恢复到可工作状态。
> 
> 说明：下面步骤按“最少必要操作”排序。遇到登录/验证码/授权弹窗就停下并告诉我（安全边界）。

---

## A. 先让 OpenClaw / 网关起来（你能跟我对话 = 这一条基本 OK）

0) 启动并解锁 1Password（用于密钥注入）
- 打开 1Password 桌面端 → 解锁（Touch ID/主密码）
- 确认“Integrate with 1Password CLI”已勾选（设置 → 开发者）

1) 确认你能在 Telegram 里收到我消息，并且我能回复。

2) 如果你感觉我“卡住/没反应”，在 Mac 终端执行（任选其一，视你安装方式）：

- 如果有 `openclaw` 命令：
  - `openclaw gateway status`
  - `openclaw gateway restart`

- 如果没有 `openclaw`（曾经出现过 CLI 找不到）：
  - 先运行：`which openclaw && openclaw --version`
  - 把输出贴给我，我会按你机器实际情况给出一条“固定可用”的启动命令。

> 备注：我们之前遇到过“openclaw CLI not found”，所以这一步以你本机实际情况为准。

---

## B. 小红书能力（xiaohongshu-mcp）恢复

### B1) 先启动 MCP 服务（HTTP 18060）
在终端执行：

```bash
cd /Users/apple/clawd/skills/xiaohongshu-mcp/bin
./xiaohongshu-mcp-darwin-arm64
```

看到类似日志表示成功：
- `启动 HTTP 服务器: :18060`

> 建议：保持这个终端窗口开着（等同于服务常驻）。

### B2) 检查登录状态
在另一个终端执行：

```bash
cd /Users/apple/clawd
source .venv/bin/activate
cd skills/xiaohongshu-mcp
python scripts/xhs_client.py status
```

期望输出：
- `✅ Logged in as: xiaohongshu-mcp`

如果显示未登录：
1) 运行登录工具（会弹二维码）：
   ```bash
   cd /Users/apple/clawd/skills/xiaohongshu-mcp/bin
   ./xiaohongshu-login-darwin-arm64
   ```
2) 手机小红书扫码登录
3) 再跑一次 `python scripts/xhs_client.py status`

> 注意：同账号不要同时在别处频繁登录，可能会把会话踢掉。

---

## C. 运行「CTF 婚嫁金钻 情报中心」日报（含 XHS 搜索源）

终端执行：

```bash
cd "/Users/apple/Desktop/CTF_婚嫁金鑽_情報中心"
uv run python scripts/run_daily.py
```

成功后会打印当日日报路径，例如：
- `.../reports/YYYY-MM-DD.md`

如果提示 XHS 超时/500：
- 先回到 **B1** 重启 `xiaohongshu-mcp` 服务（关掉窗口/重新执行启动命令）
- 再重跑 `run_daily.py`

---

## D. Browser Relay（Chrome 扩展）需要时再做

只有当你需要我控制你现有 Chrome 标签页里的 ChatGPT/Gemini 时才做：
1) 打开目标网页标签
2) 点击 OpenClaw Browser Relay 扩展按钮，确保 badge 显示 ON
3) 告诉我“已 attach”

如果出现登录/验证码/授权页面：
- 你手动完成，我暂停等待。

---

## E. 一键健康检查（你可以直接复制粘贴给我，我来判断哪里卡）

把以下输出贴给我：

```bash
# 1) xhs server 是否在 18060 提供服务（能返回 JSON 即可）
curl -m 8 -sS http://localhost:18060/api/v1/login/status || echo "xhs_status_failed"

# 2) xhs python client status
echo "---" && cd /Users/apple/clawd && source .venv/bin/activate && cd skills/xiaohongshu-mcp && python scripts/xhs_client.py status

# 3) CTF 最近一次 snapshot 的 errors
echo "---" && cd "/Users/apple/Desktop/CTF_婚嫁金鑽_情報中心" && ls -t data/snapshot_*.json | head -n 1
```

---

## F. 我需要你提供的“重启后一句话”模板

每次你重启后，你只要在 Telegram 跟我说：
- `重启完成，按 After Restart Checklist 开始`

我就会按上述顺序逐条指导你做，并在每一步告诉你“看到什么算成功/失败怎么处理”。
