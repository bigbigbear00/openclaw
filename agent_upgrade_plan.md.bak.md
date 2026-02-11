Agent Communication & Convergence — Upgrade Plan

Generated: 2026-02-08T10:13 (Asia/Shanghai)
Owner: agent:main:main (哆啦Ai熊)

Purpose
- Reduce endless back-and-forth between main and digital employees (agents) by enforcing a bounded, auditable conversation lifecycle and clear acceptance criteria per topic/task.
- Provide an actionable rollout plan to implement, test, and operationalize the policy and automation helpers.

Scope
- Applies to all digital employees (directories: /Users/apple/clawd-agents/*) and to scheduled cron tasks tracked in /Users/apple/clawd/cron_logs/job_registry.json.

Key Concepts (summary)
- Topic: one message.id (UUID) is the unit of work/interaction.
- Max rounds: default 3 full round-trips (i.e., request + up to two clarifications + final answer). Configurable.
- Timeouts: default per-round 10 minutes; total topic TTL 2 hours. Configurable.
- Acceptance criteria: structured checklist per task type (general / collection / manuscript / audit) required before status=done.
- Escalation: if rounds/timeouts exhausted, auto-escalate to main and flag for human intervention or trigger backup per job_registry.backup_trigger.

Implementation steps
1) Policy file (done)
   - /Users/apple/clawd/library/agent_comm_policy.md contains full schema, lifecycle, and the rules. (Created)

2) Communication directories (done)
   - /Users/apple/clawd/claw_comm/<agent>/inbox.jsonl (append-only JSONL)
   - /Users/apple/clawd/claw_comm/<agent>/artifacts/
   - Seed notices appended to inbox.jsonl for key agents. (Created)

3) Acceptance templates (to create)
   - Standard “conclusion card” template to be appended to every done reply: RESULT / EVIDENCE / NEXT.
   - File: /Users/apple/clawd/library/comm_templates.md

4) Quick-validator script (next)
   - Implement a lightweight validator that: reads an inbox entry with status=done, verifies required fields, checks payload_path existence/checksum, and writes verification result (done_verified / needs_revision) back into the origin inbox and into memory log.
   - Path: /Users/apple/clawd/scripts/comm_validator.py
   - MVP behavior: simple field checks + file existence. Extended behavior later: checksum check, link validation, auto web_search for evidence links.

5) Automation & monitoring (next)
   - Main will monitor all inbox files every 30 minutes (already enabled). For realtime escalation, implement a watcher that reacts to missing ack/timeouts (scripts/watch_inboxes.py).
   - Write audit entries to memory/YYYY-MM-DD.md for all escalations and finalizations.

6) Rollout & agent onboarding (next)
   - Broadcast the policy notice to all agents' inbox.jsonl and request ack within 1 hour. (Seeded some notices.)
   - For each agent, create a short "how-to" in their agent folder: /Users/apple/clawd-agents/<agent>/TOOLS.md will contain a one-line example of how to append a JSON entry to their inbox for requests/replies.

7) Metrics & feedback (ongoing)
   - Track per-topic metrics: rounds_count, time_to_done, %done_verified, escalations. Log to /Users/apple/clawd/metrics/comm_metrics.jsonl.
   - Review weekly for noise/false escalations and tune thresholds.

Safety & Governance
- No secrets in inbox entries. Use references to vaults for sensitive attachments.
- Changes to the global policy file require approval by main (agent:main:main).

Next immediate actions (by me, agent:main:main)
- Implement comm_templates.md (write templates into library).  — PENDING (I will create now if you confirm) 
- Implement comm_validator.py MVP and run it once against a sample topic (ask which topic to test). — PENDING
- Broadcast the full policy to all agents (if you say “broadcast” I will append notice to every inbox) — PENDING

Notes
- Defaults are configurable; tell me if you want different round/time thresholds.
- This plan is stored here: /Users/apple/clawd/agent_upgrade_plan.md (this file) and the canonical policy is /Users/apple/clawd/library/agent_comm_policy.md.

If you approve, I will create the validator script MVP and the comm_templates document next and run a test against the CTF topic or a sample ticket.
