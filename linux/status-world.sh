#!/usr/bin/env bash

cd /workspaces/yapay-dunya

echo "=== WORLD API ==="

if curl -fsS http://127.0.0.1:8790/api/world/status >/dev/null 2>&1; then
  echo "API : ONLINE"
else
  echo "API : OFFLINE"
fi

echo
echo "=== WORLD STATE ==="

node engine/simulation-engine.js status
