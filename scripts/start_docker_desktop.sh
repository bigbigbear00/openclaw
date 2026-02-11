#!/bin/bash
set -euo pipefail

# Start Docker Desktop on login (best-effort). Safe to re-run.
# If Docker is already running, do nothing.

if pgrep -x "Docker" >/dev/null 2>&1; then
  exit 0
fi

# Launch Docker Desktop
/usr/bin/open -a "Docker"
