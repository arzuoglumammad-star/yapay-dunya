const API = "/api";

async function remoteLinuxStatus() {

    try {

        const response =
            await fetch(`${API}/status`);

        return await response.json();

    } catch (error) {

        return {
            ok: false,
            error: String(error)
        };

    }

}

async function remoteLinuxSystem() {

    try {

        const response =
            await fetch(`${API}/system`);

        return await response.json();

    } catch (error) {

        return {
            ok: false,
            error: String(error)
        };

    }

}

window.RemoteLinux = {
    status: remoteLinuxStatus,
    system: remoteLinuxSystem
};
