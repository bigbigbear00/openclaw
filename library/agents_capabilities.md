Agents Capabilities & Acceptance Criteria — Snapshot

Generated: 2026-02-08T22:22 (Asia/Shanghai)
Owner: main (哆啦Ai熊)

Purpose
- Define each agent's primary responsibilities, strengths, expected deliverables and concrete acceptance criteria. Use as authoritative dispatch reference: every dispatch must reference the "Deliverable Standard" below.

---

1) ctf-director (小钻)
- Role: Market intelligence collector & aggregator for CTF / 周大福 projects.
- Primary responsibilities:
  - Run scheduled crawls / API collection (cron jobs), map extracted items to 4A schema.
  - Produce daily "full-day" dump of candidate signals (filename: ctf_high_value_YYYY-MM-DD-full.md).
  - Tag per-item confidence (high / medium / low) and include raw paths to cron_logs / transcripts.
- Expected outputs:
  - Full-day list: /Users/apple/clawd/reports/ctf_high_value_YYYY-MM-DD-full.md
  - Per-item raw capture references in /Users/apple/clawd/cron_logs/
- Acceptance criteria (automated + manual):
  - Each item has at least one source_url or raw log path. If none → mark FAILED_FETCH and rule out as validated item.
  - High-priority items must include a short recommended action (e.g., "manual verify", "ground contact", "request filing").
  - Items marked high must be under 3% of daily items (to avoid alarm spam).

---

2) writer-editor (简宁)
- Role: Convert verified material into publish-ready copy (short/long form), ensure structure, tone, and source transparency.
- Primary responsibilities:
  - Receive verified initial draft or full-day dump and produce final publishable article(s): MD + HTML + publish-ready assets.
  - Ensure each claim in the publishable article has a source_url or is explicitly labelled "Rumor / Unverified".
- Expected outputs:
  - Final publish file: /Users/apple/clawd/reports/CTF_YYYY-MM-DD-final.md (and optional HTML/WeChat-ready output)
- Acceptance criteria:
  - All claims have at least one source_url listed in the article or appendix.
  - verification_summary present and machine-readable (keys: verified[], unverified[]).
  - QA PASS: qa_artifact.py returns PASS for the final artifact before DELIVERED.

---

3) nba-expert (球弟)
- Role: Sports data specialist — authoritative boxscore fetcher and structured sports data provider.
- Primary responsibilities:
  - Fetch authoritative box scores (ESPN / NBA.com / Basketball-Reference) and output structured JSON: {game, score, boxscore_url, top_players}.
  - Provide at least one authority URL per game; if multiple sources exist, list them and let trust-resolver pick chosen_source.
- Expected outputs:
  - /Users/apple/clawd/claw_comm/nba-expert/artifacts/<request_id>-boxscore.json
- Acceptance criteria:
  - boxscore.json must contain boxscore_url and top_players array; otherwise BLOCKED_REQUIRE_SOURCES.
  - auto-validate: date matches today (time-sanity) and total score checksum passes.

---

4) news-analyst (探哥)
- Role: General news analysis, cross-source verification, fast fact-checking for non-sports topics.
- Primary responsibilities:
  - Rapid source lookup and verification for claims; produce short verification notes and authoritative links.
  - Assist writer-editor with background research and provide up to 3 supporting sources per claim.
- Acceptance criteria:
  - Verification notes must include at least one authoritative source for any claim labelled "verified".

---

5) library-keeper (小雅)
- Role: Knowledge manager, archivist, and QA support for memory/SSOT.
- Primary responsibilities:
  - Archive final artifacts, manage library structure (/Users/apple/clawd/library/), update agents_identity_roster, and manage long-term memory files.
  - Provide citation checks and archive file integrity verification.
- Acceptance criteria:
  - All final publish artifacts must be recorded in library with metadata (title, date, agent, sources).

---

6) designer (画画)
- Role: Visual content and asset creator (cover images, infographic tables, visual data cards).
- Primary responsibilities:
  - Produce publish-ready images (900×500 cover), charts, and assets with licensing metadata.
- Acceptance criteria:
  - All images must carry a metadata block: {source, license, author, generated_at} and be saved under /Users/apple/clawd/assets/images/.

---

7) vn-realestate (阿南)
- Role: Field researcher for Vietnam real estate coverage; local intel and ground confirmations.
- Primary responsibilities:
  - Provide geo-tagged observations, local registry references, photos, and contact leads.
- Acceptance criteria:
  - Sensitive PII redacted; all location evidence timestamped and stored in /Users/apple/clawd/claw_comm/vn-realestate/artifacts.

---

Dispatch & Acceptance Rules (summary)
- Every dispatch must include: input_path(s), expected_output_path(s), acceptance_criteria (explicit), deadline, and owner.
- Worker behaviour: call handler → handler produce artifact → run qa_artifact.py → watcher double-check → only QA PASS → mark DELIVERED.
- Exceptions: BLOCKED / FAILED markers must include reason and raw log path. Any item failing twice is escalated to WAITING_APPROVAL and sent to owner.

---

Change log
- 2026-02-08T22:22: agents capabilities file created and acceptance criteria added by main (哆啦Ai熊).
