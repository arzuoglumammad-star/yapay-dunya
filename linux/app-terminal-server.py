#!/usr/bin/env python3
import json
import os
import shlex
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8791
ROOT = Path("/workspaces/yapay-dunya").resolve()

BLOCKED = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "shutdown",
    "reboot",
    "poweroff",
    ":(){ :|:& };:",
    "dd if=/dev/zero",
    "dd if=/dev/random",
    "chmod -R 777 /",
    "chown -R",
]

def blocked(cmd):
    x = cmd.lower().replace(" ", "")
    for item in BLOCKED:
        if item.replace(" ", "") in x:
            return True
    return False

def execute(cmd):
    if not cmd.strip():
        return {"ok": True, "code": 0, "stdout": "", "stderr": ""}

    if blocked(cmd):
        return {
            "ok": False,
            "code": 126,
            "stdout": "",
            "stderr": "GUVENLIK: Bu komut engellendi."
        }

    started = time.time()

    try:
        p = subprocess.run(
            ["bash", "-lc", cmd],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "ok": p.returncode == 0,
            "code": p.returncode,
            "stdout": p.stdout[-12000:],
            "stderr": p.stderr[-12000:],
            "cwd": str(ROOT),
            "duration_ms": round((time.time() - started) * 1000)
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "code": 124,
            "stdout": "",
            "stderr": "Komut 30 saniye zaman asimi nedeniyle durduruldu.",
            "cwd": str(ROOT)
        }

    except Exception as e:
        return {
            "ok": False,
            "code": 1,
            "stdout": "",
            "stderr": str(e),
            "cwd": str(ROOT)
        }

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):

        if self.path == "/api/status":
            self.send_json({
                "ok": True,
                "service": "Yapay Dünya App Terminal",
                "version": "2.0.0",
                "engine": "linux-terminal",
                "port": PORT,
                "project": str(ROOT),
                "user": os.getenv("USER", "unknown"),
                "pid": os.getpid()
            })
            return

        if self.path == "/api/system":
            result = execute(
                "printf 'HOST='; hostname; "
                "printf '\\nOS='; uname -srm; "
                "printf '\\nPYTHON='; python3 --version; "
                "printf '\\nUSER='; whoami; "
                "printf '\\nPWD='; pwd; "
                "printf '\\nGIT='; git branch --show-current 2>/dev/null || true"
            )
            self.send_json(result)
            return

        if self.path in ["/", "/index.html", "/terminal"]:
            html = Path(__file__).with_name("app-terminal.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        self.send_json({"ok": False, "error": "Not Found"}, 404)

    def do_POST(self):

        if self.path != "/api/command":
            self.send_json({"ok": False, "error": "Not Found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))
            command = str(data.get("command", "")).strip()

            result = execute(command)
            self.send_json(result)

        except Exception as e:
            self.send_json({
                "ok": False,
                "code": 1,
                "stdout": "",
                "stderr": str(e)
            }, 400)

    def log_message(self, fmt, *args):
        return

if __name__ == "__main__":
    print(f"YAPAY DUNYA APP TERMINAL : http://127.0.0.1:{PORT}")
    print(f"PROJECT                  : {ROOT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
