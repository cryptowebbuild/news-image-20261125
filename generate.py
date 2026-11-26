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
    "E & SE ASIA": (182, 42, 42),
    "N. AMERICA": (24, 108, 164),
    "M. EAST": (196, 104, 24),
    "LAT. AM.": (164, 76, 38),
    "SUB-SAH.": (118, 48, 128),
    "OCEANIA": (22, 118, 68),
    "N. AFRICA": (152, 62, 112),
    "SOUTH ASIA": (22, 130, 88),
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
    fnt = F(SANS_BOLD_PATH, 8)
    bw = _tw(draw, cert, fnt) + 9
    bh = 13
    draw.rounded_rectangle([x_right - bw, y, x_right, y + bh], radius=2, fill=bg, outline=bd, width=1)
    draw.text((x_right - bw + 4, y + 2), cert, font=fnt, fill=fg)
    return bw


def _pin(draw, cx, cy, num, bg=CRIMSON, r=8, ring=WHITE):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=ring, width=1)
    fnt = F(SANS_BOLD_PATH, 9 if r >= 8 else 7)
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
    rng = random.Random(202611258)
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
    # USTR Section 301 Tariffs on 14 Economies
    _grad_v(draw, x0, y0, x1, y0 + 76, (24, 36, 62), (48, 72, 112))
    _grad_v(draw, x0, y0 + 76, x1, y1, (26, 68, 108), (18, 44, 78))
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
        draw.rectangle([px, y0 + 10, px + pw, y0 + 24], fill=col)
        draw.text((px + 5, y0 + 12), txt, font=f_p, fill=WHITE)
        px += pw + 6
    draw.polygon([(x0 + 46, y0 + 74), (x0 + 286, y0 + 74), (x0 + 270, y0 + 90), (x0 + 58, y0 + 90)], fill=(38, 44, 52))
    draw.rectangle([x0 + 46, y0 + 70, x0 + 286, y0 + 74], fill=CRIMSON)
    draw.rectangle([x0 + 236, y0 + 44, x0 + 266, y0 + 70], fill=(236, 238, 242), outline=(140, 148, 160))
    draw.rectangle([x0 + 244, y0 + 50, x0 + 258, y0 + 56], fill=(32, 42, 62))
    stack_cols = [(178, 36, 36), (26, 82, 148), (22, 118, 66), (202, 106, 24), (118, 48, 128), (178, 36, 36)]
    for row in range(2):
        for col_i in range(6):
            cx0 = x0 + 70 + col_i * 27
            cy0 = y0 + 58 - row * 12
            draw.rectangle([cx0, cy0, cx0 + 24, cy0 + 10], fill=stack_cols[(col_i + row * 2) % len(stack_cols)], outline=(24, 28, 34))
    _stipple(draw, x0 + 8, y0 + 80, x1 - 8, y1 - 4, 701, 55, [(74, 124, 166), (38, 86, 128)], 1)
    _ribbon(draw, x0 + 30, y1 - 18, "14 ECONOMIES · 15–35%", bg=(14, 20, 32))
    _pin(draw, x0 + 14, y1 - 14, 1, bg=REGION_COLORS["N. AMERICA"])


def _draw_hero2(draw, x0, y0, x1, y1):
    # Kospi -6.2% close 4,697.51
    _grad_v(draw, x0, y0, x1, y1, (22, 24, 30), (36, 22, 24))
    for gx in range(x0 + 16, x0 + 178, 26):
        draw.line([(gx, y0 + 18), (gx, y1 - 6)], fill=(44, 48, 58), width=1)
    for gy in range(y0 + 24, y1 - 6, 18):
        draw.line([(x0 + 6, gy), (x0 + 178, gy)], fill=(44, 48, 58), width=1)
    pts = [(x0 + 8, y0 + 28), (x0 + 40, y0 + 34), (x0 + 76, y0 + 50), (x0 + 114, y0 + 72), (x0 + 146, y0 + 88), (x0 + 172, y0 + 100)]
    draw.polygon(pts + [(x0 + 172, y1 - 2), (x0 + 8, y1 - 2)], fill=(120, 28, 30))
    draw.line(pts, fill=(248, 86, 72), width=3)
    draw.ellipse([x0 + 168, y0 + 96, x0 + 176, y0 + 104], fill=(255, 210, 92))
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
        ry = by0 + 7 + i * row_h
        draw.text((bx0 + 8, ry), k, font=f_l, fill=(214, 220, 232))
        tw = _tw(draw, v, f_l)
        draw.text((bx1 - tw - 8, ry), v, font=f_l, fill=(252, 92, 84))
    _ribbon(draw, x0, y0, "KOSPI CLOSE 4,697.51", bg=(14, 20, 32))
    _pin(draw, x0 + 14, y1 - 14, 2, bg=REGION_COLORS["E & SE ASIA"])


def _draw_hero3(draw, x0, y0, x1, y1):
    # Shenzhou-24 docks Tiangong w/ Pakistan's 1st astronaut
    _grad_v(draw, x0, y0, x1, y1, (8, 16, 38), (20, 44, 88))
    _stipple(draw, x0, y0 + 16, x1, y1 - 24, 303, 130, [(200, 215, 255), (255, 255, 230), (130, 150, 200)], 1)
    draw.polygon([
        (x0, y1), (x0, y1 - 12),
        (x0 + 80, y1 - 21), (x0 + 162, y1 - 24), (x0 + 244, y1 - 21),
        (x1, y1 - 12), (x1, y1),
    ], fill=(28, 92, 168))
    draw.line([(x0, y1 - 12), (x0 + 80, y1 - 21), (x0 + 162, y1 - 24), (x0 + 244, y1 - 21), (x1, y1 - 12)], fill=(138, 212, 255), width=2)
    rx = x0 + 58
    draw.polygon([(rx, y1 - 28), (rx - 12, y1 - 4), (rx + 12, y1 - 4)], fill=(242, 138, 34))
    draw.polygon([(rx, y1 - 33), (rx - 6, y1 - 6), (rx + 6, y1 - 6)], fill=(255, 224, 102))
    draw.polygon([(rx, y0 + 22), (rx - 5, y0 + 34), (rx + 5, y0 + 34)], fill=(244, 245, 248))
    draw.rectangle([rx - 5, y0 + 34, rx + 5, y1 - 32], fill=(238, 240, 244), outline=(170, 178, 192))
    draw.rectangle([rx - 9, y1 - 54, rx - 5, y1 - 32], fill=(214, 218, 226))
    draw.rectangle([rx + 5, y1 - 54, rx + 9, y1 - 32], fill=(214, 218, 226))
    for i in range(10):
        t = i / 9.0
        px = int(rx + 16 + t * 112)
        py = int((y0 + 34) + math.sin(t * 2.2) * -12 + 24 * (1 - t))
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 206, 74))
    sx, sy = x0 + 232, y0 + 54
    for dx in (-34, -20, 14, 28):
        draw.rectangle([sx + dx, sy - 22, sx + dx + 8, sy + 22], fill=(38, 86, 152), outline=(120, 174, 232))
    draw.rectangle([sx - 40, sy - 3, sx + 40, sy + 3], fill=(208, 214, 224))
    draw.rectangle([sx - 16, sy - 6, sx + 16, sy + 6], fill=(246, 248, 252))
    fx, fy = x1 - 74, y0 + 20
    draw.rectangle([fx, fy, fx + 30, fy + 18], fill=(198, 30, 34), outline=WHITE)
    draw.ellipse([fx + 4, fy + 4, fx + 9, fy + 9], fill=(250, 210, 48))
    pxf = fx + 36
    draw.rectangle([pxf, fy, pxf + 30, fy + 18], fill=(18, 96, 52), outline=WHITE)
    draw.rectangle([pxf, fy, pxf + 8, fy + 18], fill=WHITE)
    draw.pieslice([pxf + 12, fy + 3, pxf + 24, fy + 15], 45, 285, fill=WHITE)
    _ribbon(draw, x0, y0, "00:18 UTC · DOCKS 03:56", bg=(14, 20, 32))
    _pin(draw, x0 + 14, y1 - 14, 3, bg=REGION_COLORS["E & SE ASIA"])


def _draw_mid_art(draw, num, reg, x0, y0, x1, y1):
    w = x1 - x0
    if num == 4:
        # UK Ofgem +26% to £2,166
        _grad_v(draw, x0, y0, x1, y1, (236, 242, 248), (248, 238, 224))
        hx = x0 + 46
        draw.polygon([(hx - 26, y0 + 40), (hx, y0 + 18), (hx + 26, y0 + 40)], fill=(142, 54, 46))
        draw.rectangle([hx - 21, y0 + 40, hx + 21, y1 - 8], fill=(224, 212, 194), outline=(170, 156, 140))
        draw.pieslice([hx - 9, y0 + 45, hx + 9, y0 + 67], 160, 380, fill=(24, 118, 206))
        draw.text((x0 + 92, y0 + 20), "+26%", font=F(SERIF_BOLD_PATH, 24), fill=CRIMSON)
        draw.text((x0 + 92, y0 + 48), "£1,723 -> £2,166", font=F(SANS_BOLD_PATH, 10), fill=BLUE_OFF)
        _ribbon(draw, x0, y0, "OFGEM CAP · 1 JAN", bg=BLUE_OFF)
    elif num == 5:
        # Cairo Ring Road tanker blaze 31+ dead
        _grad_v(draw, x0, y0, x1, y1, (38, 28, 28), (74, 40, 32))
        draw.rectangle([x0, y1 - 16, x1, y1], fill=(56, 56, 62))
        draw.rectangle([x0 + 44, y1 - 34, x0 + 122, y1 - 16], fill=(160, 166, 174), outline=DARK_RULE)
        draw.ellipse([x0 + 74, y0 + 18, x0 + 118, y0 + 58], fill=(238, 92, 22))
        draw.ellipse([x0 + 82, y0 + 26, x0 + 110, y0 + 50], fill=(255, 214, 64))
        draw.text((x0 + 134, y0 + 22), "31+", font=F(SERIF_BOLD_PATH, 24), fill=WHITE)
        draw.text((x0 + 134, y0 + 48), "DEAD", font=F(SANS_BOLD_PATH, 9), fill=(255, 196, 172))
        _ribbon(draw, x0, y0, "CAIRO RING ROAD", bg=CRIMSON)
    elif num == 6:
        # Ukraine 5 regions grid cuts
        _grad_v(draw, x0, y0, x1, y1, (24, 34, 56), (48, 56, 76))
        px = x0 + 58
        draw.line([(px, y0 + 18), (px - 18, y1 - 8)], fill=(190, 198, 210), width=2)
        draw.line([(px, y0 + 18), (px + 18, y1 - 8)], fill=(190, 198, 210), width=2)
        draw.line([(px - 22, y0 + 32), (px + 22, y0 + 32)], fill=(190, 198, 210), width=2)
        draw.polygon([(x0 + 106, y0 + 22), (x0 + 96, y0 + 42), (x0 + 104, y0 + 42), (x0 + 98, y0 + 60), (x0 + 116, y0 + 38), (x0 + 106, y0 + 38)], fill=(252, 208, 62))
        draw.text((x0 + 130, y0 + 20), "5", font=F(SERIF_BOLD_PATH, 24), fill=(252, 208, 62))
        draw.text((x0 + 130, y0 + 48), "REGIONS OUT", font=F(SANS_BOLD_PATH, 9), fill=WHITE)
        _ribbon(draw, x0, y0, "POWER GRID HIT", bg=(14, 20, 32))
    elif num == 7:
        # Dhaka garment pay +36%: 12,500 -> 17,000 TAKA
        _grad_v(draw, x0, y0, x1, y1, (238, 246, 238), (224, 238, 228))
        fx = x0 + 98
        draw.polygon([(fx, y1 - 14), (fx, y0 + 34), (fx + 32, y0 + 22), (fx + 32, y0 + 34), (fx + 64, y0 + 22), (fx + 64, y0 + 34), (fx + 96, y0 + 22), (fx + 96, y1 - 14)], fill=(192, 206, 196), outline=(140, 158, 146))
        draw.rectangle([x0 + 112, y0 + 46, x0 + 144, y1 - 8], fill=(128, 140, 136))
        draw.rectangle([x0 + 154, y0 + 28, x0 + 190, y1 - 8], fill=GREEN_CONF)
        draw.line([(x0 + 128, y0 + 44), (x0 + 172, y0 + 22)], fill=(18, 102, 54), width=3)
        draw.text((x0 + 12, y0 + 20), "+36%", font=F(SERIF_BOLD_PATH, 22), fill=GREEN_CONF)
        draw.text((x0 + 12, y0 + 46), "12.5k -> 17k tk", font=F(SANS_BOLD_PATH, 9), fill=INK)
        _ribbon(draw, x0, y0, "17,000 TAKA · 4–2 VOTE", bg=GREEN_CONF)
    elif num == 8:
        # Solomons & Australia A$740m pact
        _grad_v(draw, x0, y0, x1, y1, (228, 240, 248), (244, 241, 232))
        draw.polygon([(x0 + w // 2, y0 + 14), (x0 + 56, y1 - 14), (x1 - 56, y1 - 14)], fill=None, outline=(145, 162, 178), width=2)
        fx0, fy0 = x0 + 20, y0 + 20
        draw.rectangle([fx0, fy0, fx0 + 44, fy0 + 26], fill=(16, 48, 124), outline=WHITE)
        draw.line([(fx0, fy0 + 7), (fx0 + 20, fy0 + 7)], fill=CRIMSON, width=2)
        draw.line([(fx0 + 10, fy0), (fx0 + 10, fy0 + 14)], fill=CRIMSON, width=2)
        sx0 = x1 - 64
        draw.polygon([(sx0, fy0), (sx0 + 44, fy0), (sx0, fy0 + 26)], fill=(18, 86, 156))
        draw.polygon([(sx0 + 44, fy0), (sx0 + 44, fy0 + 26), (sx0, fy0 + 26)], fill=(24, 118, 64))
        draw.line([(sx0, fy0 + 26), (sx0 + 44, fy0)], fill=(238, 194, 42), width=3)
        draw.rounded_rectangle([x0 + 50, y1 - 21, x1 - 50, y1 - 6], radius=2, fill=(24, 52, 92))
        draw.text((x0 + 60, y1 - 18), "NO FOREIGN BASES", font=F(SANS_BOLD_PATH, 9), fill=WHITE)
        _ribbon(draw, x0, y0, "A$740M SECURITY PACT", bg=REGION_COLORS["OCEANIA"])
    elif num == 9:
        # South Africa High Court voids Phala Phala report
        _grad_v(draw, x0, y0, x1, y1, (242, 238, 230), (230, 224, 214))
        draw.line([(x0 + 36, y0 + 46), (x0 + 64, y0 + 24)], fill=(104, 64, 32), width=4)
        draw.rectangle([x0 + 56, y0 + 18, x0 + 76, y0 + 34], fill=(128, 78, 40))
        draw.rectangle([x0 + 28, y0 + 54, x0 + 78, y0 + 60], fill=(116, 70, 34))
        draw.rounded_rectangle([x0 + 98, y0 + 24, x1 - 22, y0 + 50], radius=3, fill=CRIMSON)
        draw.text((x0 + 114, y0 + 29), "VOIDED", font=F(SANS_BOLD_PATH, 15), fill=WHITE)
        _ribbon(draw, x0, y0, "HIGH COURT RULING", bg=REGION_COLORS["SUB-SAH."])
    elif num == 10:
        # Netanyahu Case 4000 judges urge dropping bribery charge
        _grad_v(draw, x0, y0, x1, y1, (244, 240, 234), (234, 228, 220))
        cx = x0 + 52
        draw.line([(cx, y0 + 20), (cx, y0 + 58)], fill=INK, width=2)
        draw.line([(cx - 20, y0 + 28), (cx + 20, y0 + 28)], fill=INK, width=2)
        draw.arc([cx - 26, y0 + 28, cx - 12, y0 + 48], 0, 180, fill=MUTED, width=2)
        draw.arc([cx + 12, y0 + 28, cx + 26, y0 + 48], 0, 180, fill=MUTED, width=2)
        draw.text((x0 + 94, y0 + 22), "CASE 4000", font=F(SANS_BOLD_PATH, 13), fill=INK)
        draw.text((x0 + 94, y0 + 42), "DROP BRIBE CHARGE", font=F(SANS_BOLD_PATH, 9), fill=CRIMSON)
        _ribbon(draw, x0, y0, "TRIAL PANEL", bg=BLUE_OFF)
    elif num == 11:
        # Cartagena Éxito siege ends: 20 hostages freed
        _grad_v(draw, x0, y0, x1, y1, (236, 244, 246), (222, 232, 236))
        draw.rectangle([x0 + 26, y0 + 22, x0 + 124, y1 - 12], fill=WHITE, outline=(120, 132, 146))
        draw.rectangle([x0 + 26, y0 + 22, x0 + 124, y0 + 36], fill=(238, 194, 42))
        draw.text((x0 + 56, y0 + 24), "ÉXITO", font=F(SANS_BOLD_PATH, 9), fill=INK)
        draw.rounded_rectangle([x0 + 134, y0 + 24, x1 - 24, y0 + 48], radius=2, fill=GREEN_CONF)
        draw.text((x0 + 144, y0 + 30), "ALL FREED", font=F(SANS_BOLD_PATH, 10), fill=WHITE)
        _ribbon(draw, x0, y0, "DAWN RAID · 20 SAVED", bg=REGION_COLORS["LAT. AM."])

    _pin(draw, x1 - 14, y1 - 13, num, bg=REGION_COLORS[reg], r=8)


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
        (2, 127, 37, "E & SE ASIA"),  # Seoul Kospi
        (3, 100, 41, "E & SE ASIA"),  # Jiuquan Shenzhou-24
        (4, 0, 52, "EUROPE"),         # London Ofgem
        (5, 31, 30, "N. AFRICA"),     # Cairo Giza
        (6, 32, 49, "EUROPE"),        # Ukraine
        (7, 90, 24, "SOUTH ASIA"),    # Dhaka wage
        (8, 149, -35, "OCEANIA"),     # Canberra/Solomons
        (9, 18, -34, "SUB-SAH."),     # Cape Town
        (10, 35, 31, "M. EAST"),      # Jerusalem Case 4000
        (11, -75, 10, "LAT. AM."),    # Cartagena
    ]
    for num, lon, lat, reg in pins:
        px, py = ll(lon, lat)
        _pin(draw, px, py, num, bg=REGION_COLORS[reg], r=7)


def main():
    img = Image.new("RGB", (W, H), BG)
    _draw_parchment_grain(img)
    draw = ImageDraw.Draw(img)

    # Top dateline
    draw.text((14, 10), "THE WORLD IN ONE DAY", font=F(SANS_BOLD_PATH, 9), fill=MUTED)
    tr = "35 DATED STORIES · 10 REGIONS · ALL FROM WEDNESDAY 25 NOV 2026"
    draw.text((1010 - _tw(draw, tr, F(SANS_BOLD_PATH, 9)), 10), tr, font=F(SANS_BOLD_PATH, 9), fill=CRIMSON)
    draw.line([(14, 24), (1010, 24)], fill=DARK_RULE, width=2)

    # Masthead
    m_txt = "Wednesday 25 November 2026"
    m_f = F(SERIF_BOLD_PATH, 46)
    draw.text(((W - _tw(draw, m_txt, m_f)) // 2, 27), m_txt, font=m_f, fill=INK)
    sub = "US proposes tariffs on 14 economies · AI doubts sink Asian chips · Pakistan's first astronaut reaches Tiangong"
    sub_f = F(SERIF_ITAL_PATH, 12)
    draw.text(((W - _tw(draw, sub, sub_f)) // 2, 79), sub, font=sub_f, fill=MUTED)

    # 6 KPI metrics
    kpis = [
        ("35%", "top US 301 tariff (Vietnam); China 20% (1)", CRIMSON),
        ("-6.2%", "Kospi closes at 4,697.51; Hynix -11.1% (2)", CRIMSON),
        ("1st", "Pakistani reaches Tiangong at 03:56 UTC (3)", BLUE_OFF),
        ("+26%", "UK Ofgem energy cap rises to £2,166 (4)", CRIMSON),
        ("31+", "killed in Cairo ring-road tanker fire (5)", CRIMSON),
        ("+36%", "Dhaka garment pay raised to 17,000 tk (7)", GREEN_CONF),
    ]
    tot_w = 996
    kw = tot_w / 6.0
    for i, (num_s, desc, col) in enumerate(kpis):
        kx = int(14 + i * kw)
        if i > 0:
            draw.line([(kx - 6, 98), (kx - 6, 134)], fill=RULE, width=1)
        draw.text((kx, 97), num_s, font=F(SERIF_BOLD_PATH, 18), fill=col)
        _draw_lines(draw, kx, 118, desc, F(SANS_REG_PATH, 8), MUTED, int(kw - 10), 10, 2)

    # 24 Briefs (#12..#35) defined cleanly so region bar sums automatically = 35
    briefs = [
        (12, "M. EAST", "Hodeidah:", "Coalition hits Hodeidah; Saudis down 4 drones (AP)"),
        (13, "M. EAST", "Hormuz:", "IRGC claims 2 tankers hit mines in Strait [CLAIM] (Reuters)"),
        (14, "EUROPE", "Samara:", "Ukrainian drones strike Syzran & Kuibyshev refineries (Kyiv Ind.)"),
        (15, "EUROPE", "Strasbourg:", "EU unveils Quantum Act & €50bn tech fund (Reuters)"),
        (16, "N. AMERICA", "Washington:", "US Q3 real GDP revised up to 4.3% annualized (BEA)"),
        (17, "N. AMERICA", "Iowa:", "US Army detonates 5t degraded lead azide safely (AP)"),
        (18, "EUROPE", "Brussels:", "Puigdemont sets Dec 12 date to end 9-year Spain exile (Al Jazeera)"),
        (19, "EUROPE", "London:", "easyJet net profit plunges 96% to £20m on fuel costs (Guardian)"),
        (20, "OCEANIA", "Canberra:", "Australia annual inflation jumps to 4.9% 3-yr high (ABS)"),
        (21, "OCEANIA", "Canberra:", "Parliament apologises to LGBTQ+ military veterans (DFAT)"),
        (22, "EUROPE", "London:", "Tube strike halts Circle & Piccadilly lines from 10:00 UTC (BBC)"),
        (23, "EUROPE", "London:", "Independent review finds Met Police remains racist (Guardian)"),
        (24, "EUROPE", "Brussels:", "EU sanctions 15 firms tied to Russian military complex (EU)"),
        (25, "EUROPE", "Darmstadt:", "ESA Hera shows first close-up images of Dimorphos (ESA)"),
        (26, "EUROPE", "Geneva:", "FIDE World Chess: Gukesh & Sindarov draw Game 1 (FIDE)"),
        (27, "LAT. AM.", "Brasília:", "Brazil permanently recalls ambassador to Argentina (AP)"),
        (28, "N. AMERICA", "Washington:", "NATO chief Rutte holds Mar-a-Lago talks w/ Trump (Reuters)"),
        (29, "N. AMERICA", "Chicago:", "81.5m Thanksgiving holiday travelers face storm delays (CNN)"),
        (30, "SUB-SAH.", "Enugu:", "Nollywood pioneer Pete Edochie dies aged 79 (VON)"),
        (31, "SUB-SAH.", "Khartoum:", "Sudan rejects Ethiopia peace talks amid clashes (Reuters)"),
        (32, "N. AFRICA", "Al-Warraq:", "At least 20+ injured alongside 31 dead in tanker blaze (Health Min)"),
        (33, "E & SE ASIA", "Jakarta:", "OECD chief Cormann meets Prabowo on accession (Antara)"),
        (34, "E & SE ASIA", "Seoul:", "Births jump 12.2% YoY; Seoul subway strike averted (Yonhap)"),
        (35, "GLOBAL", "UN / New York:", "UNODC reports 47,000 women killed by partner/kin (5/hr) (UN)"),
    ]
    counts = {k: 0 for k in REGION_COLORS}
    hero_regs = ["N. AMERICA", "E & SE ASIA", "E & SE ASIA"]
    card_regs = ["EUROPE", "N. AFRICA", "EUROPE", "SOUTH ASIA", "OCEANIA", "SUB-SAH.", "M. EAST", "LAT. AM."]
    for r in hero_regs + card_regs:
        counts[r] += 1
    for _, r, _, _ in briefs:
        counts[r] += 1

    segs = [(k, counts[k], REGION_COLORS[k]) for k in REGION_COLORS if counts[k] > 0]
    ry0, ry1 = 141, 156
    cur_x = 14
    f_seg = F(SANS_BOLD_PATH, 8)
    for idx, (lbl, cnt, col) in enumerate(segs):
        sw = int(round(tot_w * (cnt / 35.0))) if idx < len(segs) - 1 else (1010 - cur_x)
        draw.rectangle([cur_x, ry0, cur_x + sw - 1, ry1], fill=col)
        s_txt = f"{lbl} {cnt}" if sw > 48 else f"{cnt}"
        tw = _tw(draw, s_txt, f_seg)
        if tw + 2 < sw:
            draw.text((cur_x + (sw - tw) // 2, ry0 + 3), s_txt, font=f_seg, fill=WHITE)
        cur_x += sw

    # UTC ticker
    draw.rectangle([14, 160, 108, 176], fill=INK)
    draw.text((21, 163), "THE DAY IN UTC", font=F(SANS_BOLD_PATH, 8), fill=GOLD)
    draw.rectangle([108, 160, 1010, 176], fill=(238, 232, 220), outline=RULE)
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
        draw.text((tx, 163), tm, font=F(SANS_BOLD_PATH, 8), fill=CRIMSON)
        tx += _tw(draw, tm, F(SANS_BOLD_PATH, 8)) + 3
        draw.text((tx, 163), ev, font=F(SANS_REG_PATH, 8), fill=INK)
        tx += _tw(draw, ev, F(SANS_REG_PATH, 8)) + 13

    # Top 3 Hero Cards
    heroes = [
        (
            1, _draw_hero1, "N. AMERICA", "WASHINGTON · TRADE", "OFFICIAL",
            "US proposes tariffs up to 35% on 14 economies",
            "USTR cites excess capacity: Vietnam 35%, India 25%, China 20%, EU 15% (Greer). USTR · Reuters",
            "Broadest Section 301 salvo; hearings open in Jan.",
        ),
        (
            2, _draw_hero2, "E & SE ASIA", "SEOUL · TAIPEI · TOKYO", "CONFIRMED",
            "AI doubts sink Asian chips; Kospi drops 6.2%",
            "Kospi closes at 4,697.51 (-6.16%); SK Hynix -11.1%, Samsung -9.9%, Taiex -4.8%. Yonhap · Reuters",
            "Sharpest test yet of AI hardware spending boom.",
        ),
        (
            3, _draw_hero3, "E & SE ASIA", "JIUQUAN · ORBIT · SPACE", "OFFICIAL",
            "Shenzhou-24 flies Pakistan's 1st astronaut",
            "Muhammad Zeeshan Ali (40) lifts off 00:18 UTC with Chinese crew and docks 03:56 UTC. Xinhua · AA",
            "First foreign national aboard China's orbital lab.",
        ),
    ]
    hc_w = 324
    hc_gap = 12
    hy0 = 182
    art_h = 104
    for idx, (num, fn, reg, loc, cert, hd, dk, wim) in enumerate(heroes):
        hx = 14 + idx * (hc_w + hc_gap)
        fn(draw, hx, hy0, hx + hc_w, hy0 + art_h)
        my = hy0 + art_h + 5
        draw.text((hx, my), loc, font=F(SANS_BOLD_PATH, 8), fill=REGION_COLORS[reg])
        _cert_badge(draw, hx + hc_w, my - 1, cert)
        ny = _draw_lines(draw, hx, my + 14, hd, F(SERIF_BOLD_PATH, 16), INK, hc_w, 18, 2)
        _draw_lines(draw, hx, ny + 3, dk, F(SANS_REG_PATH, 9), MUTED, hc_w, 12, 2)
        draw.text((hx, hy0 + art_h + 83), "WHY IT MATTERS", font=F(SANS_BOLD_PATH, 7), fill=CRIMSON)
        draw.text((hx + 72, hy0 + art_h + 83), wim, font=F(SANS_REG_PATH, 8), fill=INK)

    # 8 Spacious Mid Cards (2 x 4 grid -> 240px wide each -> #4..#11)
    draw.line([(14, 386), (1010, 386)], fill=DARK_RULE, width=1)
    cards = [
        (4, "EUROPE", "LONDON · ENERGY", "OFFICIAL", "UK energy price cap jumps 26% to £2,166", "Ofgem lifts annual household bill from £1,723 (1 Jan). Ofgem"),
        (5, "N. AFRICA", "GIZA, EGYPT · DISASTER", "OFFICIAL", "Fuel tanker blaze kills at least 31 on ring road", "Overturned truck explodes in Al-Warraq; 20+ hurt. AP"),
        (6, "EUROPE", "UKRAINE · WAR", "OFFICIAL", "Russian strikes cut power across 5 regions", "Grid attacks put Zaporizhzhia plant on diesel strain. Kyiv Post"),
        (7, "SOUTH ASIA", "DHAKA · LABOUR", "OFFICIAL", "Bangladesh lifts garment pay 36% to 17,000 tk", "Wage board votes 4–2 up from 12,500 taka. Prothom Alo"),
        (8, "OCEANIA", "CANBERRA · DIPLOMACY", "OFFICIAL", "Solomon Islands pact bars foreign bases", "A$740m treaty names Australia security partner. DFAT"),
        (9, "SUB-SAH.", "CAPE TOWN · JUSTICE", "OFFICIAL", "High Court voids Phala Phala report", "Unanimous bench dissolves impeachment panel. Maverick"),
        (10, "M. EAST", "JERUSALEM · JUSTICE", "OFFICIAL", "Judges urge dropping Netanyahu bribe charge", "Court cites weak proof in Case 4000 bribery trial. ToI"),
        (11, "LAT. AM.", "CARTAGENA · CRIME", "CONFIRMED", "Colombian forces free all 20 hostages", "Dawn raid ends 24-hr Éxito siege; 1 captor dead. CBS"),
    ]
    cw = 240
    c_gap = 12
    c_art_h = 66
    row_ys = [392, 526]
    for idx, (num, reg, loc, cert, hd, dk) in enumerate(cards):
        r_idx = idx // 4
        c_idx = idx % 4
        cx = 14 + c_idx * (cw + c_gap)
        cy = row_ys[r_idx]
        _draw_mid_art(draw, num, reg, cx, cy, cx + cw, cy + c_art_h)
        ty = cy + c_art_h + 4
        draw.text((cx, ty), loc, font=F(SANS_BOLD_PATH, 8), fill=REGION_COLORS[reg])
        _cert_badge(draw, cx + cw, ty - 1, cert)
        ny = _draw_lines(draw, cx, ty + 14, hd, F(SERIF_BOLD_PATH, 12), INK, cw, 14, 2)
        _draw_lines(draw, cx, ny + 2, dk, F(SANS_REG_PATH, 8), MUTED, cw, 11, 2)

    # Bottom section: Map (1..11) + 24 Readable Briefs (#12..#35)
    by0 = 664
    draw.line([(14, by0 - 4), (1010, by0 - 4)], fill=DARK_RULE, width=1)
    draw.text((14, by0 + 1), "WHERE IT HAPPENED · STORIES 1–11", font=F(SANS_BOLD_PATH, 9), fill=INK)
    _draw_world_map(draw, 14, by0 + 16, 316, 846)

    # Region legend below map (2 cols x 5 rows -> no overlap!)
    for idx, (lbl, cnt, col) in enumerate(segs):
        lx = 14 + (idx % 2) * 154
        ly = 852 + (idx // 2) * 12
        draw.rectangle([lx, ly + 1, lx + 8, ly + 8], fill=col)
        draw.text((lx + 11, ly), f"{lbl} ({cnt})", font=F(SANS_BOLD_PATH, 7), fill=INK)

    # Inline HOW SURE cleanly below legend
    draw.text((14, 915), "HOW SURE:", font=F(SANS_BOLD_PATH, 7), fill=INK)
    lx = 64
    for cert, desc, bd_c in [
        ("OFFICIAL", "agency/court", BLUE_OFF),
        ("CONFIRMED", "2+ outlets", GREEN_CONF),
        ("CLAIM", "unverified", AMBER_CLAIM),
    ]:
        draw.text((lx, 915), cert, font=F(SANS_BOLD_PATH, 7), fill=bd_c)
        lx += _tw(draw, cert, F(SANS_BOLD_PATH, 7)) + 3
        draw.text((lx, 915), desc, font=F(SANS_REG_PATH, 7), fill=MUTED)
        lx += _tw(draw, desc, F(SANS_REG_PATH, 7)) + 5

    # Right 24 Briefs (#12..#35) in 12 crisp readable rows x 2 cols
    draw.text((330, by0 + 1), "ALSO ON WEDNESDAY 25 NOVEMBER — 24 MORE DATED STORIES", font=F(SANS_BOLD_PATH, 9), fill=INK)
    draw.text((905, by0 + 1), "every item sourced", font=F(SANS_REG_PATH, 8), fill=MUTED)

    col_x = [330, 676]
    f_num = F(SANS_BOLD_PATH, 8)
    f_loc = F(SANS_BOLD_PATH, 8)
    f_txt = F(SANS_REG_PATH, 8)
    for idx, (num, reg, loc, txt) in enumerate(briefs):
        col_i = idx // 12
        row_i = idx % 12
        bx = col_x[col_i]
        by = by0 + 18 + row_i * 21
        draw.ellipse([bx, by + 1, bx + 15, by + 16], fill=REGION_COLORS[reg])
        ns = str(num)
        draw.text((bx + (15 - _tw(draw, ns, f_num)) // 2, by + 3), ns, font=f_num, fill=WHITE)
        draw.text((bx + 20, by + 3), loc, font=f_loc, fill=INK)
        lw = _tw(draw, loc, f_loc)
        _draw_lines(draw, bx + 24 + lw, by + 3, txt, f_txt, MUTED, 308 - lw, 10, 1)

    # DATE CHECK box
    dc_y0, dc_y1 = 930, 972
    draw.rectangle([14, dc_y0, 1010, dc_y1], fill=(241, 234, 224), outline=RULE)
    draw.rectangle([14, dc_y0, 19, dc_y1], fill=CRIMSON)
    draw.text((26, dc_y0 + 6), "DATE CHECK:", font=F(SANS_BOLD_PATH, 8), fill=CRIMSON)
    dc_body = (
        "Every story above broke or first appeared on Wed 25 Nov 2026 (UTC). Left out as prior days' news: "
        "Mon 23 Nov: Huang Nvidia return, West Java gold-pit flood start, leaked Russia war dead; "
        "Tue 24 Nov: WHO Congo Akwe clinic exit, Riyadh PIF strike, CAS Senegal AFCON ruling, Huawei Brooklyn verdict; "
        "Sun 22 Nov: COP31 collapse, 188-drone Kyiv raid."
    )
    _draw_lines(draw, 94, dc_y0 + 6, dc_body, F(SANS_REG_PATH, 8), INK, 906, 11, 3)

    # Sources + bottom strip
    draw.text((14, 979), "SOURCES: REUTERS · USTR · BEA · ABS · OFGEM · UNODC · DFAT · XINHUA · PROTHOM ALO · AP · AFP · CBS · ESA · FIDE · YONHAP", font=F(SANS_BOLD_PATH, 7), fill=MUTED)
    rt = "Original vector code art · no photos"
    draw.text((1010 - _tw(draw, rt, F(SANS_REG_PATH, 7)), 979), rt, font=F(SANS_REG_PATH, 7), fill=MUTED)

    draw.rectangle([0, 998, W, H], fill=INK)
    draw.text((14, 1005), "THE WORLD IN ONE DAY · BUILT FOR MAKE.FUN", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
    fr = "WEDNESDAY 25 NOVEMBER 2026 · ONE DAY, ONE PAGE"
    draw.text((1010 - _tw(draw, fr, F(SANS_BOLD_PATH, 8)), 1005), fr, font=F(SANS_BOLD_PATH, 8), fill=GOLD)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    print(f"Generated v8 {out_path}: {os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    main()
