"""Draws a generated character onto the blank character sheet."""
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

from gamedata import SPECIAL, SKILL_NAMES, SKILL_ATTR, WEAPONS
from generator import trait_rows

S = 2  # render at 2x the template's native size for crisp text
INK = (28, 38, 92)
RED = (150, 30, 30)


def resource(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def font_path(*names):
    fdir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    for n in names:
        p = os.path.join(fdir, n)
        if os.path.exists(p):
            return p
    return None


HAND = font_path("segoepr.ttf", "segoesc.ttf", "comic.ttf", "arial.ttf")
HANDB = font_path("segoeprb.ttf", "segoepr.ttf", "comicbd.ttf", "arialbd.ttf")
UI = font_path("seguisb.ttf", "segoeui.ttf", "arial.ttf")
UIB = font_path("segoeuib.ttf", "arialbd.ttf")
_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        try:
            _cache[key] = ImageFont.truetype(path, int(size * S))
        except Exception:
            _cache[key] = ImageFont.load_default()
    return _cache[key]


class Sheet:
    def __init__(self):
        base = Image.open(resource(os.path.join("assets", "sheet_blank.png"))).convert("RGB")
        self.w, self.h = base.size
        self.img = base.resize((self.w * S, self.h * S), Image.LANCZOS)
        self.d = ImageDraw.Draw(self.img)

    def text(self, x, y, s, path=UI, size=9, anchor="lm", fill=INK, maxw=None):
        s = str(s)
        while maxw and size > 4 and self.d.textlength(s, font=F(path, size)) > maxw * S:
            size -= 0.5
        self.d.text((x * S, y * S), s, font=F(path, size), fill=fill, anchor=anchor)

    def wrap(self, x, y, w, h, s, path=UI, size=8, fill=INK, lh=1.15, vcenter=False):
        """Fit wrapped text inside a box, shrinking the font if needed."""
        while size >= 4.5:
            f = F(path, size)
            avg = self.d.textlength("abcdefghijklmnopqrstuvwxyz", font=f) / 26 / S
            lines = textwrap.wrap(s, width=max(8, int(w / avg)))
            if len(lines) * size * lh <= h:
                break
            size -= 0.5
        f = F(path, size)
        if vcenter:
            y += (h - len(lines) * size * lh) / 2
        for i, line in enumerate(lines):
            self.d.text((x * S, (y + i * size * lh) * S), line, font=f, fill=fill)

    def check(self, x, y):
        r = 3.2
        self.d.line([((x - r) * S, y * S), ((x - 0.5) * S, (y + r) * S), ((x + r + 1) * S, (y - r - 1) * S)],
                    fill=INK, width=int(1.6 * S))

    def relabel(self, x0, y0, x1, y1, label):
        self.d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=(26, 26, 26))
        self.text((x0 + x1) / 2, (y0 + y1) / 2, label, UIB, 6.5, "mm", fill=(255, 255, 255))


# hit-location boxes: (phys DR x, value row y, rad DR x) — en DR/HP on second row (+18)
LOC_BOX = {
    "head": (411, 339, 478), "larm": (295, 408, 359), "rarm": (531, 408, 595),
    "torso": (411, 477, 478), "lleg": (301, 546, 366), "rleg": (525, 546, 590),
}
LOC_TITLE = {  # header bar rectangles, for relabelling robots
    "head": (362, 313, 487, 328, "OPTICS (1-2)"), "larm": (244, 382, 369, 397, "ARM 1 (9-11)"),
    "rarm": (479, 382, 604, 397, "ARM 2 (12-14)"), "torso": (362, 451, 487, 466, "MAIN BODY (3-8)"),
    "lleg": (250, 520, 375, 535, "ARM 3 (15-17)"), "rleg": (473, 520, 599, 535, "THRUSTER (18-20)"),
}
SPECIAL_POS = {"STR": (72, 184), "PER": (156, 184), "END": (241, 184), "CHA": (326, 184),
               "INT": (411, 184), "AGI": (496, 184), "LCK": (580, 178)}
SKILL_Y0, SKILL_DY = 286.5, 18.35
WEAPON_Y = [662, 695, 728, 761, 794]
PERK_ROWS = [76, 132, 189, 245, 302, 358, 415, 471, 528, 584, 641, 697]
PERK_ROW_H = 56


def render(c, sheet_only=False):
    sh = Sheet()
    t = sh.text

    # header
    t(260, 70, c.name, HANDB, 15, "mm", maxw=176)
    t(260, 86, f"\u201c{c.epithet}\u201d \u2022 {c.archetype}", HAND, 7.5, "mm", fill=RED, maxw=176)
    t(452, 43, "0", HAND, 8.5)
    t(452, 61, "100", HAND, 8.5)
    t(452, 84, f"{c.origin} \u2022 {c.pack}", HAND, 8, maxw=150)
    t(583, 66, "1", HANDB, 22, "mm")

    # S.P.E.C.I.A.L.
    for a in SPECIAL:
        x, y = SPECIAL_POS[a]
        t(x, y, c.special[a], HANDB, 24, "mm")
    t(596, 229, c.luck_points, HANDB, 13, "mm")

    # skills
    for i, s in enumerate(SKILL_NAMES):
        y = SKILL_Y0 + i * SKILL_DY
        if s in c.tags:
            sh.check(157, y)
        if c.skills[s]:
            t(202, y + 1, c.skills[s], HANDB, 10, "mm")

    # combat
    t(338, 273, f"+{c.melee_bonus}" if c.melee_bonus else "0", HANDB, 10, "mm")
    t(471, 273, c.defense, HANDB, 11, "mm")
    t(602, 273, c.initiative, HANDB, 11, "mm")
    t(327, 328, "Imm" if c.poison_immune else c.poison_dr, HANDB, 8.5 if c.poison_immune else 10, "mm", maxw=34)
    t(574, 323, c.hp, HANDB, 10, "mm")
    t(574, 339, c.hp, HANDB, 10, "mm")

    if c.race == "robot":
        for loc, (x0, y0, x1, y1, lab) in LOC_TITLE.items():
            sh.relabel(x0, y0, x1, y1, lab)
    for loc, (px, y, rx) in LOC_BOX.items():
        dr = c.dr[loc]
        t(px, y, dr["p"], HANDB, 9, "mm")
        t(px, y + 18, dr["e"], HANDB, 9, "mm")
        t(rx, y, "Imm" if c.rad_immune else dr["r"], HANDB, 7.5 if c.rad_immune else 9, "mm")

    # weapons
    for i, w in enumerate(c.weapons[:5]):
        d = WEAPONS[w]
        y = WEAPON_Y[i]
        attr = SKILL_ATTR[d["skill"]]
        tn = c.special[attr] + c.skills[d["skill"]]
        t(39, y, w, UI, 7.5, maxw=86)
        t(150, y, d["skill"], UI, 6.5, "mm", maxw=42)
        t(188, y, tn, HANDB, 10, "mm")
        if d["skill"] in c.tags:
            sh.check(216, y)
        dmg = d["dmg"]
        if d["skill"] in ("Melee Weapons", "Unarmed"):
            bonus = c.melee_bonus + (1 if d["skill"] == "Unarmed" and any(p == "Iron Fist" for p, _ in c.perks) else 0)
            dmg = f"{dmg}+{bonus}" if bonus else dmg
        t(271, y, dmg, HANDB, 9.5, "lm", maxw=19)
        sh.wrap(293, y - 11, 52, 22, d["eff"], UI, 6.5, vcenter=True)
        t(367, y, d["type"], UI, 7, "mm", maxw=38)
        t(405, y, d["rate"], UI, 8, "mm")
        t(438, y, d["range"], UI, 8, "mm")
        sh.wrap(458, y - 11, 71, 22, d["qual"], UI, 6.5, vcenter=True)
        ammo = d["ammo"]
        if w == "Molotov Cocktail":
            ammo = "Molotov"
        elif w in ("Baseball Grenade", "Throwing Knives", "Tomahawks"):
            ammo = w
        qty = c.ammo.get(ammo) if ammo else None
        t(552, y, qty if qty is not None else "-", HAND, 8.5, "mm")
        t(595, y, d["wt"], UI, 8, "mm")

    # caps, ammo, gear
    t(845, 60, c.caps, HANDB, 15, "mm")
    for i, (cal, q) in enumerate(sorted(c.ammo.items())):
        y = 143 + i * 15
        if y > 290:
            break
        t(700, y, cal, UI, 8, maxw=122)
        t(852, y, q, HAND, 9, "mm")

    gear = []
    for item in c.worn:
        from gamedata import APPAREL
        gear.append((item + " (worn)", APPAREL[item]["wt"]))
    if c.plating:
        gear.append((c.plating + " (installed)", "-"))
    gear += [tuple(g) for g in c.gear]
    # merge duplicates
    merged = []
    for nm, wt in gear:
        for m in merged:
            if m[0] == nm:
                m[2] += 1
                break
        else:
            merged.append([nm, wt, 1])
    gy0, gdy = 362, 15.5
    for i, (nm, wt, n) in enumerate(merged):
        y = gy0 + i * gdy
        if y > 742:
            break
        label = f"{nm} x{n}" if n > 1 else nm
        t(699, y, label, UI, 7.5, maxw=143)
        if isinstance(wt, int):
            wt = wt * n
        t(862, y, wt, UI, 7.5, "mm")
    t(862, 766, c.carry_now, HANDB, 10, "mm")
    t(862, 795, c.carry_max, HANDB, 10, "mm")

    # perks & traits
    rows = []
    for nm, eff in trait_rows(c):
        rows.append((nm, "-", eff))
    from gamedata import PERKS
    for p, r in c.perks:
        rows.append((p, r, PERKS[p][3]))
    rows.append(("Quirk", "-", c.gimmick_short))
    for i, (nm, rank, eff) in enumerate(rows):
        if i >= len(PERK_ROWS):
            break
        y = PERK_ROWS[i]
        sh.wrap(895, y + 3, 91, PERK_ROW_H - 8, nm, UIB, 7.5)
        t(1004, y + PERK_ROW_H / 2 - 2, rank, HANDB, 10, "mm")
        sh.wrap(1024, y + 3, 247, PERK_ROW_H - 8, eff, UI, 7.5)

    img = sh.img
    if sheet_only:
        return img
    return add_dossier(img, c)


def add_dossier(img, c):
    """Append a notes band under the sheet with the character's gimmick and creation notes."""
    W = img.width
    band_h = 150 * S
    out = Image.new("RGB", (W, img.height + band_h), (236, 233, 224))
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    y0 = img.height
    d.rectangle([0, y0, W, y0 + 22 * S], fill=(26, 26, 26))
    d.text((36 * S, y0 + 11 * S), "WASTELAND DOSSIER", font=F(UIB, 10), fill=(240, 190, 40), anchor="lm")
    d.text((W - 36 * S, y0 + 11 * S), f"Archetype: {c.archetype}   |   Origin: {c.origin}   |   Pack: {c.pack}",
           font=F(UI, 8), fill=(230, 230, 230), anchor="rm")

    def para(x, y, w, s, size=8.5, path=HAND, fill=INK, lh=1.35):
        f = F(path, size)
        avg = d.textlength("abcdefghijklmnopqrstuvwxyz", font=f) / 26 / S
        lines = textwrap.wrap(s, width=int(w / avg))
        for i, line in enumerate(lines):
            d.text((x * S, (y + i * size * lh) * S), line, font=f, fill=fill)
        return y + len(lines) * size * lh

    y = para(36, y0 / S + 30, 600, c.gimmick_long, 9)
    tags = ", ".join(c.tags)
    notes = [f"Tag skills: {tags}.", f"Skill points spent: {c.skill_points} (9 + INT)."]
    if c.extra_tags:
        notes.append(f"Origin/trait bonus tag(s): {', '.join(c.extra_tags)}.")
    notes += c.notes
    if c.race == "robot":
        notes.append("Robot hit locations are relabelled on the sheet. Carry weight is fixed by the chassis.")
    if c.rad_immune:
        notes.append("Radiation DR shows 'Imm' because this origin is immune to radiation damage.")
    notes.append("Combat-dice ammo amounts were already rolled. Gear marked '-' has no listed weight.")
    para(680, y0 / S + 30, 590, "  \u2022  ".join(notes), 7.5, UI, (60, 60, 60), 1.4)
    return out
