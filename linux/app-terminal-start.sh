#!/usr/bin/env bash
set -e

cd /workspaces/yapay-dunya
mkdir -p runtime logs

if curl -fsS http://127.0.0.1:8791/api/status >/dev/null 2>&1; then
    echo "APP TERMINAL : ALREADY ONLINE"
    exit 0
fi

nohup python3 linux/app-terminal-server.py \
    > logs/app-terminal.log 2>&1 &

echo $! > runtime/app-terminal.pid
sleep 1

curl -fsS http://127.0.0.1:8791/api/status
echo
echo "APP TERMINAL : ONLINE"
echo "PORT         : 8791"
