#!/usr/bin/env bash
cd /workspaces/yapay-dunya

if [ -f runtime/app-terminal.pid ]; then
  PID=$(cat runtime/app-terminal.pid)
  kill "$PID" 2>/dev/null || true
  rm -f runtime/app-terminal.pid
fi

echo "APP TERMINAL STOPPED"
