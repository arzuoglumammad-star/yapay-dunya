#!/usr/bin/env bash
set +e
cd /workspaces/yapay-dunya

if [ -f runtime/app-terminal.pid ]; then
    kill "$(cat runtime/app-terminal.pid)" 2>/dev/null || true
    rm -f runtime/app-terminal.pid
fi

pkill -f "linux/app-terminal-server.py" 2>/dev/null || true
echo "APP TERMINAL : STOPPED"
