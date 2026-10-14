// Enemy templates for the combat assistant.
// The FORMULAS follow the rulebook's NPC rules (creature HP = Body + Level, x2 Mighty, x3 Legendary;
// character HP = END + Level, +LCK Notable, +2xLCK Major; initiative; XP by level and type;
// caps = rolls of d20 equal to the NPC's wealth). The individual NUMBERS below are this app's own
// estimates, not the book's stat blocks: add the book's enemies with "Add your own enemy".

const XP_BY_LEVEL = [10, 17, 24, 31, 38, 45, 52, 60, 67, 74, 81, 88, 95, 102, 109, 116, 123, 130, 137, 144];
const XP_MULT = { Normal: 1, Mighty: 2, Notable: 2, Legendary: 3, Major: 3 };
function xpFor(level, type) {
  const base = level <= 20 ? XP_BY_LEVEL[Math.max(1, level) - 1] : 144 + 7 * (level - 20);
  return base * (XP_MULT[type] || 1);
}

const IMM = "Imm";
function creature(o) {
  const mult = { Normal: 1, Mighty: 2, Legendary: 3 }[o.type] || 1;
  return Object.assign({ kind: "creature", def: 1, wealth: 0, junk: 0, dr: { p: 0, e: 0, r: 0, po: 0 } }, o, {
    hp: (o.body + o.level) * mult,
    init: o.body + o.mind,
  });
}
function character(o) {
  const s = o.special;
  const extraHp = o.type === "Notable" ? s.LCK : o.type === "Major" ? 2 * s.LCK : 0;
  const extraInit = o.type === "Notable" ? 2 : o.type === "Major" ? 4 : 0;
  return Object.assign({ kind: "character", wealth: 1, junk: 1, dr: { p: 0, e: 0, r: 0, po: 0 } }, o, {
    hp: s.END + o.level + extraHp,
    init: s.PER + s.AGI + extraInit,
    def: s.AGI >= 9 ? 2 : 1,
    meleeBonus: s.STR >= 11 ? 3 : s.STR >= 9 ? 2 : s.STR >= 7 ? 1 : 0,
  });
}
// attack: name, tn, crit (crit range = skill rank for tagged skills), cd, type p|e|r|po, eff list, ranged, rate, ammo
const atk = (name, tn, crit, cd, type, eff = [], extra = {}) => Object.assign({ name, tn, crit, cd, type, eff, ranged: false, rate: 0 }, extra);

const ENEMY_TEMPLATES = [
  // ---- animals & insects
  creature({ id: "radroach", name: "Radroach", group: "Animals & insects", level: 1, type: "Normal", body: 5, mind: 4, def: 2,
    dr: { p: 0, e: 0, r: IMM, po: 0 }, attacks: [atk("Bite", 7, 2, 2, "p")], butchery: "Radroach meat (END + Survival, difficulty 1)" }),
  creature({ id: "bloatfly", name: "Bloatfly", group: "Animals & insects", level: 2, type: "Normal", body: 4, mind: 5, def: 2,
    dr: { p: 0, e: 0, r: IMM, po: 0 }, attacks: [atk("Larva spit", 6, 2, 2, "p", ["Radioactive"], { ranged: true, rate: 1, range: "M" })],
    butchery: "Bloatfly gland (END + Survival, difficulty 1)" }),
  creature({ id: "molerat", name: "Mole Rat", group: "Animals & insects", level: 3, type: "Normal", body: 6, mind: 4,
    dr: { p: 1, e: 0, r: 0, po: 0 }, attacks: [atk("Bite", 8, 2, 3, "p")], butchery: "Mole rat meat (END + Survival, difficulty 1)" }),
  creature({ id: "mongrel", name: "Feral Mongrel Dog", group: "Animals & insects", level: 3, type: "Normal", body: 6, mind: 4,
    dr: { p: 1, e: 0, r: 0, po: 0 }, attacks: [atk("Bite", 9, 3, 3, "p", ["Vicious"])], butchery: "Dog meat (END + Survival, difficulty 1)" }),
  creature({ id: "mirelurk", name: "Mirelurk", group: "Animals & insects", level: 6, type: "Mighty", body: 8, mind: 5,
    dr: { p: 4, e: 2, r: IMM, po: 0 }, attacks: [atk("Claws", 11, 3, 5, "p")], butchery: "Mirelurk meat and eggs (END + Survival, difficulty 2)" }),
  creature({ id: "radscorpion", name: "Radscorpion", group: "Animals & insects", level: 8, type: "Mighty", body: 9, mind: 5,
    dr: { p: 3, e: 2, r: IMM, po: IMM }, attacks: [atk("Pincers", 12, 3, 4, "p"), atk("Stinger", 12, 3, 5, "po", ["Persistent"])],
    butchery: "Radscorpion meat and poison gland (END + Survival, difficulty 2)" }),
  creature({ id: "yaoguai", name: "Yao Guai", group: "Animals & insects", level: 10, type: "Mighty", body: 10, mind: 5,
    dr: { p: 2, e: 2, r: 2, po: 0 }, attacks: [atk("Claws", 14, 4, 6, "p", ["Vicious"])], butchery: "Yao guai meat and hide (END + Survival, difficulty 2)" }),
  creature({ id: "deathclaw", name: "Deathclaw", group: "Animals & insects", level: 15, type: "Legendary", body: 12, mind: 8,
    dr: { p: 6, e: 5, r: 4, po: 0 }, attacks: [atk("Claws", 17, 5, 8, "p", ["Piercing 1", "Vicious"])],
    butchery: "Deathclaw meat and hand (END + Survival, difficulty 3)" }),
  // ---- mutated humanoids
  creature({ id: "feral", name: "Feral Ghoul", group: "Mutated humanoids", level: 4, type: "Normal", body: 6, mind: 4,
    dr: { p: 1, e: 1, r: IMM, po: 0 }, attacks: [atk("Claws", 8, 2, 3, "p", ["Radioactive"])], junk: 1 }),
  creature({ id: "glowing", name: "Glowing One", group: "Mutated humanoids", level: 8, type: "Mighty", body: 8, mind: 6,
    dr: { p: 2, e: 2, r: IMM, po: 0 }, attacks: [atk("Glowing claws", 11, 3, 4, "p", ["Radioactive", "Vicious"])], junk: 1 }),
  character({ id: "supermutant", name: "Super Mutant", group: "Mutated humanoids", level: 6, type: "Normal",
    special: { STR: 9, PER: 5, END: 9, CHA: 3, INT: 3, AGI: 5, LCK: 4 }, dr: { p: 2, e: 1, r: IMM, po: IMM },
    attacks: [atk("Board", 12, 3, 6, "p"), atk("Pipe rifle", 7, 2, 3, "p", [], { ranged: true, rate: 2, range: "C", ammo: ".38 rounds" })],
    inventory: ["Pipe rifle", "Board", "Meat bag"] }),
  character({ id: "brute", name: "Super Mutant Brute", group: "Mutated humanoids", level: 9, type: "Notable",
    special: { STR: 10, PER: 6, END: 10, CHA: 4, INT: 4, AGI: 6, LCK: 7 }, dr: { p: 3, e: 2, r: IMM, po: IMM }, wealth: 2,
    attacks: [atk("Sledgehammer", 14, 4, 7, "p", ["Breaking"]), atk("Hunting rifle", 9, 3, 6, "p", ["Piercing 1"], { ranged: true, rate: 0, range: "M", ammo: ".308 rounds" })],
    inventory: ["Sledgehammer", "Hunting rifle", "Spike armor"] }),
  // ---- robots
  creature({ id: "eyebot", name: "Eyebot", group: "Robots", level: 2, type: "Normal", body: 4, mind: 5, def: 2,
    dr: { p: 2, e: 2, r: IMM, po: IMM }, attacks: [atk("Laser", 6, 2, 3, "e", ["Piercing 1"], { ranged: true, rate: 2, range: "M" })],
    salvage: "1 uncommon material (INT + Repair, difficulty 1)" }),
  creature({ id: "protectron", name: "Protectron", group: "Robots", level: 5, type: "Normal", body: 6, mind: 5,
    dr: { p: 3, e: 2, r: IMM, po: IMM }, attacks: [atk("Head laser", 8, 2, 4, "e", ["Piercing 1"], { ranged: true, rate: 1, range: "M" }), atk("Punch", 7, 1, 3, "p")],
    salvage: "Circuitry and 2 common materials (INT + Repair, difficulty 1)" }),
  creature({ id: "gutsy", name: "Mister Gutsy", group: "Robots", level: 8, type: "Mighty", body: 8, mind: 6,
    dr: { p: 4, e: 3, r: IMM, po: IMM }, attacks: [atk("10mm auto pistol", 11, 3, 4, "p", ["Burst"], { ranged: true, rate: 4, range: "C" }),
      atk("Flamer", 11, 3, 3, "e", ["Persistent", "Spread"], { ranged: true, rate: 4, range: "C" })],
    salvage: "Fusion cell, circuitry and military-grade parts (INT + Repair, difficulty 2)" }),
  creature({ id: "assaultron", name: "Assaultron", group: "Robots", level: 12, type: "Mighty", body: 10, mind: 6,
    dr: { p: 4, e: 4, r: IMM, po: IMM }, attacks: [atk("Claws", 14, 4, 5, "p", ["Piercing 1", "Vicious"]),
      atk("Head laser", 13, 3, 8, "e", ["Piercing 2"], { ranged: true, rate: 0, range: "M" })],
    salvage: "Rare circuitry and a fusion core (INT + Repair, difficulty 3)" }),
  // ---- people
  character({ id: "scavenger", name: "Hostile Scavenger", group: "People", level: 1, type: "Normal",
    special: { STR: 5, PER: 6, END: 5, CHA: 5, INT: 5, AGI: 6, LCK: 4 }, dr: { p: 1, e: 1, r: 0, po: 0 },
    attacks: [atk("10mm pistol", 8, 2, 4, "p", [], { ranged: true, rate: 2, range: "C", ammo: "10mm rounds" }), atk("Switchblade", 7, 2, 2, "p", ["Piercing 1"])],
    inventory: ["10mm pistol", "Switchblade", "Tough clothing"] }),
  character({ id: "raider", name: "Raider", group: "People", level: 2, type: "Normal",
    special: { STR: 6, PER: 5, END: 5, CHA: 4, INT: 4, AGI: 6, LCK: 6 }, dr: { p: 1, e: 1, r: 0, po: 0 },
    attacks: [atk("Pipe gun", 8, 2, 3, "p", [], { ranged: true, rate: 2, range: "C", ammo: ".38 rounds" }), atk("Lead pipe", 8, 2, 3, "p")],
    inventory: ["Pipe gun", "Lead pipe", "Raider chest piece"] }),
  character({ id: "gunner", name: "Gunner Mercenary", group: "People", level: 5, type: "Normal",
    special: { STR: 5, PER: 7, END: 6, CHA: 4, INT: 5, AGI: 7, LCK: 4 }, dr: { p: 2, e: 1, r: 0, po: 0 }, wealth: 2,
    attacks: [atk("Hunting rifle", 10, 3, 6, "p", ["Piercing 1"], { ranged: true, rate: 0, range: "M", ammo: ".308 rounds" }), atk("Combat knife", 7, 2, 3, "p", ["Piercing 1"])],
    inventory: ["Hunting rifle", "Combat knife", "Leather chest piece"] }),
  character({ id: "raiderboss", name: "Raider Boss", group: "People", level: 6, type: "Notable",
    special: { STR: 7, PER: 6, END: 7, CHA: 6, INT: 5, AGI: 7, LCK: 7 }, dr: { p: 2, e: 2, r: 0, po: 0 }, wealth: 3, junk: 2,
    attacks: [atk(".44 pistol", 10, 3, 6, "p", ["Vicious"], { ranged: true, rate: 1, range: "C", ammo: ".44 Magnum rounds" }), atk("Machete", 10, 3, 4, "p", ["Piercing 1"])],
    inventory: [".44 pistol", "Machete", "Sturdy raider chest piece", "Jet"] }),
];

const EFFECT_NAMES = ["Burst", "Breaking", "Persistent", "Piercing", "Radioactive", "Spread", "Stun", "Vicious"];
