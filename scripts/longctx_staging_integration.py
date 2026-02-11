#!/usr/bin/env python3
"""Staging integration: wire longctx_runtime.handle_telegram_message into a simple replay that mimics the main agent message flow.
This does NOT touch production; it reads from a sample message file (or generates) and calls the handler, writing replies to transcripts/ for inspection.
"""
from pathlib import Path
import json
import time
from scripts.longctx_runtime import handle_telegram_message

TRANSCRIPTS = Path('transcripts')
TRANSCRIPTS.mkdir(exist_ok=True)

# create sample messages
msgs = []
for i in range(1,101):
    msgs.append({'id': f'm{i}', 'chat_id': 'staging-chat', 'text': f'Staging message {i} - content repeated. ' * 10})

session = {'id':'staging-main-session','project_id':'tg:staging-chat','session_summary':'S1 seed','history':[]}

out_path = TRANSCRIPTS / f'staging_run_{int(time.time())}.jsonl'
with open(out_path, 'w', encoding='utf-8') as out:
    for m in msgs:
        session['history'].append((m['id'], m['text']))
        reply = handle_telegram_message(session, m)
        record = {'msg':m, 'reply':reply}
        out.write(json.dumps(record, ensure_ascii=False) + '\n')
        time.sleep(0.01)

print('Staging integration run complete. Transcript:', out_path)
