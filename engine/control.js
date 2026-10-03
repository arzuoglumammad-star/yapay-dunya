(() => {

function render() {

  const s =
    window.YapayDunya?.getState();

  if (!s)
    return;

  let panel =
    document.getElementById(
      "world-engine-panel"
    );

  if (!panel) {

    panel =
      document.createElement("section");

    panel.id =
      "world-engine-panel";

    panel.style.cssText =
      "margin:20px 0;padding:18px;" +
      "border:1px solid #1d344d;" +
      "border-radius:22px;" +
      "background:#0b1928;color:white;";

    document
      .querySelector("main")
      ?.appendChild(panel);

  }

  const t = s.time;

  panel.innerHTML = `

    <div style="
      display:flex;
      justify-content:space-between;
      align-items:center;
    ">

      <div>

        <div style="
          font-size:11px;
          color:#7892ac;
        ">
          WORLD ENGINE v0.3.0
        </div>

        <div style="
          font-size:30px;
          font-weight:800;
        ">
          ${String(t.hour).padStart(2,"0")}:
          ${String(t.minute).padStart(2,"0")}
        </div>

        <small>
          Gün ${t.day} · Tick ${t.tick}
        </small>

      </div>

      <b style="
        color:${s.running
          ? "#7dffb0"
          : "#ff9999"};
      ">
        ${s.running
          ? "● YAŞIYOR"
          : "● DURDU"}
      </b>

    </div>

    <div style="
      display:grid;
      grid-template-columns:1fr 1fr;
      gap:8px;
      margin-top:15px;
    ">

      <div style="padding:12px;background:#102337;border-radius:14px">
        NÜFUS
        <strong style="display:block;font-size:22px">
          ${s.population}
        </strong>
      </div>

      <div style="padding:12px;background:#102337;border-radius:14px">
        PARA
        <strong style="display:block;font-size:22px">
          ${Math.round(s.economy.money).toLocaleString("tr-TR")}
        </strong>
      </div>

      <div style="padding:12px;background:#102337;border-radius:14px">
        GIDA
        <strong style="display:block;font-size:22px">
          ${Math.round(s.resources.food)}
        </strong>
      </div>

      <div style="padding:12px;background:#102337;border-radius:14px">
        ENERJİ
        <strong style="display:block;font-size:22px">
          ${Math.round(s.resources.energy)}
        </strong>
      </div>

    </div>

    <div style="
      display:grid;
      grid-template-columns:1fr 1fr 1fr;
      gap:7px;
      margin-top:12px;
    ">

      <button id="yd-start"
        style="
          padding:12px;
          border:0;
          border-radius:12px;
          background:#17486a;
          color:white;
        ">
        BAŞLAT
      </button>

      <button id="yd-stop"
        style="
          padding:12px;
          border:0;
          border-radius:12px;
          background:#43262c;
          color:white;
        ">
        DURDUR
      </button>

      <button id="yd-step"
        style="
          padding:12px;
          border:0;
          border-radius:12px;
          background:#302d22;
          color:white;
        ">
        +1 DK
      </button>

    </div>

    <button id="yd-reset"
      style="
        width:100%;
        margin-top:8px;
        padding:10px;
        border:1px solid #56383d;
        border-radius:12px;
        background:transparent;
        color:#e5a5aa;
      ">
      DÜNYAYI SIFIRLA
    </button>

    <div style="
      margin-top:18px;
      font-size:12px;
      color:#9fb2c5;
      line-height:1.8;
    ">

      Şehir: ${s.cities.length}<br>
      Vatandaş: ${s.agents.length}<br>
      İşletme: ${s.businesses.length}<br>
      Sipariş: ${s.orders.length}<br>
      Üretim: ${Math.round(s.production.food)}<br>
      Gıda fiyatı:
      ${s.economy.prices.food.toFixed(2)}

    </div>

  `;

  document.getElementById(
    "yd-start"
  ).onclick =
    () => window.YapayDunya.start();

  document.getElementById(
    "yd-stop"
  ).onclick =
    () => window.YapayDunya.stop();

  document.getElementById(
    "yd-step"
  ).onclick =
    () => window.YapayDunya.tick();

  document.getElementById(
    "yd-reset"
  ).onclick =
    () => {

      if (
        confirm(
          "Dünya tamamen sıfırlansın mı?"
        )
      )
        window.YapayDunya.reset();

    };

}

function init() {

  render();

  window.addEventListener(
    "yapay-dunya-update",
    render
  );

}

if (
  document.readyState === "loading"
) {

  document.addEventListener(
    "DOMContentLoaded",
    init
  );

} else {

  init();

}

})();
