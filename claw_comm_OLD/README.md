Claw_comm — Agent Communication Directory

Purpose
- Central filesystem channel for structured, auditable text exchanges between the main controller (哆啦Ai熊) and each digital employee (agent).

Structure
- /Users/apple/clawd/claw_comm/<agent_key>/inbox.jsonl  (append-only JSONL for messages addressed to that agent)
- /Users/apple/clawd/claw_comm/<agent_key>/artifacts/  (attachments, reports, snapshots produced for/by that agent)

How to use
1) Sending a message:
   - Create a JSON object following the schema in library/agent_comm_policy.md and append it (newline) to the recipient's inbox.jsonl.
2) Acknowledgement:
   - Recipient reads its inbox.jsonl, appends an ack entry to the sender's inbox.jsonl (or its own inbox with type=ack referencing original id).
3) Artifacts:
   - Place files under the artifacts/ folder and include the path in the message payload_path.

Notes
- Keep inbox.jsonl newline-delimited JSON objects. Do not rewrite or delete past entries; append only.
- Main (agent:main:main) will monitor inbox files and write audit lines into memory/YYYY-MM-DD.md.

Support
- If you want me to seed messages or help agents adopt this (write adapters that append JSON automatically), tell me which agents to start with.
