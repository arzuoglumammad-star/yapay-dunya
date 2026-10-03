#!/usr/bin/env python3

import json
import os
import signal
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = "/workspaces/yapay-dunya"
HOST = "0.0.0.0"
PORT = 8791

BLOCKED_PATTERNS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    "fork bomb",
    ":(){",
    "dd if=/dev/zero",
    "dd if=/dev/random",
]

MAX_COMMAND_LENGTH = 4000
TIMEOUT = 30


def is_blocked(command):
    normalized = command.lower().replace(" ", "")
    for pattern in BLOCKED_PATTERNS:
        if pattern.replace(" ", "").lower() in normalized:
            return True
    return False


def run_command(command):
    result = subprocess.run(
        ["bash", "-lc", command],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        env=os.environ.copy()
    )

    return {
        "ok": result.returncode == 0,
        "code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "cwd": ROOT
    }


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print("[APP-TERMINAL]", fmt % args)

    def send_json(self, data, code=200):
        raw = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS"
        )
        self.send_header(
            "Cache-Control",
            "no-store"
        )
        self.end_headers()

        self.wfile.write(raw)

    def send_file(self, path):
        if not os.path.isfile(path):
            self.send_error(404)
            return

        with open(path, "rb") as f:
            data = f.read()

        if path.endswith(".html"):
            content_type = "text/html; charset=utf-8"
        elif path.endswith(".js"):
            content_type = "application/javascript; charset=utf-8"
        elif path.endswith(".css"):
            content_type = "text/css; charset=utf-8"
        else:
            content_type = "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def do_GET(self):

        path = urlparse(self.path).path

        if path == "/api/status":
            self.send_json({
                "ok": True,
                "service": "Yapay Dünya App Terminal",
                "version": "2.0.0",
                "engine": "remote-linux",
                "linux": True,
                "project": ROOT,
                "port": PORT,
                "user": os.getenv("USER", "codespace"),
                "uid": os.getuid(),
                "pid": os.getpid(),
                "timestamp": time.time()
            })
            return

        if path == "/api/system":

            try:
                python_version = subprocess.check_output(
                    ["python3", "--version"],
                    text=True
                ).strip()
            except Exception:
                python_version = "unknown"

            try:
                uname = subprocess.check_output(
                    ["uname", "-a"],
                    text=True
                ).strip()
            except Exception:
                uname = "unknown"

            try:
                git_branch = subprocess.check_output(
                    ["git", "branch", "--show-current"],
                    cwd=ROOT,
                    text=True
                ).strip()
            except Exception:
                git_branch = "unknown"

            self.send_json({
                "ok": True,
                "cwd": ROOT,
                "user": os.getenv("USER", "codespace"),
                "uid": os.getuid(),
                "python": python_version,
                "uname": uname,
                "git_branch": git_branch,
                "timestamp": time.time()
            })
            return

        if path == "/api/health":
            self.send_json({
                "ok": True,
                "terminal": "online",
                "linux": "online",
                "project": os.path.isdir(ROOT),
                "timestamp": time.time()
            })
            return

        if path == "/" or path == "/index.html":
            self.send_file(
                os.path.join(ROOT, "linux", "app-terminal.html")
            )
            return

        if path == "/app.js":
            self.send_file(
                os.path.join(ROOT, "linux", "app-terminal.js")
            )
            return

        self.send_error(404)

    def do_POST(self):

        path = urlparse(self.path).path

        if path != "/api/terminal":
            self.send_json(
                {"ok": False, "error": "Endpoint bulunamadı"},
                404
            )
            return

        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

            body = self.rfile.read(length)

            payload = json.loads(
                body.decode("utf-8")
            )

            command = str(
                payload.get("command", "")
            ).strip()

        except Exception:
            self.send_json(
                {"ok": False, "error": "Geçersiz JSON"},
                400
            )
            return

        if not command:
            self.send_json(
                {"ok": False, "error": "Komut boş"},
                400
            )
            return

        if len(command) > MAX_COMMAND_LENGTH:
            self.send_json(
                {
                    "ok": False,
                    "error": "Komut çok uzun."
                },
                413
            )
            return

        if is_blocked(command):
            self.send_json(
                {
                    "ok": False,
                    "error": "Bu komut güvenlik politikası tarafından engellendi."
                },
                403
            )
            return

        try:
            self.send_json(run_command(command))

        except subprocess.TimeoutExpired:
            self.send_json(
                {
                    "ok": False,
                    "error": "Komut 30 saniyelik zaman aşımını geçti."
                },
                408
            )

        except Exception as exc:
            self.send_json(
                {
                    "ok": False,
                    "error": str(exc)
                },
                500
            )


def stop_server(signum, frame):
    raise SystemExit(0)


signal.signal(signal.SIGTERM, stop_server)
signal.signal(signal.SIGINT, stop_server)

print("=" * 60)
print("YAPAY DÜNYA APP TERMINAL v2")
print("PROJECT:", ROOT)
print("HOST:", HOST)
print("PORT:", PORT)
print("=" * 60)

server = ThreadingHTTPServer(
    (HOST, PORT),
    Handler
)

server.serve_forever()
