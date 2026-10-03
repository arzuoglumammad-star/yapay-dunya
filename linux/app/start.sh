#!/usr/bin/env bash
cd /workspaces/yapay-dunya

if ! curl -fsS http://127.0.0.1:8787/api/status >/dev/null 2>&1; then
    nohup python3 linux/server.py \
        > logs/linux-center.log 2>&1 &
fi

sleep 1

echo "=============================================="
echo " YAPAY DÜNYA LINUX CENTER"
echo "=============================================="
echo "STATUS:"
curl -fsS http://127.0.0.1:8787/api/status
echo
echo "=============================================="
