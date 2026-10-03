#!/usr/bin/env bash

cd /workspaces/yapay-dunya

if [ -f runtime/world-api.pid ]; then
  PID="$(cat runtime/world-api.pid)"
  kill "$PID" 2>/dev/null || true
  rm -f runtime/world-api.pid
fi

pkill -f "python3 linux/world-api.py" 2>/dev/null || true

echo "WORLD API STOPPED"
