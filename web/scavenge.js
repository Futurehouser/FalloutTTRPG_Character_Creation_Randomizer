// Scavenging location generator.
// Mechanics follow the Core Rulebook's scavenging rules (Degree -> difficulty, Scale -> search time,
// inhabitant counts by Scale). Location ideas, item ranges and hazard/obstacle write-ups are original.

const SCALES = {
  Tiny: { time: "1 minute", inh: null, max: 1 },
  Small: { time: "10 minutes", inh: [1, 3], max: 2 },
  Average: { time: "30 minutes", inh: [3, 6], max: 4 },
  Large: { time: "2 hours", inh: [5, 10], max: 6 },
};
const DEGREES = { "Untouched": 0, "Partly Searched": 1, "Mostly Searched": 2, "Heavily Searched": 3 };

const INHABITANTS = {
  "Animals": ["mole rats", "radroaches", "bloatflies", "radscorpions", "feral mongrel dogs", "stingwings", "mirelurks", "yao guai"],
  "Feral Ghouls": ["feral ghouls lying among old corpses", "a pack of feral ghouls", "feral ghouls led by a glowing one"],
  "Raiders": ["raiders and their mongrel dogs", "a raider gang", "raiders guarding stolen loot"],
  "Super Mutants": ["super mutants and a mutant hound", "a super mutant patrol", "super mutants guarding a meat bag stash"],
  "Robots": ["a protectron on its old patrol route", "a Mister Gutsy still on duty", "eyebots and an auto-turret", "dormant security robots"],
};

const LOCATIONS = [
  { type: "Gas Station", names: ["Red Rocket Station", "Highway 9 Fuel Stop", "Atomic Pumps", "Last Chance Gas"],
    scales: ["Small", "Average"], theme: ["Junk", "Beverages"], extra: ["Food", "Ammunition", "Chems"],
    inh: ["Animals", "Raiders", "Feral Ghouls"], hazards: ["gas", "fuel", "rotten"], nested: ["a locked cash register", "the mechanic's toolbox"] },
  { type: "Clinic", names: ["Mercy Street Clinic", "Vault-Tec Health Point", "Dr. Ferris' Practice", "County Free Clinic"],
    scales: ["Small", "Average", "Large"], theme: ["Chems", "Beverages"], extra: ["Oddities & Valuables", "Clothing", "Food"],
    inh: ["Feral Ghouls", "Raiders", "Robots"], hazards: ["toxic", "rad", "wires"], nested: ["a locked medicine cabinet", "a sealed quarantine room"] },
  { type: "Police Station", names: ["Precinct 12", "Sheriff's Office", "Highway Patrol Post", "Lexington PD"],
    scales: ["Average", "Large"], theme: ["Weapons (Ranged)", "Ammunition", "Armor"], extra: ["Weapons (Melee)", "Chems", "Oddities & Valuables"],
    inh: ["Raiders", "Robots", "Feral Ghouls"], hazards: ["mine", "shotgun", "rotten"], nested: ["the evidence locker", "the armory cage"] },
  { type: "Diner", names: ["Atomic Eats Diner", "Mom's Kitchen", "The Rocket Grill", "Starlight Drive-In Snack Bar"],
    scales: ["Small", "Average"], theme: ["Food", "Beverages"], extra: ["Junk", "Oddities & Valuables"],
    inh: ["Animals", "Feral Ghouls"], hazards: ["gas", "rotten", "toxic"], nested: ["the walk-in freezer", "the owner's safe"] },
  { type: "Suburban House", names: ["a two-story house on Maple Lane", "a burnt-out bungalow", "the Hendricks family home", "a boarded-up ranch house"],
    scales: ["Small", "Average"], theme: ["Clothing", "Junk", "Food"], extra: ["Oddities & Valuables", "Beverages", "Weapons (Melee)", "Chems"],
    inh: ["Animals", "Feral Ghouls", "Raiders"], hazards: ["rotten", "shelving", "wires"], nested: ["a wall safe behind a painting", "a basement fallout shelter"] },
  { type: "Supermarket", names: ["Super-Duper Mart", "Food 'n' Stuff", "Shop-Rite General", "Penny Saver Grocers"],
    scales: ["Average", "Large"], theme: ["Food", "Beverages", "Junk"], extra: ["Chems", "Clothing", "Oddities & Valuables"],
    inh: ["Raiders", "Feral Ghouls", "Animals", "Super Mutants"], hazards: ["shelving", "rotten", "toxic"], nested: ["the pharmacy counter", "the manager's office"] },
  { type: "Military Checkpoint", names: ["Checkpoint Bravo", "Army Roadblock 7", "National Guard Outpost", "Abandoned Army Camp"],
    scales: ["Small", "Average", "Large"], theme: ["Ammunition", "Weapons (Ranged)", "Armor"], extra: ["Weapons (Thrown/Explosives)", "Chems", "Clothing"],
    inh: ["Robots", "Super Mutants", "Raiders"], hazards: ["mine", "shotgun", "rad"], nested: ["an ammo crate", "a locked footlocker"] },
  { type: "Factory", names: ["Corvega Assembly Plant", "General Atomics Workshop", "Nuka-Cola Bottling Annex", "Steel Mill No. 3"],
    scales: ["Average", "Large"], theme: ["Junk", "Weapons (Melee)"], extra: ["Ammunition", "Armor", "Beverages", "Oddities & Valuables"],
    inh: ["Robots", "Raiders", "Super Mutants", "Feral Ghouls"], hazards: ["wires", "toxic", "fuel", "rad"], nested: ["the foreman's office", "a parts storeroom"] },
  { type: "Raider Camp", names: ["the Scrapyard Fort", "Bloody Bridge Camp", "the Tire Pile", "Skull Hill Hideout"],
    scales: ["Average", "Large"], theme: ["Weapons (Melee)", "Ammunition", "Chems"], extra: ["Weapons (Ranged)", "Armor", "Weapons (Thrown/Explosives)", "Beverages"],
    inh: ["Raiders"], hazards: ["shotgun", "mine", "fuel"], nested: ["the boss's footlocker", "a chained-up loot cage"] },
  { type: "School", names: ["Springfield Elementary", "Union High School", "Commonwealth Academy", "Vault-Tec Learning Center"],
    scales: ["Average", "Large"], theme: ["Junk", "Oddities & Valuables"], extra: ["Food", "Chems", "Beverages", "Clothing"],
    inh: ["Feral Ghouls", "Animals", "Raiders"], hazards: ["rotten", "shelving", "toxic"], nested: ["the principal's office", "the chemistry lab"] },
  { type: "Bank", names: ["First Commonwealth Bank", "Capitol Savings & Loan", "Union Trust Bank"],
    scales: ["Small", "Average"], theme: ["Oddities & Valuables"], extra: ["Junk", "Clothing", "Ammunition"],
    inh: ["Robots", "Raiders", "Feral Ghouls"], hazards: ["shotgun", "wires", "rotten"], nested: ["the vault", "a row of safety deposit boxes"] },
  { type: "Farmhouse", names: ["the Abernathy-style homestead", "an abandoned tato farm", "Old Miller's barn", "a mutfruit orchard house"],
    scales: ["Small", "Average"], theme: ["Food", "Beverages"], extra: ["Weapons (Melee)", "Junk", "Clothing", "Ammunition"],
    inh: ["Animals", "Raiders", "Super Mutants"], hazards: ["rotten", "toxic", "shotgun"], nested: ["a root cellar", "the hayloft"] },
  { type: "Radio Station", names: ["Radio Freedom Relay", "WKRT Broadcast Tower", "Galaxy News Annex"],
    scales: ["Small", "Average"], theme: ["Junk", "Oddities & Valuables"], extra: ["Ammunition", "Chems", "Food"],
    inh: ["Super Mutants", "Robots", "Raiders"], hazards: ["wires", "rotten", "rad"], nested: ["the transmitter room", "a terminal-locked archive"] },
  { type: "Subway Station", names: ["Metro Central", "Park Street Station", "Dupont Line Platform"],
    scales: ["Average", "Large"], theme: ["Junk", "Food"], extra: ["Ammunition", "Chems", "Clothing", "Weapons (Melee)"],
    inh: ["Feral Ghouls", "Animals", "Raiders"], hazards: ["rad", "toxic", "rotten"], nested: ["a maintenance tunnel", "a ticket booth safe"] },
  { type: "Vault-Tec Office", names: ["Vault-Tec Regional HQ", "Vault-Tec Sales Office", "Vault 81 Recruitment Booth"],
    scales: ["Small", "Average", "Large"], theme: ["Oddities & Valuables", "Clothing"], extra: ["Chems", "Junk", "Food", "Beverages"],
    inh: ["Robots", "Feral Ghouls"], hazards: ["wires", "rad", "shelving"], nested: ["the records room", "an executive's terminal-locked desk"] },
];

const HAZARDS = {
  rad: { kind: "Ongoing", name: "Lingering radiation", text: "Everyone inside suffers 1 combat die of Radiation damage per 10 minutes. Total it up at the end instead of rolling every 10 minutes." },
  toxic: { kind: "Ongoing", name: "Toxic fumes", text: "Leaking chemicals: 1 combat die of Poison damage per 10 minutes inside. A gas mask negates it." },
  fuel: { kind: "Occasional", name: "Spilled fuel", text: "A complication or a stray shot ignites it: 6 combat dice of Energy (fire) damage to everyone nearby." },
  gas: { kind: "Occasional", name: "Leaking gas line", text: "A spark on a failed test or a complication causes an explosion: 5 combat dice of Energy damage." },
  rotten: { kind: "Occasional", name: "Rotten floors", text: "On a complication the floor gives way: 4 combat dice of Physical damage and a fall into the level below." },
  wires: { kind: "Occasional", name: "Live wiring", text: "Exposed cables still carry power. A failed search test means a shock: 4 combat dice of Energy damage." },
  shelving: { kind: "Occasional", name: "Unstable shelving", text: "Heavy shelves topple on a complication: 3 combat dice of Physical damage." },
  shotgun: { kind: "Occasional (trap)", name: "Tripwire shotgun", text: "Spot it with a PER test. Disarm with AGI + Small Guns, difficulty 2, or take 5 combat dice of Physical damage." },
  mine: { kind: "Occasional (trap)", name: "Frag mine in a doorway", text: "Disarm with AGI + Explosives, difficulty 2, or it explodes for 6 combat dice of Physical damage." },
};

function makeObstacle(level) {
  const diff = Math.min(4, Math.max(1, Math.round(level / 3) + randint(0, 1)));
  return choice([
    { name: "Locked door / padlock", test: `PER + Lockpick, difficulty ${diff}`, alt: "A key or a strong crowbar (STR + Athletics, difficulty " + (diff + 1) + ", noisy)" },
    { name: "Terminal-controlled security door", test: `INT + Science, difficulty ${diff}`, alt: "A password found elsewhere opens it instantly" },
    { name: "Collapsed section", test: `STR or AGI + Athletics, difficulty ${diff}`, alt: `Scout another way in with PER + Survival, difficulty ${Math.max(1, diff - 1)}` },
  ].map(o => Object.assign(o, { time: `${diff * 10} minutes (2 AP halves it)` })));
}

function itemRanges(loc, scale, degree, raiders) {
  const cut = { "Untouched": -1, "Partly Searched": 0, "Mostly Searched": 1, "Heavily Searched": 2 }[degree];
  const maxBase = Math.max(1, SCALES[scale].max - cut);
  const themeMin = Math.max(0, { Tiny: 1, Small: 1, Average: randint(1, 2), Large: 2 }[scale] - Math.max(0, cut));
  const items = [];
  const theme = loc.theme.slice();
  if (!theme.includes("Junk")) theme.push("Junk");
  theme.forEach(c => items.push({ cat: c, min: Math.min(themeMin, maxBase), max: maxBase }));
  sample(loc.extra, randint(1, 2)).forEach(c =>
    items.push({ cat: c, min: 0, max: Math.max(1, Math.ceil(maxBase / 2)) }));
  if (raiders) items.forEach(i => {
    if (/Weapons|Ammunition|Chems/.test(i.cat)) i.max += 1;
  });
  return items;
}

function generateLocation(opts = {}) {
  const loc = choice(LOCATIONS);
  const partyLevel = opts.level ? +opts.level : randint(1, 8);
  const level = Math.max(1, partyLevel + randint(-1, 2));
  const scale = opts.scale && opts.scale !== "Random" ? opts.scale : choice(loc.scales);
  const degree = opts.degree && opts.degree !== "Random"
    ? opts.degree : wpick(Object.keys(DEGREES), [1, 4, 4, 2]);

  const out = { type: loc.type, name: choice(loc.names), level, scale, degree,
                difficulty: DEGREES[degree], time: SCALES[scale].time };

  // inhabitants
  const inhChance = { Tiny: 0, Small: 0.4, Average: 0.6, Large: 0.8 }[scale];
  if (rnd() < inhChance) {
    const group = choice(loc.inh);
    const [lo, hi] = SCALES[scale].inh;
    const count = randint(lo, hi);
    const lvl = Math.max(1, level - randint(0, 2));
    out.inhabitants = { group, desc: choice(INHABITANTS[group]), count, level: lvl,
                        leader: rnd() < 0.5 ? Math.min(level + 2, level + randint(0, 2)) : null };
  }
  out.items = itemRanges(loc, scale, degree, out.inhabitants && out.inhabitants.group === "Raiders");
  if (rnd() < 0.5) out.obstacle = makeObstacle(level);
  if (rnd() < 0.55) out.hazard = HAZARDS[choice(loc.hazards)];
  if (scale !== "Tiny" && scale !== "Small" ? rnd() < 0.5 : rnd() < 0.2) {
    const cats = sample(loc.theme.concat(["Oddities & Valuables", "Ammunition"]), 2).filter((c, i, a) => a.indexOf(c) === i);
    out.nested = { name: choice(loc.nested), level: level + randint(1, 2),
                   scale: "Tiny", degree: "Untouched", items: cats.map(c => ({ cat: c, min: 1, max: 2 })),
                   lock: makeObstacle(level + 2) };
  }
  out.complications = sample([
    "There's less here than it looked: the location can't be searched again until something changes.",
    "The search drags on: add half the search time again.",
    "More inhabitants arrive, or ones that were hiding wake up.",
    "Someone disturbs the place and sets off its hazard.",
    "One item the players earned is locked away behind an obstacle.",
    "Rival scavengers show up wanting the same loot.",
  ], 3);
  return out;
}
