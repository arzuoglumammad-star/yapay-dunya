#!/usr/bin/env bash

set -e

cd /workspaces/yapay-dunya

mkdir -p logs runtime

# Eski Linux Center sürecini kapat
pkill -f "python3 linux/server.py" 2>/dev/null || true

sleep 1

echo "YAPAY DÜNYA REMOTE LINUX BAŞLATILIYOR..."

nohup python3 linux/server.py \
  > logs/linux-center.log 2>&1 &

PID=$!

echo "$PID" > runtime/linux-center.pid

sleep 2

if curl -fsS \
  http://127.0.0.1:8787/api/status \
  > runtime/status.json
then

    echo
    echo "======================================"
    echo " REMOTE LINUX ONLINE"
    echo "======================================"
    echo
    echo "PID  : $PID"
    echo "PORT : 8787"
    echo
    cat runtime/status.json
    echo
    echo "======================================"

else

    echo
    echo "LINUX CENTER BAŞLATILAMADI"
    echo
    cat logs/linux-center.log || true
    exit 1

fi
