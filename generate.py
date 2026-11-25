import math
import os
import random
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

BG = (247, 243, 234)
INK = (22, 22, 24)
MUTED = (90, 86, 80)
RULE = (205, 198, 185)
DARK_RULE = (42, 40, 38)
CRIMSON = (178, 36, 36)
BLUE_OFF = (26, 82, 148)
GREEN_CONF = (22, 118, 66)
GRAY_REP = (92, 92, 96)
AMBER_CLAIM = (168, 92, 16)
GOLD = (214, 154, 42)
WHITE = (255, 255, 255)

REGION_COLORS = {
    "ASIA": (182, 42, 42),
    "M. EAST": (196, 104, 24),
    "EUROPE": (26, 68, 134),
    "AMERICAS": (24, 108, 164),
    "OCEANIA": (22, 118, 68),
    "AFRICA": (118, 48, 128),
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


def _badge(draw, x, y, text, bg=None, fg=WHITE, border=None, font_size=8, px=5, py=2, r=2):
    fnt = F(SANS_BOLD_PATH, font_size)
    tw = _tw(draw, text, fnt)
    th = _th(draw, text, fnt)
    bw = tw + px * 2
    bh = max(th + py * 2, font_size + 5)
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=r, fill=bg, outline=border, width=1 if border else 0)
    draw.text((x + px, y + (bh - th) // 2 - 1), text, font=fnt, fill=fg)
    return bw, bh


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
    # Subtle micro-paper texture over parchment only; crisp text rendered after this pass
    px = img.load()
    rng = random.Random(20261125)
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
    # Shenzhou-24 liftoff & Tiangong docking with curved Earth limb
    _grad_v(draw, x0, y0, x1, y1, (8, 16, 38), (20, 44, 88))
    _stipple(draw, x0, y0 + 14, x1, y1 - 24, 101, 130, [(200, 215, 255), (255, 255, 230), (130, 150, 200)], 1)
    # Glowing Earth limb clipped cleanly inside Hero #1
    draw.polygon([
        (x0, y1), (x0, y1 - 14),
        (x0 + 80, y1 - 22), (x0 + 162, y1 - 25), (x0 + 244, y1 - 22),
        (x1, y1 - 14), (x1, y1),
    ], fill=(28, 92, 168))
    draw.line([
        (x0, y1 - 14), (x0 + 80, y1 - 22), (x0 + 162, y1 - 25), (x0 + 244, y1 - 22), (x1, y1 - 14)
    ], fill=(138, 212, 255), width=2)
    # Atmospheric glow behind rocket
    for rad, col in [(36, (44, 62, 92)), (26, (78, 86, 98)), (18, (140, 102, 58))]:
        draw.ellipse([x0 + 62 - rad, y1 - 24 - rad, x0 + 62 + rad, y1 - 24 + rad], fill=col)
    # Launch plume & rocket
    rx = x0 + 62
    draw.polygon([(rx, y1 - 28), (rx - 14, y1 - 3), (rx + 14, y1 - 3)], fill=(242, 138, 34))
    draw.polygon([(rx, y1 - 34), (rx - 7, y1 - 7), (rx + 7, y1 - 7)], fill=(255, 224, 102))
    draw.polygon([(rx, y0 + 20), (rx - 6, y0 + 34), (rx + 6, y0 + 34)], fill=(244, 245, 248))
    draw.rectangle([rx - 6, y0 + 34, rx + 6, y1 - 32], fill=(238, 240, 244), outline=(170, 178, 192))
    draw.rectangle([rx - 10, y1 - 54, rx - 6, y1 - 32], fill=(214, 218, 226))
    draw.rectangle([rx + 6, y1 - 54, rx + 10, y1 - 32], fill=(214, 218, 226))
    draw.rectangle([rx - 6, y0 + 46, rx + 6, y0 + 52], fill=CRIMSON)
    # Dotted orbital arc to Tiangong
    for i in range(11):
        t = i / 10.0
        px = int(rx + 18 + t * 116)
        py = int((y0 + 32) + math.sin(t * 2.2) * -14 + 26 * (1 - t))
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 206, 74))
    # Tiangong solar arrays + hub
    sx, sy = x0 + 236, y0 + 50
    for dx in (-38, -22, 16, 32):
        draw.rectangle([sx + dx, sy - 22, sx + dx + 9, sy + 22], fill=(38, 86, 152), outline=(120, 174, 232))
        for ry in range(sy - 16, sy + 20, 8):
            draw.line([(sx + dx, ry), (sx + dx + 9, ry)], fill=(96, 148, 210), width=1)
    draw.rectangle([sx - 44, sy - 3, sx + 44, sy + 3], fill=(208, 214, 224))
    draw.rectangle([sx - 18, sy - 6, sx + 18, sy + 6], fill=(246, 248, 252), outline=(130, 140, 160))
    # China & Pakistan flags
    fx, fy = x1 - 78, y0 + 18
    draw.rectangle([fx, fy, fx + 32, fy + 20], fill=(198, 30, 34), outline=WHITE)
    draw.ellipse([fx + 4, fy + 4, fx + 10, fy + 10], fill=(250, 210, 48))
    pxf = fx + 38
    draw.rectangle([pxf, fy, pxf + 32, fy + 20], fill=(18, 96, 52), outline=WHITE)
    draw.rectangle([pxf, fy, pxf + 9, fy + 20], fill=WHITE)
    draw.pieslice([pxf + 13, fy + 4, pxf + 25, fy + 16], 45, 285, fill=WHITE)
    _ribbon(draw, x0, y0, "00:18 UTC · TIANGONG", bg=(14, 20, 32))
    _pin(draw, x0 + 15, y1 - 15, 1)


def _draw_hero2(draw, x0, y0, x1, y1):
    # Asia chip sell-off: dark FT terminal + candlestick/sell-off curve + subtle silicon watermark
    _grad_v(draw, x0, y0, x1, y1, (22, 24, 30), (34, 22, 24))
    # Subtle silicon chip trace lines on left
    for gx in range(x0 + 18, x0 + 170, 24):
        draw.line([(gx, y0 + 18), (gx, y1 - 6)], fill=(42, 46, 56), width=1)
    for gy in range(y0 + 24, y1 - 6, 18):
        draw.line([(x0 + 4, gy), (x0 + 178, gy)], fill=(42, 46, 56), width=1)
    # Intraday plunge curve
    pts = [
        (x0 + 8, y0 + 26),
        (x0 + 36, y0 + 30),
        (x0 + 62, y0 + 42),
        (x0 + 90, y0 + 50),
        (x0 + 116, y0 + 74),
        (x0 + 144, y0 + 86),
        (x0 + 172, y0 + 98),
    ]
    poly = pts + [(x0 + 172, y1 - 2), (x0 + 8, y1 - 2)]
    draw.polygon(poly, fill=(116, 28, 30))
    draw.line(pts, fill=(248, 86, 72), width=3)
    draw.ellipse([x0 + 168, y0 + 94, x0 + 176, y0 + 102], fill=(255, 210, 92))
    draw.text((x0 + 30, y0 + 74), "SELL CURB", font=F(SANS_BOLD_PATH, 8), fill=(255, 186, 172))
    draw.text((x0 + 30, y0 + 85), "-6.2% CLOSE", font=F(SANS_BOLD_PATH, 10), fill=WHITE)
    # Embedded right dark FT quote board
    bx0, by0, bx1, by1 = x0 + 182, y0 + 6, x1 - 6, y1 - 6
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=4, fill=(14, 18, 26), outline=(64, 72, 86), width=1)
    quotes = [
        ("KOSPI", "-6.2%"),
        ("TAIEX", "-4.8%"),
        ("NIKKEI", "-2.8%"),
        ("SK HYNIX", "-11.1%"),
        ("SAMSUNG", "-9.9%"),
        ("SOFTBANK", "-15%"),
    ]
    row_h = (by1 - by0 - 10) // len(quotes)
    f_l = F(SANS_BOLD_PATH, 8)
    for i, (k, v) in enumerate(quotes):
        ry = by0 + 5 + i * row_h
        draw.text((bx0 + 7, ry), k, font=f_l, fill=(214, 220, 232))
        tw = _tw(draw, v, f_l)
        draw.text((bx1 - tw - 7, ry), v, font=f_l, fill=(252, 92, 84))
    _ribbon(draw, x0, y0, "ASIA CLOSE · WED 25", bg=(14, 20, 32))
    _pin(draw, x0 + 15, y1 - 15, 2)


def _draw_hero3(draw, x0, y0, x1, y1):
    # Strait of Hormuz: layered sky + detailed Iran/Oman coasts + wave stipple + 2 burning tankers
    _grad_v(draw, x0, y0, x0 + (x1 - x0), y0 + 36, (186, 204, 218), (222, 212, 192))
    _grad_v(draw, x0, y0 + 36, x1, y1, (44, 96, 128), (26, 62, 94))
    # Iran northern rugged coast
    draw.polygon([
        (x0, y0), (x1, y0), (x1, y0 + 46),
        (x0 + 258, y0 + 44), (x0 + 216, y0 + 54), (x0 + 170, y0 + 38),
        (x0 + 116, y0 + 46), (x0 + 62, y0 + 34), (x0, y0 + 42),
    ], fill=(178, 152, 114), outline=(140, 116, 84))
    # Oman Musandam southern headland
    draw.polygon([
        (x0 + 195, y1), (x0 + 225, y0 + 82), (x0 + 258, y0 + 72),
        (x1, y0 + 84), (x1, y1),
    ], fill=(166, 140, 104), outline=(132, 108, 76))
    _stipple(draw, x0 + 6, y0 + 50, x0 + 215, y1 - 8, 303, 95, [(78, 134, 166), (34, 78, 108), (112, 162, 190)], 1)
    # Two damaged tankers with flames & billowing smoke plumes
    for tx, ty in [(x0 + 58, y0 + 70), (x0 + 154, y0 + 62)]:
        # Smoke plume
        for dx, dy, sr, col in [
            (-4, -18, 9, (52, 54, 60)), (4, -26, 11, (64, 66, 72)), (12, -32, 8, (86, 88, 94))
        ]:
            draw.ellipse([tx + dx - sr, ty + dy - sr, tx + dx + sr, ty + dy + sr], fill=col)
        # Tanker hull + bridge
        draw.polygon([(tx - 32, ty + 2), (tx + 34, ty + 2), (tx + 28, ty + 14), (tx - 26, ty + 14)], fill=(48, 52, 60))
        draw.rectangle([tx - 22, ty - 5, tx - 10, ty + 2], fill=(224, 224, 228))
        # Flame
        draw.polygon([(tx - 2, ty + 3), (tx + 8, ty - 20), (tx + 18, ty + 3)], fill=(238, 92, 22))
        draw.polygon([(tx + 2, ty + 3), (tx + 8, ty - 12), (tx + 14, ty + 3)], fill=(255, 214, 64))
    # Floating mine silhouette
    mx, my = x0 + 114, y0 + 88
    draw.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=(24, 28, 34))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        draw.line([(mx, my), (int(mx + 9 * math.cos(rad)), int(my + 9 * math.sin(rad)))], fill=(24, 28, 34), width=2)
    draw.text((x0 + 164, y0 + 18), "IRAN", font=F(SANS_BOLD_PATH, 9), fill=(72, 54, 34))
    draw.text((x1 - 46, y1 - 16), "OMAN", font=F(SANS_BOLD_PATH, 9), fill=(72, 54, 34))
    _ribbon(draw, x0, y0, "STRAIT OF HORMUZ", bg=(14, 20, 32))
    draw.rounded_rectangle([x0 + 72, y1 - 19, x0 + 180, y1 - 4], radius=2, fill=(14, 34, 52))
    draw.text((x0 + 78, y1 - 16), "NAVAL MINE CLAIM", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
    _pin(draw, x0 + 15, y1 - 15, 3)


def _draw_mid_art(draw, num, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    if num == 4:
        # Aust & Solomons security pact: bright daylight Canberra backdrop + two flags + pact seal
        _grad_v(draw, x0, y0, x1, y1, (228, 240, 248), (244, 241, 232))
        # Canberra Parliament triangle & pole silhouette
        draw.polygon([(x0 + w // 2, y0 + 12), (x0 + 46, y1 - 14), (x1 - 46, y1 - 14)], fill=None, outline=(145, 162, 178), width=2)
        draw.line([(x0 + w // 2, y0 + 4), (x0 + w // 2, y0 + 14)], fill=(120, 136, 152), width=2)
        # Australia flag left
        fx0, fy0 = x0 + 14, y0 + 22
        draw.rectangle([fx0, fy0, fx0 + 42, fy0 + 26], fill=(16, 48, 124), outline=WHITE)
        draw.line([(fx0, fy0 + 7), (fx0 + 18, fy0 + 7)], fill=CRIMSON, width=2)
        draw.line([(fx0 + 9, fy0), (fx0 + 9, fy0 + 14)], fill=CRIMSON, width=2)
        draw.ellipse([fx0 + 27, fy0 + 13, fx0 + 33, fy0 + 19], fill=WHITE)
        # Solomon Islands flag right
        sx0 = x1 - 56
        draw.polygon([(sx0, fy0), (sx0 + 42, fy0), (sx0, fy0 + 26)], fill=(18, 86, 156))
        draw.polygon([(sx0 + 42, fy0), (sx0 + 42, fy0 + 26), (sx0, fy0 + 26)], fill=(24, 118, 64))
        draw.line([(sx0, fy0 + 26), (sx0 + 42, fy0)], fill=(238, 194, 42), width=3)
        draw.rounded_rectangle([x0 + 38, y1 - 21, x1 - 22, y1 - 6], radius=2, fill=(24, 52, 92))
        draw.text((x0 + 45, y1 - 18), "NO FOREIGN BASES", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
        _ribbon(draw, x0, y0, "A$740M · 10 YRS", bg=BLUE_OFF)
    elif num == 5:
        # UNODC 47,000 femicides: clean bright ivory card + crimson figure + 5 region bars
        _grad_v(draw, x0, y0, x1, y1, (248, 244, 238), (238, 232, 224))
        draw.text((x0 + 8, y0 + 20), "47,000", font=F(SERIF_BOLD_PATH, 20), fill=CRIMSON)
        draw.text((x0 + 9, y0 + 43), "5 KILLED / HR", font=F(SANS_BOLD_PATH, 8), fill=(72, 68, 64))
        draw.text((x0 + 9, y0 + 54), "per 100k (UNODC)", font=F(SANS_REG_PATH, 7), fill=MUTED)
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
            by = y0 + 19 + idx * 10
            draw.text((x0 + 82, by), lbl, font=f_b, fill=INK)
            bw = int((val / 2.9) * 52)
            draw.rectangle([bx, by + 1, bx + bw, by + 7], fill=col)
            draw.text((bx + bw + 3, by), f"{val}", font=f_b, fill=INK)
        _ribbon(draw, x0, y0, "UNODC REPORT", bg=(96, 28, 36))
    elif num == 6:
        # UK Ofgem +26% cap: warm bright daylight + brick cottage + blue-amber gas flame
        _grad_v(draw, x0, y0, x1, y1, (236, 242, 248), (248, 238, 224))
        hx = x0 + 36
        draw.polygon([(hx - 24, y0 + 40), (hx, y0 + 20), (hx + 24, y0 + 40)], fill=(142, 54, 46))
        draw.rectangle([hx - 20, y0 + 40, hx + 20, y1 - 8], fill=(224, 212, 194), outline=(170, 156, 140))
        draw.pieslice([hx - 9, y0 + 45, hx + 9, y0 + 67], 160, 380, fill=(24, 118, 206))
        draw.pieslice([hx - 5, y0 + 51, hx + 5, y0 + 65], 160, 380, fill=(248, 182, 42))
        draw.text((x0 + 78, y0 + 22), "+26%", font=F(SERIF_BOLD_PATH, 24), fill=CRIMSON)
        draw.text((x0 + 78, y0 + 50), "£1,723 -> £2,166", font=F(SANS_BOLD_PATH, 9), fill=BLUE_OFF)
        _ribbon(draw, x0, y0, "OFGEM CAP", bg=CRIMSON)
    elif num == 7:
        # Coalition strikes Hodeidah & downs 4 drones: twilight Red Sea coastline + intercept arcs
        _grad_v(draw, x0, y0, x1, y1, (26, 40, 72), (58, 76, 108))
        draw.rectangle([x0, y1 - 18, x1, y1], fill=(22, 48, 78))
        draw.polygon([(x0, y1 - 18), (x0 + 65, y1 - 22), (x0 + 100, y1 - 18)], fill=(138, 118, 92))
        for dx, dy in [(x0 + 78, y0 + 28), (x0 + 114, y0 + 22), (x0 + 148, y0 + 34), (x0 + 168, y0 + 24)]:
            draw.line([(x0 + 38, y1 - 20), (dx, dy)], fill=(90, 198, 240), width=1)
            draw.ellipse([dx - 5, dy - 5, dx + 5, dy + 5], fill=(246, 134, 34))
            draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 228, 112))
        _ribbon(draw, x0, y0, "4 DRONES DOWNED", bg=(14, 20, 32))
    elif num == 8:
        # Dhaka garment wage +36%: bright green-cream background + factory roof + step rise
        _grad_v(draw, x0, y0, x1, y1, (236, 246, 238), (224, 238, 228))
        fx = x0 + 64
        draw.polygon([(fx, y1 - 16), (fx, y0 + 36), (fx + 32, y0 + 24), (fx + 32, y0 + 36), (fx + 64, y0 + 24), (fx + 64, y0 + 36), (fx + 96, y0 + 24), (fx + 96, y1 - 16)], fill=(192, 206, 196), outline=(140, 158, 146))
        draw.rectangle([x0 + 82, y0 + 48, x0 + 114, y1 - 8], fill=(128, 140, 136))
        draw.rectangle([x0 + 124, y0 + 30, x0 + 162, y1 - 8], fill=GREEN_CONF)
        draw.line([(x0 + 98, y0 + 46), (x0 + 143, y0 + 24)], fill=(18, 102, 54), width=3)
        draw.text((x0 + 10, y0 + 22), "+36%", font=F(SERIF_BOLD_PATH, 20), fill=GREEN_CONF)
        draw.text((x0 + 10, y0 + 45), "Tk 17,500", font=F(SANS_BOLD_PATH, 9), fill=INK)
        _ribbon(draw, x0, y0, "WAGE FLOOR", bg=GREEN_CONF)
    elif num == 9:
        # Samara refineries drone fire: deep indigo night + refinery silhouettes + blazing fireballs
        _grad_v(draw, x0, y0, x1, y1, (22, 28, 44), (54, 42, 48))
        _stipple(draw, x0 + 4, y0 + 14, x1 - 4, y1 - 24, 909, 45, [(140, 152, 180)], 1)
        draw.rectangle([x0, y1 - 18, x1, y1], fill=(28, 30, 36))
        for rx in (x0 + 62, x0 + 136):
            draw.rectangle([rx - 14, y1 - 36, rx + 14, y1 - 18], fill=(56, 62, 72))
            draw.rectangle([rx - 19, y0 + 28, rx - 13, y1 - 18], fill=(64, 70, 82))
            draw.ellipse([rx - 12, y0 + 26, rx + 14, y0 + 52], fill=(240, 108, 22))
            draw.ellipse([rx - 5, y0 + 33, rx + 8, y0 + 46], fill=(255, 222, 82))
        _ribbon(draw, x0, y0, "2 REFINERIES HIT", bg=(14, 20, 32))
    elif num == 10:
        # EU Quantum Act & €50bn fund: cobalt blue EU stars + glowing quantum/silicon chip
        _grad_v(draw, x0, y0, x1, y1, (22, 56, 122), (34, 82, 164))
        cx, cy = x0 + 52, y0 + 44
        for a in range(0, 360, 30):
            rad = math.radians(a)
            sx, sy = int(cx + 22 * math.cos(rad)), int(cy + 22 * math.sin(rad))
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(252, 214, 58))
        # Chip square
        qx, qy = x0 + 114, y0 + 24
        draw.rectangle([qx, qy, qx + 42, qy + 42], fill=(18, 28, 46), outline=(120, 204, 250), width=2)
        for off in (8, 18, 28, 36):
            draw.line([(qx - 6, qy + off), (qx, qy + off)], fill=(252, 214, 58), width=2)
            draw.line([(qx + 42, qy + off), (qx + 48, qy + off)], fill=(252, 214, 58), width=2)
        draw.text((qx + 6, qy + 15), "€50BN", font=F(SANS_BOLD_PATH, 9), fill=(120, 220, 255))
        _ribbon(draw, x0, y0, "EU QUANTUM ACT", bg=(12, 28, 64))
    elif num == 11:
        # Australia 4.9% Oct CPI: crisp parchment-sky background + rising monthly CPI column chart
        _grad_v(draw, x0, y0, x1, y1, (240, 244, 248), (232, 236, 240))
        cols = [("AUG", 3.6, BLUE_OFF), ("SEP", 4.3, AMBER_CLAIM), ("OCT", 4.9, CRIMSON)]
        for i, (m, v, c) in enumerate(cols):
            bx0 = x0 + 28 + i * 44
            bh = int(v * 9.5)
            draw.rectangle([bx0, y1 - 12 - bh, bx0 + 28, y1 - 12], fill=c)
            draw.text((bx0 + 3, y1 - 12 - bh - 12), f"{v}%", font=F(SANS_BOLD_PATH, 9), fill=c)
            draw.text((bx0 + 4, y1 - 11), m, font=F(SANS_BOLD_PATH, 7), fill=MUTED)
        _ribbon(draw, x0, y0, "4.9% OCT CPI", bg=CRIMSON)
    elif num == 12:
        # Israel Knesset 65-50 Oct 7 inquiry vote: light warm backdrop + Parliament hemicycle + vote tally
        _grad_v(draw, x0, y0, x1, y1, (246, 242, 234), (236, 230, 218))
        cx, cy = x0 + 132, y1 - 14
        for row_r, cnt in [(22, 13), (32, 17)]:
            for idx in range(cnt):
                ang = math.radians(180 + (idx / max(1, cnt - 1)) * 180)
                px = int(cx + row_r * math.cos(ang))
                py = int(cy + row_r * math.sin(ang))
                aye = idx < round(cnt * 65 / 115)
                col = BLUE_OFF if aye else (175, 172, 168)
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
        draw.text((x0 + 10, y0 + 22), "65–50", font=F(SERIF_BOLD_PATH, 18), fill=BLUE_OFF)
        draw.text((x0 + 10, y0 + 43), "INQUIRY PASSES", font=F(SANS_BOLD_PATH, 7), fill=INK)
        _ribbon(draw, x0, y0, "KNESSET VOTE", bg=BLUE_OFF)
    elif num == 13:
        # Balleny Islands M5.9 quake (+ Taiwan & NZ quakes): ice blue background + concentric seismic rings + seismogram
        _grad_v(draw, x0, y0, x1, y1, (224, 238, 248), (206, 224, 240))
        ex, ey = x0 + 124, y0 + 46
        for r, c in [(26, (170, 202, 228)), (18, (206, 118, 118)), (10, CRIMSON)]:
            draw.ellipse([ex - r, ey - r, ex + r, ey + r], outline=c, width=2)
        draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=CRIMSON)
        # Seismogram trace
        wpts = [(x0 + 16, y0 + 54), (x0 + 34, y0 + 54), (x0 + 44, y0 + 36), (x0 + 52, y0 + 68), (x0 + 60, y0 + 38), (x0 + 68, y0 + 58), (x0 + 82, y0 + 54)]
        draw.line(wpts, fill=CRIMSON, width=2)
        draw.text((x0 + 16, y0 + 17), "M5.9", font=F(SERIF_BOLD_PATH, 16), fill=INK)
        _ribbon(draw, x0, y0, "ANTARCTIC QUAKE", bg=(32, 54, 82))

    # Matching pin circle at bottom right corner of mid-card art (cleanest spot away from left ribbons)
    _pin(draw, x1 - 14, y1 - 13, num, r=8)


def _draw_world_map(draw, x0, y0, x1, y1):
    # Ocean background & fine graticule
    draw.rectangle([x0, y0, x1, y1], fill=(224, 234, 240), outline=RULE, width=1)
    mw, mh = x1 - x0, y1 - y0

    def ll(lon, lat):
        px = x0 + int((lon + 180.0) / 360.0 * mw)
        py = y0 + int((88.0 - lat) / 172.0 * mh)
        return px, py

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
        [(166, -35), (178, -37), (172, -46), (166, -46)],
    ]
    for poly in continents:
        draw.polygon([ll(lo, la) for lo, la in poly], fill=land, outline=coast)

    # Antarctica bottom-left inset (cleanly frames Pin #13 Balleny Is.)
    ix0, iy0, ix1, iy1 = x0 + 6, y1 - 36, x0 + 84, y1 - 6
    draw.rectangle([ix0, iy0, ix1, iy1], fill=(236, 242, 246), outline=GRAY_REP, width=1)
    draw.polygon([(ix0 + 18, iy1 - 2), (ix0 + 36, iy0 + 14), (ix0 + 60, iy0 + 18), (ix0 + 70, iy1 - 2)], fill=(232, 236, 240), outline=coast)
    draw.text((ix0 + 4, iy0 + 3), "ANTARCTICA", font=F(SANS_BOLD_PATH, 7), fill=INK)
    _pin(draw, ix0 + 65, iy0 + 16, 13, bg=REGION_COLORS["OCEANIA"], r=7)

    # Pins 1..12 plotted cleanly without collision
    pins = [
        (1, 100, 41, "ASIA"),       # Jiuquan Shenzhou-24
        (2, 127, 37, "ASIA"),       # Seoul/Tokyo/Taipei chip selloff
        (3, 56, 26, "M. EAST"),     # Strait of Hormuz
        (4, 149, -35, "OCEANIA"),   # Canberra/Solomons pact
        (5, -74, 41, "GLOBAL"),     # UNODC New York / UN
        (6, 0, 52, "EUROPE"),       # London Ofgem
        (7, 43, 15, "M. EAST"),     # Hodeidah/Ras Tanura
        (8, 90, 24, "ASIA"),        # Dhaka garment wage
        (9, 49, 53, "EUROPE"),      # Samara Russia refineries
        (10, 8, 48, "EUROPE"),      # Strasbourg EU Quantum Act
        (11, 136, -24, "OCEANIA"),  # Australia CPI (offset north of #4)
        (12, 35, 31, "M. EAST"),    # Jerusalem Knesset 65-50
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
    tr = "39 VERIFIED STORIES · ALL FROM WEDNESDAY 25 NOV 2026"
    draw.text((1010 - _tw(draw, tr, F(SANS_BOLD_PATH, 9)), 10), tr, font=F(SANS_BOLD_PATH, 9), fill=CRIMSON)
    draw.line([(14, 24), (1010, 24)], fill=DARK_RULE, width=2)

    # Masthead
    m_txt = "Wednesday 25 November 2026"
    m_f = F(SERIF_BOLD_PATH, 46)
    draw.text(((W - _tw(draw, m_txt, m_f)) // 2, 28), m_txt, font=m_f, fill=INK)

    sub = "Pakistan's first astronaut reaches Tiangong · Asia's chip stocks crash on AI doubts · Tankers burn in Hormuz · Solomons pick Australia"
    sub_f = F(SERIF_ITAL_PATH, 12)
    draw.text(((W - _tw(draw, sub, sub_f)) // 2, 82), sub, font=sub_f, fill=MUTED)

    # Region bar (39 stories across 7 regions)
    segs = [
        ("ASIA 11", 11, REGION_COLORS["ASIA"]),
        ("M. EAST 5", 5, REGION_COLORS["M. EAST"]),
        ("EUROPE 8", 8, REGION_COLORS["EUROPE"]),
        ("AMERICAS 6", 6, REGION_COLORS["AMERICAS"]),
        ("OCEANIA 5", 5, REGION_COLORS["OCEANIA"]),
        ("AFRICA 2", 2, REGION_COLORS["AFRICA"]),
        ("WORLD 2", 2, REGION_COLORS["GLOBAL"]),
    ]
    ry0, ry1 = 101, 117
    cur_x = 14
    tot_w = 996
    f_seg = F(SANS_BOLD_PATH, 8)
    for idx, (lbl, cnt, col) in enumerate(segs):
        sw = int(round(tot_w * (cnt / 39.0))) if idx < len(segs) - 1 else (1010 - cur_x)
        draw.rectangle([cur_x, ry0, cur_x + sw - 1, ry1], fill=col)
        tw = _tw(draw, lbl, f_seg)
        if tw + 4 < sw:
            draw.text((cur_x + (sw - tw) // 2, ry0 + 3), lbl, font=f_seg, fill=WHITE)
        cur_x += sw

    # THE DAY IN UTC ribbon
    draw.rectangle([14, 121, 108, 138], fill=INK)
    draw.text((21, 124), "THE DAY IN UTC", font=F(SANS_BOLD_PATH, 8), fill=GOLD)
    draw.rectangle([108, 121, 1010, 138], fill=(238, 232, 220), outline=RULE)
    ticks = [
        ("00:18", "Shenzhou-24 liftoff"),
        ("00:30", "Aus CPI hits 4.9%"),
        ("03:56", "Crew docks Tiangong"),
        ("05:30", "Taiex closes -4.8%"),
        ("06:30", "Kospi -6.2% curb"),
        ("10:00", "Tube strike starts"),
    ]
    tx = 118
    for tm, ev in ticks:
        draw.text((tx, 124), tm, font=F(SANS_BOLD_PATH, 8), fill=CRIMSON)
        tx += _tw(draw, tm, F(SANS_BOLD_PATH, 8)) + 4
        draw.text((tx, 124), ev, font=F(SANS_REG_PATH, 8), fill=INK)
        tx += _tw(draw, ev, F(SANS_REG_PATH, 8)) + 16

    # 6 KPI figure columns
    kpis = [
        ("1st", "Pakistani reaches China's Tiangong station (1)", CRIMSON),
        ("-6.2%", "Kospi close on curb; SoftBank drops -15% (2)", CRIMSON),
        ("47,000", "women killed by partner/kin (5/hr), UN says (5)", BLUE_OFF),
        ("+26%", "UK Ofgem energy cap rises to £2,166 (6)", CRIMSON),
        ("€50bn", "EU Quantum Act & tech fund unveiled (10)", BLUE_OFF),
        ("+36%", "Bangladesh garment wage lifted to Tk 17,500 (8)", GREEN_CONF),
    ]
    kw = tot_w / 6.0
    for i, (num_s, desc, col) in enumerate(kpis):
        kx = int(14 + i * kw)
        if i > 0:
            draw.line([(kx - 6, 144), (kx - 6, 186)], fill=RULE, width=1)
        draw.text((kx, 143), num_s, font=F(SERIF_BOLD_PATH, 19), fill=col)
        _draw_lines(draw, kx, 166, desc, F(SANS_REG_PATH, 8), MUTED, int(kw - 12), 10, 2)
    draw.line([(14, 190), (1010, 190)], fill=DARK_RULE, width=1)

    # Top 3 Hero Cards
    heroes = [
        (
            1, _draw_hero1, "LIFTOFF", REGION_COLORS["ASIA"], "JIUQUAN, CHINA · SPACE", "CONFIRMED",
            "Shenzhou-24 flies Pakistan's 1st astronaut to Tiangong",
            "Long March-2F lifts off at 00:18 UTC carrying Tang Hongbo, Wu Yi and payload specialist Muhammad Zeeshan Ali.",
            "XINHUA · AA · REUTERS",
        ),
        (
            2, _draw_hero2, "SELL-OFF", REGION_COLORS["ASIA"], "SEOUL · TAIPEI · TOKYO", "CONFIRMED",
            "Asia's chip stocks crash on AI bubble doubts",
            "Kospi plunges 6.2% (sell curb), SK Hynix -11.1%, Samsung -9.9%, Taiex -4.8%, SoftBank -15% and Nikkei -2.8%.",
            "AL JAZEERA · AFP · REUTERS",
        ),
        (
            3, _draw_hero3, "WAR AT SEA", REGION_COLORS["M. EAST"], "STRAIT OF HORMUZ · GULF", "CLAIM",
            "Two oil tankers hit mines and burn, Iran says",
            "IRGC Navy claims vessels took an 'unauthorised route' in Strait early Wednesday; no independent confirmation yet.",
            "IRIB · REUTERS · ARAB NEWS",
        ),
    ]
    hc_w = 324
    hc_gap = 12
    hy0 = 196
    art_h = 114
    for idx, (num, fn, cat, cat_c, loc, cert, hd, dk, src) in enumerate(heroes):
        hx = 14 + idx * (hc_w + hc_gap)
        fn(draw, hx, hy0, hx + hc_w, hy0 + art_h)
        my = hy0 + art_h + 6
        bw, _ = _badge(draw, hx, my, cat, bg=cat_c, fg=WHITE, font_size=8, px=5, py=2)
        draw.text((hx + bw + 6, my + 2), loc, font=F(SANS_BOLD_PATH, 8), fill=MUTED)
        _cert_badge(draw, hx + hc_w, my, cert)
        ny = _draw_lines(draw, hx, my + 17, hd, F(SERIF_BOLD_PATH, 16), INK, hc_w, 18, 2)
        _draw_lines(draw, hx, ny + 3, dk, F(SANS_REG_PATH, 9), MUTED, hc_w, 12, 3)
        draw.text((hx, hy0 + art_h + 94), src, font=F(SANS_BOLD_PATH, 7), fill=(116, 110, 102))

    # Mid-band header + HOW SURE inline legend
    draw.line([(14, 412), (1010, 412)], fill=DARK_RULE, width=1)
    draw.text((14, 418), "ALSO ON WEDNESDAY 25 NOVEMBER", font=F(SANS_BOLD_PATH, 9), fill=INK)
    # Inline legend on right
    lx = 468
    draw.text((lx, 419), "HOW SURE:", font=F(SANS_BOLD_PATH, 8), fill=MUTED)
    lx += _tw(draw, "HOW SURE:", F(SANS_BOLD_PATH, 8)) + 6
    for cert, desc, bd_c, bg_c in [
        ("OFFICIAL", "gov / agency", BLUE_OFF, (236, 243, 253)),
        ("CONFIRMED", "2+ outlets", GREEN_CONF, (232, 246, 238)),
        ("REPORTED", "single outlet", GRAY_REP, (242, 242, 244)),
        ("CLAIM", "one-sided", AMBER_CLAIM, (254, 244, 232)),
    ]:
        bw, _ = _badge(draw, lx, 417, cert, bg=bg_c, fg=bd_c, border=bd_c, font_size=7, px=4, py=1)
        lx += bw + 4
        draw.text((lx, 419), desc, font=F(SANS_REG_PATH, 8), fill=MUTED)
        lx += _tw(draw, desc, F(SANS_REG_PATH, 8)) + 8

    # 10 Mid Cards (2 x 5 grid -> #4..#13)
    cards = [
        (4, "CANBERRA", REGION_COLORS["OCEANIA"], "OFFICIAL", "Australia & Solomons sign security pact", "No foreign bases; A$740m aid & easier visas. DFAT",
         ),
        (5, "UNITED NATIONS", REGION_COLORS["GLOBAL"], "OFFICIAL", "UN: 47,000 women killed by partner/kin", "5/hr; Africa highest at 2.9/100k. UNODC",
         ),
        (6, "LONDON, UK", REGION_COLORS["EUROPE"], "OFFICIAL", "UK energy bills to jump 26% on gas shock", "Ofgem cap lifted £1,723 -> £2,166 (~20m homes).",
         ),
        (7, "HODEIDAH · YEMEN", REGION_COLORS["M. EAST"], "OFFICIAL", "Coalition strikes Hodeidah, downs 4 drones", "Strikes follow Riyadh hit; Houthis warn Jeddah.",
         ),
        (8, "DHAKA", REGION_COLORS["ASIA"], "OFFICIAL", "Bangladesh lifts garment pay floor 36%", "Minimum rises Tk 12,500 -> Tk 17,500/mo. Prothom Alo",
         ),
        (9, "SAMARA, RUSSIA", REGION_COLORS["EUROPE"], "REPORTED", "Ukrainian drones hit two Samara refineries", "Blazes at Syzran & Kuibyshev; Russia vows answer.",
         ),
        (10, "STRASBOURG", REGION_COLORS["EUROPE"], "OFFICIAL", "EU unveils Quantum Act & €50bn tech fund", "Virkkunen backs EU Sovereign Tech Equity Fund.",
         ),
        (11, "CANBERRA · ABS", REGION_COLORS["OCEANIA"], "OFFICIAL", "Australia inflation jumps to 4.9% 3-yr high", "Housing & power costs lift Oct CPI above forecast.",
         ),
        (12, "JERUSALEM", REGION_COLORS["M. EAST"], "OFFICIAL", "Knesset votes 65–50 for Oct 7 state inquiry", "Opposition panel passes 1st reading; PM limit 65–48.",
         ),
        (13, "BALLENY ISLANDS", REGION_COLORS["OCEANIA"], "OFFICIAL", "M5.9 Balleny quake leads 3 Pacific tremors", "Shallow 4.1 km shock joins M5.3 Taiwan & M5.2 NZ.",
         ),
    ]
    cw = 191
    c_gap = 10
    c_art_h = 74
    row_ys = [436, 566]
    for idx, (num, loc, loc_c, cert, hd, dk) in enumerate(cards):
        r_idx = idx // 5
        c_idx = idx % 5
        cx = 14 + c_idx * (cw + c_gap)
        cy = row_ys[r_idx]
        _draw_mid_art(draw, num, cx, cy, cx + cw, cy + c_art_h)
        ty = cy + c_art_h + 4
        draw.text((cx, ty), loc, font=F(SANS_BOLD_PATH, 7), fill=loc_c)
        _cert_badge(draw, cx + cw, ty - 2, cert)
        ny = _draw_lines(draw, cx, ty + 11, hd, F(SERIF_BOLD_PATH, 11), INK, cw, 13, 2)
        _draw_lines(draw, cx, ny + 2, dk, F(SANS_REG_PATH, 8), MUTED, cw, 10, 2)

    # Bottom Section: Map + 26 Briefs (#14..#39)
    by0 = 696
    draw.line([(14, by0 - 4), (1010, by0 - 4)], fill=DARK_RULE, width=1)
    draw.text((14, by0 + 1), "WHERE IT HAPPENED", font=F(SANS_BOLD_PATH, 9), fill=INK)
    draw.text((126, by0 + 1), "· PINS = STORIES 1–13", font=F(SANS_REG_PATH, 8), fill=MUTED)
    _draw_world_map(draw, 14, by0 + 16, 336, 902)

    # Map region legend
    leg_items = list(REGION_COLORS.items())
    for idx, (name, col) in enumerate(leg_items):
        lx = 14 + (idx % 4) * 82
        ly = 907 + (idx // 4) * 12
        draw.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=col)
        draw.text((lx + 11, ly), name, font=F(SANS_REG_PATH, 8), fill=INK)

    # Right 26 Briefs (#14..#39)
    draw.text((348, by0 + 1), "IN BRIEF", font=F(SANS_BOLD_PATH, 9), fill=INK)
    draw.text((400, by0 + 1), "· 26 MORE VERIFIED WEDNESDAY 25 NOV STORIES", font=F(SANS_REG_PATH, 8), fill=MUTED)

    briefs = [
        (14, "BRUSSELS", "Puigdemont sets Dec 12 to end 9-yr Spain exile", "C"),
        (15, "LONDON", "easyJet profit plunges 96% to £20m on jet fuel", "C"),
        (16, "CARTAGENA", "Police storm store, free all Colombia hostages", "O"),
        (17, "IOWA", "US Army detonates 5t degraded lead azide safely", "O"),
        (18, "WASHINGTON", "USTR readies 16-nation Section 301 probe tariffs", "R"),
        (19, "WASHINGTON", "NATO chief Rutte holds Mar-a-Lago talks w/ Trump", "C"),
        (20, "CANBERRA", "Parliament apologises to LGBTQ+ military vets", "O"),
        (21, "HOBART", "Flinders Is. bushfire forces emergency evacuations", "O"),
        (22, "DOHA", "Sooryavanshi, 15, smashes fastest List A 204 (53b)", "C"),
        (23, "LONDON", "Tube strike halts Circle & Piccadilly from 10:00 UTC", "C"),
        (24, "LONDON", "Independent review finds Met Police still racist", "O"),
        (25, "BRUSSELS", "EU sanctions 15 firms tied to Russian arms chain", "O"),
        (26, "BERN", "EU and Switzerland seal updated bilateral pacts", "O"),
        (27, "DARMSTADT", "ESA Hera reveals first close-up images of Dimorphos", "O"),
        (28, "GENEVA", "FIDE World Chess: Gukesh & Sindarov draw Game 1", "C"),
        (29, "GAZA CITY", "Strikes kill at least 4 in Shati camp despite truce", "R"),
        (30, "TEHRAN", "Iran orders winter gas rationing as cold wave hits", "R"),
        (31, "SHANGHAI", "City officials pledge loyalty amid Chen probe", "R"),
        (32, "SEOUL", "South Korea births jump 12.2%; subway strike averted", "O"),
        (33, "TAIPEI", "BBC Verify traces China-linked Taiwan deepfakes", "C"),
        (34, "KHARTOUM", "Sudan rejects Ethiopia peace talks amid clashes", "C"),
        (35, "GAUTENG", "Johannesburg imposes Level-2 water grid curbs", "O"),
        (36, "CHICAGO", "81.5m Thanksgiving holiday travelers hit storm delays", "C"),
        (37, "BRASÍLIA", "Brazil permanently recalls ambassador to Argentina", "O"),
        (38, "JAKARTA", "OECD chief Cormann meets Prabowo on accession", "O"),
        (39, "MARKETS", "Gold slips ~$3,516 (-1.2%) as US dollar firms", "C"),
    ]
    pill_cols = {
        "O": BLUE_OFF,
        "C": GREEN_CONF,
        "R": GRAY_REP,
        "CLAIM": AMBER_CLAIM,
    }
    col_x = [348, 684]
    f_num = F(SANS_BOLD_PATH, 8)
    f_loc = F(SANS_BOLD_PATH, 8)
    f_txt = F(SANS_REG_PATH, 8)
    for idx, (num, loc, txt, tag) in enumerate(briefs):
        col_i = idx // 13
        row_i = idx % 13
        bx = col_x[col_i]
        by = by0 + 17 + row_i * 17
        ns = str(num)
        draw.text((bx, by), ns, font=f_num, fill=CRIMSON)
        draw.text((bx + 15, by), loc, font=f_loc, fill=INK)
        lw = _tw(draw, loc, f_loc)
        draw.text((bx + 19 + lw, by), txt, font=f_txt, fill=MUTED)
        # tiny right-aligned tag box
        col_end = bx + 324
        pw = _tw(draw, tag, F(SANS_BOLD_PATH, 7)) + 5
        draw.rectangle([col_end - pw, by + 1, col_end, by + 11], fill=pill_cols[tag])
        draw.text((col_end - pw + 2, by + 1), tag, font=F(SANS_BOLD_PATH, 7), fill=WHITE)

    # DATE CHECK box
    dc_y0, dc_y1 = 934, 976
    draw.rectangle([14, dc_y0, 1010, dc_y1], fill=(241, 234, 224), outline=RULE)
    draw.rectangle([14, dc_y0, 19, dc_y1], fill=CRIMSON)
    draw.text((26, dc_y0 + 6), "DATE CHECK:", font=F(SANS_BOLD_PATH, 8), fill=CRIMSON)
    dc_body = (
        "Every story above broke or stepped forward on Wed 25 Nov 2026 (UTC). Left out as earlier days' news: "
        "Mon 23 Nov: Huang Nvidia return, West Java gold-pit flood onset, leaked Russia war dead, Anmer Hall break-in; "
        "Tue 24 Nov: WHO Congo Akwe clinic exit, Huawei Brooklyn verdict, Riyadh PIF strike, Senegal AFCON ruling; "
        "Sun 22 Nov: COP31 collapse, 188-drone Kyiv raid."
    )
    _draw_lines(draw, 94, dc_y0 + 6, dc_body, F(SANS_REG_PATH, 8), INK, 906, 11, 3)

    # Sources + bottom strip
    draw.text((14, 982), "SOURCES: REUTERS · AP · AL JAZEERA · AFP · BBC · XINHUA · UNODC · DFAT · OFGEM · ABS · ESA · EU · FIDE · US ARMY · PROTHOM ALO", font=F(SANS_BOLD_PATH, 7), fill=MUTED)
    rt = "Original vector code art · no photos"
    draw.text((1010 - _tw(draw, rt, F(SANS_REG_PATH, 7)), 982), rt, font=F(SANS_REG_PATH, 7), fill=MUTED)

    draw.rectangle([0, 998, W, H], fill=INK)
    draw.text((14, 1005), "THE WORLD IN ONE DAY · BUILT FOR MAKE.FUN", font=F(SANS_BOLD_PATH, 8), fill=WHITE)
    fr = "WEDNESDAY 25 NOVEMBER 2026 · ONE DAY, ONE PAGE"
    draw.text((1010 - _tw(draw, fr, F(SANS_BOLD_PATH, 8)), 1005), fr, font=F(SANS_BOLD_PATH, 8), fill=GOLD)

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    print(f"Generated v6 {out_path}: {os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    main()
