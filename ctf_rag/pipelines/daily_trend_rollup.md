# Daily Trend Rollup（每日趋势汇总）

输入：当日 `ctf_events`
输出：`ctf_trends_daily` + `ctf_claims` 草案

## 步骤
1. 事件归一化
- 统一品牌名/主题词/时间时区
- 去重（source+title+date+hash）

2. 主题聚类
- 按 topic + signal_type + region 聚类
- 统计当日频次、情绪均值、重要度

3. 基线对比
- 计算 7日/30日基线
- 输出 z-score、方向(direction)

4. 生成趋势条目
- 写入 `ctf_trends_daily`
- 标记异常波动（|z|>=2）

5. 生成观点草案（claim）
- 对每个高价值 topic 生成 1-2 条 claim
- 每条 claim 至少挂 2 条 supports 证据，若有反证必须挂 contradicts

6. 质量门槛
- 无证据 claim 不可入库
- confidence < 0.55 只入观察池，不对外输出
