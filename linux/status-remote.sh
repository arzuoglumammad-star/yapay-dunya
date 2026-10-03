#!/usr/bin/env bash

echo "======================================"
echo " REMOTE LINUX STATUS"
echo "======================================"

if curl -fsS \
  http://127.0.0.1:8787/api/status \
  2>/dev/null
then

    echo
    echo "STATUS: ONLINE"

else

    echo
    echo "STATUS: OFFLINE"

fi

echo
echo "[SYSTEM]"

curl -fsS \
  http://127.0.0.1:8787/api/system \
  2>/dev/null || true

echo
