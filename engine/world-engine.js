(() => {

"use strict";

const KEY = "yapay-dunya-real-v030";

const CONFIG = {
  MS_PER_SIM_MINUTE: 500,
  START_POPULATION: 100
};

function initialWorld() {
  return {
    id: "YD-001",
    name: "Yapay Dünya",
    version: "0.3.0",
    running: false,

    time: {
      minute: 0,
      hour: 0,
      day: 1,
      tick: 0
    },

    population: 0,

    cities: [],
    agents: [],
    businesses: [],
    orders: [],
    events: [],
    transactions: [],

    resources: {
      food: 1000,
      water: 2000,
      energy: 1500,
      raw_material: 1000
    },

    economy: {
      money: 100000,
      transactions: 0,

      prices: {
        food: 10,
        water: 5,
        energy: 8,
        raw_material: 20
      }
    },

    production: {
      food: 0,
      products: 0
    },

    statistics: {
      produced: 0,
      consumed: 0,
      trade: 0,
      orders: 0
    }
  };
}

let state = load();
let timer = null;

function load() {

  try {

    const saved =
      localStorage.getItem(KEY);

    if (saved)
      return JSON.parse(saved);

  } catch (e) {}

  return initialWorld();
}

function save() {

  localStorage.setItem(
    KEY,
    JSON.stringify(state)
  );

}

function id(prefix) {

  return prefix + "-" +
    Math.random()
      .toString(36)
      .substring(2, 9)
      .toUpperCase();

}

function log(message, type="system") {

  state.events.unshift({
    id: id("EV"),
    day: state.time.day,
    hour: state.time.hour,
    minute: state.time.minute,
    type,
    message
  });

  state.events =
    state.events.slice(0, 200);

}

function createCity() {

  const city = {
    id: id("CITY"),
    name: "Merkez Şehir",
    population: 0,
    buildings: 20,
    businesses: 0
  };

  state.cities.push(city);

  log(
    "Merkez Şehir kuruldu.",
    "city"
  );

  return city;
}

function createAgent(city, index) {

  const jobs = [
    "işçi",
    "tüccar",
    "mühendis",
    "çiftçi",
    "hizmet"
  ];

  const agent = {

    id: id("AGENT"),

    name:
      "Vatandaş " +
      (index + 1),

    cityId: city.id,

    age:
      18 +
      Math.floor(
        Math.random() * 45
      ),

    money:
      500 +
      Math.floor(
        Math.random() * 1000
      ),

    health: 100,

    hunger: 0,

    thirst: 0,

    energy: 100,

    occupation:
      jobs[
        index % jobs.length
      ]

  };

  state.agents.push(agent);

  city.population++;

  state.population++;

}

function createBusiness(city, type) {

  const business = {

    id: id("BUS"),

    name:
      type === "production"
        ? "Gıda Üretim Tesisi"
        : "Merkez Market",

    cityId: city.id,

    type,

    money: 5000,

    stock: 0,

    capacity: 20

  };

  state.businesses.push(business);

  city.businesses++;

}

function initialize() {

  if (state.cities.length)
    return;

  const city =
    createCity();

  createBusiness(
    city,
    "production"
  );

  createBusiness(
    city,
    "market"
  );

  for (
    let i = 0;
    i < CONFIG.START_POPULATION;
    i++
  ) {

    createAgent(
      city,
      i
    );

  }

  log(
    "100 vatandaş Yapay Dünya'ya yerleştirildi.",
    "population"
  );

  log(
    "Üretim tesisi ve market açıldı.",
    "business"
  );

  save();

}

function production() {

  const producers =
    state.businesses.filter(
      b =>
        b.type === "production"
    );

  if (!producers.length)
    return;

  const workers =
    state.agents.filter(
      a =>
        a.occupation === "işçi" ||
        a.occupation === "çiftçi" ||
        a.occupation === "mühendis"
    );

  const amount =
    Math.min(
      workers.length,
      producers.length * 5
    );

  if (
    state.resources.energy < amount ||
    state.resources.raw_material < amount
  )
    return;

  state.resources.energy -=
    amount;

  state.resources.raw_material -=
    amount;

  state.resources.food +=
    amount * 2;

  state.production.food +=
    amount * 2;

  state.production.products +=
    amount;

  state.statistics.produced +=
    amount;

}

function consumption() {

  const people =
    state.population;

  const food =
    people * 0.002;

  const water =
    people * 0.0015;

  state.resources.food =
    Math.max(
      0,
      state.resources.food - food
    );

  state.resources.water =
    Math.max(
      0,
      state.resources.water - water
    );

  for (
    const agent of state.agents
  ) {

    agent.hunger =
      Math.min(
        100,
        agent.hunger + 0.2
      );

    agent.thirst =
      Math.min(
        100,
        agent.thirst + 0.15
      );

  }

  state.statistics.consumed +=
    food;

}

function economy() {

  const workers =
    state.agents.filter(
      a =>
        a.occupation !== "işsiz"
    );

  const salary =
    0.05;

  for (
    const worker of workers
  ) {

    if (
      state.economy.money >=
      salary
    ) {

      worker.money +=
        salary;

      state.economy.money -=
        salary;

      state.economy.transactions++;

    }

  }

}

function market() {

  const price =
    state.economy.prices.food;

  const buyers =
    state.agents.filter(
      a =>
        a.money >= price &&
        a.hunger > 20
    );

  const amount =
    Math.min(
      buyers.length,
      Math.floor(
        state.resources.food
      )
    );

  for (
    let i = 0;
    i < amount;
    i++
  ) {

    const buyer =
      buyers[i];

    buyer.money -=
      price;

    state.economy.money +=
      price;

    state.resources.food--;

    buyer.hunger =
      Math.max(
        0,
        buyer.hunger - 20
      );

    state.statistics.trade +=
      price;

  }

}

function orders() {

  if (
    state.time.hour === 8 &&
    state.time.minute === 0
  ) {

    const order = {

      id: id("ORD"),

      day: state.time.day,

      product: "food",

      quantity:
        Math.max(
          10,
          Math.floor(
            state.population * 0.1
          )
        ),

      status: "open",

      price:
        state.economy.prices.food

    };

    state.orders.push(order);

    state.statistics.orders++;

    log(
      "Yeni gıda siparişi oluşturuldu.",
      "order"
    );

  }

}

function prices() {

  if (
    state.resources.food < 500
  ) {

    state.economy.prices.food =
      Math.min(
        100,
        state.economy.prices.food * 1.001
      );

  } else {

    state.economy.prices.food =
      Math.max(
        5,
        state.economy.prices.food * 0.999
      );

  }

}

function tick() {

  state.time.tick++;

  state.time.minute++;

  if (
    state.time.minute >= 60
  ) {

    state.time.minute = 0;
    state.time.hour++;

  }

  if (
    state.time.hour >= 24
  ) {

    state.time.hour = 0;
    state.time.day++;

    log(
      "Yeni dünya günü başladı: " +
      state.time.day,
      "day"
    );

  }

  consumption();

  production();

  economy();

  market();

  prices();

  orders();

  save();

  notify();

}

function start() {

  if (timer)
    return;

  state.running = true;

  log(
    "Yapay Dünya çalışmaya başladı.",
    "system"
  );

  timer =
    setInterval(
      tick,
      CONFIG.MS_PER_SIM_MINUTE
    );

  save();

  notify();

}

function stop() {

  if (timer) {

    clearInterval(timer);
    timer = null;

  }

  state.running = false;

  log(
    "Yapay Dünya durduruldu.",
    "system"
  );

  save();

  notify();

}

function reset() {

  stop();

  localStorage.removeItem(KEY);

  state =
    initialWorld();

  initialize();

  notify();

}

function notify() {

  window.dispatchEvent(
    new CustomEvent(
      "yapay-dunya-update",
      {
        detail:
          JSON.parse(
            JSON.stringify(state)
          )
      }
    )
  );

}

window.YapayDunya = {

  start,
  stop,
  reset,
  tick,

  getState() {

    return JSON.parse(
      JSON.stringify(state)
    );

  }

};

initialize();

})();
