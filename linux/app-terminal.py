#!/usr/bin/env python3

import os
import re
import json
import time
import uuid
import socket
import platform
import subprocess
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path("/workspaces/yapay-dunya").resolve()
HOST = "0.0.0.0"
PORT = 8791
TOKEN_FILE = ROOT / "runtime" / "terminal-token.txt"

ROOT.joinpath("runtime").mkdir(exist_ok=True)

if TOKEN_FILE.exists():
    TOKEN = TOKEN_FILE.read_text().strip()
else:
    TOKEN = uuid.uuid4().hex + uuid.uuid4().hex
    TOKEN_FILE.write_text(TOKEN)

BLOCKED = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "shutdown",
    "reboot",
    "poweroff",
    "halt",
    ":(){ :|:& };:",
    "fork bomb",
    "dd if=/dev/zero",
    "dd if=/dev/random",
    "chmod -R 777 /",
    "chown -R",
]

def safe_command(command):
    c = command.strip().lower()
    for item in BLOCKED:
        if item in c:
            return False, "Güvenlik: Bu komut engellendi."
    if len(command) > 4000:
        return False, "Komut çok uzun."
    return True, ""

def run_command(command, cwd):
    ok, msg = safe_command(command)
    if not ok:
        return {
            "ok": False,
            "code": 126,
            "stdout": "",
            "stderr": msg,
            "cwd": str(cwd)
        }

    if not cwd.exists():
        cwd = ROOT

    try:
        p = subprocess.run(
            ["/bin/bash", "-lc", command],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=60,
            env=os.environ.copy()
        )

        return {
            "ok": p.returncode == 0,
            "code": p.returncode,
            "stdout": p.stdout[-20000:],
            "stderr": p.stderr[-12000:],
            "cwd": str(cwd)
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "code": 124,
            "stdout": "",
            "stderr": "Komut 60 saniyelik zaman sınırını aştı.",
            "cwd": str(cwd)
        }

    except Exception as e:
        return {
            "ok": False,
            "code": 1,
            "stdout": "",
            "stderr": str(e),
            "cwd": str(cwd)
        }

def system_info():
    try:
        disk = os.statvfs("/")
        total = disk.f_blocks * disk.f_frsize
        free = disk.f_bavail * disk.f_frsize
    except:
        total = 0
        free = 0

    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "user": os.getenv("USER", "codespace"),
        "uid": os.getuid(),
        "project": str(ROOT),
        "cpu": os.cpu_count(),
        "disk_total": total,
        "disk_free": free,
        "time": time.time()
    }

HTML = r"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport"
 content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>Yapay Dünya — Linux Terminal</title>

<style>
*{box-sizing:border-box}
html,body{
 margin:0;
 width:100%;
 height:100%;
 background:#070b10;
 color:#d8ffe0;
 font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;
 overflow:hidden
}
body{display:flex;flex-direction:column}

.header{
 height:58px;
 flex:none;
 display:flex;
 align-items:center;
 justify-content:space-between;
 padding:0 14px;
 border-bottom:1px solid #26332b;
 background:#0c1218
}

.brand{
 font-weight:800;
 color:#6dff91;
 letter-spacing:.5px
}

.status{
 font-size:12px;
 color:#73ff9b
}

.toolbar{
 height:48px;
 flex:none;
 display:flex;
 gap:7px;
 align-items:center;
 padding:7px;
 overflow-x:auto;
 background:#0b1015;
 border-bottom:1px solid #202a24
}

button{
 border:1px solid #304238;
 background:#111a15;
 color:#bfffc9;
 border-radius:8px;
 padding:8px 11px;
 font-family:inherit;
 white-space:nowrap
}

button:active{transform:scale(.97)}

#terminal{
 flex:1;
 overflow:auto;
 padding:13px;
 white-space:pre-wrap;
 word-break:break-word;
 line-height:1.45;
 font-size:13px
}

.line{margin-bottom:6px}
.cmd{color:#74ff96}
.out{color:#d2f5d8}
.err{color:#ff7e7e}

.inputbar{
 flex:none;
 min-height:58px;
 display:flex;
 align-items:center;
 gap:7px;
 padding:8px;
 border-top:1px solid #26332b;
 background:#0c1218
}

.prompt{
 color:#6dff91;
 font-weight:bold;
 font-size:13px
}

input{
 flex:1;
 min-width:0;
 background:#05090c;
 color:#e9fff0;
 border:1px solid #314138;
 border-radius:8px;
 padding:11px;
 outline:none;
 font-family:inherit;
 font-size:14px
}

input:focus{border-color:#69ff8d}

.send{
 background:#14351d;
 border-color:#3d8d51;
 color:#9affad
}

.info{
 padding:7px 12px;
 font-size:11px;
 color:#789080;
 background:#080d11;
 border-top:1px solid #18221c
}
</style>
</head>

<body>

<div class="header">
 <div class="brand">YAPAY DÜNYA // LINUX</div>
 <div id="status" class="status">BAĞLANIYOR...</div>
</div>

<div class="toolbar">
 <button onclick="cmd('pwd')">PWD</button>
 <button onclick="cmd('ls -la')">LS</button>
 <button onclick="cmd('git status --short --branch')">GIT</button>
 <button onclick="cmd('python3 --version')">PYTHON</button>
 <button onclick="cmd('node --version')">NODE</button>
 <button onclick="cmd('uname -a')">LINUX</button>
 <button onclick="clearTerm()">TEMİZLE</button>
</div>

<div id="terminal"></div>

<div class="inputbar">
 <span id="prompt" class="prompt">codespace$</span>
 <input id="input"
        autocomplete="off"
        autocapitalize="off"
        spellcheck="false"
        placeholder="Komut yaz..."
        onkeydown="key(event)">
 <button class="send" onclick="send()">ÇALIŞTIR</button>
</div>

<div class="info">
 YAPAY DÜNYA • Remote Linux • Codespace • Terminal API : 8791
</div>

<script>
const terminal = document.getElementById("terminal");
const input = document.getElementById("input");
const promptEl = document.getElementById("prompt");
const statusEl = document.getElementById("status");

let history = [];
let historyIndex = -1;
let cwd = "/workspaces/yapay-dunya";

function print(text, cls="out"){
 const div=document.createElement("div");
 div.className="line "+cls;
 div.textContent=text;
 terminal.appendChild(div);
 terminal.scrollTop=terminal.scrollHeight;
}

function clearTerm(){
 terminal.innerHTML="";
 print("Yapay Dünya Linux Terminal temizlendi.");
}

function key(e){
 if(e.key==="Enter"){
   send();
   return;
 }

 if(e.key==="ArrowUp"){
   if(!history.length)return;
   historyIndex=Math.max(0,historyIndex-1);
   input.value=history[historyIndex] || "";
   e.preventDefault();
 }

 if(e.key==="ArrowDown"){
   if(!history.length)return;
   historyIndex=Math.min(history.length,historyIndex+1);
   input.value=history[historyIndex] || "";
   e.preventDefault();
 }
}

async function api(path, options={}){
 const r=await fetch(path,{
   ...options,
   headers:{
     "Content-Type":"application/json",
     ...(options.headers||{})
   }
 });
 return await r.json();
}

async function send(){
 const command=input.value.trim();
 if(!command)return;

 history.push(command);
 historyIndex=history.length;

 print(promptEl.textContent+" "+command,"cmd");
 input.value="";

 try{
   const data=await api("/api/terminal/exec",{
     method:"POST",
     body:JSON.stringify({
       command,
       cwd
     })
   });

   if(data.stdout)print(data.stdout,"out");
   if(data.stderr)print(data.stderr,"err");

   if(data.cwd){
     cwd=data.cwd;
     updatePrompt();
   }

   if(data.code!==0){
     print("[exit "+data.code+"]","err");
   }

 }catch(e){
   print("Terminal API bağlantı hatası: "+e,"err");
 }

 input.focus();
}

function cmd(command){
 input.value=command;
 send();
}

function updatePrompt(){
 const short=cwd.replace("/workspaces/yapay-dunya","~");
 promptEl.textContent="codespace:"+short+"$";
}

async function boot(){
 try{
   const s=await api("/api/terminal/system");
   statusEl.textContent="● ONLINE";
   statusEl.style.color="#73ff9b";

   print("YAPAY DÜNYA LINUX TERMINAL","cmd");
   print("--------------------------------");
   print("OS       : "+s.os);
   print("MACHINE  : "+s.machine);
   print("PYTHON   : "+s.python);
   print("USER     : "+s.user);
   print("PROJECT  : "+s.project);
   print("CPU      : "+s.cpu);
   print("--------------------------------");
   print("Gerçek Codespace Linux terminali hazır.");
   updatePrompt();

 }catch(e){
   statusEl.textContent="● OFFLINE";
   statusEl.style.color="#ff7777";
   print("Terminal API kullanılamıyor.","err");
 }
 input.focus();
}

boot();
</script>

</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode()

        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(raw)

    def send_html(self, html):
        raw = html.encode()

        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):

        if self.path in ["/","/terminal","/terminal/"]:
            self.send_html(HTML)
            return

        if self.path == "/api/terminal/system":
            self.send_json(system_info())
            return

        if self.path == "/api/terminal/status":
            self.send_json({
                "ok":True,
                "service":"Yapay Dünya App Terminal",
                "engine":"codespace-linux",
                "port":PORT,
                "project":str(ROOT),
                "time":time.time()
            })
            return

        self.send_json({"ok":False,"error":"Not Found"},404)

    def do_POST():

        if self.path != "/api/terminal/exec":
            self.send_json({"ok":False,"error":"Not Found"},404)
            return

        try:
            length=int(self.headers.get("Content-Length","0"))
            body=self.rfile.read(length)
            data=json.loads(body.decode())

            command=str(data.get("command","")).strip()
            cwd_raw=str(data.get("cwd",str(ROOT)))

            cwd=Path(cwd_raw).resolve()

            try:
                cwd.relative_to(ROOT)
            except ValueError:
                cwd=ROOT

            result=run_command(command,cwd)

            self.send_json(result)

        except Exception as e:
            self.send_json({
                "ok":False,
                "code":1,
                "stdout":"",
                "stderr":str(e),
                "cwd":str(ROOT)
            },500)

    def log_message(self, fmt, *args):
        print("[APP-TERMINAL]",fmt % args)

def main():

    print("="*60)
    print("YAPAY DÜNYA APP TERMINAL")
    print("="*60)
    print("PROJECT :",ROOT)
    print("PORT    :",PORT)
    print("PYTHON  :",platform.python_version())
    print("USER    :",os.getenv("USER","codespace"))
    print("="*60)

    server=ThreadingHTTPServer((HOST,PORT),Handler)

    print("STATUS  : ONLINE")
    print("URL     : /terminal")
    print("API     : /api/terminal/exec")
    print("="*60)

    server.serve_forever()

if __name__=="__main__":
    main()
