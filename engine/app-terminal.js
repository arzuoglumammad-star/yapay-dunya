(function(){

    const API = location.origin;

    window.YapayDunyaTerminal = {

        async status(){
            const r = await fetch(API + "/api/status");
            return r.json();
        },

        async system(){
            const r = await fetch(API + "/api/system");
            return r.json();
        },

        async command(command){
            const r = await fetch(API + "/api/command", {
                method:"POST",
                headers:{
                    "Content-Type":"application/json"
                },
                body:JSON.stringify({
                    command:String(command || "")
                })
            });
            return r.json();
        }

    };

})();
