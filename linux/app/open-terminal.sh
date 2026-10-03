#!/usr/bin/env bash

cd /workspaces/yapay-dunya

if ! curl -fsS http://127.0.0.1:8787/api/status >/dev/null 2>&1; then
    nohup python3 linux/server.py \
      > logs/linux-center.log 2>&1 &
    sleep 2
fi

echo
echo "========================================"
echo " YAPAY DÜNYA TERMINAL"
echo "========================================"
echo
echo "Linux API:"
curl -fsS http://127.0.0.1:8787/api/status
echo
echo
echo "Terminal:"
echo "http://127.0.0.1:8787/terminal"
echo
echo "========================================"
