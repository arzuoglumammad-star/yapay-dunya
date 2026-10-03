#!/usr/bin/env python3
import json
import os
import time
import threading
import random
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = "/workspaces/yapay-dunya"
DATA = os.path.join(ROOT, "data")
RUNTIME = os.path.join(ROOT, "runtime")
PORT = 8791
TICK_SECONDS = 2

os.makedirs(DATA, exist_ok=True)
os.makedirs(RUNTIME, exist_ok=True)

STATE_FILE = os.path.join(DATA, "world-autopilot.json")

DEFAULT = {
    "world": {
        "id": "YD-001",
        "name": "Yapay Dünya",
        "day": 1,
        "hour": 0,
        "minute": 0,
        "tick": 0,
        "running": True
    },
    "population": {
        "total": 100,
        "employed": 100,
        "unemployed": 0
    },
    "cities": [
        {
            "id": "CITY-001",
            "name": "Merkez Şehir",
            "population": 100,
            "businesses": 2
        }
    ],
    "resources": {
        "food": 1000.0,
        "water": 2000.0,
        "energy": 1500.0,
        "raw_material": 1000.0
    },
    "economy": {
        "money": 100000.0,
        "food_price": 10.0,
        "wages": 100.0,
        "sales": 0.0,
        "production_value": 0.0
    },
    "businesses": [
        {
            "id": "BUS-001",
            "name": "Gıda Üretim Tesisi",
            "type": "factory",
            "workers": 60,
            "stock": 500.0,
            "capacity": 50.0
        },
        {
            "id": "BUS-002",
            "name": "Merkez Market",
            "type": "market",
            "workers": 40,
            "stock": 500.0,
            "capacity": 100.0
        }
    ],
    "agents": [],
    "orders": [],
    "events": [],
    "metrics": {
        "births": 0,
        "deaths": 0,
        "production": 0.0,
        "consumption": 0.0,
        "sales": 0.0,
        "orders": 0,
        "transactions": 0
    },
    "system": {
        "version": "1.0.0",
        "engine": "simulation-engine",
        "autopilot": True,
        "updatedAt": None
    }
}

def load():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    state = DEFAULT.copy()
    state["agents"] = []

    jobs = [
        ("factory", "Üretim İşçisi"),
        ("market", "Market Çalışanı"),
        ("transport", "Taşıma İşçisi"),
        ("service", "Hizmet Çalışanı")
    ]

    for i in range(100):
        kind, job = jobs[i % len(jobs)]
        state["agents"].append({
            "id": f"P-{i+1:04d}",
            "name": f"Vatandaş {i+1}",
            "age": random.randint(20, 60),
            "job": job,
            "jobType": kind,
            "money": random.uniform(200, 1000),
            "needs": {
                "food": random.uniform(60, 100),
                "water": random.uniform(60, 100),
                "energy": random.uniform(60, 100)
            },
            "alive": True
        })

    save(state)
    return state

def save(state):
    state["system"]["updatedAt"] = datetime.now(timezone.utc).isoformat()
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_FILE)

STATE = load()
LOCK = threading.RLock()

def add_event(text, kind="system"):
    STATE["events"].insert(0, {
        "time": datetime.now(timezone.utc).isoformat(),
        "type": kind,
        "message": text
    })
    STATE["events"] = STATE["events"][:50]

def simulate_minute():
    with LOCK:
        w = STATE["world"]

        w["minute"] += 1
        w["tick"] += 1

        if w["minute"] >= 60:
            w["minute"] = 0
            w["hour"] += 1

        if w["hour"] >= 24:
            w["hour"] = 0
            w["day"] += 1
            add_event(f"Gün {w['day']} başladı", "time")

        # İnsan tüketimi
        population = STATE["population"]["total"]

        food_use = population * 0.035
        water_use = population * 0.06
        energy_use = population * 0.025

        STATE["resources"]["food"] = max(
            0, STATE["resources"]["food"] - food_use
        )
        STATE["resources"]["water"] = max(
            0, STATE["resources"]["water"] - water_use
        )
        STATE["resources"]["energy"] = max(
            0, STATE["resources"]["energy"] - energy_use
        )

        STATE["metrics"]["consumption"] += food_use

        # Üretim
        factory = STATE["businesses"][0]
        production = min(
            factory["capacity"] / 60.0,
            STATE["resources"]["energy"] * 0.01,
            STATE["resources"]["raw_material"] * 0.01
        )

        STATE["resources"]["food"] += production
        STATE["resources"]["energy"] = max(
            0, STATE["resources"]["energy"] - production * 0.4
        )
        STATE["resources"]["raw_material"] = max(
            0, STATE["resources"]["raw_material"] - production * 0.3
        )

        factory["stock"] += production
        STATE["metrics"]["production"] += production
        STATE["economy"]["production_value"] += production * STATE["economy"]["food_price"]

        # Maaş
        wage_per_minute = STATE["economy"]["wages"] / 1440.0
        wage_total = population * wage_per_minute

        STATE["economy"]["money"] = max(
            0, STATE["economy"]["money"] - wage_total
        )

        # Market satışı
        market = STATE["businesses"][1]

        demand = population * 0.02

        sale = min(
            demand,
            market["stock"],
            STATE["resources"]["food"]
        )

        market["stock"] = max(0, market["stock"] - sale)

        revenue = sale * STATE["economy"]["food_price"]

        STATE["economy"]["money"] += revenue
        STATE["economy"]["sales"] += revenue
        STATE["metrics"]["sales"] += revenue
        STATE["metrics"]["transactions"] += int(max(0, sale))

        # Üretim tesisinden markete sevkiyat
        if market["stock"] < 200 and factory["stock"] > 100:
            transfer = min(100, factory["stock"])
            factory["stock"] -= transfer
            market["stock"] += transfer

            order = {
                "id": f"ORD-{STATE['world']['tick']:06d}",
                "type": "restock",
                "from": factory["id"],
                "to": market["id"],
                "quantity": transfer,
                "status": "completed",
                "time": datetime.now(timezone.utc).isoformat()
            }

            STATE["orders"].insert(0, order)
            STATE["orders"] = STATE["orders"][:100]
            STATE["metrics"]["orders"] += 1

            add_event(
                f"Market yeniden stoklandı: {transfer:.1f} gıda",
                "order"
            )

        # Fiyat mekanizması
        stock = market["stock"]

        if stock < 100:
            STATE["economy"]["food_price"] *= 1.003
        elif stock > 400:
            STATE["economy"]["food_price"] *= 0.998

        STATE["economy"]["food_price"] = max(
            1,
            min(100, STATE["economy"]["food_price"])
        )

        # Agent ihtiyaçları
        for person in STATE["agents"]:
            if not person.get("alive"):
                continue

            person["needs"]["food"] -= 0.03
            person["needs"]["water"] -= 0.05
            person["needs"]["energy"] -= 0.02

            if person["needs"]["food"] < 20:
                person["needs"]["food"] = 100
                person["money"] = max(
                    0,
                    person["money"] - STATE["economy"]["food_price"]
                )

        # Otomatik olaylar
        if STATE["resources"]["food"] < 300:
            add_event(
                "Gıda rezervi kritik seviyeye yaklaşıyor",
                "warning"
            )

        if STATE["resources"]["energy"] < 300:
            add_event(
                "Enerji rezervi kritik seviyeye yaklaşıyor",
                "warning"
            )

        save(STATE)

def simulation_loop():
    while True:
        try:
            if STATE["world"]["running"]:
                simulate_minute()
            time.sleep(TICK_SECONDS)
        except Exception as e:
            add_event(f"Motor hatası: {str(e)}", "error")
            time.sleep(TICK_SECONDS)

class Handler(BaseHTTPRequestHandler):

    def _json(self, obj, code=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ("/", "/api", "/api/state", "/api/world"):
            with LOCK:
                self._json(STATE)
            return

        if path == "/api/status":
            self._json({
                "ok": True,
                "service": "Yapay Dünya Autopilot",
                "version": "1.0.0",
                "engine": "simulation-engine",
                "port": PORT,
                "running": STATE["world"]["running"],
                "tick": STATE["world"]["tick"]
            })
            return

        if path == "/api/metrics":
            with LOCK:
                self._json(STATE["metrics"])
            return

        self._json({"ok": False, "error": "Not Found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/control":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"

            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = {}

            action = payload.get("action")

            with LOCK:
                if action == "start":
                    STATE["world"]["running"] = True
                    add_event("Simülasyon başlatıldı", "control")

                elif action == "stop":
                    STATE["world"]["running"] = False
                    add_event("Simülasyon durduruldu", "control")

                elif action == "tick":
                    simulate_minute()

                elif action == "reset":
                    global STATE
                    STATE = load()

                else:
                    self._json({
                        "ok": False,
                        "error": "Geçersiz action"
                    }, 400)
                    return

                save(STATE)
                self._json({
                    "ok": True,
                    "action": action,
                    "world": STATE["world"]
                })
            return

        self._json({"ok": False, "error": "Not Found"}, 404)

    def log_message(self, fmt, *args):
        return

threading.Thread(
    target=simulation_loop,
    daemon=True
).start()

print(f"YAPAY DÜNYA AUTOPILOT ONLINE : {PORT}")

HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
