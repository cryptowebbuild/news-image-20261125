"""
Master Editorial Broadsheet Generator v3 for news-image-20261125:
  "Wednesday 25 November 2026" — 36 Verified Stories, Zero Prior-Day Bleed,
  11 Daylight & Data-Rich Vector Panels, Non-Overlapping World Map, UTC Strip & Date Check.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1024, 1024
SCALE = 2
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def _find_font(candidates: list[str]) -> str:
    search_dirs = [
        r"C:\Windows\Fonts",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
        "/usr/share/fonts/truetype/freefont",
        "/usr/share/fonts/truetype/msttcorefonts",
    ]
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for c in candidates:
            p = os.path.join(d, c)
            if os.path.isfile(p):
                return p
    raise FileNotFoundError(f"Could not locate any font from {candidates}")


def ft(kind: str, size: int) -> ImageFont.FreeTypeFont:
    mapping = {
        "serif_bold": ["georgiab.ttf", "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"],
        "serif_italic": ["georgiai.ttf", "DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf"],
        "sans": ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
        "sans_bold": ["arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
    }
    return ImageFont.truetype(_find_font(mapping[kind]), size)


# Crisp 1x broadsheet typographic scale
F_TOPBAR = ft("sans_bold", 10)
F_MAST = ft("serif_bold", 50)
F_REG_BAR = ft("sans_bold", 9)
F_UTC_LBL = ft("sans_bold", 8)
F_UTC_TXT = ft("sans", 9)
F_KPI_NUM = ft("serif_bold", 19)
F_KPI_TXT = ft("sans", 9)

F_LEAD_TAG = ft("sans_bold", 8)
F_LEAD_TITLE = ft("serif_bold", 16)
F_LEAD_BODY = ft("sans", 10)
F_LEAD_SRC = ft("sans_bold", 8)

F_CARD_TAG = ft("sans_bold", 8)
F_CARD_TITLE = ft("serif_bold", 12)
F_CARD_SRC = ft("sans", 8)
F_ART_PILL = ft("sans_bold", 8)
F_ART_BIG = ft("serif_bold", 14)

F_SEC_HDR = ft("sans_bold", 10)
F_BRIEF_CITY = ft("sans_bold", 9)
F_BRIEF_TXT = ft("sans", 9)
F_PIN = ft("sans_bold", 9)
F_DATE_BOLD = ft("sans_bold", 9)
F_DATE_TXT = ft("sans", 9)

# Classic high-contrast ivory newsprint palette
PAPER = (247, 243, 234)
PAPER_WARM = (239, 233, 221)
CARD_BG = (252, 250, 245)
INK = (18, 22, 30)
SLATE = (58, 66, 78)
MUTED = (96, 105, 118)
RULE_DARK = (24, 28, 36)
RULE_LIGHT = (208, 201, 186)

CRIMSON = (176, 30, 34)
NAVY = (26, 62, 122)
AMERICAS_BLUE = (46, 94, 152)
TEAL = (20, 114, 104)
AMBER = (176, 94, 16)
EMERALD = (24, 114, 66)
GOLD_ACCENT = (250, 204, 21)

OCEAN = (224, 235, 244)
LAND = (212, 205, 190)
LAND_EDGE = (140, 134, 122)

REGION_COLORS = {
    "ASIA": TEAL,
    "EUROPE": NAVY,
    "AMERICAS": AMERICAS_BLUE,
    "ME": CRIMSON,
    "AFRICA": EMERALD,
    "OCEANIA": AMBER,
}


@dataclass(frozen=True)
class LeadArticle:
    num: int
    region_code: str
    badge: str
    badge_col: tuple[int, int, int]
    region_line: str
    headline: str
    summary: str
    sources: str
    art_pill: str
    drawer: Callable[[int, int], Image.Image]


@dataclass(frozen=True)
class CardArticle:
    num: int
    region_code: str
    region_line: str
    headline: str
    sources: str
    accent: tuple[int, int, int]
    art_pill: str
    drawer: Callable[[int, int], Image.Image]


def wrap_lines(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip()
        bb = draw.textbbox((0, 0), cand, font=font)
        if bb[2] - bb[0] <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_lines(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    max_w: int,
    line_h: int,
    max_lines: int,
) -> int:
    lines = wrap_lines(draw, text, font, max_w)
    assert len(lines) <= max_lines, f"Wrapped too many lines ({len(lines)}>{max_lines}): {text}"
    for i, ln in enumerate(lines):
        draw.text((x, y + i * line_h), ln, font=font, fill=fill)
    return y + len(lines) * line_h


# ---------------------------------------------------------------------------
# 11 Bespoke 2x Supersampled Editorial Illustrations (Daylight & Data Mix)
# ---------------------------------------------------------------------------
def art_shenzhou24(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (12, 20, 44))
    d = ImageDraw.Draw(im)
    # Orbital Earth horizon + stars
    for sx, sy in [(44, 24), (112, 42), (186, 18), (274, 30), (358, 22), (434, 48), (528, 26), (594, 38)]:
        d.ellipse([sx, sy, sx + 4, sy + 4], fill=(226, 232, 240))
    d.ellipse([-140, int(h * 0.72), w + 140, h + 380], fill=(30, 82, 182))
    d.arc([-140, int(h * 0.72), w + 140, h + 380], 200, 340, fill=(147, 197, 253), width=4)
    # Dashed ascent curve from Jiuquan -> Tiangong
    for t in range(12):
        p0x = int(126 + t * 24)
        p0y = int(146 - math.sin(t / 11.0 * 1.45) * 84)
        d.ellipse([p0x, p0y, p0x + 7, p0y + 7], fill=(250, 204, 21))
    # Long March rocket rising left-center
    rx = int(w * 0.25)
    d.polygon([(rx, 18), (rx - 14, 52), (rx + 14, 52)], fill=(220, 38, 38))
    d.rectangle([rx - 14, 52, rx + 14, 134], fill=(241, 245, 249))
    d.rectangle([rx - 22, 96, rx - 14, 138], fill=(203, 213, 225))
    d.rectangle([rx + 14, 96, rx + 22, 138], fill=(203, 213, 225))
    d.polygon([(rx - 24, 138), (rx + 24, 138), (rx, h - 8)], fill=(249, 115, 22))
    d.polygon([(rx - 12, 138), (rx + 12, 138), (rx, h - 24)], fill=(254, 240, 138))
    # China & Pakistan flags side by side near orbit
    d.rectangle([42, int(h * 0.68), 90, int(h * 0.68) + 28], fill=(220, 38, 38), outline=(255, 255, 255), width=2)
    d.ellipse([48, int(h * 0.68) + 6, 60, int(h * 0.68) + 18], fill=(250, 204, 21))
    # Tiangong solar wing station upper right
    tx, ty = int(w * 0.74), 92
    for wx in (tx - 84, tx + 30):
        d.rectangle([wx, ty - 28, wx + 54, ty - 8], fill=(59, 130, 246), outline=(250, 204, 21), width=2)
        d.rectangle([wx, ty + 8, wx + 54, ty + 28], fill=(59, 130, 246), outline=(250, 204, 21), width=2)
    d.rounded_rectangle([tx - 38, ty - 9, tx + 38, ty + 9], radius=4, fill=(248, 250, 252))
    d.rectangle([tx - 62, ty - 48, tx - 14, ty - 20], fill=(21, 128, 61), outline=(255, 255, 255), width=2)
    d.ellipse([tx - 46, ty - 42, tx - 28, ty - 26], fill=(255, 255, 255))
    return im


def art_hodeidah_strikes(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (242, 224, 198))
    d = ImageDraw.Draw(im)
    # Warm Red Sea morning sky + harbor sea
    d.rectangle([0, int(h * 0.42), w, int(h * 0.68)], fill=(228, 196, 158))
    d.rectangle([0, int(h * 0.68), w, h], fill=(48, 86, 122))
    # Harbor quay, gantry cranes, oil tanks
    d.rectangle([0, int(h * 0.62), int(w * 0.62), int(h * 0.72)], fill=(94, 86, 76))
    for cx in (88, 174, 260):
        d.line([(cx, int(h * 0.62)), (cx, 66)], fill=(64, 72, 84), width=5)
        d.line([(cx - 12, 74), (cx + 42, 54)], fill=(180, 48, 42), width=4)
    # Cargo vessels & port smoke plume
    d.polygon([(354, int(h * 0.76)), (492, int(h * 0.76)), (516, int(h * 0.66)), (340, int(h * 0.66))], fill=(51, 65, 85))
    d.ellipse([198, 46, 312, 118], fill=(120, 114, 110))
    d.ellipse([226, 62, 290, 112], fill=(234, 88, 12))
    d.ellipse([242, 74, 276, 102], fill=(253, 224, 71))
    # Patriot / interceptor arc over Red Sea right
    d.arc([340, 26, 580, 160], 200, 325, fill=(22, 101, 52), width=4)
    d.ellipse([472, 54, 494, 76], fill=(250, 204, 21), outline=(220, 38, 38), width=3)
    return im


def art_russia_leak(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (236, 232, 224))
    d = ImageDraw.Draw(im)
    # Pale dawn sky + sombre steppe + memorial crosses left + data leak chart right
    d.rectangle([0, int(h * 0.60), w, h], fill=(96, 102, 92))
    d.rectangle([int(w * 0.50), 16, w - 16, h - 14], fill=(248, 245, 238), outline=(180, 174, 162), width=2)
    # Silhouette of burning Samara refinery towers top left horizon
    for tx, tw, th in [(42, 24, 44), (74, 18, 56), (104, 26, 40)]:
        d.rectangle([tx, int(h * 0.60) - th, tx + tw, int(h * 0.60)], fill=(68, 72, 82))
    d.ellipse([66, int(h * 0.60) - 72, 112, int(h * 0.60) - 34], fill=(234, 88, 12))
    # Ordered rows of crosses in foreground left
    for row, cy in enumerate([int(h * 0.70), int(h * 0.84)]):
        step = 34 if row == 0 else 44
        for cx in range(28, int(w * 0.48), step):
            sh = 20 if row == 0 else 28
            d.line([(cx, cy - sh), (cx, cy + 6)], fill=(238, 240, 244), width=4)
            d.line([(cx - 8, cy - sh + 7), (cx + 8, cy - sh + 7)], fill=(238, 240, 244), width=4)
    # Ascending mortality bars right panel (2022 -> 2026: ~500k)
    bars = [("22", 24), ("23", 46), ("24", 72), ("25", 98), ("26", 122)]
    for idx, (_yr, bh) in enumerate(bars):
        bx = int(w * 0.54) + idx * 52
        col = CRIMSON if idx == 4 else ((186, 62, 62) if idx == 3 else (142, 150, 162))
        d.rectangle([bx, h - 28 - bh, bx + 34, h - 28], fill=col)
    return im


def art_solomons_pact(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (222, 238, 248))
    d = ImageDraw.Draw(im)
    # Australia & Coral Sea map corridor + Flags + Pact Seal
    d.polygon([(0, h), (28, 42), (144, 52), (178, h)], fill=(198, 174, 134), outline=(146, 124, 88))
    d.polygon([(346, 22), (416, 30), (446, 56), (370, 68)], fill=(116, 166, 126), outline=(72, 114, 82))
    d.line([(122, 74), (366, 46)], fill=TEAL, width=5)
    d.ellipse([114, 66, 130, 82], fill=NAVY, outline=(255, 255, 255), width=2)
    d.ellipse([358, 38, 374, 54], fill=TEAL, outline=(255, 255, 255), width=2)
    # Australia flag bottom-left, Solomons diagonal flag mid-right
    d.rectangle([58, 14, 108, 40], fill=NAVY, outline=(255, 255, 255), width=2)
    d.rectangle([58, 14, 78, 26], fill=CRIMSON)
    d.rectangle([244, 22, 294, 48], fill=(21, 128, 61), outline=(255, 255, 255), width=2)
    d.polygon([(244, 22), (294, 22), (244, 48)], fill=NAVY)
    d.line([(244, 48), (294, 22)], fill=GOLD_ACCENT, width=4)
    # Compact signed ribbon pill bottom-right
    d.rounded_rectangle([w - 146, h - 36, w - 12, h - 10], radius=5, fill=TEAL, outline=(255, 255, 255), width=2)
    return im


def art_kospi_rout(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (18, 24, 38))
    d = ImageDraw.Draw(im)
    for gy in (26, 54, 82):
        d.line([(14, gy), (w - 14, gy)], fill=(34, 44, 66), width=2)
    pts = [(26, 24), (86, 30), (142, 48), (204, 44), (266, 72), (336, 92), (446, 96)]
    d.line(pts, fill=(239, 68, 68), width=5)
    for px, py in pts[-2:]:
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(254, 202, 202))
    # Selloff bars background left
    for i, bh in enumerate([16, 28, 42, 56, 70]):
        bx = 34 + i * 28
        d.rectangle([bx, h - 10 - bh, bx + 16, h - 10], fill=(153, 27, 27))
    return im


def art_cricket_204(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (22, 44, 68))
    d = ImageDraw.Draw(im)
    # Night cricket outfield + bright pitch
    d.rectangle([0, int(h * 0.56), w, h], fill=(34, 122, 64))
    d.polygon([(140, h), (210, int(h * 0.56)), (270, int(h * 0.56)), (340, h)], fill=(198, 178, 134))
    # Stumps
    for sx in (232, 240, 248):
        d.line([(sx, int(h * 0.52)), (sx, int(h * 0.66))], fill=(250, 204, 21), width=3)
    # Stadium light towers
    for fx in (56, w - 56):
        d.line([(fx, 14), (fx, int(h * 0.56))], fill=(148, 163, 184), width=3)
        d.rectangle([fx - 16, 10, fx + 16, 22], fill=(254, 249, 195))
    # Soaring six-ball trajectory arc
    d.arc([76, 14, 344, 122], 195, 345, fill=(250, 204, 21), width=4)
    d.ellipse([334, 40, 348, 54], fill=(220, 38, 38), outline=(255, 255, 255), width=2)
    return im


def art_ebola_drc(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (214, 232, 222))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.68), w, h], fill=(104, 136, 98))
    # White WHO medical clinic tent with bold red cross + ambulance
    d.polygon([(56, int(h * 0.72)), (88, 36), (222, 36), (254, int(h * 0.72))], fill=(252, 252, 252), outline=(148, 163, 184), width=2)
    d.rectangle([147, 50, 163, 86], fill=CRIMSON)
    d.rectangle([137, 60, 173, 76], fill=CRIMSON)
    # Evacuation truck left/right
    d.rounded_rectangle([278, 56, 376, int(h * 0.74)], radius=5, fill=(248, 250, 252), outline=(100, 116, 139), width=2)
    d.rectangle([290, 64, 326, 74], fill=NAVY)
    d.ellipse([292, int(h * 0.68), 312, int(h * 0.86)], fill=(30, 41, 59))
    d.ellipse([348, int(h * 0.68), 368, int(h * 0.86)], fill=(30, 41, 59))
    return im


def art_dhaka_wage(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (242, 246, 238))
    d = ImageDraw.Draw(im)
    # Daylight factory skyline background + bold rising emerald wage bars
    for fx, fw, fh in [(28, 44, 52), (82, 52, 66), (144, 38, 48)]:
        d.rectangle([fx, h - fh, fx + fw, h], fill=(168, 180, 174))
    # Bar 1: Tk 12,500 vs Bar 2: Tk 17,000 (+36%)
    d.rectangle([226, h - 54, 286, h - 10], fill=(148, 163, 184))
    d.rectangle([310, h - 88, 376, h - 10], fill=EMERALD)
    d.line([(204, h - 10), (420, h - 10)], fill=(100, 116, 139), width=3)
    return im


def art_australia_cpi(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (248, 242, 232))
    d = ImageDraw.Draw(im)
    # Ascending CPI quarters -> 4.9% 3-yr high
    heights = [28, 36, 48, 62, 84]
    for i, bh in enumerate(heights):
        bx = 42 + i * 48
        col = AMBER if i == 4 else ((208, 132, 52) if i == 3 else (180, 172, 158))
        d.rectangle([bx, h - 12 - bh, bx + 32, h - 12], fill=col)
    d.line([(28, h - 12), (296, h - 12)], fill=(96, 105, 118), width=3)
    d.line([(56, h - 46), (250, h - 92)], fill=CRIMSON, width=4)
    return im


def art_west_java_pit(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (218, 232, 224))
    d = ImageDraw.Draw(im)
    # Cross-section: hillside earth + overflowing river + vertical 100m flooded pit
    d.rectangle([0, int(h * 0.44), w, h], fill=(122, 86, 54))
    d.rectangle([0, int(h * 0.34), int(w * 0.40), int(h * 0.48)], fill=(56, 132, 198))
    d.rectangle([int(w * 0.34), int(h * 0.36), int(w * 0.56), h - 6], fill=(32, 74, 128))
    # Headframe & rescue marker
    d.line([(int(w * 0.32), int(h * 0.42)), (int(w * 0.45), 14), (int(w * 0.58), int(h * 0.42))], fill=(51, 65, 85), width=4)
    return im


def art_iowa_blast(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (226, 236, 244))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.70), w, h], fill=(116, 136, 86))
    # Prairie blast warning zone triangle + controlled smoke plume
    cx = int(w * 0.32)
    d.ellipse([cx - 56, 14, cx + 62, 76], fill=(110, 114, 122))
    d.ellipse([cx - 26, 36, cx + 28, 76], fill=(234, 88, 12))
    # Caution perimeter bar & hazard triangle right
    tx = int(w * 0.72)
    d.polygon([(tx, 22), (tx - 38, 84), (tx + 38, 84)], fill=GOLD_ACCENT, outline=RULE_DARK, width=4)
    d.line([(tx, 42), (tx, 64)], fill=RULE_DARK, width=5)
    d.ellipse([tx - 4, 70, tx + 4, 78], fill=RULE_DARK)
    return im


# ---------------------------------------------------------------------------
# World Map Projection & Non-Overlapping Pins (Exact 1x/2x Match)
# ---------------------------------------------------------------------------
WORLD_POLYGONS: list[list[tuple[float, float]]] = [
    [(-166, 66), (-140, 70), (-94, 72), (-62, 62), (-54, 48), (-72, 42), (-81, 26), (-92, 17), (-106, 20), (-124, 40), (-136, 57)],
    [(-52, 60), (-42, 82), (-18, 78), (-24, 65)],
    [(-80, 10), (-62, 11), (-35, -6), (-42, -23), (-58, -39), (-68, -54), (-75, -44), (-72, -18), (-81, -4)],
    [(-9, 37), (3, 43), (-5, 49), (10, 56), (6, 62), (24, 70), (42, 66), (48, 52), (38, 46), (26, 41), (16, 39), (12, 43), (2, 42)],
    [(-8, 51), (-2, 58), (2, 53), (-5, 50)],
    [(-17, 15), (-12, 29), (10, 37), (33, 31), (43, 12), (51, 11), (41, -3), (40, -18), (28, -33), (18, -34), (12, -16), (9, 4), (-7, 5)],
    [(44, -25), (50, -13), (47, -24)],
    [(34, 31), (42, 37), (56, 25), (60, 22), (50, 14), (43, 13), (35, 29)],
    [(44, 65), (72, 72), (126, 72), (168, 65), (144, 52), (132, 42), (122, 34), (120, 23), (108, 12), (102, 2), (96, 16), (86, 21), (78, 8), (68, 23), (58, 26), (42, 42)],
    [(130, 32), (141, 44), (145, 42), (137, 34)],
    [(96, 5), (118, -2), (136, -4), (132, -8), (106, -8)],
    [(114, -22), (130, -12), (142, -12), (153, -27), (148, -38), (134, -34), (116, -34)],
]

PINS: list[tuple[int, float, float, tuple[int, int, int]]] = [
    (1, 100.3, 40.9, TEAL),            # Jiuquan, China
    (2, 42.9, 14.8, CRIMSON),          # Hodeidah, Yemen
    (3, 49.5, 53.2, NAVY),             # Samara / Moscow, Russia
    (4, 159.9, -9.4, AMBER),           # Honiara / Canberra Solomons
    (5, 127.0, 37.6, NAVY),            # Seoul / Tokyo
    (6, 51.5, 25.3, CRIMSON),          # Doha, Qatar
    (7, 29.8, 1.6, EMERALD),           # Ituri, DR Congo
    (8, 90.4, 23.8, EMERALD),          # Dhaka, Bangladesh
    (9, 149.1, -35.3, AMBER),          # Canberra, Australia
    (10, 106.8, -6.6, TEAL),           # Bogor, West Java
    (11, -91.2, 40.8, AMERICAS_BLUE),  # Middletown, Iowa, US
]


def _proj_1x(lon: float, lat: float, x: int, y: int, w: int, h: int) -> tuple[float, float]:
    return (
        x + ((lon + 180.0) / 360.0 * (w - 12)) + 6.0,
        y + ((84.0 - lat) / 142.0 * (h - 12)) + 6.0,
    )


def draw_map_surface(im: Image.Image, mx: int, my: int, mw: int, mh: int) -> None:
    d = ImageDraw.Draw(im)
    d.rectangle([mx * SCALE, my * SCALE, (mx + mw) * SCALE, (my + mh) * SCALE], fill=OCEAN, outline=RULE_LIGHT, width=2)
    for lon in (-120, -60, 0, 60, 120):
        px, _ = _proj_1x(lon, 0, mx, my, mw, mh)
        d.line([(int(px * SCALE), my * SCALE + 4), (int(px * SCALE), (my + mh) * SCALE - 4)], fill=(208, 222, 236), width=2)
    for lat in (-40, 0, 40):
        _, py = _proj_1x(0, lat, mx, my, mw, mh)
        d.line([(mx * SCALE + 4, int(py * SCALE)), ((mx + mw) * SCALE - 4, int(py * SCALE))], fill=(208, 222, 236), width=2)

    for poly_pts in WORLD_POLYGONS:
        pts_2x = []
        for lon, lat in poly_pts:
            px, py = _proj_1x(lon, lat, mx, my, mw, mh)
            pts_2x.append((int(round(px * SCALE)), int(round(py * SCALE))))
        d.polygon(pts_2x, fill=LAND, outline=LAND_EDGE)

    # Assert non-overlapping pin spacing at 1x
    coords = []
    for num, lon, lat, col in PINS:
        px, py = _proj_1x(lon, lat, mx, my, mw, mh)
        for pnum, ox, oy in coords:
            dist = math.hypot(px - ox, py - oy)
            assert dist >= 13.5, f"Pins {num} and {pnum} too close: {dist:.1f}px"
        coords.append((num, px, py))
        cx, cy = int(round(px * SCALE)), int(round(py * SCALE))
        r = 12
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(255, 255, 255), width=2)


def draw_map_pin_nums(draw: ImageDraw.ImageDraw, mx: int, my: int, mw: int, mh: int) -> None:
    for num, lon, lat, _col in PINS:
        px, py = _proj_1x(lon, lat, mx, my, mw, mh)
        t = str(num)
        bb = draw.textbbox((0, 0), t, font=F_PIN)
        draw.text((int(round(px)) - (bb[2] - bb[0]) // 2, int(round(py)) - (bb[3] - bb[1]) // 2 - 1), t, font=F_PIN, fill=(255, 255, 255))


# ---------------------------------------------------------------------------
# 100% Date-Verified Wednesday 25 November 2026 Content (36 Stories)
# ---------------------------------------------------------------------------
KPIS = [
    ("1st", "Pakistani astronaut aboard China's Tiangong station", NAVY),
    ("≈500,000", "Russian war dead exposed in leaked Rosstat data", CRIMSON),
    ("-6.16%", "Kospi sell curb; SoftBank drops ~14% in AI rout", CRIMSON),
    ("204/53b", "Vaibhav Sooryavanshi, 15, smashes List A record", EMERALD),
    ("5,775", "DRC Ebola deaths as WHO pulls Akwe clinic teams", AMBER),
    ("+36%", "Bangladesh lifts garment minimum wage to Tk 17,000", TEAL),
]

LEADS = [
    LeadArticle(
        1,
        "ASIA",
        "LIFTOFF",
        TEAL,
        "ASIA · SPACE · JIUQUAN",
        "Shenzhou-24 launches 1st foreign astronaut to Tiangong",
        "Long March-2F lifts off at 00:18 UTC carrying Tang Hongbo, Wu Yi and Pakistani payload specialist Muhammad Zeeshan Ali.",
        "XINHUA · AP · REUTERS",
        "00:18 UTC · CREW 3",
        art_shenzhou24,
    ),
    LeadArticle(
        2,
        "ME",
        "AIRSTRIKES",
        CRIMSON,
        "MIDDLE EAST · CONFLICT · HODEIDAH",
        "Saudi-led coalition bombs Hodeidah; downs 4 drones",
        "Jets strike Houthi port, Saada & Amran in Wed retaliation after Tue PIF hit; Houthis warn Jeddah ships.",
        "REUTERS · AL JAZEERA · ARAB NEWS",
        "4 DRONES DOWNED",
        art_hodeidah_strikes,
    ),
    LeadArticle(
        3,
        "EUROPE",
        "LEAKED",
        CRIMSON,
        "EUROPE · WAR DATA · MOSCOW & SAMARA",
        "Leaked Rosstat files reveal ~500,000 Russian dead",
        "Hacked mortality data shows ~490k–500k war dead as Ukrainian drones strike two Samara oil refineries overnight.",
        "MEDIAZONA · BBC · KYIV IND.",
        "~490K–500K DEAD",
        art_russia_leak,
    ),
]

CARDS = [
    CardArticle(4, "OCEANIA", "OCEANIA · CANBERRA", "Australia–Solomons seal A$740M base-ban pact", "DFAT · GUARDIAN · ABC", AMBER, "A$740M PACT", art_solomons_pact),
    CardArticle(5, "ASIA", "ASIA · SEOUL / TOKYO", "Kospi sinks 6.16% curb; SoftBank slides ~14%", "REUTERS · CHOSUN", CRIMSON, "-6.16% CURB", art_kospi_rout),
    CardArticle(6, "ASIA", "SOUTH ASIA / QATAR", "Boy of 15 hits 204 off 53 balls with 28 sixes", "ICC · BBC · THE HINDU", EMERALD, "204* (53)", art_cricket_204),
    CardArticle(7, "AFRICA", "AFRICA · ITURI, DRC", "WHO pulls Ebola teams from Congo; 5,775 dead", "WHO · AL JAZEERA", CRIMSON, "11,613 CASES", art_ebola_drc),
    CardArticle(8, "ASIA", "ASIA · DHAKA", "Bangladesh lifts garment floor +36% to Tk 17k", "PROTHOM ALO · BDNEWS24", EMERALD, "Tk 12.5k -> 17k", art_dhaka_wage),
    CardArticle(9, "OCEANIA", "OCEANIA · CANBERRA", "Australian Oct CPI jumps to 4.9% 3-yr high", "ABS · ABC · XINHUA", AMBER, "4.9% OCT CPI", art_australia_cpi),
    CardArticle(10, "ASIA", "SE ASIA · WEST JAVA", "Flooded 100m illegal gold shaft traps miners", "WASHPOST · JAKARTA GLOBE", TEAL, "100M PIT", art_west_java_pit),
    CardArticle(11, "AMERICAS", "AMERICAS · IOWA, US", "Army detonates 5t lead azide; 5-mile alert", "US ARMY · ILLINOIS.GOV", AMERICAS_BLUE, "5-MILE EVAC", art_iowa_blast),
]

# 25 numbered briefs (#12-#36) distributed 9 + 8 + 8 across 3 newspaper columns
BRIEFS_COLS: list[list[tuple[int, str, str, str, str]]] = [
    [
        (12, "AMERICAS", "WASHINGTON", "USTR readies 16-nation Section 301 overcapacity tariffs", "REUTERS"),
        (13, "AMERICAS", "PALM BEACH", "NATO chief Rutte holds Mar-a-Lago talks with Trump", "NATO.INT"),
        (14, "AMERICAS", "NEW YORK", "UNODC: 47,000 women killed by partners/kin (5/hr)", "UNODC"),
        (15, "AMERICAS", "UNITED STATES", "81.5m Americans face coastal storms in holiday travel", "AAA / AP"),
        (16, "AMERICAS", "WASHINGTON", "US AG dodges House probe on Trump Nvidia role", "BBC"),
        (17, "EUROPE", "LONDON", "Record 5,258 summer heat deaths in England", "UKHSA"),
        (18, "EUROPE", "LONDON", "UK sanctions Yemen Houthis & 4 senior officials", "GOV.UK"),
        (19, "EUROPE", "BRUSSELS", "EU states debate €210B frozen Russian asset loans", "EUROM"),
        (20, "EUROPE", "MOSCOW", "Putin hosts Brunei Sultan Hassanal Bolkiah for talks", "KREMLIN"),
    ],
    [
        (21, "EUROPE", "DARMSTADT", "ESA Hera reveals first close-up images of Dimorphos", "ESA"),
        (22, "EUROPE", "KYIV / SEA", "'We'll keep sinking Russian ships,' Ukraine vows", "AJ"),
        (23, "EUROPE", "GENEVA", "FIDE Chess: Gukesh & Sindarov draw Game 1 in 38", "FIDE"),
        (24, "EUROPE", "FRANKFURT", "Lufthansa pilot union blasts airline as talks fail", "AA"),
        (25, "ASIA", "SHANGHAI", "Party officials pledge loyalty amid Chen Jining probe", "REUTERS"),
        (26, "OCEANIA", "HOBART", "Tasmania Flinders Is. blaze triggers boat rescues", "GUARD"),
        (27, "OCEANIA", "CANBERRA", "Parliament apologises to historic LGBTQ military", "DEFENCE"),
        (28, "ASIA", "PANAY, PH", "Shallow M5.3 earthquake shakes Panay; checks start", "PHIVOLCS"),
    ],
    [
        (29, "ASIA", "JAKARTA", "OECD chief Cormann meets Prabowo on accession", "ANTARA"),
        (30, "ASIA", "TAIPEI", "BBC Verify exposes China-linked deepfake ads", "BBC"),
        (31, "ASIA", "BANGKOK", "Thailand DDPM warns 15 southern provinces on floods", "NATION"),
        (32, "ME", "GAZA / DOHA", "Israeli strikes kill 7 in Gaza as Qatar urges truce", "AJ / QNA"),
        (33, "ME", "TEHRAN", "Iran warns of winter gas rationing as cold deepens", "AJ"),
        (34, "EUROPE", "LONDON / UCL", "Gold slips to ~$3,545/oz; UCL Matchday 5 kicks off", "REUTERS"),
        (35, "AFRICA", "DAURA, NIG.", "Monarch, 92, suspended over viral palace assault video", "BBC"),
        (36, "AFRICA", "GAUTENG, SA", "Level-2 water curbs hit Johannesburg amid grid crisis", "AFNEWS"),
    ],
]


def compute_region_counts() -> dict[str, int]:
    counts: dict[str, int] = {k: 0 for k in REGION_COLORS}
    seen_nums: list[int] = []
    for lead in LEADS:
        counts[lead.region_code] += 1
        seen_nums.append(lead.num)
    for card in CARDS:
        counts[card.region_code] += 1
        seen_nums.append(card.num)
    for col in BRIEFS_COLS:
        for n, reg, _c, _t, _s in col:
            counts[reg] += 1
            seen_nums.append(n)
    assert seen_nums == list(range(1, 37)), f"Story numbers mismatch: {seen_nums}"
    assert sum(counts.values()) == 36, f"Expected 36 stories, got {sum(counts.values())}"
    return counts


def render() -> None:
    counts = compute_region_counts()
    hi = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), PAPER)
    dh = ImageDraw.Draw(hi)

    # Top folio strip & crisp masthead rules (2x)
    dh.rectangle([0, 0, WIDTH * SCALE, 21 * SCALE], fill=RULE_DARK)
    dh.line([14 * SCALE, 75 * SCALE, 1010 * SCALE, 75 * SCALE], fill=RULE_DARK, width=4)

    # Full-width colored region distribution bar (y: 78..92, x: 14..1010 = 996px wide)
    reg_order = [
        ("ASIA", "ASIA-PACIFIC"),
        ("EUROPE", "EUROPE"),
        ("AMERICAS", "AMERICAS"),
        ("ME", "MIDDLE EAST"),
        ("AFRICA", "AFRICA"),
        ("OCEANIA", "OCEANIA"),
    ]
    total = 36
    rx = 14
    rem_w = 996
    bar_segments: list[tuple[str, int, int, tuple[int, int, int]]] = []
    for idx, (rk, rlabel) in enumerate(reg_order):
        cnt = counts[rk]
        sw = rem_w if idx == len(reg_order) - 1 else round(996 * cnt / total)
        bar_segments.append((f"{rlabel} {cnt}", rx, sw, REGION_COLORS[rk]))
        dh.rectangle([rx * SCALE, 78 * SCALE, (rx + sw) * SCALE, 92 * SCALE], fill=REGION_COLORS[rk])
        rx += sw
        rem_w -= sw

    # UTC Timeline Strip (y: 95..112)
    dh.rectangle([14 * SCALE, 95 * SCALE, 1010 * SCALE, 112 * SCALE], fill=PAPER_WARM)
    dh.rectangle([14 * SCALE, 95 * SCALE, 104 * SCALE, 112 * SCALE], fill=RULE_DARK)
    dh.line([14 * SCALE, 113 * SCALE, 1010 * SCALE, 113 * SCALE], fill=RULE_DARK, width=2)

    # 6 Hairline KPI Columns (y: 115..158, clean ivory with thin vertical hairlines)
    kpi_w = 166
    for i in range(1, 6):
        kx = (14 + i * kpi_w) * SCALE
        dh.line([kx, 119 * SCALE, kx, 153 * SCALE], fill=RULE_LIGHT, width=2)
    dh.line([14 * SCALE, 158 * SCALE, 1010 * SCALE, 158 * SCALE], fill=RULE_DARK, width=2)

    # 3 Hero Lead Art Panels (y: 164..268, h=104, lw=322, gap=15)
    lw, lgap = 322, 15
    for idx, lead in enumerate(LEADS):
        lx, ly = 14 + idx * (lw + lgap), 164
        art = lead.drawer(lw * SCALE, 104 * SCALE)
        hi.paste(art, (lx * SCALE, ly * SCALE))
        dh.rectangle([lx * SCALE, (ly + 108) * SCALE, (lx + 68) * SCALE, (ly + 121) * SCALE], fill=lead.badge_col)
        # Overlay subtle pill box inside top-right of artwork
        dh.rounded_rectangle([(lx + lw - 122) * SCALE, (ly + 6) * SCALE, (lx + lw - 6) * SCALE, (ly + 21) * SCALE], radius=4, fill=(18, 22, 30), outline=(255, 255, 255), width=1)
    dh.line([14 * SCALE, 379 * SCALE, 1010 * SCALE, 379 * SCALE], fill=RULE_DARK, width=3)

    # 8 Mid Cards (2 rows x 4 cols: y=401..659)
    cw, ch, cgap = 240, 125, 12
    for idx, card in enumerate(CARDS):
        col, row = idx % 4, idx // 4
        cx = 14 + col * (cw + cgap)
        cy = 401 + row * (ch + 8)
        art = card.drawer(cw * SCALE, 54 * SCALE)
        hi.paste(art, (cx * SCALE, cy * SCALE))
        dh.ellipse([(cx + 5) * SCALE, (cy + 5) * SCALE, (cx + 21) * SCALE, (cy + 21) * SCALE], fill=card.accent, outline=(255, 255, 255), width=2)
        dh.rounded_rectangle([(cx + cw - 92) * SCALE, (cy + 5) * SCALE, (cx + cw - 5) * SCALE, (cy + 19) * SCALE], radius=4, fill=(18, 22, 30), outline=(255, 255, 255), width=1)
        dh.line([cx * SCALE, (cy + ch) * SCALE, (cx + cw) * SCALE, (cy + ch) * SCALE], fill=RULE_LIGHT, width=2)
    dh.line([14 * SCALE, 663 * SCALE, 1010 * SCALE, 663 * SCALE], fill=RULE_DARK, width=3)

    # World Map Surface (x=14..322, y=684..892)
    mx, my, mw, mh = 14, 684, 308, 208
    draw_map_surface(hi, mx, my, mw, mh)

    # Date Check Box (y: 952..998) + Bottom Footer (1002..1024)
    dh.line([14 * SCALE, 950 * SCALE, 1010 * SCALE, 950 * SCALE], fill=RULE_DARK, width=2)
    dh.rectangle([14 * SCALE, 954 * SCALE, 1010 * SCALE, 998 * SCALE], fill=PAPER_WARM)
    dh.rectangle([14 * SCALE, 954 * SCALE, 18 * SCALE, 998 * SCALE], fill=CRIMSON)
    dh.rectangle([0, 1002 * SCALE, WIDTH * SCALE, HEIGHT * SCALE], fill=RULE_DARK)

    # Downsample crisp 2x artwork onto 1024x1024 surface
    img = hi.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    # 1x Sharp Typography Layer
    draw.text((14, 5), "THE WORLD IN ONE DAY", font=F_TOPBAR, fill=(255, 255, 255))
    center_lbl = "36 VERIFIED STORIES · 6 REGIONS · ZERO PRIOR-DAY BLEED"
    cb = draw.textbbox((0, 0), center_lbl, font=F_REG_BAR)
    draw.text(((WIDTH - (cb[2] - cb[0])) // 2, 5), center_lbl, font=F_REG_BAR, fill=(203, 213, 225))
    draw.text((806, 5), "EVERY STORY DATED WED 25 NOV", font=F_TOPBAR, fill=GOLD_ACCENT)

    mast = "Wednesday 25 November 2026"
    mb = draw.textbbox((0, 0), mast, font=F_MAST)
    assert mb[2] - mb[0] < 996
    draw.text(((WIDTH - (mb[2] - mb[0])) // 2, 21), mast, font=F_MAST, fill=INK)

    # Full-width region count labels (short label fallback only if bar too narrow)
    for txt, sx, sw, _col in bar_segments:
        tb = draw.textbbox((0, 0), txt, font=F_REG_BAR)
        show_txt = txt
        if tb[2] - tb[0] > sw - 6:
            show_txt = txt.replace("MIDDLE EAST", "M. EAST")
            tb = draw.textbbox((0, 0), show_txt, font=F_REG_BAR)
        assert tb[2] - tb[0] <= sw - 4, f"Region label overflow {show_txt}: {tb[2]-tb[0]} > {sw}"
        draw.text((sx + (sw - (tb[2] - tb[0])) // 2, 80), show_txt, font=F_REG_BAR, fill=(255, 255, 255))

    # Chronological UTC timeline text
    draw.text((21, 99), "THE DAY IN UTC", font=F_UTC_LBL, fill=GOLD_ACCENT)
    utc_slots = [
        ("00:18", "Shenzhou-24 liftoff"),
        ("00:30", "Aus CPI hits 4.9%"),
        ("01:22", "Solomons pact signed"),
        ("02:46", "Hodeidah bombed"),
        ("06:00", "Kospi -6.16% curb"),
        ("11:30", "Putin–Brunei · Rutte"),
    ]
    ux = 112
    uw = (1010 - 112) // len(utc_slots)
    for t_str, desc in utc_slots:
        tb = draw.textbbox((0, 0), t_str, font=F_UTC_LBL)
        tw = tb[2] - tb[0]
        draw.text((ux, 98), t_str, font=F_UTC_LBL, fill=CRIMSON)
        draw.text((ux + tw + 4, 98), desc, font=F_UTC_TXT, fill=INK)
        ux += uw

    # 6 KPI Stats
    for i, (num_txt, desc_txt, col) in enumerate(KPIS):
        kx = 20 + i * kpi_w
        draw.text((kx, 117), num_txt, font=F_KPI_NUM, fill=col)
        draw_text_lines(draw, kx, 138, desc_txt, F_KPI_TXT, SLATE, kpi_w - 14, 10, 2)

    # 3 Hero Leads Text
    for idx, lead in enumerate(LEADS):
        lx, ly = 14 + idx * (lw + lgap), 164
        draw.ellipse([lx + 6, ly + 6, lx + 23, ly + 23], fill=lead.badge_col, outline=(255, 255, 255))
        nb = draw.textbbox((0, 0), str(lead.num), font=F_PIN)
        draw.text((lx + 14 - (nb[2] - nb[0]) // 2, ly + 8), str(lead.num), font=F_PIN, fill=(255, 255, 255))
        # Artwork top-right pill
        pb = draw.textbbox((0, 0), lead.art_pill, font=F_ART_PILL)
        draw.text((lx + lw - 64 - (pb[2] - pb[0]) // 2, ly + 8), lead.art_pill, font=F_ART_PILL, fill=GOLD_ACCENT)
        # Badge
        bb_tag = draw.textbbox((0, 0), lead.badge, font=F_LEAD_TAG)
        draw.text((lx + (68 - (bb_tag[2] - bb_tag[0])) // 2, ly + 109), lead.badge, font=F_LEAD_TAG, fill=(255, 255, 255))
        draw.text((lx + 74, ly + 109), lead.region_line, font=F_LEAD_TAG, fill=MUTED)
        ny = draw_text_lines(draw, lx, ly + 125, lead.headline, F_LEAD_TITLE, INK, lw, 19, 2)
        draw_text_lines(draw, lx, ny + 3, lead.summary, F_LEAD_BODY, SLATE, lw, 12, 3)
        draw.text((lx, ly + 202), lead.sources, font=F_LEAD_SRC, fill=MUTED)

    # Section strip 2
    draw.text((14, 384), "THE DAY IN EIGHT", font=F_SEC_HDR, fill=INK)
    draw.text((712, 385), "BESPOKE VECTOR & DATA GRAPHICS · ALL WED 25 NOV", font=F_LEAD_SRC, fill=MUTED)

    # 8 Mid Cards Text
    for idx, card in enumerate(CARDS):
        col, row = idx % 4, idx // 4
        cx, cy = 14 + col * (cw + cgap), 401 + row * (ch + 8)
        nt = str(card.num)
        nb = draw.textbbox((0, 0), nt, font=F_PIN)
        draw.text((cx + 13 - (nb[2] - nb[0]) // 2, cy + 7), nt, font=F_PIN, fill=(255, 255, 255))
        pb = draw.textbbox((0, 0), card.art_pill, font=F_ART_PILL)
        draw.text((cx + cw - 48 - (pb[2] - pb[0]) // 2, cy + 7), card.art_pill, font=F_ART_PILL, fill=(255, 255, 255))
        if card.num == 4:
            # Signed ribbon label inside bottom-right seal
            draw.text((cx + cw - 68, cy + 38), "NO BASES", font=F_ART_PILL, fill=(255, 255, 255))
        elif card.num == 8:
            draw.text((cx + 116, cy + 31), "12.5k", font=F_CARD_SRC, fill=(255, 255, 255))
            draw.text((cx + 164, cy + 24), "17k", font=F_CARD_TAG, fill=(255, 255, 255))
        elif card.num == 9:
            draw.text((cx + 158, cy + 26), "4.9% CPI", font=F_CARD_TAG, fill=CRIMSON)
        draw.text((cx, cy + 57), card.region_line, font=F_CARD_TAG, fill=card.accent)
        draw_text_lines(draw, cx, cy + 69, card.headline, F_CARD_TITLE, INK, cw, 15, 2)
        draw.text((cx, cy + 106), card.sources, font=F_CARD_SRC, fill=MUTED)

    # Bottom Atlas & 25 Briefs
    draw.text((14, 668), "WHERE IT HAPPENED", font=F_SEC_HDR, fill=INK)
    draw.text((336, 668), "ALSO ON WEDNESDAY 25 NOV — 25 MORE VERIFIED STORIES", font=F_SEC_HDR, fill=INK)
    draw.text((902, 669), "PIN = STORY #1–11", font=F_LEAD_SRC, fill=MUTED)
    draw_map_pin_nums(draw, mx, my, mw, mh)
    draw_text_lines(
        draw,
        mx,
        897,
        "1 Jiuquan · 2 Hodeidah · 3 Samara · 4 Honiara · 5 Seoul · 6 Doha · 7 Ituri DRC · 8 Dhaka · 9 Canberra · 10 West Java · 11 Iowa",
        F_CARD_SRC,
        SLATE,
        mw,
        12,
        4,
    )

    # 3 Briefs Columns (x=336..1010, col w=216, gap=12)
    bcol_w = 216
    for cidx, items in enumerate(BRIEFS_COLS):
        bx = 336 + cidx * (bcol_w + 12)
        step_y = 29 if len(items) == 9 else 33
        for ridx, (num, reg, city, text, src) in enumerate(items):
            by = 684 + ridx * step_y
            prefix = f"{num}  {city} "
            pb = draw.textbbox((0, 0), prefix, font=F_BRIEF_CITY)
            pw = pb[2] - pb[0]
            draw.text((bx, by), prefix, font=F_BRIEF_CITY, fill=REGION_COLORS[reg])
            words = f"{text} [{src}]".split()
            l1, l2, filled = [], [], False
            cur = ""
            for w in words:
                cand = f"{cur} {w}".strip()
                wb = draw.textbbox((0, 0), cand, font=F_BRIEF_TXT)
                if not filled and pw + (wb[2] - wb[0]) <= bcol_w:
                    cur = cand
                    l1.append(w)
                else:
                    filled = True
                    l2.append(w)
            draw.text((bx + pw, by), " ".join(l1), font=F_BRIEF_TXT, fill=INK)
            if l2:
                l2_lines = wrap_lines(draw, " ".join(l2), F_BRIEF_TXT, bcol_w)
                assert len(l2_lines) == 1, f"Brief overflow {num} {city}: {l2_lines}"
                draw.text((bx, by + 12), l2_lines[0], font=F_BRIEF_TXT, fill=SLATE)

    # Date Check Strip
    draw.text((24, 958), "DATE CHECK:", font=F_DATE_BOLD, fill=CRIMSON)
    dc_txt = (
        "Excluded earlier days — Mon 23 Nov: Huang Nvidia return (+31.5%), Villavicencio car bomb, Anmer Hall break-in. "
        "Tue 24 Nov: Houthi PIF Tower strike in Riyadh, Huawei Brooklyn verdict, Senegal AFCON restoration, Sarkozy trial order, Sanofi $41B deal. "
        "Nov 20: Bayelsa boat crash. All 36 dispatches above broke or developed Wednesday 25 Nov 2026."
    )
    draw_text_lines(draw, 94, 957, dc_txt, F_DATE_TXT, INK, 908, 12, 3)

    # Bottom Footer
    draw.text(
        (14, 1006),
        "SOURCES: REUTERS · AP · BBC · GUARDIAN · AL JAZEERA · XINHUA · MEDIAZONA · ICC · WHO · UNODC · ABS · ESA · DFAT · NATO",
        font=F_TOPBAR,
        fill=(226, 232, 240),
    )
    draw.text((828, 1006), "WEDNESDAY 25 NOVEMBER 2026", font=F_TOPBAR, fill=GOLD_ACCENT)

    img.save(OUT_PATH, format="PNG", optimize=True)
    print(f"Generated v3 {OUT_PATH}: {os.path.getsize(OUT_PATH)} bytes")


if __name__ == "__main__":
    render()
