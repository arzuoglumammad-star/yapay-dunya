#!/usr/bin/env python3

import os
import json
import shutil
import subprocess
import platform
import socket
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8787

PROJECT = Path.home() / "yapay-dunya"
LINUX_DIR = PROJECT / "linux"
INDEX = LINUX_DIR / "index.html"


def json_response(handler, data, code=200):

    body = json.dumps(
        data,
        ensure_ascii=False
    ).encode("utf-8")

    handler.send_response(code)
    handler.send_header(
        "Content-Type",
        "application/json; charset=utf-8"
    )
    handler.send_header(
        "Access-Control-Allow-Origin",
        "*"
    )
    handler.send_header(
        "Content-Length",
        str(len(body))
    )
    handler.end_headers()

    handler.wfile.write(body)


def html_response(handler):

    try:

        body = INDEX.read_bytes()

        handler.send_response(200)

        handler.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        handler.send_header(
            "Content-Length",
            str(len(body))
        )

        handler.end_headers()

        handler.wfile.write(body)

    except Exception as e:

        json_response(
            handler,
            {
                "hata": str(e)
            },
            500
        )


def system_info():

    total, used, free = shutil.disk_usage(PROJECT)

    return {

        "service":
            "YAPAY DUNYA LINUX CENTER",

        "version":
            "1.0.0",

        "hostname":
            socket.gethostname(),

        "platform":
            platform.platform(),

        "system":
            platform.system(),

        "machine":
            platform.machine(),

        "python":
            platform.python_version(),

        "user":
            os.environ.get(
                "USER",
                "unknown"
            ),

        "project":
            str(PROJECT),

        "disk_total":
            total,

        "disk_used":
            used,

        "disk_free":
            free
    }


def run_command(command):

    command = command.strip()

    if not command:

        return {
            "ok": False,
            "error": "Komut boş."
        }

    blocked = [

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

    for item in blocked:

        if item in command:

            return {

                "ok": False,

                "error":
                    "Bu komut V1 güvenlik filtresinde engellendi."

            }

    try:

        process = subprocess.run(

            command,

            shell=True,

            cwd=str(PROJECT),

            capture_output=True,

            text=True,

            timeout=30

        )

        return {

            "ok": True,

            "exit":
                process.returncode,

            "stdout":
                process.stdout,

            "stderr":
                process.stderr

        }

    except subprocess.TimeoutExpired:

        return {

            "ok": False,

            "error":
                "Komut 30 saniyelik zaman aşımına uğradı."

        }

    except Exception as e:

        return {

            "ok": False,

            "error":
                str(e)

        }


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path in ["/", "/index.html"]:

            html_response(self)

            return

        if self.path == "/api/status":

            json_response(

                self,

                {

                    "service":
                        "YAPAY DUNYA LINUX CENTER",

                    "version":
                        "1.0.0",

                    "status":
                        "online"

                }

            )

            return

        if self.path == "/api/system":

            json_response(
                self,
                system_info()
            )

            return

        json_response(

            self,

            {

                "error":
                    "Endpoint bulunamadı.",

                "service":
                    "YAPAY DUNYA LINUX CENTER"

            },

            404

        )

    def do_POST(self):

        if self.path != "/api/terminal":

            json_response(

                self,

                {
                    "error":
                        "Endpoint bulunamadı."
                },

                404

            )

            return

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            raw = self.rfile.read(length)

            data = json.loads(
                raw.decode("utf-8")
            )

            command = data.get(
                "command",
                ""
            )

            result = run_command(command)

            json_response(
                self,
                result
            )

        except Exception as e:

            json_response(

                self,

                {
                    "ok": False,
                    "error": str(e)
                },

                400

            )

    def log_message(
        self,
        format,
        *args
    ):

        return


print("")
print("==========================================")
print(" YAPAY DUNYA LINUX CENTER v1")
print("==========================================")
print("PROJECT:", PROJECT)
print("URL: http://127.0.0.1:" + str(PORT))
print("==========================================")
print("")

server = HTTPServer(
    (HOST, PORT),
    Handler
)

server.serve_forever()
