cron_guard plugin

Purpose: Scan job_registry and cron_logs to detect missed jobs, conflicts, and propose fixes. This is a lightweight dry-run tool intended to be invoked manually by agent:main. It does not modify registry when run in dry-run mode.

Usage (dry-run):
python3 cron_guard.py scan --dry-run

Outputs:
- reports/cron_guard_<timestamp>.md (recommendations + patch preview)
- /Users/apple/clawd/reports/job_conflicts_2026-02-09.md (existing)

Notes: apply mode requires explicit approval and will produce a patch file rather than auto-applying.
