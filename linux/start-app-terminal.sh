#!/usr/bin/env bash
set -e

cd /workspaces/yapay-dunya

mkdir -p runtime logs

PID="runtime/app-terminal.pid"

if [ -f "$PID" ]; then
    OLD="$(cat "$PID" 2>/dev/null || true)"
    if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
        echo "APP TERMINAL zaten çalışıyor: PID $OLD"
        exit 0
    fi
fi

nohup python3 linux/app-terminal.py > logs/app-terminal.log 2>&1 &
NEWPID=$!

echo "$NEWPID" > "$PID"

sleep 2

if curl -fsS http://127.0.0.1:8791/api/terminal/status >/tmp/yapay_terminal_status.json; then
    echo
    echo "=========================================="
    echo " YAPAY DÜNYA APP TERMINAL : ONLINE"
    echo " PORT                      : 8791"
    echo " PID                       : $NEWPID"
    echo "=========================================="
    cat /tmp/yapay_terminal_status.json
    echo
else
    echo "APP TERMINAL başlatılamadı."
    tail -50 logs/app-terminal.log || true
    exit 1
fi
