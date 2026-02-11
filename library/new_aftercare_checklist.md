# /new 后防断层清单（必做）

> 目标：/new 后 60 秒内恢复“数字人记忆”，避免设定/路由/协作机制丢失。

## A. 先加载（只读）
1) 宪法层：`/Users/apple/clawd/MEMORY.md`
2) 智能体身份 SSOT：`/Users/apple/clawd/library/agents_identity_roster.md`
3) 智能体命名/群绑定：`/Users/apple/clawd/library/agents_roster.md`
4) 最近 1–2 天流水账：`/Users/apple/clawd/memory/YYYY-MM-DD.md`
5) 会议室：`/Users/apple/clawd/shared/meeting_room.md`

## B. 再做 3 个快速自检（不改配置）
- 运行自检脚本（只读）：`python3 /Users/apple/clawd/scripts/aftercare_selfcheck.py`
- 1) 当前 `agents.list` 是否包含全部智能体（main/小钻/阿南/探哥/球弟/小雅/画画/简宁）
- 2) `bindings` 是否齐全且群ID正确（特别是写作工坊：-5260834117）
- 3) 主控 main 的 telegram group sessions 应为 0（防止抢答/串线）

## C. 涉及配置改动前的硬门槛
- 如果要 patch `openclaw.json`：先把“变更前后 diff + 风险点 + 回滚方案”写出来，再动手。
- 禁止在没完成 A/B 的情况下做 agents.list/bindings 相关 patch。
