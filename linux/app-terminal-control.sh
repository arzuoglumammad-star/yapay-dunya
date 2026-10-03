#!/usr/bin/env bash

ROOT="/workspaces/yapay-dunya"
PORT="8791"

cd "$ROOT"

case "${1:-status}" in

status)
    curl -fsS \
        "http://127.0.0.1:${PORT}/api/status"
    echo
    ;;

start)
    bash linux/app-terminal-watchdog.sh
    ;;

stop)
    if [ -f runtime/app-terminal.pid ]; then
        PID="$(cat runtime/app-terminal.pid)"

        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
        fi

        rm -f runtime/app-terminal.pid
    fi

    echo "APP TERMINAL STOPPED"
    ;;

restart)
    bash linux/app-terminal-control.sh stop
    sleep 1
    bash linux/app-terminal-control.sh start
    ;;

logs)
    tail -100 logs/app-terminal.log
    ;;

*)
    echo "Usage:"
    echo "  bash linux/app-terminal-control.sh status"
    echo "  bash linux/app-terminal-control.sh start"
    echo "  bash linux/app-terminal-control.sh stop"
    echo "  bash linux/app-terminal-control.sh restart"
    echo "  bash linux/app-terminal-control.sh logs"
    ;;

esac
