#!/usr/bin/env bash
set -e
cd /workspaces/yapay-dunya
mkdir -p runtime logs

if [ -f runtime/app-terminal.pid ]; then
  PID=$(cat runtime/app-terminal.pid 2>/dev/null || true)
  if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
    echo "APP TERMINAL zaten çalışıyor: PID $PID"
    exit 0
  fi
fi

nohup python3 linux/app-terminal.py \
  > logs/app-terminal.log 2>&1 &

PID=$!
echo "$PID" > runtime/app-terminal.pid

sleep 2

if curl -fsS http://127.0.0.1:8791/api/status >/dev/null; then
  echo "APP TERMINAL ONLINE"
  echo "PID : $PID"
  echo "PORT: 8791"
else
  echo "APP TERMINAL BAŞLATILAMADI"
  tail -30 logs/app-terminal.log || true
  exit 1
fi
