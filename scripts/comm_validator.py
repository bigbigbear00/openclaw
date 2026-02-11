#!/usr/bin/env python3
"""
Minimal comm_validator (Stage 3 adjusted)
- Reads message JSON
- Verifies model provider exists in catalog
- Logs token usage to metrics/topic_tokens.jsonl
- If pricing tiers include nonzero rates, also writes cost record to metrics/topic_costs.jsonl
- Performs simple Gate checks (rounds)
"""
import sys, json, os, datetime

BASE='/Users/apple/clawd'
CATALOG=os.path.join(BASE,'library','models','catalog.json')
PRICING=os.path.join(BASE,'library','pricing_table.json')
TOKEN_METRICS=os.path.join(BASE,'metrics','topic_tokens.jsonl')
COST_METRICS=os.path.join(BASE,'metrics','topic_costs.jsonl')

os.makedirs(os.path.join(BASE,'metrics'), exist_ok=True)

if len(sys.argv)<2:
    print('Usage: comm_validator.py /path/to/message.json')
    sys.exit(2)

msgp=sys.argv[1]
with open(msgp,'r',encoding='utf-8') as f:
    msg=json.load(f)
with open(CATALOG,'r',encoding='utf-8') as f:
    catalog=json.load(f)
with open(PRICING,'r',encoding='utf-8') as f:
    pricing=json.load(f)

model_provider=msg.get('meta',{}).get('model_provider') or msg.get('model_provider')
model_tier=msg.get('meta',{}).get('model_tier') or msg.get('model_tier') or 'L3'

catalog_ids=[m.get('id') for m in catalog.get('models',[])]
provider_ok=False
if model_provider:
    for mid in catalog_ids:
        if mid.startswith(model_provider):
            provider_ok=True
            break

in_tokens=msg.get('meta',{}).get('input_tokens',0)
out_tokens=msg.get('meta',{}).get('output_tokens',0)

# write token metrics always
token_record={
    'timestamp': datetime.datetime.now().isoformat(),
    'message_id': msg.get('id'),
    'topic': msg.get('subject'),
    'model_provider': model_provider,
    'model_tier': model_tier,
    'input_tokens': in_tokens,
    'output_tokens': out_tokens
}
with open(TOKEN_METRICS,'a',encoding='utf-8') as tf:
    tf.write(json.dumps(token_record,ensure_ascii=False)+"\n")

# determine if pricing tiers have nonzero
any_price=False
for v in pricing.get('tiers',{}).values():
    if v.get('per_1k_input_tokens',0)>0 or v.get('per_1k_output_tokens',0)>0:
        any_price=True

if any_price:
    per_in=pricing['tiers'].get(model_tier,pricing['tiers'].get('L3',{})).get('per_1k_input_tokens',0)
    per_out=pricing['tiers'].get(model_tier,pricing['tiers'].get('L3',{})).get('per_1k_output_tokens',0)
    cost=(in_tokens/1000.0)*per_in + (out_tokens/1000.0)*per_out
    cost_record={
        'timestamp': datetime.datetime.now().isoformat(),
        'message_id': msg.get('id'),
        'topic': msg.get('subject'),
        'model_tier': model_tier,
        'input_tokens': in_tokens,
        'output_tokens': out_tokens,
        'estimated_cost_usd': round(cost,6)
    }
    with open(COST_METRICS,'a',encoding='utf-8') as cf:
        cf.write(json.dumps(cost_record,ensure_ascii=False)+"\n")

# simple gates (tokens-first enforcement)
ok=True
notes=[]
rounds=msg.get('meta',{}).get('rounds')
if rounds and rounds>10:
    ok=False
    notes.append('rounds exceed safe limit')

if not provider_ok:
    notes.append('model_provider not matched in catalog -> needs_resolution')

# tokens-first gating: always evaluate token thresholds regardless of pricing
try:
    warn_threshold=200000
    gate_threshold=500000
    breaker_threshold=1000000
    total_tokens = in_tokens + out_tokens
    if total_tokens >= breaker_threshold:
        notes.append('BREAKER triggered: tokens >= {}'.format(breaker_threshold))
    elif total_tokens >= gate_threshold:
        notes.append('GATE triggered: tokens >= {}'.format(gate_threshold))
    elif total_tokens >= warn_threshold:
        notes.append('WARN: tokens >= {}'.format(warn_threshold))
except Exception:
    notes.append('token gating check failed')

print('VALIDATION_RESULT:', 'PASS' if ok else 'FAIL')
if any_price:
    print('ESTIMATED_COST_USD:', round(cost,6))
print('TOKENS_LOGGED:', in_tokens, out_tokens)
if notes:
    print('NOTES:')
    for n in notes:
        print('-',n)

sys.exit(0 if ok else 3)
