# Agent → 主控（哆啦Ai熊）沟通协议 v1

## 目的
让每个 Agent 知道：什么时候必须主动找主控，怎么说，怎么回执。

## 1) 必须主动上报的场景
1. 阻塞：权限、依赖、数据缺失导致无法继续
2. 风险：可能误报、串线、成本异常、来源不可靠
3. 决策：出现 A/B/C 取舍且影响对外输出
4. 超时：预计无法按 ETA 完成
5. 完成：任务完成并可交付

## 2) 消息格式（统一）
```
[TO:MAIN][AGENT:<id>][TYPE:blocker|risk|decision|eta|done]
任务: <一句话>
状态: <进行中/阻塞/完成>
需要主控: <明确动作>
ETA: <时间>
产物: <路径或无>
```

## 3) 升级规则
- TYPE=blocker/risk：立即发，不等待
- 连续 30 分钟无进展：必须发 eta 更新
- done 必须带产物路径

## 4) 禁止项
- 不要发长篇背景，先给结论
- 不要无请求地反复 ping
- 不确定信息必须标“待核验”
- 无新增事实时，禁止“凑更新”或改写旧内容冒充新进展

## 5) Cron 对外输出硬规则（A方案）
1. **NO_CHANGE => NO_REPLY**：无新增事实、无新增影响、无新增动作建议时，必须回复 `NO_REPLY`。
2. **STRICT_OUTPUT**：脚本类任务若指令要求“仅输出 stdout/结果体”，不得附加说明、前后缀、解释。
3. **状态卡（STATE_CARD）必填**：
```
[STATE_CARD]
status: PLANNED|RUNNING|BLOCKED|FAILED|DONE
eta: <ISO时间或相对时间>
artifact: <绝对路径或none>
blocker: <无则none>
```
4. 用户可见播报默认 1-2 句：`新增事实 + 影响 + 下一步`。超过 2 句需有明确新增价值。

## 6) 参数白名单统一（统一规则层 v1）
适用于所有调用 `web_search` 的 Agent：
- `search_lang` 仅允许：`en | zh-hans | zh-hant | vi`
- `ui_lang` 仅允许：`en-US | zh-CN | zh-TW`（不确定可省略）
- `country` 仅允许 Brave 合法枚举（不确定用 `ALL`）
- 非法参数必须自动降级修正，禁止直接透传。

详情见：`/Users/apple/clawd/library/agents/统一规则层_v1_2026-02-11.md`

## 6) 示例

## 5) 示例
```
[TO:MAIN][AGENT:news-analyst][TYPE:risk]
任务: 晚间预警
状态: 进行中
需要主控: 确认是否以准确性优先（降速）
ETA: 00:50
产物: /Users/apple/clawd/reports/news_qms_v1.md
```
