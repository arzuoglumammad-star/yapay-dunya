#!/usr/bin/env bash

ROOT="/workspaces/yapay-dunya"
PORT="8791"

cd "$ROOT"

mkdir -p runtime logs

if curl -fsS --max-time 3 \
    "http://127.0.0.1:${PORT}/api/status" \
    >/dev/null 2>&1
then
    echo "APP TERMINAL ONLINE"
    exit 0
fi

echo "APP TERMINAL OFFLINE — STARTING"

nohup python3 linux/app-terminal.py \
    > logs/app-terminal.log \
    2>&1 </dev/null &

PID=$!

echo "$PID" > runtime/app-terminal.pid

sleep 2

if curl -fsS --max-time 3 \
    "http://127.0.0.1:${PORT}/api/status" \
    >/dev/null 2>&1
then
    echo "APP TERMINAL STARTED"
    exit 0
fi

echo "APP TERMINAL START FAILED"
tail -50 logs/app-terminal.log || true
exit 1
