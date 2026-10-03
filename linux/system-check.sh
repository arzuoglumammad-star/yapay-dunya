#!/usr/bin/env bash

echo "======================================"
echo " YAPAY DÜNYA REMOTE LINUX"
echo "======================================"
echo

echo "[SYSTEM]"
uname -a

echo
echo "[USER]"
whoami

echo
echo "[UID]"
id -u

echo
echo "[PYTHON]"
python3 --version

echo
echo "[GIT]"
git --version

echo
echo "[PROJECT]"
pwd

echo
echo "[DISK]"
df -h /

echo
echo "[MEMORY]"
free -h 2>/dev/null || true

echo
echo "[CPU]"
nproc 2>/dev/null || true

echo
echo "[PORT 8787]"
if curl -fsS http://127.0.0.1:8787/api/status >/dev/null 2>&1; then
    echo "ONLINE"
else
    echo "OFFLINE"
fi

echo
echo "SYSTEM_CHECK_COMPLETE"
