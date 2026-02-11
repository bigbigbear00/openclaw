#!/usr/bin/env bash
# Simple handler tests runner (minimal)
set -e
BASE=/Users/apple/clawd
HANDLERS=$BASE/scripts/handlers
TEST_LOG=$BASE/logs/handler_tests.log
echo "Running handler tests: $(date)" > "$TEST_LOG"
# Test nba_expert handler with a dry-run request id (will not call external if sample exists)
REQ=eecaa4d4-b8f6-4b77-81da-1c1116b5b47b
ART=$BASE/claw_comm/nba-expert/artifacts
mkdir -p "$ART"
python3 "$HANDLERS/nba_expert.py" "$REQ" "$ART" >> "$TEST_LOG" 2>&1 || echo "nba_expert handler failed" >> "$TEST_LOG"
# Check output
if [ -f "$ART/${REQ}-boxscore.json" ]; then
  echo "nba_expert test: PASS" >> "$TEST_LOG"
else
  echo "nba_expert test: FAIL (no boxscore produced)" >> "$TEST_LOG"
fi
# writer-editor test
REQ2=eecaa4d4-b8f6-4b77-81da-1c1116b5b47b
OUT=$BASE/reports/test-writer-output.md
python3 "$HANDLERS/writer_editor.py" "$REQ2" "$ART" "$OUT" >> "$TEST_LOG" 2>&1 || echo "writer_editor handler failed" >> "$TEST_LOG"
if [ -f "$OUT" ]; then
  echo "writer_editor test: PASS" >> "$TEST_LOG"
else
  echo "writer_editor test: FAIL" >> "$TEST_LOG"
fi
echo "Handler tests completed: $(date)" >> "$TEST_LOG"
cat "$TEST_LOG"
