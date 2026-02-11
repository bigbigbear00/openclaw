#!/usr/bin/env python3
"""Simple simulator for longctx compaction behavior (staging).
Generates N messages, appends to session history (in-memory), and runs compaction logic using config.
"""
import json
from pathlib import Path
from math import floor

# Load config
cfg_path = Path('library/specs/longctx_openclaw_config.json')
cfg = json.loads(cfg_path.read_text())['longctx']

# Simple token estimator: english ~4 chars/token, chinese ~2 chars/token approximation
def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    cjk = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    if cjk > len(text) * 0.2:
        return max(1, len(text)//2)
    return max(1, len(text)//4)

# Session state
session = {
    'id': 'sim-session',
    'project_id': 'tg:sim',
    'session_summary': 'S1: Initialized.',
    'summary_cursor_msg_id': None,
    'history': []  # list of (msg_id, text)
}

# model context limit for simulation
ctx_limit = 400000
reserve = max(cfg['reserveMinTokens'], floor(ctx_limit * cfg['reserveRatio']))
budget = ctx_limit - reserve

yellow = budget * cfg['yellowRatio']
red = budget * cfg['redRatio']

# generate messages
def gen_msg(i):
    return f"Message {i}: This is a test message to simulate content and length. " * 5

# simple S2 summarize: join and truncate
def summarize_to_s2(evict_msgs, target_tokens=800):
    text = '\n'.join(m[1] for m in evict_msgs)
    # crude truncate by chars
    approx_chars = target_tokens * 4
    return text[:approx_chars]

# simulate
def simulate(num_msgs=1000):
    audit = []
    for i in range(1, num_msgs+1):
        mid = f'm{i}'
        text = gen_msg(i)
        session['history'].append((mid, text))
        # build context tokens estimate: system + user + S1 + window + rag(0)
        system_tok = 300
        user_tok = estimate_tokens(text)
        s1_tok = estimate_tokens(session['session_summary'])
        # window tokens: sum last N messages until cap by windowTurns (use 20)
        window_turns = 20
        window_msgs = session['history'][-window_turns:]
        window_tok = sum(estimate_tokens(m[1]) for m in window_msgs)
        est = system_tok + user_tok + s1_tok + window_tok
        compaction = False
        s2_written = 0
        if est > yellow:
            # shrink window: take half
            window_msgs = window_msgs[-(window_turns//2):]
            window_tok = sum(estimate_tokens(m[1]) for m in window_msgs)
            est = system_tok + user_tok + s1_tok + window_tok
        if est > red:
            compaction = True
            # evict oldest half of window_msgs to S2
            evict = session['history'][:len(session['history'])//2]
            s2 = summarize_to_s2(evict, target_tokens=cfg['s2TargetTokens'])
            # append to local DB file memory via sqlite script: reuse scripts/longctx_staging_test.py logic? here just write file
            s2_path = Path('data/s2_sim.txt')
            s2_path.parent.mkdir(parents=True, exist_ok=True)
            with open(s2_path, 'a', encoding='utf-8') as f:
                f.write(f"S2 from {evict[0][0]} to {evict[-1][0]}\n")
                f.write(s2 + '\n---\n')
            # update S1: naive prepend
            session['session_summary'] = (session['session_summary'] + '\n' + s2)[:cfg['s1TargetTokens']*4]
            session['summary_cursor_msg_id'] = evict[-1][0]
            # drop evicted
            session['history'] = session['history'][len(evict):]
            s2_written = 1
            # recompute est
            window_msgs = session['history'][-window_turns:]
            window_tok = sum(estimate_tokens(m[1]) for m in window_msgs)
            est = system_tok + user_tok + s1_tok + window_tok
        audit.append({'msg_id': mid, 'est': est, 'compaction': compaction, 's2_written': s2_written})
    return audit

if __name__ == '__main__':
    a = simulate(500)
    print('Simulated', len(a), 'messages. Sample events:')
    samples = [e for e in a if e['compaction']]
    print('Compaction events:', len(samples))
    if samples:
        print(samples[:5])
