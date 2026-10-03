#!/usr/bin/env python3

from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import subprocess
import json
import os
import platform
import time

ROOT = Path("/workspaces/yapay-dunya")
APP = ROOT / "linux" / "app"
PORT = 8792

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

class Handler(SimpleHTTPRequestHandler):

    def _json(self, data, code=200):

        raw = json.dumps(
            data,
            ensure_ascii=False
        ).encode()

        self.send_response(code)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.end_headers()

        self.wfile.write(raw)

    def do_GET(self):

        if self.path == "/":
            self.path = "/terminal.html"

        if self.path == "/api/status":

            self._json({
                "ok": True,
                "service": "Yapay Dünya Integrated Linux Terminal",
                "version": "1.0.0",
                "engine": "remote-linux",
                "port": PORT
            })

            return

        if self.path == "/api/system":

            self._json({
                "ok": True,
                "system": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python": platform.python_version(),
                "user": os.environ.get(
                    "USER",
                    "codespace"
                ),
                "cwd": str(ROOT),
                "time": time.time()
            })

            return

        return super().do_GET()

    def do_POST(self):

        if self.path != "/api/terminal":

            self._json({
                "ok": False,
                "error": "Not Found"
            },404)

            return

        try:

            length=int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            body=self.rfile.read(length)

            data=json.loads(
                body.decode("utf-8")
            )

            command=str(
                data.get(
                    "command",
                    ""
                )
            ).strip()

        except Exception as e:

            self._json({
                "ok":False,
                "error":str(e)
            },400)

            return

        if not command:

            self._json({
                "ok":False,
                "error":"Komut boş."
            },400)

            return

        lower=command.lower()

        for blocked in BLOCKED:

            if blocked in lower:

                self._json({
                    "ok":False,
                    "error":
                    "Bu tehlikeli komut güvenlik nedeniyle engellendi."
                },403)

                return

        try:

            result=subprocess.run(
                command,
                shell=True,
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
                env=os.environ.copy()
            )

            self._json({
                "ok": result.returncode == 0,
                "code": result.returncode,
                "output": result.stdout,
                "error": result.stderr
            })

        except subprocess.TimeoutExpired:

            self._json({
                "ok":False,
                "error":
                "Komut 30 saniyelik süreyi aştı."
            },408)

        except Exception as e:

            self._json({
                "ok":False,
                "error":str(e)
            },500)

    def log_message(self,format,*args):
        return

if __name__ == "__main__":

    os.chdir(APP)

    server=ThreadingHTTPServer(
        ("0.0.0.0",PORT),
        Handler
    )

    print(
        f"Yapay Dünya Terminal :{PORT}"
    )

    server.serve_forever()
