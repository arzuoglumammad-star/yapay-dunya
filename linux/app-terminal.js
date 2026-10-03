const YDTerminal = (() => {

    const API = window.YD_TERMINAL_API || "";

    const output =
        document.getElementById("output");

    const input =
        document.getElementById("command");

    const connection =
        document.getElementById("connection");

    function print(text, type = "output-line") {

        const line =
            document.createElement("div");

        line.className = type;

        line.textContent =
            String(text ?? "");

        output.appendChild(line);

        output.scrollTop =
            output.scrollHeight;
    }

    async function request(
        endpoint,
        options = {}
    ) {

        const response =
            await fetch(
                API + endpoint,
                {
                    cache: "no-store",
                    ...options
                }
            );

        return response.json();
    }

    async function health() {

        try {

            const data =
                await request("/api/status");

            if (!data.ok)
                throw new Error("offline");

            connection.textContent =
                "● LINUX ONLINE";

            connection.className =
                "online";

            print(
                "YAPAY DÜNYA LINUX TERMINAL HAZIR",
                "success"
            );

            print(
                "Proje: " + data.project,
                "muted"
            );

            print(
                "Kullanıcı: " + data.user,
                "muted"
            );

            print("");

        } catch (error) {

            connection.textContent =
                "● OFFLINE";

            connection.style.color =
                "#ff7373";

            print(
                "Linux backend bağlantısı kurulamadı.",
                "error"
            );
        }
    }

    async function run(command) {

        command =
            String(command || "").trim();

        if (!command)
            return;

        print(
            "$ " + command,
            "command"
        );

        try {

            const data =
                await request(
                    "/api/terminal",
                    {
                        method:"POST",

                        headers:{
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                command
                            })
                    }
                );

            if (data.stdout)
                print(data.stdout);

            if (data.stderr)
                print(
                    data.stderr,
                    "error"
                );

            if (
                data.code !== undefined &&
                data.code !== 0
            ) {
                print(
                    "[exit " +
                    data.code +
                    "]",
                    "error"
                );
            }

        } catch (error) {

            print(
                "Bağlantı hatası: " +
                error.message,
                "error"
            );
        }
    }

    function execute() {

        const command =
            input.value.trim();

        if (!command)
            return;

        input.value = "";

        run(command);
    }

    input.addEventListener(
        "keydown",
        event => {

            if (
                event.key === "Enter"
            ) {
                execute();
            }
        }
    );

    health();

    return {
        run,
        execute,
        health
    };

})();
