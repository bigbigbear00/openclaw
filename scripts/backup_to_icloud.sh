#!/usr/bin/env bash
set -euo pipefail

# Prefer Desktop when it is synced with iCloud (“Desktop & Documents” enabled).
# This avoids TCC restrictions on Mobile Documents path for background jobs.
DEST="$HOME/Desktop/OpenClawBackup"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/backup_to_icloud_$STAMP.log"

mkdir -p "$DEST" "$LOG_DIR"

echo "[backup_to_icloud] start: $(date '+%Y-%m-%dT%H:%M:%S%z')" | tee -a "$LOG_FILE"
echo "[backup_to_icloud] dest:  $DEST" | tee -a "$LOG_FILE"

echo "\n== 1) Backup clawd workspace ==" | tee -a "$LOG_FILE"
rsync -a --delete \
  --exclude ".git/" \
  --exclude "node_modules/" \
  --exclude ".DS_Store" \
  "/Users/apple/clawd/" \
  "$DEST/clawd/" | tee -a "$LOG_FILE"

echo "\n== 2) Backup clawd-agents workspaces ==" | tee -a "$LOG_FILE"
if [ -d "/Users/apple/clawd-agents" ]; then
  rsync -a --delete \
    --exclude ".git/" \
    --exclude "node_modules/" \
    --exclude ".DS_Store" \
    "/Users/apple/clawd-agents/" \
    "$DEST/clawd-agents/" | tee -a "$LOG_FILE"
else
  echo "[backup_to_icloud] /Users/apple/clawd-agents not found; skip" | tee -a "$LOG_FILE"
fi

echo "\n== 3) Backup OpenClaw config + memory index ==" | tee -a "$LOG_FILE"
mkdir -p "$DEST/openclaw_home"

# Config (contains tokens). Store it for full restore; protect iCloud account accordingly.
rsync -a "$HOME/.openclaw/openclaw.json" "$DEST/openclaw_home/" | tee -a "$LOG_FILE"

# Memory (vector/fts). Needed for “记忆都在”.
if [ -d "$HOME/.openclaw/memory" ]; then
  rsync -a --delete "$HOME/.openclaw/memory/" "$DEST/openclaw_home/memory/" | tee -a "$LOG_FILE"
fi

echo "\n[backup_to_icloud] done: $(date '+%Y-%m-%dT%H:%M:%S%z')" | tee -a "$LOG_FILE"
echo "[backup_to_icloud] log:  $LOG_FILE" | tee -a "$LOG_FILE"
