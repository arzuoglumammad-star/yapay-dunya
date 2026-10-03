#!/usr/bin/env bash

cd /workspaces/yapay-dunya
mkdir -p runtime logs

if curl -fsS http://127.0.0.1:8790/api/world/status >/dev/null 2>&1; then
  echo "WORLD API ALREADY ONLINE"
  exit 0
fi

nohup python3 linux/world-api.py \
  > logs/world-api.log 2>&1 &

echo $! > runtime/world-api.pid

sleep 1

if curl -fsS http://127.0.0.1:8790/api/world/status >/dev/null 2>&1; then
  echo "WORLD API ONLINE : 8790"
else
  echo "WORLD API FAILED"
  cat logs/world-api.log
  exit 1
fi
