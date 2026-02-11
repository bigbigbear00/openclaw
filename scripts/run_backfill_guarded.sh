#!/usr/bin/env bash
set -euo pipefail

PY="/Users/apple/clawd/memory_system/.venv/bin/python"
TASK_ID="3af5e243-a47c-41c7-8453-496fa479713e"
LOCK="/tmp/memory_backfill.lock"
LOCKDIR="/tmp/memory_backfill.lock.d"
STATE="/Users/apple/clawd/reports/backfill_${TASK_ID}.state"
LOG="/Users/apple/clawd/reports/backfill_${TASK_ID}.log"
INCIDENT="/Users/apple/clawd/reports/incident_backfill_rate_limit.log"

TS(){ date -u +"%Y-%m-%dT%H:%M:%SZ"; }
append(){
  local line="$1"
  echo -e "$line" | tee -a "$LOG"
}

if ! mkdir "$LOCKDIR" 2>/dev/null; then
  append "$(TS)\tstate: skipped_by_lock\tlockdir=$LOCKDIR"
  echo -e "$(TS)\tstate: skipped_by_lock\tlockdir=$LOCKDIR" >> "$STATE"
  exit 0
fi

echo $$ > "$LOCKDIR/pid"
echo "$(TS)" > "$LOCKDIR/created_at"
ln -sf "$LOCKDIR" "$LOCK" 2>/dev/null || true

cleanup(){
  if [[ -d "$LOCKDIR" ]]; then
    rm -rf "$LOCKDIR"
    append "$(TS)\tstate: lock_removed\tlockdir=$LOCKDIR"
    echo -e "$(TS)\tstate: lock_removed\tlockdir=$LOCKDIR" >> "$STATE"
  fi
  if [[ -L "$LOCK" || -e "$LOCK" ]]; then
    rm -f "$LOCK" || true
  fi
}
trap cleanup EXIT INT TERM

append "$(TS)\tstate: lock_created\tlockdir=$LOCKDIR"
echo -e "$(TS)\tstate: lock_created\tlockdir=$LOCKDIR" >> "$STATE"

GUARD_JSON="$($PY - <<'PY'
import json
from memory_system.memory_v1_rag import CFG, get_conn
ret={"db_ok":False,"errs":None,"calls":None,"has_429":None,"est_cost":None,"risky":True,"reason":"db_error"}
try:
    with get_conn(CFG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM memory_request_metrics WHERE created_at > now() - interval '1 hour' AND (meta->>'error') IS NOT NULL")
            errs=int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM memory_request_metrics WHERE created_at > now() - interval '1 hour'")
            calls=int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM memory_request_metrics WHERE created_at > now() - interval '1 hour' AND (meta::text ILIKE '%429%' OR coalesce(query,'') ILIKE '%429%')")
            has_429=int(cur.fetchone()[0])
            est_cost=round(calls*0.05,4)
            risky=bool(has_429>0 or est_cost>5.0)
            ret.update({"db_ok":True,"errs":errs,"calls":calls,"has_429":has_429,"est_cost":est_cost,"risky":risky,"reason":"ok" if not risky else "has_429_or_over_budget"})
except Exception as e:
    ret["reason"]=f"db_error:{e}"
print(json.dumps(ret, ensure_ascii=False))
PY
)"

append "$(TS)\tguard: $GUARD_JSON"

if $PY - <<PY
import json
j=json.loads('''$GUARD_JSON''')
raise SystemExit(0 if j.get('risky') else 1)
PY
then
  echo -e "$(TS)\tbackfill aborted: recent 429 or budget over \$5" >> "$INCIDENT"
  append "$(TS)\tstate: skipped_rate_limit\tguard=$GUARD_JSON"
  echo -e "$(TS)\tstate: skipped_rate_limit\tguard=$GUARD_JSON" >> "$STATE"
  exit 0
fi

FILES=(
  /Users/apple/clawd/tmp/tg_export_manual/messages.html
  /Users/apple/clawd/tmp/tg_export_manual/messages2.html
  /Users/apple/clawd/tmp/tg_export_manual/messages3.html
)
RUN=0
SKIP=0
FAIL=0
SESSION_BASE="tg_backfill_20260211_guarded"

append "$(TS)\tstate: running_backfill\tfiles=${#FILES[@]}"

idx=0
for f in "${FILES[@]}"; do
  idx=$((idx+1))
  if [[ ! -f "$f" ]]; then
    append "[skip] missing $f"
    SKIP=$((SKIP+1))
    continue
  fi

  append "[run] $f"
  set +e
  OUT=$(OPENAI_API_KEY="${OPENAI_API_KEY:-}" "$PY" -m memory_system.scripts.backfill_telegram_html \
    --html "$f" \
    --user_id hua_liu \
    --session_id "${SESSION_BASE}_${idx}" \
    --chunk_size 120 \
    --key_turns 30 \
    --lock-mode external \
    --max-runtime-sec 600 \
    --chunk-timeout-sec 45 2>&1)
  RC=$?
  set -e

  append "$OUT"
  if [[ $RC -eq 0 ]]; then
    RUN=$((RUN+1))
  else
    FAIL=$((FAIL+1))
  fi
done

append "$(TS)\tstate: completed\tran=$RUN\tskipped=$SKIP\tfailed=$FAIL"
echo -e "$(TS)\tstate: completed\tran=$RUN\tskipped=$SKIP\tfailed=$FAIL" >> "$STATE"
