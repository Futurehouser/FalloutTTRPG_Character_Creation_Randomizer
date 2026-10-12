"""Builds a random level-1 character following the Core Rulebook's six creation steps."""
import random

from gamedata import (SPECIAL, SKILLS, SKILL_ATTR, SKILL_NAMES, WEAPONS, ARM_WEAPON, APPAREL,
                      ROBOT_PLATING, TRINKETS, PERKS, ARCHETYPES, ORIGINS, PACK_AFFINITY,
                      ORIGIN_TRAITS, SURVIVOR_TRAITS, HUMAN_FIRST, HUMAN_LAST, GHOUL_FIRST,
                      GHOUL_LAST, GHOUL_NICK, MUTANT_NAMES, MUTANT_TITLES, ROBOT_NAMES,
                      ROBOT_TITLES, EPITHETS, HIGH_LINES, LOW_LINES, PERK_LINES, ORIGIN_LINES)

LOCS = ["head", "larm", "rarm", "torso", "lleg", "rleg"]
CD_FACES = [1, 2, 0, 0, 1, 1]  # combat die: 1, 2, blank, blank, 1+Effect, 1+Effect


def roll_cd(n):
    return sum(random.choice(CD_FACES) for _ in range(n))


def wpick(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


class Character:
    def __init__(self):
        self.notes = []          # creation notes shown in the dossier band
        self.gear = []           # [name, weight]
        self.ammo = {}           # caliber -> qty
        self.weapons = []        # weapon names
        self.worn = []           # apparel names
        self.plating = None
        self.arms = []
        self.caps = 0
        self.perks = []          # [name, rank]
        self.traits = []         # [name, effect]
        self.extra_tags = []


def generate():
    c = Character()
    c.origin = random.choice(list(ORIGINS))
    o = ORIGINS[c.origin]
    c.race = o["race"]
    c.archetype = random.choice(o["arch"])
    aw, sw, _ = ARCHETYPES[c.archetype]

    # equipment pack chosen early so the build is coherent with it
    c.pack = wpick(o["packs"], [4 if c.archetype in PACK_AFFINITY[p] else 1 for p in o["packs"]])

    # gender / persona
    if c.race == "robot":
        c.gender = "F" if c.pack == "Miss Nanny" else "M"
    else:
        c.gender = random.choice("MF")
    c.no_pincer = False

    # ---- Step 1: origin & Survivor traits
    c.survivor_traits = []
    c.bonus_perk = False
    if c.origin == "Survivor":
        if random.random() < 0.35:
            c.survivor_traits = [random.choice(list(SURVIVOR_TRAITS))]
            c.bonus_perk = True
        else:
            c.survivor_traits = random.sample(list(SURVIVOR_TRAITS), 2)

    # ---- Step 2: S.P.E.C.I.A.L.
    c.special = {a: 5 for a in SPECIAL}
    cap = {a: 10 for a in SPECIAL}
    if c.race == "mutant":
        c.special["STR"] += 2
        c.special["END"] += 2
        cap.update(STR=12, END=12, INT=6, CHA=6)
    points = 5
    weights = {a: aw.get(a, 0) + 1 for a in SPECIAL}
    # optionally lower a weak attribute from 5 to 4 to buy another point
    for _ in range(random.choice([0, 1, 1, 2])):
        cands = [a for a in SPECIAL if c.special[a] == 5 and aw.get(a, 0) == 0]
        if cands:
            c.special[random.choice(cands)] = 4
            points += 1
    while points:
        opts = [a for a in SPECIAL if c.special[a] < cap[a]]
        a = wpick(opts, [weights[x] ** 2 for x in opts])
        c.special[a] += 1
        points -= 1
    if "Gifted" in c.survivor_traits:
        opts = [a for a in SPECIAL if c.special[a] < cap[a]]
        for a in random.sample(sorted(opts, key=lambda x: -weights[x])[:4], 2):
            c.special[a] += 1

    # ---- Mister Handy arms (affects which skills make sense)
    if c.race == "robot":
        attach = list(ARM_WEAPON)
        if c.pack == "Miss Nanny":
            c.arms = ["Pincer", "Flamer", random.choice([x for x in attach if x not in ("Pincer", "Flamer")])]
        elif c.pack == "Mister Farmhand":
            c.arms = ["Pincer", "Buzz-Saw", "Laser Emitter"]
        elif c.pack == "Mister Gutsy":
            c.arms = ["10mm Auto Pistol", "Buzz-Saw", "Laser Emitter"]
            c.no_pincer = True
        elif c.pack == "Mister Handy":
            c.arms = ["Pincer", "Flamer", "Buzz-Saw"]
        else:  # Nurse Handy
            first = random.choice(["Pincer", "Buzz-Saw"])
            c.arms = [first, "Buzz-Saw", random.choice([x for x in attach if x not in (first, "Buzz-Saw")])]
        if "Pincer" not in c.arms:
            c.no_pincer = True

    # ---- Step 3: tag skills & ranks
    banned = set()
    if c.no_pincer:
        banned |= {"Lockpick", "Repair", "Throwing", "Unarmed"}
    skw = {s: sw.get(s, 0) * 3 + 1 for s in SKILL_NAMES}
    for s in banned:
        skw[s] = 0

    def pick_tags(n, pool):
        chosen = []
        for _ in range(n):
            opts = [s for s in pool if s not in chosen and skw[s] > 0]
            chosen.append(wpick(opts, [skw[s] ** 2 for s in opts]))
        return chosen

    c.tags = []
    if c.origin == "Brotherhood Initiate":
        c.tags += pick_tags(1, ["Energy Weapons", "Science", "Repair"])
        c.extra_tags = list(c.tags)
    if c.origin == "Ghoul":
        c.tags.append("Survival")
        c.extra_tags = ["Survival"]
    core = pick_tags(3, [s for s in SKILL_NAMES if s not in c.tags])
    c.tags += core
    extra_n = (1 if c.origin == "Vault Dweller" else 0) + (1 if "Educated" in c.survivor_traits else 0)
    if extra_n:
        more = pick_tags(extra_n, [s for s in SKILL_NAMES if s not in c.tags])
        c.tags += more
        c.extra_tags += more

    c.skills = {s: 0 for s in SKILL_NAMES}
    for s in c.tags:
        c.skills[s] = 2
    max_rank = 3  # creation limit (super mutants are capped at 4 anyway)
    c.skill_points = 9 + c.special["INT"]
    pts = c.skill_points
    while pts:
        opts = [s for s in SKILL_NAMES if c.skills[s] < max_rank and skw[s] > 0]
        if not opts:
            break
        s = wpick(opts, [skw[x] * (2 if x in c.tags else 1) for x in opts])
        c.skills[s] += 1
        pts -= 1

    # ---- Step 4: perk(s)
    c.perks = []
    n_perks = 2 if c.bonus_perk else 1
    fav = ARCHETYPES[c.archetype][2]
    for _ in range(n_perks):
        p = choose_perk(c, fav)
        if p:
            c.perks.append([p, 1])

    # ---- Step 6: equipment (before derived stats, since armor changes DR)
    equip(c)

    # ---- Step 5: derived statistics
    derive(c)

    # ---- identity & gimmick
    name(c)
    gimmick(c)
    return c


def perk_ok(c, name):
    ranks, req, flags, _ = PERKS[name]
    if any(c.special[a] < v for a, v in req.items()):
        return False
    if flags.get("gender") and flags["gender"] != c.gender:
        return False
    if flags.get("robot_no") and c.race == "robot":
        return False
    if flags.get("pain_train") and c.race != "mutant":
        return False
    taken = [p for p, _ in c.perks]
    if name in taken or flags.get("excl") in taken:
        return False
    return True


def choose_perk(c, fav):
    opts = [p for p in PERKS if perk_ok(c, p)]
    if not opts:
        return None
    return wpick(opts, [12 if p in fav else 1 for p in opts])


def add_gear(c, item, wt="-"):
    c.gear.append([item, wt])


def add_ammo(c, cal, base, cd):
    c.ammo[cal] = c.ammo.get(cal, 0) + base + roll_cd(cd)


def equip(c):
    p = c.pack
    trinket = False
    arch = c.archetype
    if p == "Brotherhood Initiate":
        c.worn += ["Brotherhood Fatigues", "Brotherhood Hood"]
        c.weapons.append("Combat Knife")
        if arch == "Laser Jockey" or random.random() < 0.5:
            c.weapons.append("Laser Pistol"); add_ammo(c, "Fusion Cell", 10, 5)
        else:
            c.weapons.append("10mm Pistol"); add_ammo(c, "10mm", 10, 5)
        add_gear(c, "Brotherhood holotags", "<1")
    elif p == "Brotherhood Scribe":
        c.worn += ["Brotherhood Scribe's Armor", "Brotherhood Scribe's Hat"]
        c.weapons.append("Combat Knife")
        if random.random() < 0.6:
            c.weapons.append("Laser Pistol"); add_ammo(c, "Fusion Cell", 6, 3)
        else:
            c.weapons.append("10mm Pistol"); add_ammo(c, "10mm", 6, 3)
        add_gear(c, "Brotherhood holotags", "<1")
    elif c.race == "robot":
        c.plating = "Mister Gutsy Plating" if p == "Mister Gutsy" else "Standard Plating"
        for a in c.arms:
            w = ARM_WEAPON[a]
            c.weapons.append(w)
            if WEAPONS[w]["ammo"]:
                add_ammo(c, WEAPONS[w]["ammo"], 20, 0)
        c.caps += 25 if p == "Mister Farmhand" else 10
        extras = {
            "Miss Nanny": ["Behavioral analysis mod", "Hazard detection mod"],
            "Mister Farmhand": ["Bag of fertilizer", "Mutfruit", "Mutfruit"],
            "Mister Gutsy": ["Recon sensors mod"],
            "Mister Handy": ["Robot repair kit", "Integral boiler mod"],
            "Nurse Handy": ["Stimpak", "Diagnosis mod"],
        }[p]
        for e in extras:
            add_gear(c, e, "<1" if e in ("Stimpak", "Mutfruit") else "-")
    elif p == "Brute" or p == "Skirmisher":
        c.worn.append("Raider Chest Piece")
        c.worn.append(random.choice(["Raider Head Armor", "Raider Leg (L)", "Raider Arm (L)"]))
        if p == "Brute":
            c.weapons.append("Pipe Rifle"); add_ammo(c, ".38", 6, 3)
            c.weapons.append(random.choice(["Baseball Bat", "Machete"]))
        else:
            c.weapons.append("Heavy Pipe Bolt-Action"); add_ammo(c, ".308", 8, 4)
            c.weapons.append("Board")
        trinket = True
        c.caps += 5
    elif p == "Vault-Tec Resident":
        c.worn.append("Vault Jumpsuit")
        add_gear(c, "Vault-Tec canteen (1 Purified Water)", 1)
        add_gear(c, "Pip-Boy")
        c.weapons += ["10mm Pistol", "Switchblade"]
        add_ammo(c, "10mm", 6, 3)
        add_gear(c, "Stimpak", "<1"); add_gear(c, "Stimpak", "<1")
        c.caps += 10
    elif p == "Vault-Tec Security":
        c.worn += ["Vault Jumpsuit", "Vault-Tec Security Armor", "Vault-Tec Security Helmet"]
        add_gear(c, "Vault-Tec canteen (1 Purified Water)", 1)
        add_gear(c, "Pip-Boy")
        c.weapons += ["10mm Pistol", "Baton"]
        add_ammo(c, "10mm", 8, 4)
        add_gear(c, "Stimpak", "<1")
    elif p == "Mercenary":
        c.worn.append("Tough Clothing")
        if random.random() < 0.5:
            c.worn.append("Leather Chest Piece")
        else:
            c.worn += [random.choice(["Leather Arm (L)", "Leather Arm (R)"]),
                       random.choice(["Leather Leg (L)", "Leather Leg (R)"])]
        rng = {"Sharpshooter": ["Hunting Rifle", "Pipe Bolt-Action"],
               "Gunslinger": ["10mm Pistol", ".44 Pistol"]}.get(
            arch, ["10mm Pistol", ".44 Pistol", "Hunting Rifle", "Pipe Bolt-Action"])
        gun = random.choice(rng)
        c.weapons.append(gun); add_ammo(c, WEAPONS[gun]["ammo"], 10, 5)
        c.weapons.append(random.choice(["Machete", "Baseball Bat", "Tire Iron"]))
        add_gear(c, "Job notice (pays 50 caps)", "-")
        c.caps += 15
    elif p == "Raider":
        c.worn += ["Harness", "Raider Chest Piece", random.choice(["Raider Arm (L)", "Raider Arm (R)"])]
        c.weapons.append(random.choice(["Lead Pipe", "Pool Cue", "Tire Iron"]))
        c.weapons.append("Pipe Gun"); add_ammo(c, ".38", 10, 5)
        add_gear(c, random.choice(["Jet", "RadAway"]), "<1")
        if random.random() < 0.5:
            c.weapons.append("Molotov Cocktail"); c.ammo["Molotov"] = c.ammo.get("Molotov", 0) + 1
        else:
            add_gear(c, "Stimpak", "<1")
        c.caps += 15
    elif p == "Settler":
        c.worn.append("Tough Clothing")
        c.weapons.append(random.choice(["Switchblade", "Pipe Wrench", "Rolling Pin", "Knuckles"]))
        c.weapons.append("Pipe Gun"); add_ammo(c, ".38", 6, 3)
        add_gear(c, "Food x2 (roll random food table)", "-")
        trinket = True
        c.caps += 45
    elif p == "Trader":
        c.worn.append("Tough Clothing")
        if random.random() < 0.5:
            c.worn.append("Leather Chest Piece")
        else:
            c.worn += ["Leather Arm (L)", "Leather Leg (R)"]
        c.weapons.append("Pipe Gun"); add_ammo(c, ".38", 8, 4)
        trinket = True
        add_gear(c, "Wares: 3 rolls each ammo/aid/junk", "-")
        add_gear(c, "Pack brahmin (carries the wares)", "-")
        c.caps += 50
    elif p == "Wanderer":
        c.worn.append("Drifter Outfit")
        c.weapons.append(random.choice(["Switchblade", "Pipe Wrench", "Rolling Pin", "Knuckles"]))
        c.weapons.append("Pipe Gun"); add_ammo(c, ".38", 8, 4)
        add_gear(c, random.choice(["Jet", "RadAway"]), "<1")
        trinket = True
        c.caps += 30

    if trinket:
        c.trinket = random.choice(TRINKETS)
        add_gear(c, c.trinket + " (trinket)", "<1")
    else:
        c.trinket = None

    # tag skill items
    for s in c.tags:
        if s == "Athletics":
            add_gear(c, "Casual clothing", 2); add_gear(c, "Buffout", "<1")
        elif s == "Barter":
            bonus = random.randint(1, 20) + random.randint(1, 20)
            c.caps += bonus
            c.notes.append(f"Barter tag: +{bonus} caps (2d20).")
        elif s == "Big Guns":
            add_ammo(c, "Flamer Fuel", 4, 2)
        elif s == "Energy Weapons":
            add_ammo(c, "Fusion Cell", 6, 3)
        elif s == "Explosives":
            if random.random() < 0.5:
                if "Molotov Cocktail" not in c.weapons:
                    c.weapons.append("Molotov Cocktail")
                c.ammo["Molotov"] = c.ammo.get("Molotov", 0) + 2
            else:
                c.weapons.append("Baseball Grenade"); c.ammo["Baseball Grenade"] = 2
        elif s == "Lockpick":
            add_ammo(c, "Bobby Pins", 4, 2)
        elif s == "Medicine":
            add_gear(c, "First aid kit"); add_gear(c, "Stimpak", "<1")
        elif s == "Melee Weapons":
            m = random.choice(["Machete", "Baseball Bat"])
            if m in c.weapons:
                m = "Machete" if m == "Baseball Bat" else "Baseball Bat"
            c.weapons.append(m)
        elif s == "Pilot":
            add_gear(c, "Broken car parts (5 common scrap)")
        elif s == "Repair":
            add_gear(c, "Multi-Tool")
        elif s == "Science":
            add_gear(c, "Lab coat", 2); add_gear(c, "Mentats", "<1")
        elif s == "Small Guns":
            cals = [WEAPONS[w]["ammo"] for w in c.weapons if WEAPONS[w]["skill"] == "Small Guns"]
            if cals:
                add_ammo(c, random.choice(cals), 6, 3)
            else:
                c.notes.append("Small Guns tag: 6+3 CD ammo once you own a gun.")
        elif s == "Sneak":
            add_gear(c, "Calmex", "<1")
        elif s == "Speech":
            add_gear(c, "Formal hat", "<1"); add_gear(c, "Formal clothing", 2)
        elif s == "Survival":
            add_gear(c, "Purified water", 1); add_gear(c, "Purified water", 1)
            add_gear(c, "Iguana on a stick", "<1")
        elif s == "Throwing":
            if random.random() < 0.5:
                c.weapons.append("Throwing Knives"); add_ammo(c, "Throwing Knives", 4, 2)
            else:
                c.weapons.append("Tomahawks"); add_ammo(c, "Tomahawks", 2, 1)
        elif s == "Unarmed":
            if c.race != "robot":
                c.weapons.append("Knuckles")
            else:
                add_gear(c, "Knuckles", "<1")

    if c.race != "robot" and not any(WEAPONS[w]["skill"] == "Unarmed" for w in c.weapons):
        c.weapons.append("Unarmed Strike")
    # keep at most 5 weapons on the sheet, prefer the ones matching tags
    if len(c.weapons) > 5:
        c.weapons.sort(key=lambda w: (WEAPONS[w]["skill"] not in c.tags, w == "Unarmed Strike"))
        for w in c.weapons[5:]:
            add_gear(c, w, WEAPONS[w]["wt"])
        c.weapons = c.weapons[:5]


def num(w):
    return w if isinstance(w, (int, float)) else 0


def derive(c):
    s = c.special
    perk_names = [p for p, _ in c.perks]
    # carry weight
    if c.race == "robot":
        c.carry_max = 150 + ROBOT_PLATING[c.plating]["carry"]
    elif "Small Frame" in c.survivor_traits:
        c.carry_max = 150 + 5 * s["STR"]
    else:
        c.carry_max = 150 + 10 * s["STR"]
    if "Strong Back" in perk_names and c.race != "robot":
        c.carry_max += 25
    c.defense = 2 if s["AGI"] >= 9 else 1
    c.initiative = s["PER"] + s["AGI"]
    c.hp = s["END"] + s["LCK"]
    c.melee_bonus = 0 if s["STR"] <= 6 else 1 if s["STR"] <= 8 else 2 if s["STR"] <= 10 else 3
    if "Heavy Handed" in c.survivor_traits:
        c.melee_bonus += 1
    c.luck_points = s["LCK"] - (1 if "Gifted" in c.survivor_traits else 0)

    # damage resistances per location
    c.dr = {l: {"p": 0, "e": 0, "r": 0} for l in LOCS}
    if c.race == "robot":
        pl = ROBOT_PLATING[c.plating]
        for l in LOCS:
            c.dr[l]["p"] += pl["p"]; c.dr[l]["e"] += pl["e"]
    for item in c.worn:
        a = APPAREL[item]
        for l in a["locs"]:
            c.dr[l]["p"] += a["p"]; c.dr[l]["e"] += a["e"]; c.dr[l]["r"] += a["r"]
    bonus = {"Toughness": "p", "Refractor": "e", "Rad Resistance": "r"}
    for p in perk_names:
        if p in bonus:
            for l in LOCS:
                c.dr[l][bonus[p]] += 1
    c.rad_immune = c.race in ("ghoul", "mutant", "robot")
    c.poison_immune = c.race in ("mutant", "robot")
    c.poison_dr = 2 if "Snakeater" in perk_names else 0

    # current load
    load = sum(num(APPAREL[i]["wt"]) for i in c.worn)
    load += sum(num(WEAPONS[w]["wt"]) for w in c.weapons)
    load += sum(num(w) for _, w in c.gear)
    c.carry_now = load


def name(c):
    g = c.gender
    if c.race == "human":
        first = random.choice(HUMAN_FIRST[g])
        last = random.choice([x for x in HUMAN_LAST if x != first])
        c.name = f"{first} {last}"
    elif c.race == "ghoul":
        first = random.choice(GHOUL_FIRST[g])
        last = random.choice([x for x in GHOUL_LAST if x != first])
        c.name = f"{first} {last}"
        if random.random() < 0.35:
            c.name = f'{first} "{random.choice(GHOUL_NICK)}" {last}'
    elif c.race == "mutant":
        n1, n2 = random.sample(MUTANT_NAMES, 2)
        style = random.random()
        if style < 0.4:
            c.name = f"{random.choice(MUTANT_TITLES)} {n1}"
        elif style < 0.7:
            c.name = n1[: max(2, len(n1) // 2 + 1)] + n2[len(n2) // 2:].lower()
        else:
            c.name = n1
    else:
        a, b = random.sample(ROBOT_NAMES, 2)
        if random.random() < 0.5:
            base = a[: max(2, len(a) // 2)] + b[len(b) // 2:]
        else:
            base = a
        title = ROBOT_TITLES[c.pack]
        tag = f"{random.choice('ACEGKMRTVX')}{random.choice('BDLNPSZ')}-{random.randint(1, 99)}"
        c.name = random.choice([f"{title} {base}", base, f"{base} ({tag})"])


def gimmick(c):
    s = c.special
    order = sorted(SPECIAL, key=lambda a: (-s[a], random.random()))
    top = order[0]
    low = min(SPECIAL, key=lambda a: (s[a], random.random()))
    c.epithet = random.choice(EPITHETS[top])
    high_line = random.choice(HIGH_LINES[top])
    if s[low] <= 4 or (s[low] <= 5 and s[top] - s[low] >= 4):
        low_line = random.choice(LOW_LINES[low])
    else:
        low_line = "and is annoyingly decent at everything else"
    perk = c.perks[0][0] if c.perks else None
    perk_line = PERK_LINES.get(perk, f"Swears by their {perk} instincts.") if perk else ""
    pron = {"M": "He", "F": "She"}[c.gender] if c.race != "robot" else "It"
    pron = "It" if c.race == "robot" and random.random() < 0.3 else pron
    c.gimmick_short = f'"{c.epithet}": {high_line}, {low_line}. {perk_line}'
    trinket_line = f" Never parts with {c.trinket[0].lower() + c.trinket[1:]}." if c.trinket else ""
    c.gimmick_long = (f"{c.name}, known as \"{c.epithet}\", {high_line}, {low_line}. {perk_line} "
                      f"{random.choice(ORIGIN_LINES[c.origin])}{trinket_line}")
    c.gimmick_pron = pron


def trait_rows(c):
    rows = []
    if c.origin in ORIGIN_TRAITS:
        rows.append(ORIGIN_TRAITS[c.origin])
    for t in c.survivor_traits:
        rows.append((f"Trait: {t}", SURVIVOR_TRAITS[t]))
    if c.race == "robot":
        if c.no_pincer:
            rows.append(("No Pincer", "No unarmed attacks; can't manipulate objects, Lockpick, Repair or Throw."))
        rows.append(("Arms: " + ", ".join(c.arms), "Optics 1-2, Body 3-8, Arm1 9-11, Arm2 12-14, Arm3 15-17, Thruster 18-20."))
    return rows
