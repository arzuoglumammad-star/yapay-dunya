#!/usr/bin/env python3
import os
import json
import time
import secrets
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8791
ROOT = "/workspaces/yapay-dunya"
TOKEN_FILE = os.path.join(ROOT, "runtime", "terminal.token")

os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)

if os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        MASTER_TOKEN = f.read().strip()
else:
    MASTER_TOKEN = secrets.token_urlsafe(32)
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(MASTER_TOKEN)
    os.chmod(TOKEN_FILE, 0o600)

SESSIONS = {}

HTML = r'''<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#05070b">
<title>Yapay Dünya Terminal</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;width:100%;height:100%;background:#05070b;color:#e8edf5;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
body{display:flex;flex-direction:column}
header{
 height:62px;display:flex;align-items:center;justify-content:space-between;
 padding:0 14px;border-bottom:1px solid #202632;background:#090c12;
 position:sticky;top:0;z-index:5
}
.brand{font-family:system-ui,sans-serif;font-weight:800;font-size:17px}
.status{font-size:12px;color:#62e6a4}
main{flex:1;display:flex;flex-direction:column;min-height:0}
#login{
 padding:22px;display:flex;flex-direction:column;gap:12px;
 max-width:520px;width:100%;margin:auto
}
input,button{
 font:inherit;border-radius:12px;border:1px solid #293140;
 background:#0d121a;color:#e8edf5;padding:13px
}
button{cursor:pointer}
button:active{transform:scale(.98)}
.primary{background:#172235}
#terminal{display:none;flex:1;flex-direction:column;min-height:0}
#output{
 flex:1;overflow:auto;padding:15px;white-space:pre-wrap;word-break:break-word;
 font-size:13px;line-height:1.55;background:#030509
}
.line{color:#9aa7b8}
.ok{color:#72e0a7}
.err{color:#ff8585}
.cmd{color:#7fb4ff}
.bar{
 display:flex;gap:7px;padding:8px;border-top:1px solid #202632;
 background:#090c12;overflow:auto
}
.quick{white-space:nowrap;padding:9px 11px}
.inputbar{
 display:flex;gap:8px;padding:9px;background:#090c12;
 border-top:1px solid #202632;padding-bottom:calc(9px + env(safe-area-inset-bottom))
}
.prompt{color:#62e6a4;padding:13px 0 13px 4px}
#command{flex:1;min-width:0}
.send{min-width:62px}
.small{font-family:system-ui,sans-serif;font-size:12px;color:#7f8a9b}
.hidden{display:none!important}
</style>
</head>
<body>

<header>
 <div class="brand">YAPAY DÜNYA · TERMINAL</div>
 <div class="status" id="status">● BAĞLANIYOR</div>
</header>

<main>

<section id="login">
 <div style="font-family:system-ui;font-size:24px;font-weight:800">Linux Terminal</div>
 <div class="small">
   Yapay Dünya uygulamasından Codespace Linux ortamına bağlan.
 </div>
 <input id="token" type="password" autocomplete="off" placeholder="Terminal erişim anahtarı">
 <button class="primary" onclick="login()">TERMINALE BAĞLAN</button>
 <div id="loginMsg" class="small"></div>
</section>

<section id="terminal">
 <div id="output"></div>

 <div class="bar">
  <button class="quick" onclick="run('pwd')">PWD</button>
  <button class="quick" onclick="run('ls -la')">LS</button>
  <button class="quick" onclick="run('git status --short --branch')">GIT</button>
  <button class="quick" onclick="run('python3 --version')">PYTHON</button>
  <button class="quick" onclick="run('node --version')">NODE</button>
  <button class="quick" onclick="run('uname -a')">SYSTEM</button>
  <button class="quick" onclick="clearOutput()">CLEAR</button>
 </div>

 <div class="inputbar">
  <div class="prompt">$</div>
  <input id="command" autocomplete="off" autocapitalize="off" spellcheck="false"
         placeholder="komut yaz..." enterkeyhint="send">
  <button class="send" onclick="sendCommand()">ÇALIŞTIR</button>
 </div>
</section>

</main>

<script>
let logged=false;

const output=document.getElementById("output");
const command=document.getElementById("command");
const statusEl=document.getElementById("status");

function print(text, cls="line"){
  const d=document.createElement("div");
  d.className=cls;
  d.textContent=text;
  output.appendChild(d);
  output.scrollTop=output.scrollHeight;
}

function clearOutput(){
  output.innerHTML="";
}

async function login(){
  const token=document.getElementById("token").value.trim();
  const msg=document.getElementById("loginMsg");

  if(!token){
    msg.textContent="Anahtarı gir.";
    return;
  }

  msg.textContent="Bağlanıyor...";

  try{
    const r=await fetch("/api/login",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({token})
    });

    const j=await r.json();

    if(!j.ok){
      msg.textContent=j.error || "Erişim reddedildi.";
      return;
    }

    logged=true;
    document.getElementById("login").style.display="none";
    document.getElementById("terminal").style.display="flex";
    statusEl.textContent="● LINUX ONLINE";
    print("YAPAY DÜNYA TERMINAL", "ok");
    print("Linux bağlantısı hazır.");
    print("Çalışma dizini: /workspaces/yapay-dunya");
    print("");
    command.focus();
  }catch(e){
    msg.textContent="Sunucuya bağlanılamadı.";
  }
}

async function run(cmd){
  if(!logged)return;
  command.value="";
  print("$ "+cmd,"cmd");

  try{
    const r=await fetch("/api/exec",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({command:cmd})
    });

    const j=await r.json();

    if(j.stdout) print(j.stdout);
    if(j.stderr) print(j.stderr,"err");
    print("[exit "+j.code+" | "+j.ms+" ms]");
  }catch(e){
    print("Bağlantı hatası: "+e.message,"err");
  }
}

function sendCommand(){
  const cmd=command.value.trim();
  if(cmd) run(cmd);
}

command.addEventListener("keydown",e=>{
  if(e.key==="Enter"){
    e.preventDefault();
    sendCommand();
  }
});

window.addEventListener("load",()=>{
  document.getElementById("token").focus();
});
</script>
</body>
</html>
'''

def json_response(handler, data, code=200):
    raw = json.dumps(data, ensure_ascii=False).encode()
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(raw)

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def cookie_session(self):
        cookie = self.headers.get("Cookie", "")
        for item in cookie.split(";"):
            item=item.strip()
            if item.startswith("YDSESSION="):
                return item.split("=",1)[1]
        return None

    def authenticated(self):
        sid=self.cookie_session()
        return bool(sid and sid in SESSIONS)

    def do_GET(self):
        path=urlparse(self.path).path

        if path in ["/", "/terminal"]:
            raw=HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if path=="/api/status":
            json_response(self,{
                "ok":True,
                "service":"Yapay Dünya App Terminal",
                "linux":"online",
                "port":PORT,
                "project":ROOT,
                "authenticated":self.authenticated()
            })
            return

        json_response(self,{"ok":False,"error":"Not found"},404)

    def do_POST(self):
        path=urlparse(self.path).path

        try:
            length=int(self.headers.get("Content-Length","0"))
            body=self.rfile.read(length)
            data=json.loads(body.decode() or "{}")
        except Exception:
            data={}

        if path=="/api/login":
            token=str(data.get("token",""))

            if not secrets.compare_digest(token,MASTER_TOKEN):
                json_response(self,{"ok":False,"error":"Geçersiz erişim anahtarı."},401)
                return

            sid=secrets.token_urlsafe(32)
            SESSIONS[sid]=time.time()

            self.send_response(200)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header(
                "Set-Cookie",
                "YDSESSION="+sid+"; Path=/; HttpOnly; SameSite=Lax"
            )
            raw=json.dumps({"ok":True}).encode()
            self.send_header("Content-Length",str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return

        if path=="/api/exec":
            if not self.authenticated():
                json_response(self,{"ok":False,"error":"Yetkisiz erişim."},401)
                return

            command=str(data.get("command","")).strip()

            if not command:
                json_response(self,{"ok":False,"error":"Komut boş."},400)
                return

            if len(command)>4000:
                json_response(self,{"ok":False,"error":"Komut çok uzun."},400)
                return

            blocked=[
                "rm -rf /",
                "rm -rf /*",
                "mkfs",
                "shutdown",
                "poweroff",
                "reboot",
                ":(){ :|:& };:",
                "dd if=/dev/zero",
                "dd if=/dev/random"
            ]

            lower=command.lower()

            if any(x in lower for x in blocked):
                json_response(self,{
                    "ok":False,
                    "error":"Güvenlik nedeniyle bu komut engellendi."
                },403)
                return

            started=time.time()

            try:
                p=subprocess.run(
                    command,
                    shell=True,
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                ms=int((time.time()-started)*1000)

                json_response(self,{
                    "ok":p.returncode==0,
                    "code":p.returncode,
                    "stdout":p.stdout[-30000:],
                    "stderr":p.stderr[-30000:],
                    "cwd":ROOT,
                    "ms":ms
                })

            except subprocess.TimeoutExpired as e:
                json_response(self,{
                    "ok":False,
                    "code":124,
                    "stdout":(e.stdout or "")[-30000:] if e.stdout else "",
                    "stderr":"Komut 60 saniyelik zaman aşımına uğradı.",
                    "cwd":ROOT,
                    "ms":60000
                },408)

            except Exception as e:
                json_response(self,{
                    "ok":False,
                    "code":1,
                    "stdout":"",
                    "stderr":str(e),
                    "cwd":ROOT,
                    "ms":int((time.time()-started)*1000)
                },500)

            return

        json_response(self,{"ok":False,"error":"Not found"},404)

print("="*60)
print("YAPAY DÜNYA APP TERMINAL")
print("="*60)
print("PORT :",PORT)
print("ROOT :",ROOT)
print("TOKEN:",MASTER_TOKEN)
print("="*60)
print("URL  : /terminal")
print("="*60)

server=ThreadingHTTPServer((HOST,PORT),Handler)
server.serve_forever()
