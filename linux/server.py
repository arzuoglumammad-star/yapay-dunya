#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import subprocess
import json
import os
import platform
import shutil
import time

HOST = "0.0.0.0"
PORT = 8787
PROJECT = Path("/workspaces/yapay-dunya")

BLOCKED = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "shutdown",
    "poweroff",
    "reboot",
    "dd if=/dev/zero",
    "dd if=/dev/random",
    ":(){ :|:& };:"
]

def system_info():
    disk = shutil.disk_usage("/")
    return {
        "ok": True,
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "user": os.getenv("USER", "unknown"),
        "uid": os.getuid(),
        "project": str(PROJECT),
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_free": disk.free,
        "time": time.time()
    }

def run_command(command):
    command = command.strip()

    if not command:
        return {"ok": False, "output": "Komut boş."}

    low = command.lower()

    for item in BLOCKED:
        if item in low:
            return {
                "ok": False,
                "output": "GÜVENLİK: Tehlikeli komut engellendi."
            }

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "ok": result.returncode == 0,
            "code": result.returncode,
            "output": (result.stdout + result.stderr)[-20000:]
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "output": "Komut 30 saniyelik zaman aşımına uğradı."
        }

    except Exception as exc:
        return {
            "ok": False,
            "output": str(exc)
        }

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data):
        raw = json.dumps(
            data,
            ensure_ascii=False
        ).encode()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):

        if self.path == "/api/status":
            self.send_json({
                "ok": True,
                "service": "Yapay Dünya Remote Linux Center",
                "version": "2.0.0"
            })
            return

        if self.path == "/api/system":
            self.send_json(system_info())
            return

        if self.path == "/api/git":
            result = run_command(
                "git status --short --branch"
            )
            self.send_json(result)
            return

        if self.path in ["/", "/index.html"]:

            file = PROJECT / "linux" / "index.html"

            if not file.exists():
                self.send_error(404)
                return

            raw = file.read_bytes()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.send_header(
                "Content-Length",
                str(len(raw))
            )
            self.end_headers()
            self.wfile.write(raw)
            return

        self.send_error(404)

    def do_POST(self):

        if self.path != "/api/terminal":
            self.send_error(404)
            return

        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            body = self.rfile.read(length)
            data = json.loads(body.decode())

            result = run_command(
                data.get("command", "")
            )

            self.send_json(result)

        except Exception as exc:
            self.send_json({
                "ok": False,
                "output": str(exc)
            })

print("")
print("==========================================")
print(" YAPAY DUNYA REMOTE LINUX CENTER v2")
print("==========================================")
print("Project:", PROJECT)
print("Port:", PORT)
print("")

server = HTTPServer(
    (HOST, PORT),
    Handler
)

server.serve_forever()
