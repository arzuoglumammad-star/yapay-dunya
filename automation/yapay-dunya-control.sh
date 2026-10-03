#!/usr/bin/env bash
cd /workspaces/yapay-dunya

case "${1:-status}" in
  start)
    bash automation/yapay-dunya-autostart.sh
    ;;
  stop)
    if [ -f runtime/world-autopilot.pid ]; then
      kill "$(cat runtime/world-autopilot.pid)" 2>/dev/null || true
      rm -f runtime/world-autopilot.pid
    fi
    echo "AUTOPILOT_STOPPED"
    ;;
  status)
    curl -fsS http://127.0.0.1:8790/api/status 2>/dev/null || true
    echo
    curl -fsS http://127.0.0.1:8791/api/status 2>/dev/null || true
    echo
    ;;
  world)
    curl -fsS http://127.0.0.1:8791/api/state
    ;;
  *)
    echo "Kullanım: start | stop | status | world"
    ;;
esac
