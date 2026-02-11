#!/usr/bin/env python3
"""
Minimal Agent Worker
- Polls its inbox.jsonl every 30s
- For each new request (status=open), append an ack to sender inbox and after a simulated action, append a done entry with artifact_path
- Writes topic_state update to /Users/apple/clawd/metrics/topics_state.json
"""
import time, json, os, sys
from pathlib import Path
from datetime import datetime

if len(sys.argv)<2:
    print('Usage: agent_worker.py <agent_key>')
    sys.exit(2)

agent = sys.argv[1]
BASE = Path('/Users/apple/clawd')
COMM = BASE/'claw_comm'/agent
inbox = COMM/'inbox.jsonl'
ART = COMM/'artifacts'
ART.mkdir(parents=True, exist_ok=True)
TOPIC_STATE = BASE/'metrics'/'topics_state.jsonl'
TOPIC_STATE.parent.mkdir(parents=True, exist_ok=True)

# simple offset file
offset_file = COMM/'offset.txt'
if not offset_file.exists():
    offset_file.write_text('0')

def append_inbox(target_agent, message):
    tpath = BASE/'claw_comm'/target_agent/'inbox.jsonl'
    with open(tpath, 'a', encoding='utf-8') as f:
        f.write(json.dumps(message, ensure_ascii=False) + '\n')

def write_topic_state(entry):
    with open(TOPIC_STATE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

print(f'Worker starting for agent: {agent}')
while True:
    try:
        last = int(offset_file.read_text())
        lines = []
        if inbox.exists():
            with open(inbox,'r',encoding='utf-8') as f:
                lines = f.read().splitlines()
        for idx in range(last, len(lines)):
            try:
                msg = json.loads(lines[idx])
            except Exception:
                continue
            # process only requests with status open
            if msg.get('type')=='request' and msg.get('status','')=='open':
                req_id = msg.get('id')
                sender = msg.get('from','agent:unknown')
                sender_agent = sender.split(':')[-1]
                # write ack to sender inbox
                ack = {
                    'id': 'ack-'+req_id,
                    'timestamp': datetime.now().isoformat(),
                    'from': f'agent:{agent}',
                    'to': sender,
                    'type': 'ack',
                    'subject': f'ack for {req_id}',
                    'body': 'ack',
                    'status': 'in-progress'
                }
                append_inbox(sender_agent, ack)
                # attempt to call a handler for this agent: scripts/handlers/<agent>.py
                handler = Path('/Users/apple/clawd/scripts/handlers')/f"{agent}.py"
                art_path = str(ART/f'{req_id}-artifact.txt')
                if handler.exists():
                    # call handler with (request_id, artifacts_dir, optional output)
                    import subprocess
                    try:
                        # handler is expected to create <request_id>-boxscore.json or other artifacts
                        subprocess.run(['python3', str(handler), req_id, str(ART)], check=True, timeout=60)
                        # after handler, run QA on produced artifacts
                        # prefer boxscore json
                        boxjson = ART/f"{req_id}-boxscore.json"
                        if boxjson.exists():
                            # run QA
                            from subprocess import run
                            run(['python3','/Users/apple/clawd/scripts/qa_artifact.py', str(boxjson)])
                            art_path = str(boxjson)
                            qa_file = ART/f"{req_id}-qa.json"
                            qa_pass = False
                            if qa_file.exists():
                                import json
                                q = json.loads(qa_file.read_text(encoding='utf-8'))
                                qa_pass = (q.get('result')=='PASS')
                            if qa_pass:
                                status='DELIVERED'
                                # write done
                                done = {
                                    'id': 'done-'+req_id,
                                    'timestamp': datetime.now().isoformat(),
                                    'from': f'agent:{agent}',
                                    'to': sender,
                                    'type': 'done',
                                    'subject': f'done for {req_id}',
                                    'body': 'done',
                                    'status': 'done',
                                    'payload_path': art_path
                                }
                                append_inbox(sender_agent, done)
                                topic_entry = {
                                    'id': req_id,
                                    'agent': agent,
                                    'timestamp': datetime.now().isoformat(),
                                    'status': status,
                                    'artifact': art_path,
                                    'qa': 'PASS'
                                }
                                write_topic_state(topic_entry)
                            else:
                                # QA failed
                                topic_entry = {
                                    'id': req_id,
                                    'agent': agent,
                                    'timestamp': datetime.now().isoformat(),
                                    'status': 'FAILED_QA',
                                    'artifact': art_path
                                }
                                write_topic_state(topic_entry)
                                # notify sender of failed QA
                                fail_msg = {
                                    'id': 'failed-'+req_id,
                                    'timestamp': datetime.now().isoformat(),
                                    'from': f'agent:{agent}',
                                    'to': sender,
                                    'type': 'notice',
                                    'subject': f'FAILED_QA for {req_id}',
                                    'body': 'QA failed: placeholder or invalid artifact',
                                    'status': 'failed'
                                }
                                append_inbox(sender_agent, fail_msg)
                        else:
                            # handler did not produce expected artifact
                            topic_entry = {
                                'id': req_id,
                                'agent': agent,
                                'timestamp': datetime.now().isoformat(),
                                'status': 'FAILED_FETCH',
                                'artifact': ''
                            }
                            write_topic_state(topic_entry)
                            fail_msg = {
                                'id': 'failed-'+req_id,
                                'timestamp': datetime.now().isoformat(),
                                'from': f'agent:{agent}',
                                'to': sender,
                                'type': 'notice',
                                'subject': f'FAILED_FETCH for {req_id}',
                                'body': 'Handler did not produce expected artifact',
                                'status': 'failed'
                            }
                            append_inbox(sender_agent, fail_msg)
                    except Exception as e:
                        # handler error
                        topic_entry = {
                            'id': req_id,
                            'agent': agent,
                            'timestamp': datetime.now().isoformat(),
                            'status': 'FAILED_HANDLER',
                            'artifact': ''
                        }
                        write_topic_state(topic_entry)
                        err_msg = {
                            'id': 'error-'+req_id,
                            'timestamp': datetime.now().isoformat(),
                            'from': f'agent:{agent}',
                            'to': sender,
                            'type': 'notice',
                            'subject': f'ERROR handler {req_id}',
                            'body': str(e),
                            'status': 'failed'
                        }
                        append_inbox(sender_agent, err_msg)
                else:
                    # no handler: block and notify
                    topic_entry = {
                        'id': req_id,
                        'agent': agent,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'BLOCKED_NO_HANDLER',
                        'artifact': ''
                    }
                    write_topic_state(topic_entry)
                    block_msg = {
                        'id': 'blocked-'+req_id,
                        'timestamp': datetime.now().isoformat(),
                        'from': f'agent:{agent}',
                        'to': sender,
                        'type': 'notice',
                        'subject': f'BLOCKED_NO_HANDLER for {req_id}',
                        'body': 'No handler implemented for agent to produce real artifact',
                        'status': 'blocked'
                    }
                    append_inbox(sender_agent, block_msg)
            # update offset
            offset_file.write_text(str(idx+1))
    except Exception as e:
        # log error to memory
        mem = BASE/'memory'/ (datetime.now().strftime('%Y-%m-%d') + '.md')
        with open(mem,'a',encoding='utf-8') as mf:
            mf.write('\nWorker error for '+agent+': '+str(e)+'\n')
    time.sleep(30)
