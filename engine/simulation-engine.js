#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const DATA = path.join(ROOT, "data", "world-state.json");

const MINUTES_PER_DAY = 1440;

function nowISO() {
  return new Date().toISOString();
}

function money(n) {
  return Math.max(0, Number(n) || 0);
}

function load() {
  if (!fs.existsSync(DATA)) return createWorld();
  try {
    return JSON.parse(fs.readFileSync(DATA, "utf8"));
  } catch {
    return createWorld();
  }
}

function save(world) {
  world.updatedAt = nowISO();
  fs.writeFileSync(DATA, JSON.stringify(world, null, 2));
}

function createWorld() {
  const world = {
    version: "1.0.0",
    status: "running",
    createdAt: nowISO(),
    updatedAt: nowISO(),

    clock: {
      day: 1,
      minute: 0,
      totalMinutes: 0
    },

    economy: {
      moneySupply: 100000,
      prices: {
        food: 10,
        water: 4,
        energy: 3,
        raw_material: 6
      },
      inflation: 0,
      transactions: 0,
      totalSales: 0,
      totalWages: 0
    },

    resources: {
      food: 1000,
      water: 2000,
      energy: 1500,
      raw_material: 1000
    },

    cities: [
      {
        id: "city-001",
        name: "Merkez Şehir",
        population: 100,
        prosperity: 50,
        businesses: ["business-001", "business-002"]
      }
    ],

    agents: [],
    businesses: [],
    orders: [],
    events: [],
    metrics: {
      births: 0,
      deaths: 0,
      employed: 0,
      unemployed: 0,
      production: 0,
      consumption: 0,
      sales: 0,
      orders: 0
    }
  };

  const jobs = [
    "üretim",
    "market",
    "taşıma",
    "hizmet",
    "enerji"
  ];

  for (let i = 1; i <= 100; i++) {
    world.agents.push({
      id: `agent-${String(i).padStart(4, "0")}`,
      name: `Vatandaş ${i}`,
      cityId: "city-001",
      age: 18 + (i % 50),
      job: jobs[i % jobs.length],
      employerId: i % 5 === 0 ? "business-002" : "business-001",
      balance: 100 + ((i * 17) % 300),
      dailyNeed: {
        food: 1,
        water: 2,
        energy: 0.5
      },
      satisfaction: 70
    });
  }

  world.businesses.push(
    {
      id: "business-001",
      name: "Gıda Üretim Tesisi",
      type: "producer",
      cityId: "city-001",
      employees: 80,
      cash: 15000,
      stock: {
        food: 500
      },
      productionPerMinute: 3,
      wagePerDay: 120
    },
    {
      id: "business-002",
      name: "Merkez Market",
      type: "retail",
      cityId: "city-001",
      employees: 20,
      cash: 10000,
      stock: {
        food: 300,
        water: 500
      },
      wagePerDay: 100
    }
  );

  save(world);
  return world;
}

function addEvent(world, type, message, data = {}) {
  world.events.unshift({
    id: `event-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    time: world.clock.totalMinutes,
    day: world.clock.day,
    type,
    message,
    data
  });

  if (world.events.length > 100) {
    world.events.length = 100;
  }
}

function consume(world) {
  let food = 0;
  let water = 0;
  let energy = 0;

  for (const agent of world.agents) {
    const f = Math.min(agent.dailyNeed.food / MINUTES_PER_DAY, 0.01);
    const w = Math.min(agent.dailyNeed.water / MINUTES_PER_DAY, 0.02);
    const e = Math.min(agent.dailyNeed.energy / MINUTES_PER_DAY, 0.005);

    food += f;
    water += w;
    energy += e;

    agent.satisfaction -= 0.01;

    if (world.resources.food > 0) {
      world.resources.food = Math.max(0, world.resources.food - f);
    } else {
      agent.satisfaction -= 0.1;
    }

    if (world.resources.water > 0) {
      world.resources.water = Math.max(0, world.resources.water - w);
    } else {
      agent.satisfaction -= 0.2;
    }

    if (world.resources.energy > 0) {
      world.resources.energy = Math.max(0, world.resources.energy - e);
    } else {
      agent.satisfaction -= 0.1;
    }

    agent.satisfaction = Math.max(0, Math.min(100, agent.satisfaction));
  }

  world.metrics.consumption += food + water + energy;
}

function produce(world) {
  const producer = world.businesses.find(x => x.type === "producer");
  if (!producer) return;

  const possible = Math.min(
    producer.productionPerMinute,
    world.resources.energy,
    world.resources.raw_material
  );

  if (possible <= 0) return;

  producer.stock.food = (producer.stock.food || 0) + possible;
  world.resources.food += possible;

  world.resources.energy -= possible * 0.4;
  world.resources.raw_material -= possible * 0.2;

  world.metrics.production += possible;
}

function payWages(world) {
  if (world.clock.minute !== 480) return;

  for (const business of world.businesses) {
    const wage = business.employees * business.wagePerDay;

    if (business.cash >= wage) {
      business.cash -= wage;
      world.economy.moneySupply += wage;
      world.economy.totalWages += wage;

      const workers = world.agents.filter(
        a => a.employerId === business.id
      );

      for (const worker of workers) {
        worker.balance += business.wagePerDay;
      }
    }
  }

  addEvent(world, "wages", "Günlük maaş ödemeleri gerçekleştirildi.");
}

function market(world) {
  const market = world.businesses.find(x => x.type === "retail");
  if (!market) return;

  let sales = 0;

  for (const agent of world.agents) {
    const need = 0.01;

    if ((market.stock.food || 0) >= need && agent.balance >= world.economy.prices.food * need) {
      const cost = world.economy.prices.food * need;

      market.stock.food -= need;
      agent.balance -= cost;
      market.cash += cost;

      world.economy.totalSales += cost;
      world.economy.transactions++;
      sales += cost;

      agent.satisfaction = Math.min(100, agent.satisfaction + 0.02);
    }
  }

  world.metrics.sales += sales;
}

function updatePrices(world) {
  const demand = world.agents.length;
  const supply = world.resources.food;

  if (supply < demand * 5) {
    world.economy.prices.food *= 1.0005;
  } else if (supply > demand * 12) {
    world.economy.prices.food *= 0.9995;
  }

  world.economy.prices.food = Math.max(
    1,
    Math.min(1000, world.economy.prices.food)
  );

  const base = 10;
  world.economy.inflation =
    ((world.economy.prices.food - base) / base) * 100;
}

function createOrders(world) {
  if (world.clock.minute !== 480) return;

  const market = world.businesses.find(x => x.type === "retail");
  const producer = world.businesses.find(x => x.type === "producer");

  if (!market || !producer) return;

  if ((market.stock.food || 0) < 100) {
    const quantity = 300;

    world.orders.push({
      id: `order-${Date.now()}`,
      type: "restock",
      buyerId: market.id,
      sellerId: producer.id,
      product: "food",
      quantity,
      price: world.economy.prices.food,
      status: "created",
      createdAt: nowISO()
    });

    market.stock.food += quantity;
    producer.stock.food = Math.max(
      0,
      (producer.stock.food || 0) - quantity
    );

    world.metrics.orders++;

    addEvent(
      world,
      "order",
      `Market ${quantity} birim gıda siparişi oluşturdu.`,
      { quantity }
    );
  }
}

function updateEmployment(world) {
  world.metrics.employed = world.agents.filter(a => a.employerId).length;
  world.metrics.unemployed =
    world.agents.length - world.metrics.employed;
}

function tick(world, minutes = 1) {
  minutes = Math.max(1, Math.floor(Number(minutes) || 1));

  for (let i = 0; i < minutes; i++) {
    world.clock.totalMinutes++;
    world.clock.minute++;

    if (world.clock.minute >= MINUTES_PER_DAY) {
      world.clock.minute = 0;
      world.clock.day++;

      addEvent(
        world,
        "day",
        `Yeni gün başladı: ${world.clock.day}`
      );
    }

    consume(world);
    produce(world);
    market(world);
    payWages(world);
    createOrders(world);
    updatePrices(world);
    updateEmployment(world);
  }

  save(world);
  return world;
}

function status(world) {
  return {
    version: world.version,
    status: world.status,
    clock: world.clock,
    population: world.agents.length,
    cities: world.cities.length,
    businesses: world.businesses.length,
    orders: world.orders.length,
    resources: world.resources,
    economy: world.economy,
    metrics: world.metrics,
    updatedAt: world.updatedAt
  };
}

function main() {
  const command = process.argv[2] || "status";
  let world = load();

  if (command === "init") {
    world = createWorld();
  } else if (command === "tick") {
    world = tick(world, process.argv[3] || 1);
  } else if (command === "run") {
    world.status = "running";
    save(world);
  } else if (command === "stop") {
    world.status = "stopped";
    save(world);
  } else if (command === "reset") {
    world = createWorld();
  }

  console.log(JSON.stringify(status(world), null, 2));
}

main();
