#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="$HOME/yapay-dunya"
LINUX="$PROJECT/linux"

echo "=========================================="
echo " YAPAY DUNYA — LINUX CENTER V1 FIX"
echo "=========================================="

mkdir -p "$LINUX"

# --------------------------------------------------
# 1 — SERVER.PY
# --------------------------------------------------

cat > "$LINUX/server.py" <<'PY'
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
PY

chmod +x "$LINUX/server.py"


# --------------------------------------------------
# 2 — LINUX CENTER HTML
# --------------------------------------------------

cat > "$LINUX/index.html" <<'HTML'
<!DOCTYPE html>

<html lang="tr">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width,
initial-scale=1,
maximum-scale=1,
viewport-fit=cover">

<title>Yapay Dünya — Linux Center</title>

<style>

*{
box-sizing:border-box;
}

html,
body{

margin:0;

padding:0;

background:#05080d;

color:#e9eef5;

font-family:
system-ui,
-apple-system,
BlinkMacSystemFont,
"Segoe UI",
sans-serif;

}

body{

padding:
env(safe-area-inset-top)
16px
env(safe-area-inset-bottom);

}

.app{

width:100%;

max-width:760px;

margin:auto;

}

.header{

height:64px;

display:flex;

align-items:center;

justify-content:space-between;

}

.logo{

font-size:20px;

font-weight:800;

}

.status{

font-size:11px;

font-weight:800;

padding:7px 10px;

border-radius:999px;

background:#10251a;

color:#67e8a5;

}

.card{

background:#0d131b;

border:
1px solid #202a36;

border-radius:18px;

padding:16px;

margin-bottom:14px;

}

.title{

font-size:12px;

font-weight:800;

letter-spacing:.08em;

text-transform:uppercase;

color:#8491a0;

margin-bottom:12px;

}

.stats{

display:grid;

grid-template-columns:
1fr 1fr;

gap:10px;

}

.stat{

background:#080c12;

border-radius:12px;

padding:12px;

min-height:70px;

}

.stat span{

display:block;

font-size:11px;

color:#788493;

}

.stat b{

display:block;

margin-top:5px;

font-size:15px;

overflow:hidden;

text-overflow:ellipsis;

white-space:nowrap;

}

.terminal{

background:#020406;

border:
1px solid #1d2731;

border-radius:14px;

overflow:hidden;

}

.termbar{

padding:10px 12px;

border-bottom:
1px solid #1d2731;

font:

11px
ui-monospace,
SFMono-Regular,
Menlo,
monospace;

color:#7f8b99;

}

.output{

height:330px;

overflow:auto;

padding:13px;

white-space:pre-wrap;

word-break:break-word;

font:

13px/1.55
ui-monospace,
SFMono-Regular,
Menlo,
monospace;

color:#d7dee8;

}

.command{

display:flex;

align-items:center;

border-top:
1px solid #1d2731;

}

.prompt{

padding-left:12px;

color:#67e8a5;

font-family:monospace;

}

input{

flex:1;

min-width:0;

padding:13px 10px;

border:0;

outline:0;

background:transparent;

color:#fff;

font:

14px
ui-monospace,
SFMono-Regular,
Menlo,
monospace;

}

button{

width:100%;

margin-top:10px;

padding:13px;

border:0;

border-radius:12px;

background:#18222e;

color:#fff;

font-weight:800;

}

button:active{

transform:scale(.98);

}

.quick{

display:grid;

grid-template-columns:
1fr 1fr;

gap:8px;

margin-top:10px;

}

.quick button{

margin:0;

font-size:12px;

}

.footer{

text-align:center;

font-size:10px;

color:#5e6977;

padding:8px;

}

</style>

</head>

<body>

<div class="app">

<header class="header">

<div class="logo">
YAPAY DÜNYA
</div>

<div
id="status"
class="status">

LINUX ONLINE

</div>

</header>


<section class="card">

<div class="title">
Linux System
</div>

<div class="stats">

<div class="stat">

<span>HOST</span>

<b id="host">—</b>

</div>

<div class="stat">

<span>USER</span>

<b id="user">—</b>

</div>

<div class="stat">

<span>PYTHON</span>

<b id="python">—</b>

</div>

<div class="stat">

<span>SYSTEM</span>

<b id="system">—</b>

</div>

<div class="stat">

<span>MACHINE</span>

<b id="machine">—</b>

</div>

<div class="stat">

<span>DISK FREE</span>

<b id="disk">—</b>

</div>

</div>

</section>


<section class="card">

<div class="title">
Real Linux Terminal
</div>

<div class="terminal">

<div class="termbar">

YAPAY-DUNYA / LINUX CENTER v1

</div>

<div
id="output"
class="output">

Yapay Dünya Linux Center başlatıldı.

Gerçek Termux ortamına bağlı.

Proje:
~/yapay-dunya

Hazır.

</div>

<div class="command">

<div class="prompt">
$
</div>

<input
id="command"
placeholder="komut yaz..."
autocomplete="off"
autocapitalize="off"
spellcheck="false">

</div>

</div>


<button onclick="runCommand()">
ÇALIŞTIR
</button>


<div class="quick">

<button onclick="quick('pwd')">
PWD
</button>

<button onclick="quick('ls')">
LS
</button>

<button onclick="quick('git status')">
GIT STATUS
</button>

<button onclick="quick('python3 --version')">
PYTHON
</button>

</div>

</section>


<div class="footer">

YAPAY DÜNYA LINUX CENTER v1.0.0

</div>

</div>


<script>

const API =
"http://127.0.0.1:8787";

const input =
document.getElementById("command");

const output =
document.getElementById("output");


function print(text){

output.textContent +=
"\n\n" + text;

output.scrollTop =
output.scrollHeight;

}


async function runCommand(){

const command =
input.value.trim();

if(!command)
return;

print("$ " + command);

input.value = "";

try{

const response =
await fetch(
API + "/api/terminal",
{

method:"POST",

headers:{
"Content-Type":
"application/json"
},

body:
JSON.stringify({
command:command
})

}
);

const data =
await response.json();

if(data.stdout)
print(data.stdout);

if(data.stderr)
print(data.stderr);

if(data.error)
print(
"ERROR: " +
data.error
);

}
catch(error){

print(
"Linux bağlantısı kurulamadı."
);

print(
error.message
);

}

}


function quick(command){

input.value =
command;

runCommand();

}


async function loadSystem(){

try{

const response =
await fetch(
API + "/api/system"
);

const data =
await response.json();

document.getElementById(
"host"
).textContent =
data.hostname || "—";

document.getElementById(
"user"
).textContent =
data.user || "—";

document.getElementById(
"python"
).textContent =
data.python || "—";

document.getElementById(
"system"
).textContent =
data.system || "—";

document.getElementById(
"machine"
).textContent =
data.machine || "—";

const free =
(
data.disk_free /
1024 /
1024 /
1024
).toFixed(1);

document.getElementById(
"disk"
).textContent =
free + " GB";

}
catch(error){

document.getElementById(
"status"
).textContent =
"LINUX OFFLINE";

}

}


input.addEventListener(
"keydown",
function(event){

if(event.key === "Enter")
runCommand();

}
);


loadSystem();

</script>

</body>

</html>
HTML


# --------------------------------------------------
# 3 — START SCRIPT
# --------------------------------------------------

cat > "$LINUX/start.sh" <<'SH'
#!/data/data/com.termux/files/usr/bin/bash

cd "$HOME/yapay-dunya/linux"

echo ""
echo "=========================================="
echo " YAPAY DUNYA LINUX CENTER v1"
echo "=========================================="
echo "URL:"
echo "http://127.0.0.1:8787"
echo "=========================================="
echo ""

python3 server.py
SH

chmod +x "$LINUX/start.sh"


# --------------------------------------------------
# 4 — TEST
# --------------------------------------------------

echo ""
echo "[TEST] Python..."
python3 --version

echo ""
echo "[TEST] Server syntax..."
python3 -m py_compile "$LINUX/server.py"

echo ""
echo "[TEST] HTML..."
test -f "$LINUX/index.html"

echo ""
echo "[TEST] Start script..."
test -x "$LINUX/start.sh"

echo ""
echo "[TEST] API..."
echo "Dosyalar hazır."


# --------------------------------------------------
# 5 — GITIGNORE
# --------------------------------------------------

touch "$PROJECT/.gitignore"

grep -qxF "linux/server.log" "$PROJECT/.gitignore" 2>/dev/null || \
echo "linux/server.log" >> "$PROJECT/.gitignore"

grep -qxF "*.log" "$PROJECT/.gitignore" 2>/dev/null || \
echo "*.log" >> "$PROJECT/.gitignore"


# --------------------------------------------------
# 6 — GIT
# --------------------------------------------------

cd "$PROJECT"

git add linux .gitignore index.html 2>/dev/null || true

git commit -m "feat: Linux Center v1" 2>/dev/null || true

git push 2>/dev/null || true


# --------------------------------------------------
# 7 — SONUÇ
# --------------------------------------------------

echo ""
echo "=========================================="
echo " TAMAMLANDI"
echo "=========================================="
echo ""
echo "Linux Center:"
echo "$LINUX"
echo ""
echo "Başlat:"
echo "bash ~/yapay-dunya/linux/start.sh"
echo ""
echo "Arayüz:"
echo "http://127.0.0.1:8787/"
echo ""
echo "Kontrol:"
echo "python3 -m py_compile ~/yapay-dunya/linux/server.py"
echo ""
echo "=========================================="
echo " HAZIR"
echo "=========================================="

