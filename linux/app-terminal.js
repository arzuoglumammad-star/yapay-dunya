const output = document.getElementById("output");
const input = document.getElementById("command");
const statusEl = document.getElementById("status");

function print(text, cls="line"){
    const div=document.createElement("div");
    div.className=cls;
    div.textContent=text;
    output.appendChild(div);
    output.scrollTop=output.scrollHeight;
}

async function status(){
    try{
        const r=await fetch("/api/status");
        const d=await r.json();

        if(d.ok){
            statusEl.textContent="● LINUX ONLINE";
            statusEl.className="status";
            print("YAPAY DÜNYA LINUX TERMINAL HAZIR","success");
            print("Proje: "+d.project);
            print("Kullanıcı: "+d.user);
            print("");
        }
    }catch(e){
        statusEl.textContent="● OFFLINE";
        statusEl.style.color="#ff6666";
        print("Terminal bağlantısı kurulamadı","error");
    }
}

async function run(command){
    input.value="";
    print("$ "+command,"prompt");

    try{
        const r=await fetch("/api/terminal",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({command})
        });

        const d=await r.json();

        if(d.stdout) print(d.stdout);
        if(d.stderr) print(d.stderr,"error");

        if(d.code !== undefined && d.code !== 0){
            print("[exit "+d.code+"]","error");
        }
    }catch(e){
        print("Bağlantı hatası: "+e.message,"error");
    }
}

function execute(){
    const cmd=input.value.trim();
    if(cmd) run(cmd);
}

input.addEventListener("keydown",e=>{
    if(e.key==="Enter") execute();
});

status();
</script>
