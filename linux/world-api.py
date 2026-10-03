#!/usr/bin/env python3

import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = "/workspaces/yapay-dunya"
ENGINE = os.path.join(ROOT, "engine", "simulation-engine.js")
PORT = 8790

def run_engine(*args):
    p = subprocess.run(
        ["node", ENGINE, *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )

    if p.returncode != 0:
        return {
            "ok": False,
            "code": p.returncode,
            "error": p.stderr[-4000:]
        }

    try:
        return {
            "ok": True,
            "data": json.loads(p.stdout)
        }
    except Exception:
        return {
            "ok": False,
            "code": 0,
            "error": "Invalid engine JSON",
            "raw": p.stdout[-4000:]
        }

class Handler(BaseHTTPRequestHandler):

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        if self.path == "/api/world":
            self.send_json(run_engine("status"))
            return

        if self.path == "/api/world/status":
            self.send_json(run_engine("status"))
            return

        self.send_json({
            "ok": True,
            "service": "Yapay Dünya World API",
            "version": "1.0.0",
            "engine": "simulation-engine",
            "port": PORT
        })

    def do_POST(self):
        if self.path not in (
            "/api/world/tick",
            "/api/world/run",
            "/api/world/stop",
            "/api/world/reset"
        ):
            self.send_json({"ok": False, "error": "Not found"}, 404)
            return

        if self.path == "/api/world/tick":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"

            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                payload = {}

            minutes = max(
                1,
                min(100000, int(payload.get("minutes", 1)))
            )

            self.send_json(run_engine("tick", minutes))
            return

        if self.path == "/api/world/run":
            self.send_json(run_engine("run"))
            return

        if self.path == "/api/world/stop":
            self.send_json(run_engine("stop"))
            return

        if self.path == "/api/world/reset":
            self.send_json(run_engine("reset"))
            return

    def log_message(self, fmt, *args):
        print("[WORLD-API]", fmt % args, flush=True)

if __name__ == "__main__":
    print(f"Yapay Dünya World API : http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
