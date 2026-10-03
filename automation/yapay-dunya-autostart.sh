#!/usr/bin/env bash
set -e

cd /workspaces/yapay-dunya

mkdir -p runtime logs

PID_FILE="runtime/world-autopilot.pid"
LOG_FILE="logs/world-autopilot.log"

if [ -f "$PID_FILE" ]; then
    PID="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        echo "AUTOPILOT_ALREADY_RUNNING PID=$PID"
        exit 0
    fi
fi

nohup python3 engine/world-autopilot.py \
    > "$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"

sleep 2

if curl -fsS http://127.0.0.1:8791/api/status >/tmp/yd-status.json; then
    cat /tmp/yd-status.json
else
    echo "AUTOPILOT_START_FAILED"
    tail -50 "$LOG_FILE" || true
    exit 1
fi
