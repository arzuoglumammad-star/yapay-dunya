(() => {

    const API =
        window.YD_TERMINAL_API;

    if (!API) return;

    function create() {

        if (
            document.getElementById(
                "yd-terminal-launcher"
            )
        ) return;

        const style =
            document.createElement("style");

        style.textContent = `
        #yd-terminal-launcher{
            position:fixed;
            right:16px;
            bottom:88px;
            z-index:99999;
            width:52px;
            height:52px;
            border:0;
            border-radius:16px;
            background:#101820;
            color:#fff;
            box-shadow:
                0 8px 28px rgba(0,0,0,.35);
            font-size:21px;
        }

        #yd-terminal-panel{
            position:fixed;
            inset:
                12px
                12px
                12px
                12px;
            z-index:100000;
            display:none;
            flex-direction:column;
            overflow:hidden;
            border:1px solid #27313c;
            border-radius:18px;
            background:#05070a;
            box-shadow:
                0 20px 60px rgba(0,0,0,.55);
        }

        #yd-terminal-panel.open{
            display:flex;
        }

        #yd-terminal-head{
            height:54px;
            flex:0 0 54px;
            display:flex;
            align-items:center;
            justify-content:space-between;
            padding:0 12px;
            background:#0b0f14;
            border-bottom:1px solid #202731;
            color:#fff;
            font-weight:700;
        }

        #yd-terminal-close{
            border:0;
            border-radius:9px;
            background:#202832;
            color:#fff;
            width:38px;
            height:34px;
            font-size:18px;
        }

        #yd-terminal-frame{
            width:100%;
            height:calc(100% - 54px);
            border:0;
            background:#05070a;
        }
        `;

        document.head.appendChild(style);

        const launcher =
            document.createElement("button");

        launcher.id =
            "yd-terminal-launcher";

        launcher.textContent = "⌘";

        launcher.title =
            "Yapay Dünya Terminal";

        document.body.appendChild(
            launcher
        );

        const panel =
            document.createElement("div");

        panel.id =
            "yd-terminal-panel";

        panel.innerHTML = `
            <div id="yd-terminal-head">
                <span>Yapay Dünya — Linux Terminal</span>
                <button id="yd-terminal-close">×</button>
            </div>

            <iframe
                id="yd-terminal-frame"
                title="Yapay Dünya Linux Terminal"
                src="${API}/"
                allow="clipboard-read; clipboard-write">
            </iframe>
        `;

        document.body.appendChild(
            panel
        );

        launcher.onclick = () => {
            panel.classList.add("open");
        };

        panel.querySelector(
            "#yd-terminal-close"
        ).onclick = () => {
            panel.classList.remove("open");
        };
    }

    if (
        document.readyState ===
        "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            create
        );
    } else {
        create();
    }

})();
