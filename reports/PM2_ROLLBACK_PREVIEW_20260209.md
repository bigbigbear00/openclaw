PM2 回滚预览报告

生成时间: 2026-02-09T08:02:06Z

目的: 导出当前 pm2 状态并生成预 rollback 预览（只读）。

已执行（只读/备份）步骤:
1) pm2 save — 已执行，生成 dump 文件: ~/.pm2/dump.pm2
2) 归档: 已把 dump 与 pm2 日志目录打包到: /Users/apple/clawd/archive/pm2_prerollback_20260209T080206Z.tar.gz
   - SHA256: b1507bd6f318cb3edb806fea00b659044a45731dc0942f1c606c1a291233d242
3) 当前 pm2 列表 (摘录):
   - worker-* 均为 stopped / disabled
   - 无 index-reader-ctf-director（已删除）

预期回滚动作（仅为预览 — 不会自动执行）:
- 若要恢复到“初始干净状态”，将执行如下命令:
  1) pm2 stop all
  2) pm2 delete all
  3) pm2 save (更新 empty dump)
  4) 可选: 删除 ~/.pm2/dump.pm2 与 ~/.pm2/logs/* （建议保留日志备份）
- 若要保留部分 app（示例：openclaw-gateway），请在下列命令中排除该 app 名称。

回滚风险提示（短）:
- 删除 pm2 管理的 app 会停止并移除对应进程（若部分服务需长期运行，操作会中断）
- 建议在执行前确认是否要保留 openclaw-gateway 或其它关键 app

后续步骤（请回复）:
- 继续执行回滚（完全清空 pm2） — 回复: EXECUTE_ROLLBACK_EMPTY (我会再次确认并执行)
- 继续执行回滚但保留指定 app — 回复: EXECUTE_ROLLBACK_KEEP <app_name1,app_name2>
- 仅保留当前备份与预览，不执行 — 回复: ABORT_ROLLBACK

审计位置:
- 归档: /Users/apple/clawd/archive/pm2_prerollback_20260209T080206Z.tar.gz
- 报告: /Users/apple/clawd/reports/PM2_ROLLBACK_PREVIEW_20260209.md
- 审计日志追加: /Users/apple/clawd/memory/2026-02-09.md
