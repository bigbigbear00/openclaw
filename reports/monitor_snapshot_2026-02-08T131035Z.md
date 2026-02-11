# Monitor snapshot
Generated at: 2026-02-08T131035Z

## pm2 status
```
┌────┬──────────────────────────┬─────────────┬─────────┬─────────┬──────────┬────────┬──────┬───────────┬──────────┬──────────┬──────────┬──────────┐
│ id │ name                     │ namespace   │ version │ mode    │ pid      │ uptime │ ↺    │ status    │ cpu      │ mem      │ user     │ watching │
├────┼──────────────────────────┼─────────────┼─────────┼─────────┼──────────┼────────┼──────┼───────────┼──────────┼──────────┼──────────┼──────────┤
│ 5  │ worker-ctf               │ default     │ N/A     │ fork    │ 81795    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 2  │ worker-ctf-director      │ default     │ N/A     │ fork    │ 81680    │ 3h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 6  │ worker-designer          │ default     │ N/A     │ fork    │ 81796    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 7  │ worker-library-keeper    │ default     │ N/A     │ fork    │ 81798    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 8  │ worker-main              │ default     │ N/A     │ fork    │ 81797    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 3  │ worker-nba               │ default     │ N/A     │ fork    │ 81793    │ 2h     │ 0    │ online    │ 0%       │ 8.3mb    │ apple    │ disabled │
│ 0  │ worker-nba-expert        │ default     │ N/A     │ fork    │ 81678    │ 3h     │ 0    │ online    │ 0%       │ 8.3mb    │ apple    │ disabled │
│ 9  │ worker-news-analyst      │ default     │ N/A     │ fork    │ 81799    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 10 │ worker-vn-realestate     │ default     │ N/A     │ fork    │ 81800    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 4  │ worker-writer            │ default     │ N/A     │ fork    │ 81794    │ 2h     │ 0    │ online    │ 0%       │ 8.1mb    │ apple    │ disabled │
│ 1  │ worker-writer-editor     │ default     │ N/A     │ fork    │ 81679    │ 3h     │ 0    │ online    │ 0%       │ 8.2mb    │ apple    │ disabled │
└────┴──────────────────────────┴─────────────┴─────────┴─────────┴──────────┴────────┴──────┴───────────┴──────────┴──────────┴──────────┴──────────┘

```
## Recent topics_state entries
```
{"id":"test-failed-placeholder","agent":"designer","timestamp":"2026-02-08T17:55:00","status":"FAILED_QA_PLACEHOLDER","artifact":"/Users/apple/clawd/claw_comm/designer/artifacts/test-failed-placeholder.txt"}
{"id": "7808de93-8c0c-48d2-9229-ce3b64d746c2", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.312823", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/ctf-director/artifacts/7808de93-8c0c-48d2-9229-ce3b64d746c2-artifact.txt"}
{"id": "test-failed-placeholder", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.363874", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/designer/artifacts/test-failed-placeholder.txt"}
{"id": "test-qa.json", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.415092", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/designer/artifacts/test-qa.json"}
{"id": "eecaa4d4-b8f6-4b77-81da-1c1116b5b47b", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.466570", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/nba-expert/artifacts/eecaa4d4-b8f6-4b77-81da-1c1116b5b47b-artifact.txt"}
{"id": "eecaa4d4-b8f6-4b77-81da-1c1116b5b47b", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.518075", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/nba-expert/artifacts/eecaa4d4-b8f6-4b77-81da-1c1116b5b47b-boxscore.json"}
{"id": "eecaa4d4-qa.json", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.569253", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/nba-expert/artifacts/eecaa4d4-qa.json"}
{"id": "e1fdf51e-41ca-4cea-bd81-ec2734f90119", "agent": "artifacts", "timestamp": "2026-02-08T18:29:58.619852", "status": "QA_MISSING", "artifact": "/Users/apple/clawd/claw_comm/writer-editor/artifacts/e1fdf51e-41ca-4cea-bd81-ec2734f90119-artifact.txt"}
{"id": "PILOT-NBA-2026-02-08", "agent": "writer-editor", "timestamp": "2026-02-08T18:32:45.667689", "status": "DELIVERED", "artifact": "/Users/apple/clawd/reports/PILOT_TOPIC_NBA_2026-02-08-updated.md", "qa": "PASS", "publish_ready": true}
```
## QA failures (artifacts)
- /Users/apple/clawd/claw_comm/writer-editor/artifacts/e1fdf51e-qa.json
- /Users/apple/clawd/claw_comm/designer/artifacts/test-qa.json
- /Users/apple/clawd/claw_comm/ctf-director/artifacts/7808de93-qa.json
