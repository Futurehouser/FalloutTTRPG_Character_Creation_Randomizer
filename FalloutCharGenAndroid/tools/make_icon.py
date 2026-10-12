"""Draws the app icon: a yellow S.P.E.C.I.A.L.-style gear with a radiation trefoil,
crossed by a pencil (character creation), on a vault-blue tile."""
import math, os, sys
from PIL import Image, ImageDraw, ImageFilter

N = 1024
BLUE_T, BLUE_B = (28, 70, 140), (12, 30, 70)
YEL, YEL_D, INK = (246, 196, 40), (176, 128, 10), (20, 26, 48)

def gear(d, cx, cy, r_out, r_in, teeth, fill):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4) - math.pi / 2
        r = r_out if (i % 4) in (0, 1) else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)

def icon(size, round_mask=False, full_bleed=False):
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    bg = Image.new("RGBA", (N, N))
    bd = ImageDraw.Draw(bg)
    for y in range(N):
        t = y / N
        bd.line([(0, y), (N, y)], fill=tuple(int(BLUE_T[k] * (1 - t) + BLUE_B[k] * t) for k in range(3)) + (255,))
    # faint wasteland horizon stripes
    for i, yy in enumerate(range(700, N, 46)):
        bd.rectangle([0, yy, N, yy + 10], fill=(40, 84, 150, 255))
    mask = Image.new("L", (N, N), 0)
    md = ImageDraw.Draw(mask)
    if full_bleed:
        md.rectangle([0, 0, N, N], fill=255)
    elif round_mask:
        md.ellipse([0, 0, N - 1, N - 1], fill=255)
    else:
        md.rounded_rectangle([0, 0, N - 1, N - 1], radius=200, fill=255)
    img.paste(bg, (0, 0), mask)

    d = ImageDraw.Draw(img)
    cx, cy = N / 2, N / 2 - 10
    sc = 0.78 if (round_mask or full_bleed) else 0.9
    # drop shadow
    sh = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    gear(ImageDraw.Draw(sh), cx + 14, cy + 18, 400 * sc, 340 * sc, 12, (0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    gear(d, cx, cy, 400 * sc, 340 * sc, 12, YEL_D)
    gear(d, cx, cy - 8, 392 * sc, 334 * sc, 12, YEL)
    d.ellipse([cx - 255 * sc, cy - 255 * sc, cx + 255 * sc, cy + 255 * sc], fill=INK)
    d.ellipse([cx - 232 * sc, cy - 232 * sc, cx + 232 * sc, cy + 232 * sc], fill=YEL)
    # radiation trefoil
    R, r0 = 205 * sc, 52 * sc
    for k in range(3):
        a0 = -90 + 120 * k - 30
        d.pieslice([cx - R, cy - R, cx + R, cy + R], a0, a0 + 60, fill=INK)
    d.ellipse([cx - r0 - 26 * sc, cy - r0 - 26 * sc, cx + r0 + 26 * sc, cy + r0 + 26 * sc], fill=YEL)
    d.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=INK)
    # pencil across the gear (bottom-left to top-right)
    pen = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pen)
    L, Wd = 760 * sc, 78 * sc
    x0 = N / 2 - L / 2
    y = N / 2 - Wd / 2
    pd.rectangle([x0 + 120 * sc, y, x0 + L - 70 * sc, y + Wd], fill=(226, 74, 50))          # body
    pd.rectangle([x0 + 120 * sc, y + Wd * 0.33, x0 + L - 70 * sc, y + Wd * 0.66], fill=(196, 56, 38))
    pd.rectangle([x0 + L - 70 * sc, y - 4, x0 + L - 20 * sc, y + Wd + 4], fill=(200, 200, 205))  # ferrule
    pd.rounded_rectangle([x0 + L - 24 * sc, y, x0 + L + 30 * sc, y + Wd], radius=int(20 * sc), fill=(240, 150, 160))  # eraser
    pd.polygon([(x0 + 120 * sc, y), (x0 + 120 * sc, y + Wd), (x0, y + Wd / 2)], fill=(240, 205, 150))  # wood
    pd.polygon([(x0 + 40 * sc, y + Wd / 2 - 15 * sc), (x0 + 40 * sc, y + Wd / 2 + 15 * sc), (x0, y + Wd / 2)], fill=INK)  # lead
    pen = pen.rotate(35, resample=Image.BICUBIC, center=(N / 2, N / 2))
    pen = pen.transform(pen.size, Image.AFFINE, (1, 0, -40 * sc, 0, 1, -170 * sc))
    shadow = pen.split()[3].point(lambda v: v * 0.45)
    shim = Image.new("RGBA", (N, N), (0, 0, 0, 0)); shim.putalpha(shadow)
    shim = shim.transform(shim.size, Image.AFFINE, (1, 0, -12, 0, 1, -16)).filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(shim)
    img.alpha_composite(pen)
    return img.resize((size, size), Image.LANCZOS)

if __name__ == "__main__":
    res = sys.argv[1]
    for name, px in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
        dd = os.path.join(res, f"mipmap-{name}")
        os.makedirs(dd, exist_ok=True)
        icon(px).save(os.path.join(dd, "ic_launcher.png"))
        icon(px, round_mask=True).save(os.path.join(dd, "ic_launcher_round.png"))
    icon(512).save(os.path.join(res, "..", "..", "icon_512.png"))
    print("icons written")
