Credentials migration: 2026-02-10T09:23:00+08:00

Actions:
- chmod 700 /Users/apple/.openclaw/credentials
- Backed up original openclaw.json -> /Users/apple/clawd/reports/backups/openclaw.json.pre_migrate_20260210.bak
- Extracted and moved sensitive keys into /Users/apple/.openclaw/credentials/migrated_keys.json (mode 600)
  - Fields migrated (examples): channels.telegram.botToken, tools.web.search.apiKey, talk.apiKey, skills.entries.*.apiKey, etc.
- Rewrote /Users/apple/.openclaw/openclaw.json replacing migrated keys with placeholders (__REDACTED__...)

Note: PLEASE rotate the migrated keys at provider consoles if they were used in external services. The migrated_keys.json is owner-only readable (600). If you want me to revoke/rotate keys automatically, tell me which provider to contact.
