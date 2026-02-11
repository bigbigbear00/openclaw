# /shared - 跨 Agent 协作区

此目录用于 Agent 间的信息共享与交接。

## 目录结构

```
shared/
├── announcements.md    # 公告板（重要通知）
├── handoffs/           # Agent 间交接文件
│   └── {from}-to-{to}-{date}.md
└── README.md
```

## 使用规范

### announcements.md
- 全局重要通知（如政策变化、系统升级）
- 各 Agent 启动时可检查
- 由 Main 或 library-keeper 维护

### handoffs/
- Agent A 发现需要 Agent B 处理的事项
- 文件命名：`{from}-to-{to}-{date}.md`
- 示例：`news-analyst-to-vn-realestate-2026-02-05.md`

## 权限
- 所有 Agent 可读
- 写入需通过 Main 或 library-keeper
