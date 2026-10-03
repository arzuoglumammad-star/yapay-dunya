(function () {
    "use strict";

    const TERMINAL_URL =
        window.YAPAY_DUNYA_TERMINAL_URL ||
        localStorage.getItem("yapay-dunya-terminal-url") ||
        "";

    window.YapayDunyaTerminal = {

        open() {
            const url =
                TERMINAL_URL ||
                "/terminal";

            window.open(
                url,
                "YapayDunyaLinuxTerminal",
                "noopener,noreferrer"
            );
        },

        setURL(url) {
            localStorage.setItem(
                "yapay-dunya-terminal-url",
                url
            );
        }
    };

    window.addEventListener("DOMContentLoaded", () => {

        if (document.getElementById("yd-linux-terminal-button")) {
            return;
        }

        const button = document.createElement("button");

        button.id = "yd-linux-terminal-button";

        button.textContent = "⌘ Linux Terminal";

        button.style.cssText = `
            position:fixed;
            right:16px;
            bottom:88px;
            z-index:999999;
            height:46px;
            padding:0 16px;
            border:1px solid rgba(100,180,255,.35);
            border-radius:14px;
            background:#101923;
            color:#dff4ff;
            font:700 13px system-ui;
            box-shadow:0 8px 30px rgba(0,0,0,.35);
            cursor:pointer;
        `;

        button.onclick = () => {
            window.YapayDunyaTerminal.open();
        };

        document.body.appendChild(button);
    });
})();
