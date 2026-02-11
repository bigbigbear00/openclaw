#!/usr/bin/env python3
"""
Minimal inbox watcher (Stage 3 MVP)
- Scans /Users/apple/clawd/claw_comm/*/inbox.jsonl for new entries (offset per agent)
- Processes entries by appending an ack to sender inbox and marking local offset
- Dedupe by message id
- Writes topic state to /Users/apple/clawd/metrics/topics_state.json
"""
import os, json, time, glob, datetime
BASE='/Users/apple/clawd'
COMM=os.path.join(BASE,'claw_comm')
OFFSETS=os.path.join(BASE,'claw_comm','offsets.json')
TOPIC_STATE=os.path.join(BASE,'metrics','topics_state.json')

if not os.path.isdir(os.path.join(BASE,'metrics')):
    os.makedirs(os.path.join(BASE,'metrics'))

# load offsets
if os.path.exists(OFFSETS):
    offsets=json.load(open(OFFSETS,'r',encoding='utf-8'))
else:
    offsets={}

# load topic state
if os.path.exists(TOPIC_STATE):
    topics=json.load(open(TOPIC_STATE,'r',encoding='utf-8'))
else:
    topics={}

# scan agents
for agent_dir in os.listdir(COMM):
    inbox=os.path.join(COMM,agent_dir,'inbox.jsonl')
    if not os.path.exists(inbox):
        continue
    last=offsets.get(agent_dir,0)
    with open(inbox,'r',encoding='utf-8') as f:
        lines=f.read().splitlines()
    for i,line in enumerate(lines[last:],start=last):
        try:
            msg=json.loads(line)
        except Exception:
            continue
        mid=msg.get('id')
        if not mid:
            # skip malformed messages without id
            continue
        # dedupe
        if str(mid) in topics:
            # already seen
            pass
        else:
            # write minimal topic entry
            topics[str(mid)]={
                'timestamp': msg.get('timestamp'),
                'from': msg.get('from'),
                'to': msg.get('to'),
                'subject': msg.get('subject'),
                'status': msg.get('status','open')
            }
            # append ack to sender inbox if exists
            sender=msg.get('from','agent:unknown').split(':')[-1]
            sender_inbox=os.path.join(COMM,sender,'inbox.jsonl')
            ack={'id': 'ack-'+str(mid), 'timestamp': datetime.datetime.now().isoformat(), 'from': 'agent:main:main','to': msg.get('from'),'type':'ack','subject':'ack for '+str(mid),'body':'ack','status':'done'}
            if os.path.exists(sender_inbox):
                with open(sender_inbox,'a',encoding='utf-8') as sf:
                    sf.write(json.dumps(ack,ensure_ascii=False)+"\n")
        # additional: if message is a done notice, enforce QA check before marking DELIVERED
        if msg.get('type') in ('done','notice') and ('done for' in (msg.get('subject') or '')):
            # extract request id from subject
            try:
                req_id = (msg.get('subject') or '').split()[-1]
            except:
                req_id = None
            # expected artifact dir
            art_dir=os.path.join(COMM,agent_dir,'artifacts')
            qa_file=os.path.join(art_dir, (req_id or '') + '-qa.json')
            if req_id and os.path.exists(qa_file):
                try:
                    q=json.load(open(qa_file,'r',encoding='utf-8'))
                    if q.get('result')=='PASS':
                        topics[req_id]['status']='DELIVERED'
                        topics[req_id]['artifact']=msg.get('payload_path','')
                        topics[req_id]['qa']='PASS'
                    else:
                        topics[req_id]['status']='FAILED_QA'
                except Exception:
                    topics[req_id]['status']='FAILED_QA'
            else:
                topics[req_id]['status']='FAILED_QA_MISSING'
        offsets[agent_dir]=i+1
# persist offsets and topics
with open(OFFSETS,'w',encoding='utf-8') as f:
    json.dump(offsets,f,ensure_ascii=False,indent=2)
with open(TOPIC_STATE,'w',encoding='utf-8') as f:
    json.dump(topics,f,ensure_ascii=False,indent=2)
print('watcher run complete; processed dirs:', list(offsets.keys()))
