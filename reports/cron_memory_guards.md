Cron guards deployed: 2026-02-10

Changes applied:
- backfill_telegram_html.py: added pre-checks for /tmp/memory_backfill.lock and a soft-budget check based on memory_request_metrics; aborts if lock present or recent errors/costs exceed SOFT_BUDGET_USD=5. Writes incident log to ~/clawd/reports/incident_backfill_rate_limit.log on abort.
- Cron jobs updated (payload text) to require guard checks before performing heavy tasks: 3af5e243 (backfill), a8c46e0e (daily refine), 42839235 (nightly dedupe).

Notes:
- The script creates /tmp/memory_backfill.lock during execution and removes it on normal completion. If the script crashes, the lock may remain and will need manual removal.
- The soft-budget check is conservative: it marks risky if any recent error meta exists or estimated cost (calls * $0.05) > $5.

Next recommended steps:
- Integrate lock removal in failure handler (ensure finally: os.remove(lock_path)).
- Replace the rough cost estimator with provider-side quota API checks if available.
- Consider rotating incident log and centralizing path (/Users/apple/clawd/reports/incident_backfill_rate_limit.log).
