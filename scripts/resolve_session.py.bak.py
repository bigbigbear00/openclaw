#!/usr/bin/env python3
"""
Resolve session key for an agent.
Usage: resolve_session.py <agent_key>
Prints JSON: {"label":..., "sessionKey":...} or {"result":"NO_SESSION_YET"}
Logic:
 - Check expected session file: /Users/apple/.openclaw/agents/<agent>/sessions/sessions.json
 - If not found, grep /Users/apple/.openclaw/agents/*/sessions/*.json for group id bindings in openclaw.json
 - Build simple session_roster cache if present at /Users/apple/clawd/library/sessions/session_roster.json
"""
import sys, json, glob, os
from pathlib import Path

def load_roster():
    p=Path('/Users/apple/clawd/library/sessions/session_roster.json')
    if p.exists():
        return json.load(open(p,'r',encoding='utf-8'))
    return {}

if len(sys.argv)<2:
    print(json.dumps({"result":"NO_SESSION_YET"}))
    sys.exit(0)
agent=sys.argv[1]
# 1) check per-agent sessions.json
agent_sessions=Path(f'/Users/apple/.openclaw/agents/{agent}/sessions/sessions.json')
if agent_sessions.exists():
    try:
        data=json.load(open(agent_sessions,'r',encoding='utf-8'))
        # assume data is dict with sessionKey or a list
        if isinstance(data, dict) and data.get('sessionKey'):
            print(json.dumps({'label':agent,'sessionKey':data.get('sessionKey')}))
            sys.exit(0)
        # or look for first session entry
        if isinstance(data, list) and len(data)>0 and isinstance(data[0], dict) and data[0].get('sessionKey'):
            print(json.dumps({'label':agent,'sessionKey':data[0].get('sessionKey')}))
            sys.exit(0)
    except Exception:
        pass
# 2) check roster cache
roster=load_roster()
if agent in roster:
    entry=roster[agent]
    if entry.get('sessionKey'):
        print(json.dumps({'label':agent,'sessionKey':entry.get('sessionKey')}))
        sys.exit(0)
# 3) grep for session-like entries across agents
candidates=[]
for p in glob.glob('/Users/apple/.openclaw/agents/*/sessions/*.json'):
    try:
        j=json.load(open(p,'r',encoding='utf-8'))
        # if file contains a mapping for this agent key or peer id
        if isinstance(j, dict) and (j.get('agent')==agent or j.get('label')==agent):
            if j.get('sessionKey'):
                print(json.dumps({'label':agent,'sessionKey':j.get('sessionKey')}))
                sys.exit(0)
        # scan nested
        if isinstance(j, list):
            for it in j:
                if isinstance(it, dict):
                    if it.get('agent')==agent or it.get('label')==agent or agent in json.dumps(it):
                        if it.get('sessionKey'):
                            print(json.dumps({'label':agent,'sessionKey':it.get('sessionKey')}))
                            sys.exit(0)
    except Exception:
        continue
# 4) fallback: NO_SESSION_YET
print(json.dumps({'result':'NO_SESSION_YET'}))
