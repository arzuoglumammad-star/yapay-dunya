#!/usr/bin/env bash

pkill -f "python3 linux/server.py" 2>/dev/null || true

rm -f runtime/linux-center.pid

echo "REMOTE LINUX CENTER DURDURULDU."
