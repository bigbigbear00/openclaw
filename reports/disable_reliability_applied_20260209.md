DISABLE RELIABILITY - CHANGE REPORT

Generated: 2026-02-09T09:04:14Z

Action summary
- Owner instruction: disable all "reliability/backup"/task-补跑 mechanisms (S/A/B level) across the workspace.
- Per owner authorization, the following actions were taken (local-only):
  1) Full backup created (pre-change):
     - /Users/apple/clawd/archive/disable_reliability_pre_20260209T090414Z.tar.gz
     - sha256: 65bc32f3330df3963ff1dba91b0272777ef5a43570620f238b756e01f5f213a6
     - Included files: cron_logs/job_registry.json, cron_logs/job_monitor.py, cron_logs/job_marker.py, ~/.openclaw/openclaw.json
  2) job_registry.json: all jobs (jobs + daily_jobs) set to "enabled": false. File updated_at set to 2026-02-09T09:03:00+00:00.
     - Path: /Users/apple/clawd/cron_logs/job_registry.json
  3) Monitoring scripts disabled (moved):
     - /Users/apple/clawd/cron_logs/job_monitor.py -> /Users/apple/clawd/cron_logs/job_monitor.py.disabled
     - /Users/apple/clawd/cron_logs/job_marker.py -> /Users/apple/clawd/cron_logs/job_marker.py.disabled

Verification (commands you can run)
- Confirm backup exists:
  - ls -l /Users/apple/clawd/archive/disable_reliability_pre_20260209T090414Z.tar.gz
  - shasum -a 256 /Users/apple/clawd/archive/disable_reliability_pre_20260209T090414Z.tar.gz
- Confirm registry disabled:
  - cat /Users/apple/clawd/cron_logs/job_registry.json | grep -i enabled
- Confirm monitoring scripts disabled:
  - ls -l /Users/apple/clawd/cron_logs/job_monitor.py* /Users/apple/clawd/cron_logs/job_marker.py*

Rollback procedure (how to restore previous behavior)
1) Restore the pre-change archive (if needed):
   - tar -xzf /Users/apple/clawd/archive/disable_reliability_pre_20260209T090414Z.tar.gz -C /
   - (This will restore job_registry.json and the monitoring scripts to their original paths.)
2) Reload job_registry if the system expects in-memory state:
   - (If any service caches job_registry, restart or send config reload to that service.)
3) Re-enable pm2 jobs if they were stopped/removed as part of earlier operations:
   - pm2 resurrect (or pm2 start <app> as needed)
4) Verify:
   - pm2 ls
   - ps aux | egrep 'job_monitor|index_reader' | egrep -v grep
   - run a test cron check and confirm job_monitor.py logs the events

Risk and notes
- With reliability systems disabled, missed jobs will not be auto-detected or auto-retried. Manual patrols and audits are required.
- Backups were taken before the change and are stored locally; if you want an additional off-host backup, provide a remote upload target.
- The openclaw.json file (backup contains API keys) was included in the pre-change archive to preserve full configuration; it is sensitive — treat the backup securely.

Audit trail
- /Users/apple/clawd/memory/2026-02-09.md contains appended entries noting the backup and the change with timestamps.

If you want I can now:
- (1) schedule a manual patrol checklist and run it immediately, reporting findings; or
- (2) execute rollback now and restore prior state; or
- (3) keep current state and set reminders for manual audits.

Reply with one: PATROL / ROLLBACK / HOLD
