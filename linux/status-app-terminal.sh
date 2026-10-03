#!/usr/bin/env bash
cd /workspaces/yapay-dunya

echo "=========================================="
echo " YAPAY DÜNYA APP TERMINAL STATUS"
echo "=========================================="

if curl -fsS http://127.0.0.1:8791/api/status 2>/dev/null; then
  echo
  echo "STATUS : ONLINE"
  echo "PORT   : 8791"
  echo "URL    : /terminal"
else
  echo
  echo "STATUS : OFFLINE"
fi

echo "=========================================="
