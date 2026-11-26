import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

BG = (247, 243, 234)
INK = (22, 22, 24)
MUTED = (88, 84, 78)
RULE = (205, 198, 185)
DARK_RULE = (38, 36, 34)
CRIMSON = (178, 34, 34)
BLUE_OFF = (24, 80, 146)
GREEN_CONF = (22, 118, 66)
GRAY_REP = (92, 92, 96)
AMBER_CLAIM = (168, 92, 16)
GOLD = (214, 154, 42)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "EUROPE": (26, 68, 134),
    "N. AMERICA": (24, 108, 164),
    "EAST ASIA": (182, 42, 42),
    "AFRICA": (118, 48, 128),
    "M. EAST": (196, 104, 24),
    "S & SE ASIA": (22, 130, 88),
    "LAT. AM.": (164, 76, 38),
    "OCEANIA": (22, 118, 68),
    "GLOBAL": (66, 72, 82),
}


def _find_font(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"None of fonts found: {candidates}")


SERIF_BOLD_PATH = _find_font([
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/timesbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
])
SERIF_ITAL_PATH = _find_font([
    "C:/Windows/Fonts/georgiai.ttf",
    "C:/Windows/Fonts/timesi.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
])
SANS_REG_PATH = _find_font([
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
])
SANS_BOLD_PATH = _find_font([
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
])

_FONT_CACHE = {}


def F(path, size):
    k = (path, size)
    if k not in _FONT_CACHE:
        _FONT_CACHE[k] = ImageFont.truetype(path, size)
    return _FONT_CACHE[k]


def _tw(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]


def _th(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def _wrap(draw, text, font, max_w, max_lines=3):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = w if not cur else f"{cur} {w}"
        if _tw(draw, test, font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and _tw(draw, last + "...", font) > max_w:
            last = " ".join(last.split()[:-1]) if " " in last else last[:-1]
        lines[-1] = (last + "...") if last else "..."
    return lines


def _draw_lines(draw, x, y, text, font, color, max_w, line_h, max_lines=3):
    lines = _wrap(draw, text, font, max_w, max_lines)
    for i, ln in enumerate(lines):
        draw.text((x, y + i * line_h), ln, font=font, fill=color)
    return y + len(lines) * line_h


def _grad_v(draw, x0, y0, x1, y1, c_top, c_bot):
    h = max(1, y1 - y0)
    for dy in range(h):
        t = dy / max(1, h - 1)
        r = int(c_top[0] * (1 - t) + c_bot[0] * t)
        g = int(c_top[1] * (1 - t) + c_bot[1] * t)
        b = int(c_top[2] * (1 - t) + c_bot[2] * t)
        draw.line([(x0, y0 + dy), (x1 - 1, y0 + dy)], fill=(r, g, b))


def _stipple(draw, x0, y0, x1, y1, seed, count, colors, size=1):
    rng = random.Random(seed)
    for _ in range(count):
        px = rng.randint(x0, x1 - 1)
        py = rng.randint(y0, y1 - 1)
        c = colors[rng.randint(0, len(colors) - 1)]
        if size <= 1:
            draw.point((px, py), fill=c)
        else:
            draw.ellipse([px, py, px + size, py + size], fill=c)


def _cert_badge(draw, x_right, y, cert):
    styles = {
        "OFFICIAL": ((236, 243, 253), BLUE_OFF, BLUE_OFF),
        "CONFIRMED": ((232, 246, 238), GREEN_CONF, GREEN_CONF),
        "REPORTED": ((242, 242, 244), GRAY_REP, GRAY_REP),
        "CLAIM": ((254, 244, 232), AMBER_CLAIM, AMBER_CLAIM),
    }
    bg, fg, bd = styles[cert]
    fnt = F(SANS_BOLD_PATH, 7)
    bw = _tw(draw, cert, fnt) + 8
    bh = 12
    draw.rounded_rectangle([x_right - bw, y, x_right, y + bh], radius=2, fill=bg, outline=bd, width=1)
    draw.text((x_right - bw + 4, y + 2), cert, font=fnt, fill=fg)
    return bw


def _pin(draw, cx, cy, num, bg=CRIMSON, r=8, ring=WHITE):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=ring, width=1)
    fnt = F(SANS_BOLD_PATH, 8 if r >= 8 else 7)
    s = str(num)
    tw = _tw(draw, s, fnt)
    th = _th(draw, s, fnt)
    draw.text((cx - tw // 2, cy - th // 2 - 1), s, font=fnt, fill=WHITE)


def _ribbon(draw, x0, y0, text, bg=(18, 24, 34), fg=WHITE):
    fnt = F(SANS_BOLD_PATH, 8)
    bw = _tw(draw, text, fnt) + 10
    draw.rectangle([x0, y0, x0 + bw, y0 + 14], fill=bg)
    draw.text((x0 + 5, y0 + 2), text, font=fnt, fill=fg)


def _draw_parchment_grain(img):
    px = img.load()
    rng = random.Random(202611257)
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            d = rng.randint(-3, 3)
            r, g, b = px[x, y]
            px[x, y] = (
                max(0, min(255, r + d)),
                max(0, min(255, g + d)),
                max(0, min(255, b + d)),
            )


def _draw_hero1(draw, x0, y0, x1, y1):
    # Hero 1: US Section 301 Tariffs on 14 Economies (container ship + 4 country tariff banners)
    _grad_v(draw, x0, y0, x1, y0 + 70, (24, 36, 62), (48, 72, 112))
    _grad_v(draw, x0, y0 + 70, x1, y1, (26, 68, 108), (18, 44, 78))
    # 4 top rate pills
    pills = [
        ("CHINA 20%", (178, 36, 36)),
        ("INDIA 25%", (202, 106, 24)),
        ("EU 15%", (28, 78, 152)),
        ("VIETNAM 35%", (142, 32, 92)),
    ]
    px = x0 + 8
    f_p = F(SANS_BOLD_PATH, 8)
    for txt, col in pills:
        pw = _tw(draw, txt, f_p) + 10
        draw.rectangle([px, y0 + 8, px + pw, y0 + 22], fill=col)
        draw.text((px + 5, y0 + 10), txt, font=f_p, fill=WHITE)
        px += pw + 6
    # Cargo ship silhouette & stacked containers
    draw.polygon([(x0 + 46, y0 + 68), (x0 + 286, y0 + 68), (x0 + 270, y0 + 84), (x0 + 58, y0 + 84)], fill=(38, 44, 52))
    draw.rectangle([x0 + 46, y0 + 64, x0 + 286, y0 + 68], fill=CRIMSON)
    draw.rectangle([x0 + 236, y0 + 38, x0 + 266, y0 + 64], fill=(236, 238, 242), outline=(140, 148, 160))
    draw.rectangle([x0 + 244, y0 + 44, x0 + 258, y0 + 50], fill=(32, 42, 62))
    stack_cols = [(178, 36, 36), (26, 82, 148), (22, 118, 66), (202, 106, 24), (118, 48, 128), (178, 36, 36)]
    for row in range(2):
        for col_i in range(6):
            cx0 = x0 + 70 + col_i * 27
            cy0 = y0 + 52 - row * 12
            draw.rectangle([cx0, cy0, cx0 + 24, cy0 + 10], fill=stack_cols[(col_i + row * 2) % len(stack_cols)], outline=(24, 28, 34))
    _stipple(draw, x0 + 8, y0 + 74, x1 - 8, y1 - 4, 701, 45, [(74, 124, 166), (38, 86, 128)], 1)
    _ribbon(draw, x0 + 30, y1 - 18, "14 ECONOMIES · SECTION 301", bg=(14, 20, 32))
    _pin(draw, x0 + 14, y1 - 14, 1, bg=REGION_COLORS["N. AMERICA"])


def _draw_hero2(draw, x0, y0, x1, y1):
    # Hero 2: Asia chip crash Kospi 4,697.51
    _grad_v(draw, x0, y0, x1, y1, (22, 24, 30), (36, 22, 24))
    for gx in range(x0 + 16, x0 + 178, 26):
        draw.line([(gx, y0 + 18), (gx, y1 - 6)], fill=(44, 48, 58), width=1)
    for gy in range(y0 + 22, y1 - 6, 18):
        draw.line([(x0 + 6, gy), (x0 + 178, gy)], fill=(44, 48, 58), width=1)
    pts = [(x0 + 8, y0 + 26), (x0 + 40, y0 + 32), (x0 + 76, y0 + 46), (x0 + 114, y0 + 66), (x0 + 146, y0 + 82), (x0 + 172, y0 + 94)]
    draw.polygon(pts + [(x0 + 172, y1 - 2), (x0 + 8, y1 - 2)], fill=(120, 28, 30))
    draw.line(pts, fill=(248, 86, 72), width=3)
    draw.ellipse([x0 + 168, y0 + 90, x0 + 176, y0 + 98], fill=(255, 210, 92))
    bx0, by0, bx1, by1 = x0 + 182, y0 + 6, x1 - 6, y1 - 6
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=4, fill=(14, 18, 26), outline=(64, 72, 86), width=1)
    quotes = [
        ("KOSPI", "-6.2%"),
        ("HYNIX", "-11.1%"),
        ("SAMSUNG", "-9.9%"),
        ("TAIEX", "-4.8%"),
        ("NIKKEI", "-2.8%"),
    ]
    row_h = (by1 - by0 - 10) // len(quotes)
    f_l = F(SANS_BOLD_PATH, 8)
    for i, (k, v) in enumerate(quotes):
        ry = by0 + 6 + i * row_h
        draw.text((bx0 + 8, ry), k, font=f_l, fill=(214, 220, 232))
        tw = _tw(draw, v, f_l)
        draw.text((bx1 - tw - 8, ry), v, font=f_l, fill=(252, 92, 84))
    _ribbon(draw, x0, y0, "KOSPI CLOSE 4,697.51", bg=(14, 20, 32))
    _pin(draw, x0 + 14, y1 - 14, 2, bg=REGION_COLORS["EAST ASIA"])


def _draw_hero3(draw, x0, y0, x1, y1):
    # Hero 3: Shenzhou-24 flies Pakistan's 1st astronaut to Tiangong
    _grad_v(draw, x0, y0, x1, y1, (8, 16, 38), (20, 44, 88))
    _stipple(draw, x0, y0 + 14, x1, y1 - 24, 303, 120, [(200, 215, 255), (255, 255, 230), (130, 150, 200)], 1)
    # Clipped curved Earth limb
    draw.polygon([
        (x0, y1), (x0, y1 - 12),
        (x0 + 80, y1 - 20), (x0 + 162, y1 - 23), (x0 + 244, y1 - 20),
        (x1, y1 - 12), (x1, y1),
    ], fill=(28, 92, 168))
    draw.line([(x0, y1 - 12), (x0 + 80, y1 - 20), (x0 + 162, y1 - 23), (x0 + 244, y1 - 20), (x1, y1 - 12)], fill=(138, 212, 255), width=2)
    rx = x0 + 58
    draw.polygon([(rx, y1 - 26), (rx - 12, y1 - 4), (rx + 12, y1 - 4)], fill=(242, 138, 34))
    draw.polygon([(rx, y1 - 31), (rx - 6, y1 - 6), (rx + 6, y1 - 6)], fill=(255, 224, 102))
    draw.polygon([(rx, y0 + 20), (rx - 5, y0 + 32), (rx + 5, y0 + 32)], fill=(244, 245, 248))
    draw.rectangle([rx - 5, y0 + 32, rx + 5, y1 - 30], fill=(238, 240, 244), outline=(170, 178, 192))
    draw.rectangle([rx - 9, y1 - 50, rx - 5, y1 - 30], fill=(214, 218, 226))
    draw.rectangle([rx + 5, y1 - 50, rx + 9, y1 - 30], fill=(214, 218, 226))
    for i in range(10):
        t = i / 9.0
        px = int(rx + 16 + t * 112)
        py = int((y0 + 32) + math.sin(t * 2.2) * -12 + 24 * (1 - t))
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 206, 74))
    sx, sy = x0 + 232, y0 + 50
    for dx in (-34, -20, 14, 28):
        draw.rectangle([sx + dx, sy - 20, sx + dx + 8, sy + 20], fill=(38, 86, 152), outline=(120, 174, 232))
    draw.rectangle([sx - 40, sy - 3, sx + 40, sy + 3], fill=(208, 214, 224))
    draw.rectangle([sx - 16, sy - 6, sx + 16, sy + 6], fill=(246, 248, 252))
    fx, fy = x1 - 74, y0 + 18
    draw.rectangle([fx, fy, fx + 30, fy + 18], fill=(198, 30, 34), outline=WHITE)
    draw.ellipse([fx + 4, fy + 4, fx + 9, fy + 9], fill=(250, 210, 48))
    pxf = fx + 36
    draw.rectangle([pxf, fy, pxf + 30, fy + 18], fill=(18, 96, 52), outline=WHITE)
    draw.rectangle([pxf, fy, pxf + 8, fy + 18], fill=WHITE)
    draw.pieslice([pxf + 12, fy + 3, pxf + 24, fy + 15], 45, 285, fill=WHITE)
    _ribbon(draw, x0, y0, "00:18 UTC · DOCKS 03:56", bg=(14, 20, 32))
    _pin(draw, x0 + 14, y1 - 14, 3, bg=REGION_COLORS["EAST ASIA"])


def _draw_mid_art(draw, num, reg, x0, y0, x1, y1):
    w = x1 - x0
    if num == 4:
        # Dhaka garment pay +36%: 12,500 -> 17,000 TAKA
        _grad_v(draw, x0, y0, x1, y1, (238, 246, 238), (224, 238, 228))
        fx = x0 + 74
        draw.polygon([(fx, y1 - 14), (fx, y0 + 34), (fx + 30, y0 + 22), (fx + 30, y0 + 34), (fx + 60, y0 + 22), (fx + 60, y0 + 34), (fx + 90, y0 + 22), (fx + 90, y1 - 14)], fill=(192, 206, 196), outline=(140, 158, 146))
        draw.rectangle([x0 + 88, y0 + 44, x0 + 116, y1 - 8], fill=(128, 140, 136))
        draw.rectangle([x0 + 124, y0 + 28, x0 + 158, y1 - 8], fill=GREEN_CONF)
        draw.line([(x0 + 102, y0 + 42), (x0 + 141, y0 + 22)], fill=(18, 102, 54), width=3)
        draw.text((x0 + 8, y0 + 20), "+36%", font=F(SERIF_BOLD_PATH, 19), fill=GREEN_CONF)
        draw.text((x0 + 8, y0 + 42), "Tk 12.5k->17k", font=F(SANS_BOLD_PATH, 8), fill=INK)
        _ribbon(draw, x0, y0, "17,000 TAKA · 4–2", bg=GREEN_CONF)
    elif num == 5:
        # Cairo Ring Road tanker explosion: 31+ dead
        _grad_v(draw, x0, y0, x1, y1, (38, 28, 28), (74, 40, 32))
        draw.rectangle([x0, y1 - 14, x1, y1], fill=(56, 56, 62))
        draw.rectangle([x0 + 36, y1 - 30, x0 + 106, y1 - 14], fill=(160, 166, 174), outline=DARK_RULE)
        draw.ellipse([x0 + 62, y0 + 18, x0 + 102, y0 + 54], fill=(238, 92, 22))
        draw.ellipse([x0 + 70, y0 + 26, x0 + 94, y0 + 48], fill=(255, 214, 64))
        draw.text((x0 + 112, y0 + 22), "31+", font=F(SERIF_BOLD_PATH, 20), fill=WHITE)
        draw.text((x0 + 112, y0 + 44), "DEAD", font=F(SANS_BOLD_PATH, 8), fill=(255, 196, 172))
        _ribbon(draw, x0, y0, "CAIRO RING ROAD", bg=CRIMSON)
    elif num == 6:
        # UK Ofgem cap +26% to £2,166
        _grad_v(draw, x0, y0, x1, y1, (236, 242, 248), (248, 238, 224))
        hx = x0 + 34
        draw.polygon([(hx - 22, y0 + 38), (hx, y0 + 18), (hx + 22, y0 + 38)], fill=(142, 54, 46))
        draw.rectangle([hx - 18, y0 + 38, hx + 18, y1 - 8], fill=(224, 212, 194), outline=(170, 156, 140))
        draw.pieslice([hx - 8, y0 + 43, hx + 8, y0 + 63], 160, 380, fill=(24, 118, 206))
        draw.text((x0 + 72, y0 + 20), "+26%", font=F(SERIF_BOLD_PATH, 22), fill=CRIMSON)
        draw.text((x0 + 72, y0 + 46), "£1,723 -> £2,166", font=F(SANS_BOLD_PATH, 9), fill=BLUE_OFF)
        _ribbon(draw, x0, y0, "OFGEM CAP · 1 JAN", bg=BLUE_OFF)
    elif num == 7:
        # Australia & Solomons A$740m pact
        _grad_v(draw, x0, y0, x1, y1, (228, 240, 248), (244, 241, 232))
        draw.polygon([(x0 + w // 2, y0 + 12), (x0 + 46, y1 - 14), (x1 - 46, y1 - 14)], fill=None, outline=(145, 162, 178), width=2)
        fx0, fy0 = x0 + 14, y0 + 20
        draw.rectangle([fx0, fy0, fx0 + 40, fy0 + 24], fill=(16, 48, 124), outline=WHITE)
        draw.line([(fx0, fy0 + 7), (fx0 + 18, fy0 + 7)], fill=CRIMSON, width=2)
        draw.line([(fx0 + 9, fy0), (fx0 + 9, fy0 + 14)], fill=CRIMSON, width=2)
        sx0 = x1 - 54
        draw.polygon([(sx0, fy0), (sx0 + 40, fy0), (sx0, fy0 + 24)], fill=(18, 86, 156))
        draw.polygon([(sx0 + 40, fy0), (sx0 + 40, fy0 + 24), (sx0, fy0 + 24)], fill=(24, 118, 64))
        draw.line([(sx0, fy0 + 24), (sx0 + 40, fy0)], fill=(238, 194, 42), width=3)
        draw.rounded_rectangle([x0 + 30, y1 - 19, x1 - 26, y1 - 5], radius=2, fill=(24, 52, 92))
        draw.text((x0 + 36, y1 - 16), "NO FOREIGN BASES", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
        _ribbon(draw, x0, y0, "A$740M SECURITY PACT", bg=REGION_COLORS["OCEANIA"])
    elif num == 8:
        # UNODC 47,000 women killed / 5 per hr
        _grad_v(draw, x0, y0, x1, y1, (248, 244, 238), (238, 232, 224))
        draw.text((x0 + 8, y0 + 18), "47,000", font=F(SERIF_BOLD_PATH, 19), fill=CRIMSON)
        draw.text((x0 + 9, y0 + 40), "5 KILLED / HR", font=F(SANS_BOLD_PATH, 8), fill=(72, 68, 64))
        bars = [
            ("Africa", 2.9, (118, 48, 128)),
            ("Amer.", 1.4, (24, 108, 164)),
            ("Ocean.", 1.1, (22, 118, 68)),
            ("Asia", 0.6, (182, 42, 42)),
            ("Europe", 0.5, (26, 68, 134)),
        ]
        bx = x0 + 114
        f_b = F(SANS_BOLD_PATH, 7)
        for idx, (lbl, val, col) in enumerate(bars):
            by = y0 + 17 + idx * 10
            draw.text((x0 + 82, by), lbl, font=f_b, fill=INK)
            bw = int((val / 2.9) * 50)
            draw.rectangle([bx, by + 1, bx + bw, by + 7], fill=col)
            draw.text((bx + bw + 3, by), f"{val}", font=f_b, fill=INK)
        _ribbon(draw, x0, y0, "UNODC REPORT", bg=(96, 28, 36))
    elif num == 9:
        # Ukraine 5 regions out / Zaporizhzhia grid
        _grad_v(draw, x0, y0, x1, y1, (24, 34, 56), (48, 56, 76))
        px = x0 + 48
        draw.line([(px, y0 + 18), (px - 14, y1 - 8)], fill=(190, 198, 210), width=2)
        draw.line([(px, y0 + 18), (px + 14, y1 - 8)], fill=(190, 198, 210), width=2)
        draw.line([(px - 18, y0 + 30), (px + 18, y0 + 30)], fill=(190, 198, 210), width=2)
        draw.polygon([(x0 + 88, y0 + 22), (x0 + 78, y0 + 40), (x0 + 86, y0 + 40), (x0 + 80, y0 + 56), (x0 + 96, y0 + 36), (x0 + 88, y0 + 36)], fill=(252, 208, 62))
        draw.text((x0 + 106, y0 + 22), "5", font=F(SERIF_BOLD_PATH, 22), fill=(252, 208, 62))
        draw.text((x0 + 106, y0 + 45), "REGIONS", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
        _ribbon(draw, x0, y0, "POWER GRID HIT", bg=(14, 20, 32))
    elif num == 10:
        # Cape Town Phala Phala report voided
        _grad_v(draw, x0, y0, x1, y1, (242, 238, 230), (230, 224, 214))
        draw.line([(x0 + 28, y0 + 44), (x0 + 52, y0 + 24)], fill=(104, 64, 32), width=4)
        draw.rectangle([x0 + 44, y0 + 18, x0 + 62, y0 + 32], fill=(128, 78, 40))
        draw.rectangle([x0 + 22, y0 + 52, x0 + 64, y0 + 58], fill=(116, 70, 34))
        draw.rounded_rectangle([x0 + 78, y0 + 24, x1 - 12, y0 + 48], radius=3, fill=CRIMSON)
        draw.text((x0 + 88, y0 + 29), "VOIDED", font=F(SANS_BOLD_PATH, 13), fill=WHITE)
        _ribbon(draw, x0, y0, "HIGH COURT RULING", bg=REGION_COLORS["AFRICA"])
    elif num == 11:
        # Netanyahu Case 4000 judges urge dropping bribery charge
        _grad_v(draw, x0, y0, x1, y1, (244, 240, 234), (234, 228, 220))
        cx = x0 + 42
        draw.line([(cx, y0 + 20), (cx, y0 + 56)], fill=INK, width=2)
        draw.line([(cx - 18, y0 + 28), (cx + 18, y0 + 28)], fill=INK, width=2)
        draw.arc([cx - 24, y0 + 28, cx - 10, y0 + 46], 0, 180, fill=MUTED, width=2)
        draw.arc([cx + 10, y0 + 28, cx + 24, y0 + 46], 0, 180, fill=MUTED, width=2)
        draw.text((x0 + 74, y0 + 22), "CASE 4000", font=F(SANS_BOLD_PATH, 11), fill=INK)
        draw.text((x0 + 74, y0 + 38), "DROP BRIBE", font=F(SANS_BOLD_PATH, 9), fill=CRIMSON)
        _ribbon(draw, x0, y0, "TRIAL PANEL", bg=BLUE_OFF)
    elif num == 12:
        # Coalition strikes Hodeidah; Saudis down 4 drones
        _grad_v(draw, x0, y0, x1, y1, (24, 38, 68), (54, 72, 102))
        draw.rectangle([x0, y1 - 16, x1, y1], fill=(22, 48, 78))
        for dx, dy in [(x0 + 74, y0 + 26), (x0 + 108, y0 + 22), (x0 + 138, y0 + 32), (x0 + 162, y0 + 24)]:
            draw.line([(x0 + 36, y1 - 18), (dx, dy)], fill=(90, 198, 240), width=1)
            draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(246, 134, 34))
            draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 228, 112))
        _ribbon(draw, x0, y0, "4 DRONES DOWNED", bg=(14, 20, 32))
    elif num == 13:
        # Cartagena supermarket siege ends: 20 hostages freed
        _grad_v(draw, x0, y0, x1, y1, (236, 244, 246), (222, 232, 236))
        draw.rectangle([x0 + 20, y0 + 22, x0 + 102, y1 - 12], fill=WHITE, outline=(120, 132, 146))
        draw.rectangle([x0 + 20, y0 + 22, x0 + 102, y0 + 34], fill=(238, 194, 42))
        draw.text((x0 + 44, y0 + 24), "ÉXITO", font=F(SANS_BOLD_PATH, 8), fill=INK)
        draw.rounded_rectangle([x0 + 108, y0 + 24, x1 - 12, y0 + 46], radius=2, fill=GREEN_CONF)
        draw.text((x0 + 114, y0 + 29), "ALL FREED", font=F(SANS_BOLD_PATH, 9), fill=WHITE)
        _ribbon(draw, x0, y0, "DAWN RAID · 20 SAVED", bg=REGION_COLORS["LAT. AM."])

    _pin(draw, x1 - 13, y1 - 12, num, bg=REGION_COLORS[reg], r=7)


def _draw_world_map(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(224, 234, 240), outline=RULE, width=1)
    mw, mh = x1 - x0, y1 - y0

    def ll(lon, lat):
        return x0 + int((lon + 180.0) / 360.0 * mw), y0 + int((86.0 - lat) / 150.0 * mh)

    for gx in (-120, -60, 0, 60, 120):
        px, _ = ll(gx, 0)
        draw.line([(px, y0), (px, y1)], fill=(210, 222, 230), width=1)
    for gy in (-30, 0, 30, 60):
        _, py = ll(0, gy)
        draw.line([(x0, py), (x1, py)], fill=(210, 222, 230), width=1)

    land = (212, 206, 190)
    coast = (168, 162, 148)
    continents = [
        [(-168, 66), (-135, 70), (-95, 68), (-64, 52), (-78, 34), (-84, 24), (-96, 19), (-84, 9), (-95, 16), (-114, 30), (-125, 48), (-150, 58)],
        [(-80, 11), (-62, 10), (-36, -6), (-42, -23), (-62, -44), (-68, -55), (-76, -42), (-74, -18), (-81, -4)],
        [(-10, 36), (3, 44), (-6, 51), (10, 58), (24, 68), (42, 66), (36, 46), (26, 38), (12, 42), (4, 38)],
        [(-17, 15), (-5, 36), (11, 37), (33, 31), (42, 12), (51, 12), (40, -10), (28, -34), (18, -35), (12, -16), (9, 4), (-7, 5)],
        [(35, 44), (42, 70), (105, 75), (170, 66), (140, 44), (126, 34), (122, 22), (106, 12), (96, 16), (78, 8), (68, 24), (56, 26), (44, 14), (35, 31)],
        [(114, -22), (132, -12), (153, -24), (148, -38), (132, -33), (116, -34)],
    ]
    for poly in continents:
        draw.polygon([ll(lo, la) for lo, la in poly], fill=land, outline=coast)

    pins = [
        (1, -77, 39, "N. AMERICA"),   # Washington USTR
        (2, 127, 37, "EAST ASIA"),    # Seoul Kospi
        (3, 100, 41, "EAST ASIA"),    # Jiuquan Shenzhou-24
        (4, 90, 24, "S & SE ASIA"),   # Dhaka wage
        (5, 31, 30, "AFRICA"),        # Cairo Giza
        (6, 0, 52, "EUROPE"),         # London Ofgem
        (7, 149, -35, "OCEANIA"),     # Canberra/Solomons
        (8, -74, 41, "GLOBAL"),       # UNODC NY
        (9, 32, 49, "EUROPE"),        # Ukraine 5 regions
        (10, 18, -34, "AFRICA"),      # Cape Town Phala Phala
        (11, 35, 31, "M. EAST"),      # Jerusalem Case 4000
        (12, 43, 15, "M. EAST"),      # Hodeidah/Ras Tanura
        (13, -75, 10, "LAT. AM."),    # Cartagena Colombia
    ]
    for num, lon, lat, reg in pins:
        px, py = ll(lon, lat)
        _pin(draw, px, py, num, bg=REGION_COLORS[reg], r=6)


def main():
    img = Image.new("RGB", (W, H), BG)
    _draw_parchment_grain(img)
    draw = ImageDraw.Draw(img)

    # Top bar
    draw.text((14, 10), "THE WORLD IN ONE DAY", font=F(SANS_BOLD_PATH, 9), fill=MUTED)
    tr = "50 STORIES · 9 REGIONS · EVERY ONE FIRST REPORTED WED 25 NOV 2026"
    draw.text((1010 - _tw(draw, tr, F(SANS_BOLD_PATH, 9)), 10), tr, font=F(SANS_BOLD_PATH, 9), fill=CRIMSON)
    draw.line([(14, 24), (1010, 24)], fill=DARK_RULE, width=2)

    # Masthead
    m_txt = "Wednesday 25 November 2026"
    m_f = F(SERIF_BOLD_PATH, 45)
    draw.text(((W - _tw(draw, m_txt, m_f)) // 2, 27), m_txt, font=m_f, fill=INK)
    sub = "US proposes tariffs on 14 economies · AI doubts sink Asian chips · Pakistan's first astronaut reaches Tiangong"
    sub_f = F(SERIF_ITAL_PATH, 12)
    draw.text(((W - _tw(draw, sub, sub_f)) // 2, 79), sub, font=sub_f, fill=MUTED)

    # 6 KPI metrics
    kpis = [
        ("35%", "top US 301 tariff (Vietnam); China 20% (1)", CRIMSON),
        ("-6.2%", "Kospi close 4,697.51; Hynix -11.1% (2)", CRIMSON),
        ("1st", "Pakistani reaches Tiangong at 03:56 UTC (3)", BLUE_OFF),
        ("31+", "killed in Cairo ring-road tanker blaze (5)", CRIMSON),
        ("+26%", "UK Ofgem cap lifted to £2,166/yr (6)", CRIMSON),
        ("+36%", "Dhaka garment pay raised to 17,000 tk (4)", GREEN_CONF),
    ]
    tot_w = 996
    kw = tot_w / 6.0
    for i, (num_s, desc, col) in enumerate(kpis):
        kx = int(14 + i * kw)
        if i > 0:
            draw.line([(kx - 6, 98), (kx - 6, 134)], fill=RULE, width=1)
        draw.text((kx, 97), num_s, font=F(SERIF_BOLD_PATH, 18), fill=col)
        _draw_lines(draw, kx, 118, desc, F(SANS_REG_PATH, 8), MUTED, int(kw - 10), 9, 2)

    # Region bar (sum = 50 exact count)
    segs = [
        ("EUROPE 12", 12, REGION_COLORS["EUROPE"]),
        ("N. AMERICA 9", 9, REGION_COLORS["N. AMERICA"]),
        ("M. EAST 7", 7, REGION_COLORS["M. EAST"]),
        ("AFRICA 6", 6, REGION_COLORS["AFRICA"]),
        ("E. ASIA 5", 5, REGION_COLORS["EAST ASIA"]),
        ("OCEANIA 5", 5, REGION_COLORS["OCEANIA"]),
        ("LAT 3", 3, REGION_COLORS["LAT. AM."]),
        ("SEA 2", 2, REGION_COLORS["S & SE ASIA"]),
        ("1", 1, REGION_COLORS["GLOBAL"]),
    ]
    ry0, ry1 = 140, 154
    cur_x = 14
    f_seg = F(SANS_BOLD_PATH, 8)
    for idx, (lbl, cnt, col) in enumerate(segs):
        sw = int(round(tot_w * (cnt / 50.0))) if idx < len(segs) - 1 else (1010 - cur_x)
        draw.rectangle([cur_x, ry0, cur_x + sw - 1, ry1], fill=col)
        tw = _tw(draw, lbl, f_seg)
        if tw + 2 < sw:
            draw.text((cur_x + (sw - tw) // 2, ry0 + 2), lbl, font=f_seg, fill=WHITE)
        cur_x += sw

    # UTC ticker
    draw.rectangle([14, 158, 108, 173], fill=INK)
    draw.text((21, 160), "THE DAY IN UTC", font=F(SANS_BOLD_PATH, 8), fill=GOLD)
    draw.rectangle([108, 158, 1010, 173], fill=(238, 232, 220), outline=RULE)
    ticks = [
        ("00:18", "Shenzhou-24 liftoff"),
        ("00:30", "Aus CPI 4.9%"),
        ("03:56", "Tiangong dock"),
        ("06:30", "Kospi 4,697.51"),
        ("07:00", "Ofgem +26%"),
        ("13:30", "US GDP 4.3%"),
        ("15:00", "USTR 14-nation"),
    ]
    tx = 116
    for tm, ev in ticks:
        draw.text((tx, 160), tm, font=F(SANS_BOLD_PATH, 8), fill=CRIMSON)
        tx += _tw(draw, tm, F(SANS_BOLD_PATH, 8)) + 3
        draw.text((tx, 160), ev, font=F(SANS_REG_PATH, 8), fill=INK)
        tx += _tw(draw, ev, F(SANS_REG_PATH, 8)) + 13

    # Top 3 Hero Cards with WHY IT MATTERS
    heroes = [
        (
            1, _draw_hero1, "N. AMERICA", "WASHINGTON · TRADE", "OFFICIAL",
            "US proposes tariffs up to 35% on 14 economies",
            "USTR cites excess capacity: Vietnam up to 35%, India 25%, China 20%, EU 15%. USTR · Reuters",
            "Broadest Section 301 salvo; hearings open in Jan.",
        ),
        (
            2, _draw_hero2, "EAST ASIA", "SEOUL · TAIPEI · TOKYO", "CONFIRMED",
            "AI doubts sink Asian chips; Kospi drops 6.2%",
            "Kospi closes -6.16% at 4,697.51; SK Hynix -11.1%, Samsung -9.9%, Taiex -4.8%. Yonhap · Reuters",
            "Sharpest test of AI hardware spending boom.",
        ),
        (
            3, _draw_hero3, "EAST ASIA", "JIUQUAN · ORBIT · SPACE", "OFFICIAL",
            "Shenzhou-24 flies Pakistan's 1st astronaut",
            "Muhammad Zeeshan Ali (40) lifts off 00:18 UTC with Chinese crew, docks 03:56 UTC. Xinhua · AA",
            "China's station receives its first foreign guest.",
        ),
    ]
    hc_w = 324
    hc_gap = 12
    hy0 = 179
    art_h = 94
    for idx, (num, fn, reg, loc, cert, hd, dk, wim) in enumerate(heroes):
        hx = 14 + idx * (hc_w + hc_gap)
        fn(draw, hx, hy0, hx + hc_w, hy0 + art_h)
        my = hy0 + art_h + 4
        draw.text((hx, my), loc, font=F(SANS_BOLD_PATH, 8), fill=REGION_COLORS[reg])
        _cert_badge(draw, hx + hc_w, my - 1, cert)
        ny = _draw_lines(draw, hx, my + 12, hd, F(SERIF_BOLD_PATH, 14), INK, hc_w, 16, 2)
        _draw_lines(draw, hx, ny + 2, dk, F(SANS_REG_PATH, 8), MUTED, hc_w, 10, 2)
        draw.text((hx, hy0 + art_h + 74), "WHY IT MATTERS", font=F(SANS_BOLD_PATH, 7), fill=CRIMSON)
        draw.text((hx + 72, hy0 + art_h + 74), wim, font=F(SANS_REG_PATH, 8), fill=INK)

    # 10 Mid Cards (2 x 5 -> #4..#13)
    draw.line([(14, 365), (1010, 365)], fill=DARK_RULE, width=1)
    cards = [
        (4, "S & SE ASIA", "DHAKA · LABOUR", "OFFICIAL", "Bangladesh lifts garment pay 36% to 17,000 taka", "Wage board passes 4–2 hike (12,500->17k). Prothom Alo"),
        (5, "AFRICA", "GIZA, EGYPT", "OFFICIAL", "Fuel tanker blaze kills at least 31 on ring road", "Overturned tanker explodes in Al-Warraq; 20+ hurt. Health Min"),
        (6, "EUROPE", "LONDON · ENERGY", "OFFICIAL", "UK energy bills jump 26% to £2,166 from Jan", "Ofgem lifts cap from £1,723 for ~20m homes. Ofgem"),
        (7, "OCEANIA", "CANBERRA · PACT", "OFFICIAL", "Solomons sign A$740m Australia security pact", "Treaty bars foreign bases in Honiara. DFAT"),
        (8, "GLOBAL", "UNITED NATIONS", "OFFICIAL", "UNODC: 47,000 women killed by partner/kin", "5 killed/hr globally; Africa 2.9/100k. UNODC"),
        (9, "EUROPE", "UKRAINE · WAR", "OFFICIAL", "Russian strikes cut power across 5 regions", "Energy grids hit; Zaporizhzhia strained. Kyiv Post"),
        (10, "AFRICA", "CAPE TOWN · COURT", "OFFICIAL", "High Court voids Phala Phala report", "Bench dissolves impeachment panel. Daily Maverick"),
        (11, "M. EAST", "JERUSALEM · TRIAL", "OFFICIAL", "Judges urge dropping Netanyahu bribe charge", "Panel cites weak proof in Case 4000. Tol"),
        (12, "M. EAST", "HODEIDAH · YEMEN", "CONFIRMED", "Coalition hits Hodeidah; Saudis down 4 drones", "Air defences intercept 4 drones over Ras Tanura. AP"),
        (13, "LAT. AM.", "CARTAGENA · CRIME", "CONFIRMED", "Police storm Éxito store, free 20 hostages", "Dawn raid ends 24-hr siege; 1 captor killed. CBS"),
    ]
    cw = 191
    c_gap = 10
    c_art_h = 58
    row_ys = [370, 492]
    for idx, (num, reg, loc, cert, hd, dk) in enumerate(cards):
        r_idx = idx // 5
        c_idx = idx % 5
        cx = 14 + c_idx * (cw + c_gap)
        cy = row_ys[r_idx]
        _draw_mid_art(draw, num, reg, cx, cy, cx + cw, cy + c_art_h)
        ty = cy + c_art_h + 4
        draw.text((cx, ty), loc, font=F(SANS_BOLD_PATH, 7), fill=REGION_COLORS[reg])
        _cert_badge(draw, cx + cw, ty - 1, cert)
        ny = _draw_lines(draw, cx, ty + 10, hd, F(SERIF_BOLD_PATH, 11), INK, cw, 12, 2)
        _draw_lines(draw, cx, ny + 2, dk, F(SANS_REG_PATH, 8), MUTED, cw, 10, 2)

    # Bottom section: Map (1..13) + 37 Briefs (#14..#50)
    by0 = 620
    draw.line([(14, by0 - 4), (1010, by0 - 4)], fill=DARK_RULE, width=1)
    draw.text((14, by0 + 1), "WHERE IT HAPPENED · STORIES 1–13", font=F(SANS_BOLD_PATH, 9), fill=INK)
    _draw_world_map(draw, 14, by0 + 16, 316, 868)
    leg = [
        ("EUR 12", "EUROPE"), ("NA 9", "N. AMERICA"), ("ME 7", "M. EAST"),
        ("AFR 6", "AFRICA"), ("EA 5", "EAST ASIA"), ("OCE 5", "OCEANIA"),
        ("LAT 3", "LAT. AM."), ("SEA 2", "S & SE ASIA"), ("GL 1", "GLOBAL"),
    ]
    for idx, (lbl, reg) in enumerate(leg):
        lx = 14 + (idx % 3) * 102
        ly = 875 + (idx // 3) * 12
        draw.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=REGION_COLORS[reg])
        draw.text((lx + 11, ly), lbl, font=F(SANS_BOLD_PATH, 8), fill=INK)

    # 37 Briefs (#14..#50) with region color number squares
    draw.text((330, by0 + 1), "ALSO ON WEDNESDAY — 37 MORE VERIFIED STORIES", font=F(SANS_BOLD_PATH, 9), fill=INK)
    draw.text((642, by0 + 1), "NUMBERED & COLOUR-MATCHED BY REGION", font=F(SANS_REG_PATH, 8), fill=MUTED)

    briefs = [
        (14, "EUROPE", "STRASBOURG:", "EU unveils Quantum Act & €50bn tech fund (O)"),
        (15, "EUROPE", "SAMARA:", "Ukrainian drones hit Syzran & Kuibyshev refineries (R)"),
        (16, "N. AMERICA", "WASHINGTON:", "US Q3 real GDP revised up to 4.3% by BEA (O)"),
        (17, "OCEANIA", "CANBERRA:", "Australia October CPI inflation rises to 4.9% (O)"),
        (18, "EUROPE", "BRUSSELS:", "Puigdemont sets Dec 12 to end 9-yr Spain exile (C)"),
        (19, "EUROPE", "LONDON:", "easyJet net profit plunges 96% to £20m on fuel (C)"),
        (20, "N. AMERICA", "IOWA:", "US Army detonates 5t degraded lead azide safely (O)"),
        (21, "M. EAST", "HORMUZ:", "IRGC says 2 tankers hit mines & burn in Strait (CLAIM)"),
        (22, "M. EAST", "JERUSALEM:", "Knesset votes 65–50 for Oct 7 inquiry panel (O)"),
        (23, "OCEANIA", "ANTARCTICA:", "Shallow M5.9 Balleny quake leads 3 tremors (O)"),
        (24, "AFRICA", "ENUGU:", "Nollywood icon Pete Edochie dies aged 79 (C)"),
        (25, "EUROPE", "LONDON:", "Tube strike halts Circle & Piccadilly from 10:00 UTC (C)"),
        (26, "EUROPE", "LONDON:", "Independent review finds Met Police still racist (O)"),
        (27, "EUROPE", "BRUSSELS:", "EU sanctions 15 firms tied to Russian arms chain (O)"),
        (28, "EUROPE", "BERN:", "EU and Switzerland seal updated bilateral pacts (O)"),
        (29, "EUROPE", "DARMSTADT:", "ESA Hera shows first close-up images of Dimorphos (O)"),
        (30, "EUROPE", "GENEVA:", "FIDE World Chess: Gukesh & Sindarov draw Game 1 (C)"),
        (31, "OCEANIA", "CANBERRA:", "Parliament apologises to LGBTQ+ military veterans (O)"),
        (32, "OCEANIA", "HOBART:", "Flinders Is. bushfire prompts emergency evacuations (O)"),
        (33, "M. EAST", "DOHA:", "Sooryavanshi, 15, smashes fastest List A 204 off 53b (C)"),
        (34, "M. EAST", "GAZA CITY:", "Strikes kill at least 4 in Shati camp despite truce (R)"),
        (35, "M. EAST", "TEHRAN:", "Iran orders winter gas rationing as cold wave hits (R)"),
        (36, "EAST ASIA", "SHANGHAI:", "Officials pledge loyalty amid Chen Jining probe (R)"),
        (37, "EAST ASIA", "SEOUL:", "Births jump 12.2% YoY; subway strike averted (O)"),
        (38, "EAST ASIA", "TAIPEI:", "BBC Verify traces China-linked deepfake campaign (C)"),
        (39, "AFRICA", "KHARTOUM:", "Sudan rejects Ethiopia peace talks amid clashes (C)"),
        (40, "AFRICA", "GAUTENG:", "Johannesburg enforces Level-2 water grid curbs (O)"),
        (41, "AFRICA", "MONROVIA:", "Liberia advances $5.7bn Bea Mountain agreement (C)"),
        (42, "N. AMERICA", "WASHINGTON:", "NATO chief Rutte holds Mar-a-Lago talks w/ Trump (C)"),
        (43, "N. AMERICA", "CHICAGO:", "81.5m Thanksgiving travelers face storm delays (C)"),
        (44, "N. AMERICA", "NEW YORK:", "Dow erases 1,100-pt slide to close slightly higher (C)"),
        (45, "N. AMERICA", "IOWA / EPA:", "5-mile safety cordon cleared after Army munitions blast (O)"),
        (46, "N. AMERICA", "WASHINGTON:", "Section 301 hearings set for January over excess capacity (O)"),
        (47, "N. AMERICA", "OTTAWA:", "Canada reviews Arctic aerospace response protocols (R)"),
        (48, "LAT. AM.", "BRASÍLIA:", "Brazil permanently recalls ambassador to Argentina (O)"),
        (49, "LAT. AM.", "CARTAGENA:", "President confirms zero civilian casualties in raid (O)"),
        (50, "S & SE ASIA", "JAKARTA:", "OECD chief Cormann meets Prabowo on accession (O)"),
    ]
    col_x = [330, 676]
    f_num = F(SANS_BOLD_PATH, 7)
    f_loc = F(SANS_BOLD_PATH, 7)
    f_txt = F(SANS_REG_PATH, 7)
    for idx, (num, reg, loc, txt) in enumerate(briefs):
        col_i = 0 if idx < 19 else 1
        row_i = idx if idx < 19 else idx - 19
        bx = col_x[col_i]
        by = by0 + 16 + row_i * 15
        draw.rectangle([bx, by + 1, bx + 13, by + 11], fill=REGION_COLORS[reg])
        ns = str(num)
        draw.text((bx + (13 - _tw(draw, ns, f_num)) // 2, by + 2), ns, font=f_num, fill=WHITE)
        draw.text((bx + 17, by + 2), loc, font=f_loc, fill=INK)
        lw = _tw(draw, loc, f_loc)
        draw.text((bx + 20 + lw, by + 2), txt, font=f_txt, fill=MUTED)

    # DATE CHECK box
    dc_y0, dc_y1 = 924, 964
    draw.rectangle([14, dc_y0, 1010, dc_y1], fill=(241, 234, 224), outline=RULE)
    draw.rectangle([14, dc_y0, 19, dc_y1], fill=CRIMSON)
    draw.text((26, dc_y0 + 5), "DATE CHECK:", font=F(SANS_BOLD_PATH, 8), fill=CRIMSON)
    dc_body = (
        "Every story above broke or first appeared on Wed 25 Nov 2026 (UTC). Left out as prior days: "
        "Mon 23 Nov: Huang Nvidia return, West Java gold-pit flood onset, leaked Russia war dead; "
        "Tue 24 Nov: WHO Congo Akwe clinic exit, Riyadh PIF strike, CAS Senegal AFCON ruling, Huawei Brooklyn verdict; "
        "Sun 22 Nov: COP31 collapse, 188-drone Kyiv raid."
    )
    _draw_lines(draw, 94, dc_y0 + 5, dc_body, F(SANS_REG_PATH, 8), INK, 906, 11, 3)

    # HOW SURE inline bar & sources
    lx = 14
    draw.text((lx, 969), "HOW SURE:", font=F(SANS_BOLD_PATH, 8), fill=INK)
    lx += _tw(draw, "HOW SURE:", F(SANS_BOLD_PATH, 8)) + 6
    for cert, desc, bd_c in [
        ("O / OFFICIAL", "agency or court record", BLUE_OFF),
        ("C / CONFIRMED", "2+ major outlets", GREEN_CONF),
        ("R / REPORTED", "single wire", GRAY_REP),
        ("CLAIM", "one-sided account", AMBER_CLAIM),
    ]:
        draw.text((lx, 969), cert, font=F(SANS_BOLD_PATH, 8), fill=bd_c)
        lx += _tw(draw, cert, F(SANS_BOLD_PATH, 8)) + 4
        draw.text((lx, 969), desc + "   ", font=F(SANS_REG_PATH, 8), fill=MUTED)
        lx += _tw(draw, desc + "   ", F(SANS_REG_PATH, 8)) + 4

    draw.text((14, 983), "SOURCES: REUTERS · USTR · BEA · ABS · OFGEM · UNODC · DFAT · XINHUA · PROTHOM ALO · AP · AFP · CBS · ESA · FIDE · YONHAP", font=F(SANS_BOLD_PATH, 7), fill=MUTED)
    rt = "Original vector code art · no photos"
    draw.text((1010 - _tw(draw, rt, F(SANS_REG_PATH, 7)), 983), rt, font=F(SANS_REG_PATH, 7), fill=MUTED)

    draw.rectangle([0, 998, W, H], fill=INK)
    draw.text((14, 1005), "THE WORLD IN ONE DAY · BUILT FOR MAKE.FUN", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
    fr = "WEDNESDAY 25 NOVEMBER 2026 · ONE DAY, ONE PAGE"
    draw.text((1010 - _tw(draw, fr, F(SANS_BOLD_PATH, 8)), 1005), fr, font=F(SANS_BOLD_PATH, 8), fill=GOLD)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    print(f"Generated v7 {out_path}: {os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    main()
