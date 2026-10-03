#!/usr/bin/env python3

import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = "/workspaces/yapay-dunya"
PORT = 8791

BLOCKED = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "shutdown",
    "reboot",
    "poweroff",
    ":(){ :|:& };:",
    "dd if=/dev/zero",
    "dd if=/dev/random"
]

def blocked(cmd):
    low = cmd.lower().replace(" ", "")
    return any(x.replace(" ", "") in low for x in BLOCKED)

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(raw)

    def send_file(self, path):
        if not os.path.exists(path):
            self.send_error(404)
            return

        with open(path, "rb") as f:
            data = f.read()

        self.send_response(200)

        if path.endswith(".html"):
            ct = "text/html; charset=utf-8"
        elif path.endswith(".js"):
            ct = "application/javascript"
        elif path.endswith(".css"):
            ct = "text/css"
        else:
            ct = "application/octet-stream"

        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/api/status":
            self.send_json({
                "ok": True,
                "service": "Yapay Dünya App Terminal",
                "version": "1.0.0",
                "linux": True,
                "project": ROOT,
                "port": PORT,
                "user": os.getenv("USER", "codespace")
            })
            return

        if path == "/api/system":
            try:
                uname = subprocess.check_output(
                    ["uname", "-a"], text=True
                ).strip()
            except Exception:
                uname = "unknown"

            self.send_json({
                "ok": True,
                "cwd": ROOT,
                "user": os.getenv("USER", "codespace"),
                "uid": os.getuid(),
                "python": subprocess.check_output(
                    ["python3", "--version"], text=True
                ).strip(),
                "uname": uname,
                "time": time.time()
            })
            return

        if path == "/" or path == "/index.html":
            self.send_file(os.path.join(ROOT, "linux", "app-terminal.html"))
            return

        if path == "/app.js":
            self.send_file(os.path.join(ROOT, "linux", "app-terminal.js"))
            return

        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path != "/api/terminal":
            self.send_json({"ok": False, "error": "Not found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            data = json.loads(body.decode("utf-8"))
            command = str(data.get("command", "")).strip()
        except Exception:
            self.send_json({"ok": False, "error": "Invalid JSON"}, 400)
            return

        if not command:
            self.send_json({"ok": False, "error": "Komut boş"}, 400)
            return

        if blocked(command):
            self.send_json({
                "ok": False,
                "error": "Bu komut güvenlik nedeniyle engellendi."
            }, 403)
            return

        try:
            result = subprocess.run(
                ["bash", "-lc", command],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=30
            )

            self.send_json({
                "ok": result.returncode == 0,
                "code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "cwd": ROOT
            })

        except subprocess.TimeoutExpired:
            self.send_json({
                "ok": False,
                "error": "Komut 30 saniye zaman aşımına uğradı."
            }, 408)

        except Exception as e:
            self.send_json({
                "ok": False,
                "error": str(e)
            }, 500)

    def log_message(self, fmt, *args):
        print("[APP-TERMINAL]", fmt % args)

print("=" * 60)
print("YAPAY DÜNYA APP TERMINAL")
print("PROJECT:", ROOT)
print("PORT:", PORT)
print("=" * 60)

server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
server.serve_forever()
