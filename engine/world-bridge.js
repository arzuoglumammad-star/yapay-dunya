window.YapayDunyaWorld = {
  async status() {
    const r = await fetch("/api/world/status");
    return r.json();
  },

  async tick(minutes = 1) {
    const r = await fetch("/api/world/tick", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ minutes })
    });

    return r.json();
  },

  async run() {
    const r = await fetch("/api/world/run", {
      method: "POST"
    });

    return r.json();
  },

  async stop() {
    const r = await fetch("/api/world/stop", {
      method: "POST"
    });

    return r.json();
  },

  async reset() {
    const r = await fetch("/api/world/reset", {
      method: "POST"
    });

    return r.json();
  }
};
