#!/usr/bin/env python3
"""
Notify an agent and ensure they read the agent index.json
Usage: notify_agent_and_enqueue.py <agent_id> <message>

Behavior:
- Write a request into /Users/apple/clawd/claw_comm/<agent>/index.json for the agent to pull
- Append the same message into the agent's sessions input_queue to simulate an incoming session input
- Append a request record into the agent inbox.jsonl for audit
- Print the paths written for evidence
"""
import sys, json, os
from pathlib import Path
from datetime import datetime

if len(sys.argv) < 3:
    print('Usage: notify_agent_and_enqueue.py <agent_id> <message>')
    sys.exit(2)

agent = sys.argv[1]
msg = sys.argv[2]
BASE = Path('/Users/apple/clawd')
COMM = BASE/'claw_comm'/agent
COMM.mkdir(parents=True,exist_ok=True)
# 1) write index.json
index_path = COMM/'index.json'
index_payload = {
    'id': f'notify-{agent}-{int(datetime.utcnow().timestamp())}',
    'timestamp': datetime.utcnow().isoformat(),
    'from': 'agent:main:main',
    'type': 'request',
    'subject': 'master_notify_and_read',
    'body': msg,
    'deadline': (datetime.utcnow().isoformat()),
    'priority': 'high'
}
# if index.json exists, merge by adding last_request
if index_path.exists():
    try:
        j = json.loads(index_path.read_text(encoding='utf-8'))
    except:
        j = {}
else:
    j = {}
j['last_request'] = index_payload
index_path.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding='utf-8')

# 2) enqueue into agent session input_queue
sess_dir = Path(f'/Users/apple/.openclaw/agents/{agent}/sessions')
sess_dir.mkdir(parents=True,exist_ok=True)
input_q = sess_dir/'input_queue.json'
queue = []
if input_q.exists():
    try:
        queue = json.loads(input_q.read_text(encoding='utf-8'))
    except:
        queue = []
queue.append({'from':'agent:main:main','text':msg,'timestamp':datetime.utcnow().isoformat()})
input_q.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding='utf-8')

# 3) append audit to inbox
inbox = COMM/'inbox.jsonl'
ack = {
    'id': index_payload['id'] + '-audit',
    'timestamp': datetime.utcnow().isoformat(),
    'from': 'agent:main:main',
    'to': f'agent:{agent}',
    'type': 'notice',
    'subject': 'notify_and_enqueue_audit',
    'body': msg,
    'status': 'open'
}
with open(inbox, 'a', encoding='utf-8') as f:
    f.write(json.dumps(ack, ensure_ascii=False) + "\n")

print('WROTE index:', index_path)
print('WROTE input_queue:', input_q)
print('WROTE inbox audit:', inbox)
