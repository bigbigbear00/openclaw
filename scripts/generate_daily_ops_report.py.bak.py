#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, date

OPS_BOARD = Path("/Users/apple/clawd/metrics/ops_board.md")
TOPICS_STATE = Path("/Users/apple/clawd/metrics/topics_state.jsonl")
TOKENS_LOG = Path("/Users/apple/clawd/metrics/topic_tokens.jsonl")
COSTS_LOG = Path("/Users/apple/clawd/metrics/topic_costs.jsonl")
TEMPLATE = Path("/Users/apple/clawd/reports/DAILY_OPS_REPORT_TEMPLATE.md")
OUT_DIR = Path("/Users/apple/clawd/reports/daily")

def load_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        try:
            out.append(json.loads(line))
        except:
            continue
    return out

def main():
    today = date.today().isoformat()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    topics = load_jsonl(TOPICS_STATE)
    tokens = load_jsonl(TOKENS_LOG)
    costs = load_jsonl(COSTS_LOG)

    delivered = [t for t in topics if str(t.get('status','')).upper() == 'DELIVERED']
    publish_ready = [t for t in topics if t.get('publish_ready') is True]
    blocked = [t for t in topics if 'BLOCKED' in str(t.get('status','')).upper() or str(t.get('status','')).upper().startswith('BLOCKED')]
    failed_qa = [t for t in topics if 'FAILED_QA' in str(t.get('status','')).upper()]

    total_in = sum(x.get('input_tokens',0) for x in tokens)
    total_out = sum(x.get('output_tokens',0) for x in tokens)
    total_tokens = total_in + total_out

    external_cost = 0.0
    for c in costs:
        if c.get('pricing_status') == 'exact':
            external_cost += float(c.get('estimated_cost_usd',0) or 0)

    internal_free_tokens = 0
    for c in costs:
        if c.get('pricing_status') == 'internal_free':
            internal_free_tokens += int(c.get('input_tokens',0) or 0) + int(c.get('output_tokens',0) or 0)

    top_lines = []
    for t in sorted(delivered, key=lambda x: x.get('timestamp',''), reverse=True)[:5]:
        top_lines.append(f"- {t.get('id')} | {t.get('agent')} | publish_ready={t.get('publish_ready')} | tokens={t.get('tokens', 'n/a')}")
    top_block = '\n'.join(top_lines) if top_lines else '- (none)'

    exc_lines = []
    for t in failed_qa[:5]:
        exc_lines.append(f"- FAILED_QA: {t.get('id')} ({t.get('agent')})")
    for t in blocked[:5]:
        exc_lines.append(f"- BLOCKED: {t.get('id')} reason={t.get('blocked_reason','')}")
    exceptions_block = '\n'.join(exc_lines) if exc_lines else '- None'

    waiting = [t for t in topics if str(t.get('status','')).upper().startswith('WAITING_APPROVAL')]
    approval_lines = [f"- {t.get('id')} requires boss decision" for t in waiting]
    approval_block = '\n'.join(approval_lines) if approval_lines else '- None'

    next_actions = []
    if failed_qa:
        next_actions.append('- Review FAILED_QA topics and fix handlers.')
    if waiting:
        next_actions.append('- Boss approval needed for WAITING_APPROVAL topics.')
    if not delivered:
        next_actions.append('- No deliveries today; check workers.')
    next_block = '\n'.join(next_actions) if next_actions else '- Continue Pilot Week as planned.'

    tpl = TEMPLATE.read_text(encoding='utf-8')
    report = (tpl.replace('{{date}}', today)
        .replace('{{delivered_count}}', str(len(delivered)))
        .replace('{{publish_ready_count}}', str(len(publish_ready)))
        .replace('{{blocked_count}}', str(len(blocked)))
        .replace('{{failed_qa_count}}', str(len(failed_qa)))
        .replace('{{top_topics_block}}', top_block)
        .replace('{{total_input_tokens}}', str(total_in))
        .replace('{{total_output_tokens}}', str(total_out))
        .replace('{{total_tokens}}', str(total_tokens))
        .replace('{{external_cost_usd}}', f"{external_cost:.4f}")
        .replace('{{internal_free_tokens}}', str(internal_free_tokens))
        .replace('{{exceptions_block}}', exceptions_block)
        .replace('{{approval_block}}', approval_block)
        .replace('{{next_actions_block}}', next_block)
        .replace('{{generated_at}}', datetime.utcnow().isoformat()+'Z') )

    out_path = OUT_DIR / f"OPS_DAILY_{today}.md"
    out_path.write_text(report, encoding='utf-8')
    print(f"[OK] Daily ops report generated: {out_path}")

if __name__ == "__main__":
    main()
