# NBA 全覆盖规范 v1（球弟）

更新时间：2026-02-10

## 1) 目标
- 时效：重大事件 10 分钟级；常规轮询 30 分钟级
- 结构：每次输出固定四段
  - A. 已官宣
  - B. 高可信流言
  - C. 走势判断
  - D. 对湖人影响
- 优先级：湖人 > 西部卡位 > 全联盟

## 2) 数据面
- 新闻/流言：ESPN、CBS、RotoWire、RealGM、Yahoo(NBA)
- 伤病：ESPN Injuries（专线）
- 排名/赛况：NBA Stats API（nba_api）
- 赛程：NBA Stats 未来7天拉取（后续并行接入虎扑翻页）

## 3) 任务面（P0）
- `scripts/nba_push_digest.py`：30分钟快讯（四段结构）
- `scripts/nba_injury_watch.py`：伤病专线
- `scripts/nba_standings_watch.py`：西部卡位
- `scripts/nba_schedule_watch.py`：未来7天赛程（湖人优先）

## 4) 风险与回退
- 若 NBA Stats SSL/网络异常：降级为 RSS+ESPN 文本通报
- 若无新增命中：输出“暂无新增命中”，不强行刷屏

## 5) 验收口径
- 结构完整率：100%
- 重大事件漏报率：<5%（按日人工抽检）
- 湖人影响字段覆盖率：100%
