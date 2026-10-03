(function () {

    const RemoteLinux = {

        base: "/api",

        async status() {

            try {

                const response =
                    await fetch(
                        `${this.base}/status`
                    );

                return await response.json();

            } catch (error) {

                return {
                    ok: false,
                    error: String(error)
                };

            }

        },

        async system() {

            try {

                const response =
                    await fetch(
                        `${this.base}/system`
                    );

                return await response.json();

            } catch (error) {

                return {
                    ok: false,
                    error: String(error)
                };

            }

        },

        async command(command) {

            try {

                const response =
                    await fetch(
                        `${this.base}/terminal`,
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                command
                            })
                        }
                    );

                return await response.json();

            } catch (error) {

                return {
                    ok: false,
                    error: String(error)
                };

            }

        }

    };

    window.RemoteLinux = RemoteLinux;

})();
