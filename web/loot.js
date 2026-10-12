// Loot roller: pick a category, enter a 2d20 result (2-40), get the item and its quantity.
// The default tables below are ORIGINAL to this app (not the rulebook's tables): common items sit
// on the middle results (the most likely 2d20 totals), rare items on the extremes.
// Every row can be edited in the app, so you can type in the tables from your own book.

const LOOT_CATEGORIES = [
  "Ammunition", "Armor", "Clothing", "Food", "Beverages", "Chems",
  "Oddities & Valuables", "Junk", "Weapons (Ranged)", "Weapons (Melee)", "Weapons (Thrown/Explosives)",
];

// [name, fixed quantity, combat dice to add] - listed from most common to rarest
const LOOT_POOLS = {
  "Ammunition": [
    [".38 rounds", 10, 5], ["10mm rounds", 8, 4], ["Shotgun shells", 6, 3], [".308 rounds", 6, 3],
    ["5.56mm rounds", 8, 4], ["Fusion cells", 12, 6], [".45 rounds", 8, 4], [".44 Magnum rounds", 4, 2],
    ["Flamer fuel", 10, 5], [".50 caliber rounds", 4, 2], ["Plasma cartridges", 8, 4], ["5mm rounds", 20, 10],
    ["Railway spikes", 6, 3], ["Flares", 2, 1], ["Missiles", 2, 1], ["Fusion core", 1, 0], ["Mini-nuke", 1, 0],
  ],
  "Armor": [
    ["Raider arm", 1, 0], ["Raider leg", 1, 0], ["Leather arm", 1, 0], ["Raider chest piece", 1, 0],
    ["Leather leg", 1, 0], ["Leather chest piece", 1, 0], ["Metal helmet", 1, 0], ["Metal arm", 1, 0],
    ["Metal leg", 1, 0], ["Sturdy raider chest piece", 1, 0], ["Metal chest piece", 1, 0],
    ["Vault-Tec security helmet", 1, 0], ["Combat armor arm", 1, 0], ["Combat armor leg", 1, 0],
    ["Sturdy leather chest piece", 1, 0], ["Combat armor chest piece", 1, 0], ["Synth armor arm", 1, 0],
    ["Heavy metal chest piece", 1, 0], ["Power armor frame (no pieces)", 1, 0], ["T-45 power armor arm", 1, 0],
    ["T-60 power armor helmet", 1, 0],
  ],
  "Clothing": [
    ["Casual clothing", 1, 0], ["Tough clothing", 1, 0], ["Sack hood", 1, 0], ["Harness", 1, 0],
    ["Hood or cowl", 1, 0], ["Road leathers", 1, 0], ["Hard hat", 1, 0], ["Vault jumpsuit", 1, 0],
    ["Drifter outfit", 1, 0], ["Gas mask", 1, 0], ["Lab coat", 1, 0], ["Formal hat", 1, 0],
    ["Formal clothing", 1, 0], ["Utility coveralls", 1, 0], ["Military fatigues", 1, 0],
    ["Brotherhood fatigues", 1, 0], ["Hazmat suit", 1, 0], ["Spike armor", 1, 0],
  ],
  "Food": [
    ["Mutfruit", 1, 1], ["Tato", 1, 1], ["Corn", 1, 1], ["Radroach meat", 1, 0], ["Carrot", 1, 1],
    ["Iguana bits", 1, 0], ["Pork n' Beans (can)", 1, 0], ["Mole rat meat", 1, 0], ["Razorgrain", 1, 1],
    ["Potato Crisps", 1, 0], ["Cram", 1, 0], ["Instamash", 1, 0], ["Melon", 1, 0], ["Gourd", 1, 0],
    ["Sugar Bombs", 1, 0], ["Fancy Lads Snack Cakes", 1, 0], ["Salisbury Steak", 1, 0],
    ["Yum Yum Deviled Eggs", 1, 0], ["Brain fungus", 1, 0], ["Glowing fungus", 1, 0], ["Deathclaw steak", 1, 0],
  ],
  "Beverages": [
    ["Dirty water", 1, 1], ["Nuka-Cola", 1, 0], ["Beer", 1, 1], ["Purified water", 1, 0], ["Whiskey", 1, 0],
    ["Brahmin milk", 1, 0], ["Wine", 1, 0], ["Bourbon", 1, 0], ["Vodka", 1, 0], ["Rum", 1, 0],
    ["Moonshine", 1, 0], ["Nuka-Cola Cherry", 1, 0], ["Nuka-Cola Quantum", 1, 0],
  ],
  "Chems": [
    ["Stimpak", 1, 0], ["RadAway", 1, 0], ["Rad-X", 1, 0], ["Healing salve", 1, 0], ["Jet", 1, 0],
    ["Buffout", 1, 0], ["Mentats", 1, 0], ["Med-X", 1, 0], ["Calmex", 1, 0], ["Psycho", 1, 0],
    ["Day Tripper", 1, 0], ["Daddy-O", 1, 0], ["Addictol", 1, 0], ["Overdrive", 1, 0], ["Fury", 1, 0],
    ["Super stimpak", 1, 0], ["X-Cell", 1, 0],
  ],
  "Oddities & Valuables": [
    ["Bottle caps", 5, 3], ["Bobby pins", 2, 2], ["Pre-War money", 3, 2], ["Lighter", 1, 0],
    ["Blank holotape", 1, 0], ["Note hinting at a nearby stash", 1, 0], ["Key to a locked container nearby", 1, 0],
    ["Magazine (random issue)", 1, 0], ["Locked container", 1, 0], ["Gold pocket watch", 1, 0],
    ["Holotape with old recordings", 1, 0], ["First aid kit", 1, 0], ["Multi-Tool", 1, 0],
    ["Robot repair kit", 1, 0], ["Stealth Boy", 1, 0], ["Pre-War gold bar", 1, 0],
  ],
  "Junk": [
    ["Tin cans (common materials)", 1, 1], ["Duct tape (common materials)", 1, 0],
    ["Bent cutlery (common materials)", 1, 1], ["Coffee mug (common materials)", 1, 0],
    ["Desk fan (common + uncommon)", 1, 0], ["Clipboard (common materials)", 1, 0],
    ["Toy car (common materials)", 1, 0], ["Telephone (common + uncommon)", 1, 0],
    ["Hot plate (common + uncommon)", 1, 0], ["Typewriter (uncommon materials)", 1, 0],
    ["Camera (uncommon materials)", 1, 0], ["Fuse box parts (uncommon)", 1, 0],
    ["Military-grade circuit board (rare)", 1, 0], ["Nuclear material (rare)", 1, 0],
  ],
  "Weapons (Ranged)": [
    ["Pipe gun", 1, 0], ["Pipe bolt-action", 1, 0], ["Pipe revolver", 1, 0], ["10mm pistol", 1, 0],
    ["Hunting rifle", 1, 0], ["Double-barrel shotgun", 1, 0], [".44 pistol", 1, 0], ["Laser pistol", 1, 0],
    ["Combat shotgun", 1, 0], ["Submachine gun", 1, 0], ["Combat rifle", 1, 0], ["Assault rifle", 1, 0],
    ["Laser rifle", 1, 0], ["Institute laser", 1, 0], ["Plasma pistol", 1, 0], ["Flamer", 1, 0],
    ["Gauss rifle", 1, 0], ["Minigun", 1, 0], ["Missile launcher", 1, 0], ["Fat Man", 1, 0],
  ],
  "Weapons (Melee)": [
    ["Switchblade", 1, 0], ["Lead pipe", 1, 0], ["Pipe wrench", 1, 0], ["Tire iron", 1, 0], ["Rolling pin", 1, 0],
    ["Pool cue", 1, 0], ["Board", 1, 0], ["Baseball bat", 1, 0], ["Knuckles", 1, 0], ["Machete", 1, 0],
    ["Combat knife", 1, 0], ["Walking cane", 1, 0], ["Boxing glove", 1, 0], ["Sledgehammer", 1, 0],
    ["Sword", 1, 0], ["Ripper", 1, 0], ["Power fist", 1, 0], ["Super sledge", 1, 0], ["Shishkebab", 1, 0],
    ["Deathclaw gauntlet", 1, 0],
  ],
  "Weapons (Thrown/Explosives)": [
    ["Molotov cocktails", 2, 1], ["Throwing knives", 4, 2], ["Tomahawks", 2, 1], ["Baseball grenades", 2, 1],
    ["Javelins", 2, 1], ["Frag grenades", 2, 1], ["Frag mine", 1, 1], ["Pulse grenade", 1, 0],
    ["Bottlecap mine", 1, 0], ["Plasma grenade", 1, 0], ["Pulse mine", 1, 0], ["Nuka grenade", 1, 0],
  ],
};

const ROLLS = Array.from({ length: 39 }, (_, i) => i + 2); // 2..40

function defaultTable(cat) {
  const pool = LOOT_POOLS[cat];
  // most likely totals first (21 is the peak of 2d20), then outward
  const order = ROLLS.slice().sort((a, b) => Math.abs(a - 21) - Math.abs(b - 21) || a - b);
  const table = {};
  order.forEach((r, k) => {
    const [name, base, cd] = pool[Math.floor((k * pool.length) / order.length)];
    table[r] = { name, base, cd };
  });
  return table;
}

let LOOT_OVERRIDES = {}; // { category: { roll: {name, base, cd} } }

async function loadLootOverrides() {
  LOOT_OVERRIDES = await Platform.loadJSON("loot_tables", {});
}

function lootTable(cat) {
  return Object.assign(defaultTable(cat), LOOT_OVERRIDES[cat] || {});
}

function lootLookup(cat, roll) {
  return lootTable(cat)[roll] || null;
}

// combat die: 1, 2, 0, 0, 1 (+Effect), 1 (+Effect)
const CD_FACE_VALUE = [1, 2, 0, 0, 1, 1];
function rollCombatDice(n) {
  const faces = [];
  for (let i = 0; i < n; i++) faces.push(1 + Math.floor(Math.random() * 6));
  return { faces, total: faces.reduce((s, f) => s + CD_FACE_VALUE[f - 1], 0) };
}

function quantityText(e) {
  if (!e.cd) return e.base > 1 ? `${e.base}` : "1";
  return `${e.base} + ${e.cd} combat ${e.cd === 1 ? "die" : "dice"}`;
}
