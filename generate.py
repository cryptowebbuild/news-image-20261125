"""
Master Editorial Broadsheet Generator v5 for news-image-20261125:
  Full-bleed 2x supersampled editorial illustrations with smooth atmospheric
  gradients and embedded data charts (zero heavy black sticker overlays),
  pure Wednesday 25 November 2026 curated stories (up to 11:30 UTC),
  inline HOW SURE epistemic badges, chronological UTC ticker, 6 hairline KPIs,
  non-overlapping 11-pin world map, 2-column scannable briefs, and DATE CHECK.
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
    raise FileNotFoundError(f"Could not locate font from {candidates}")


def ft(kind: str, size: int) -> ImageFont.FreeTypeFont:
    mapping = {
        "serif_bold": ["georgiab.ttf", "DejaVuSerif-Bold.ttf", "LiberationSerif-Bold.ttf"],
        "serif_italic": ["georgiai.ttf", "DejaVuSerif-Italic.ttf", "LiberationSerif-Italic.ttf"],
        "sans": ["arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
        "sans_bold": ["arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
    }
    return ImageFont.truetype(_find_font(mapping[kind]), size)


# Editorial broadsheet 1x type scale
F_TOPBAR = ft("sans_bold", 10)
F_MAST = ft("serif_bold", 54)
F_DECK = ft("serif_italic", 12)
F_REG_BAR = ft("sans_bold", 9)
F_UTC_LBL = ft("sans_bold", 9)
F_UTC_TXT = ft("sans", 9)
F_KPI_NUM = ft("serif_bold", 20)
F_KPI_TXT = ft("sans", 9)

F_LEAD_TAG = ft("sans_bold", 8)
F_LEAD_TITLE = ft("serif_bold", 16)
F_LEAD_BODY = ft("sans", 10)
F_LEAD_SRC = ft("sans_bold", 8)

F_CARD_TAG = ft("sans_bold", 8)
F_CARD_TITLE = ft("serif_bold", 12)
F_CARD_BODY = ft("sans", 9)
F_STATUS = ft("sans_bold", 8)

F_SEC_HDR = ft("sans_bold", 10)
F_BRIEF_NUM = ft("sans_bold", 9)
F_BRIEF_CITY = ft("sans_bold", 9)
F_BRIEF_TXT = ft("sans", 9)
F_PIN = ft("sans_bold", 9)
F_DATE_BOLD = ft("sans_bold", 9)
F_DATE_TXT = ft("sans", 9)
F_ART_LBL = ft("sans_bold", 8)
F_ART_MED = ft("sans_bold", 11)
F_ART_BIG = ft("serif_bold", 18)

# Classic high-contrast ivory broadsheet palette
PAPER = (247, 243, 234)
PAPER_WARM = (239, 234, 222)
INK = (16, 20, 28)
SLATE = (54, 62, 74)
MUTED = (94, 104, 118)
RULE_DARK = (22, 26, 34)
RULE_LIGHT = (206, 198, 184)

CRIMSON = (176, 30, 34)
NAVY = (24, 62, 126)
AMERICAS_BLUE = (44, 92, 158)
TEAL = (20, 112, 102)
AMBER = (176, 92, 16)
EMERALD = (24, 116, 62)
AFRICA_PLUM = (108, 48, 134)
GLOBAL_SLATE = (66, 78, 92)
GOLD = (250, 204, 21)

OCEAN = (222, 233, 242)
LAND = (204, 198, 182)
LAND_EDGE = (138, 132, 118)

REGION_META = [
    ("ASIA", "ASIA", CRIMSON),
    ("ME", "MIDDLE EAST", AMBER),
    ("EUROPE", "EUROPE", NAVY),
    ("AMERICAS", "AMERICAS", AMERICAS_BLUE),
    ("AFRICA", "AFRICA", AFRICA_PLUM),
    ("OCEANIA", "OCEANIA", EMERALD),
    ("GLOBAL", "GLOBAL", GLOBAL_SLATE),
]
REGION_COLORS = {k: c for k, _lbl, c in REGION_META}

STATUS_COLORS: dict[str, tuple[tuple[int, int, int], tuple[int, int, int]]] = {
    "CONFIRMED": ((230, 245, 235), (20, 106, 56)),
    "OFFICIAL": ((230, 239, 250), (24, 62, 126)),
    "REPORTED": ((243, 241, 235), (72, 80, 92)),
    "CLAIM": ((254, 240, 226), (176, 82, 16)),
}


@dataclass(frozen=True)
class LeadArticle:
    num: int
    region: str
    tag_lbl: str
    tag_col: tuple[int, int, int]
    status: str
    place_line: str
    headline: str
    summary: str
    sources: str
    drawer: Callable[[int, int], Image.Image]


@dataclass(frozen=True)
class CardArticle:
    num: int
    region: str
    status: str
    place_line: str
    headline: str
    summary: str
    drawer: Callable[[int, int], Image.Image]


def _grad_v(im: Image.Image, top: tuple[int, int, int], bot: tuple[int, int, int], y0: int = 0, y1: int | None = None) -> None:
    d = ImageDraw.Draw(im)
    w, h = im.size
    end = h if y1 is None else min(h, y1)
    span = max(1, end - y0)
    for y in range(y0, end):
        t = (y - y0) / span
        c = tuple(int(top[i] * (1.0 - t) + bot[i] * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
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
    draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int], max_w: int, line_h: int, max_lines: int
) -> int:
    lines = wrap_lines(draw, text, font, max_w)
    assert len(lines) <= max_lines, f"Wrapped {len(lines)} > {max_lines}: {text}"
    for i, ln in enumerate(lines):
        draw.text((x, y + i * line_h), ln, font=font, fill=fill)
    return y + len(lines) * line_h


def draw_status_box(draw: ImageDraw.ImageDraw, rx: int, y: int, status: str) -> None:
    bg, fg = STATUS_COLORS[status]
    bw = draw.textbbox((0, 0), status, font=F_STATUS)[2] + 8
    draw.rectangle([rx - bw, y, rx, y + 12], fill=bg, outline=fg, width=1)
    draw.text((rx - bw + 4, y + 1), status, font=F_STATUS, fill=fg)


# ---------------------------------------------------------------------------
# 11 Full-Bleed Bespoke 2x Editorial Scenes with Embedded Data Graphics
# ---------------------------------------------------------------------------
def art_shenzhou24(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (14, 22, 48))
    _grad_v(im, (10, 16, 38), (26, 46, 92))
    d = ImageDraw.Draw(im)
    for sx, sy in [(44, 28), (118, 52), (206, 22), (318, 42), (420, 26), (528, 48), (596, 22), (96, 98), (382, 84)]:
        d.ellipse([sx, sy, sx + 4, sy + 4], fill=(226, 232, 240))
    # Glowing curved Earth limb at base
    d.ellipse([-140, int(h * 0.72), w + 140, h + 380], fill=(32, 86, 198))
    d.arc([-140, int(h * 0.72), w + 140, h + 380], 200, 340, fill=(147, 197, 253), width=4)
    # Dashed trajectory curve Jiuquan -> Tiangong
    for t in range(14):
        px = int(196 + t * 18)
        py = int(146 - math.sin(t / 13.0 * 1.45) * 62)
        d.ellipse([px, py, px + 6, py + 6], fill=GOLD)
    # Long March rocket rising center-left with plume
    rx = int(w * 0.30)
    d.polygon([(rx, 24), (rx - 14, 58), (rx + 14, 58)], fill=CRIMSON)
    d.rectangle([rx - 14, 58, rx + 14, 144], fill=(241, 245, 249))
    d.rectangle([rx - 22, 108, rx - 14, 148], fill=(203, 213, 225))
    d.rectangle([rx + 14, 108, rx + 22, 148], fill=(203, 213, 225))
    d.polygon([(rx - 24, 148), (rx + 24, 148), (rx, h - 6)], fill=(249, 115, 22))
    d.polygon([(rx - 12, 148), (rx + 12, 148), (rx, h - 22)], fill=(254, 240, 138))
    # Tiangong station upper right + China/Pakistan flags
    tx, ty = int(w * 0.76), 102
    for wx in (tx - 78, tx + 24):
        d.rectangle([wx, ty - 28, wx + 54, ty - 8], fill=(59, 130, 246), outline=GOLD, width=2)
        d.rectangle([wx, ty + 8, wx + 54, ty + 28], fill=(59, 130, 246), outline=GOLD, width=2)
    d.rounded_rectangle([tx - 34, ty - 9, tx + 34, ty + 9], radius=4, fill=(248, 250, 252))
    d.rectangle([tx - 54, 40, tx - 8, 66], fill=CRIMSON, outline=(255, 255, 255), width=2)
    d.rectangle([tx + 2, 40, tx + 48, 66], fill=EMERALD, outline=(255, 255, 255), width=2)
    d.ellipse([tx + 18, 46, tx + 32, 60], fill=(255, 255, 255))
    return im


def art_chips_crash(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (24, 20, 32))
    _grad_v(im, (30, 24, 42), (16, 18, 28))
    d = ImageDraw.Draw(im)
    for gx in range(36, int(w * 0.62), 54):
        d.line([(gx, 12), (gx, h - 12)], fill=(44, 48, 68), width=2)
    for gy in range(36, h - 20, 40):
        d.line([(16, gy), (int(w * 0.62), gy)], fill=(44, 48, 68), width=2)
    # Jagged steep intraday selloff curve
    pts = [(20, 42), (76, 52), (124, 44), (176, 84), (228, 76), (288, 128), (344, 154), (392, 174)]
    d.line(pts, fill=(239, 68, 68), width=5)
    d.polygon(pts + [(392, h), (20, h)], fill=(127, 29, 29))
    d.line(pts, fill=(248, 113, 113), width=5)
    # Sleek translucent right scorecard box inside scene
    d.rounded_rectangle([w - 224, 14, w - 12, h - 14], radius=6, fill=(14, 18, 30), outline=(71, 85, 105), width=2)
    return im


def art_hormuz_tankers(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (156, 198, 224))
    _grad_v(im, (148, 192, 222), (82, 138, 186))
    d = ImageDraw.Draw(im)
    # Iran northern coast & Oman southern Musandam cape framing the Strait
    d.polygon([(0, 0), (w, 0), (w, 56), (480, 66), (340, 82), (180, 74), (0, 96)], fill=(188, 166, 132), outline=(136, 118, 92))
    d.polygon([(0, h), (0, 142), (96, 152), (210, h)], fill=(198, 178, 142), outline=(146, 128, 98))
    d.polygon([(380, h), (470, 134), (w, 124), (w, h)], fill=(198, 178, 142), outline=(146, 128, 98))
    # Burning tanker #1 & #2 with plumes
    for bx, by, sc in [(196, 148, 1.0), (356, 132, 0.85)]:
        hw, hh = int(68 * sc), int(18 * sc)
        d.ellipse([bx - hw, by - 58, bx + hw, by], fill=(82, 86, 94))
        d.ellipse([bx - 22, by - 36, bx + 22, by + 4], fill=(234, 88, 12))
        d.ellipse([bx - 10, by - 24, bx + 12, by - 2], fill=GOLD)
        d.polygon([(bx - hw, by), (bx + hw, by), (bx + hw - 12, by + hh), (bx - hw + 10, by + hh)], fill=(38, 44, 58))
    # Mine blast ring
    mx, my = 278, 168
    d.ellipse([mx - 12, my - 12, mx + 12, my + 12], fill=CRIMSON, outline=GOLD, width=3)
    return im


def art_solomons_pact(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (228, 220, 204))
    _grad_v(im, (238, 232, 218), (216, 206, 190))
    d = ImageDraw.Draw(im)
    # Summit room with Australia & Solomon flags + treaty desk
    d.rectangle([48, 14, 156, 74], fill=NAVY, outline=(255, 255, 255), width=2)
    d.rectangle([48, 14, 96, 42], fill=CRIMSON)
    d.rectangle([324, 14, 432, 74], fill=EMERALD, outline=(255, 255, 255), width=2)
    d.polygon([(324, 14), (432, 14), (324, 74)], fill=NAVY)
    d.line([(324, 74), (432, 14)], fill=GOLD, width=5)
    # Leaders & treaty desk
    for px in (188, 292):
        d.ellipse([px - 14, 42, px + 14, 70], fill=(186, 138, 108))
        d.rectangle([px - 22, 70, px + 22, 104], fill=(30, 41, 59))
    d.rectangle([104, 92, 376, h], fill=(138, 92, 54))
    d.rounded_rectangle([194, 74, 286, 98], radius=4, fill=(252, 250, 244), outline=AMBER, width=2)
    return im


def art_unodc_femicide(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (38, 30, 44))
    _grad_v(im, (48, 36, 56), (26, 20, 34))
    d = ImageDraw.Draw(im)
    # Right side embedded 5-continent bar chart (Africa 2.9, Americas 1.4, Oceania 1.1, Asia 0.6, Europe 0.5)
    bars = [(2.9, AFRICA_PLUM), (1.4, AMERICAS_BLUE), (1.1, EMERALD), (0.6, CRIMSON), (0.5, NAVY)]
    for i, (val, col) in enumerate(bars):
        by = 36 + i * 15
        bw = int(val / 3.0 * 176)
        d.rectangle([w - 196, by, w - 196 + bw, by + 11], fill=col)
    return im


def art_uk_energy(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (232, 238, 246))
    _grad_v(im, (226, 236, 246), (206, 222, 238))
    d = ImageDraw.Draw(im)
    # Cozy brick home with gas flame warning + steep orange/red price meter
    cx = 134
    d.polygon([(cx - 64, 52), (cx, 18), (cx + 64, 52)], fill=CRIMSON)
    d.rectangle([cx - 52, 52, cx + 52, h - 6], fill=(30, 58, 108))
    d.ellipse([cx - 18, 60, cx + 18, 98], fill=(249, 115, 22))
    d.ellipse([cx - 9, 72, cx + 9, 96], fill=GOLD)
    return im


def art_hodeidah_drones(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (22, 34, 58))
    _grad_v(im, (18, 28, 52), (48, 66, 98))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.72), w, h], fill=(34, 72, 114))
    for kx in (64, 128, 204):
        d.line([(kx, int(h * 0.72)), (kx, 48)], fill=(100, 116, 139), width=4)
    for fx, fy in [(302, 46), (368, 34), (416, 56)]:
        d.ellipse([fx - 14, fy - 14, fx + 14, fy + 14], fill=(234, 88, 12), outline=GOLD, width=2)
        d.line([(160, 108), (fx, fy)], fill=(125, 211, 252), width=3)
    return im


def art_west_java(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (212, 228, 214))
    _grad_v(im, (218, 234, 222), (188, 212, 192))
    d = ImageDraw.Draw(im)
    # Lush hills & flooded 100m vertical gold pit cutaway
    d.rectangle([0, 44, w, h], fill=(128, 86, 52))
    d.rectangle([0, 32, 168, 52], fill=(48, 124, 196))
    d.rectangle([156, 36, 260, h], fill=(32, 72, 128))
    d.line([(134, 44), (208, 10), (282, 44)], fill=(64, 72, 84), width=4)
    d.line([(208, 10), (208, 92)], fill=GOLD, width=3)
    return im


def art_dhaka_wage(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (234, 244, 236))
    _grad_v(im, (240, 248, 242), (220, 236, 226))
    d = ImageDraw.Draw(im)
    # Sewing machine / factory silhouette left + bright emerald +36% stair right
    d.rectangle([38, 76, 148, h - 10], fill=(138, 152, 146))
    d.rectangle([104, 38, 144, 76], fill=(118, 134, 128))
    for i, bh in enumerate([34, 54, 82]):
        bx = 228 + i * 62
        d.rectangle([bx, h - 10 - bh, bx + 42, h - 10], fill=EMERALD if i == 2 else (148, 163, 184))
    d.line([(212, h - 10), (424, h - 10)], fill=SLATE, width=3)
    return im


def art_samara_refineries(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (24, 26, 38))
    _grad_v(im, (20, 22, 34), (42, 34, 44))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.72), w, h], fill=(16, 18, 24))
    for tx, tw, th in [(54, 42, 58), (112, 22, 84), (274, 46, 54), (338, 24, 82)]:
        d.rectangle([tx, int(h * 0.72) - th, tx + tw, int(h * 0.72)], fill=(58, 66, 80))
    for fx, fy in [(142, 42), (318, 36)]:
        d.ellipse([fx - 36, fy - 24, fx + 44, fy + 26], fill=(86, 92, 102))
        d.ellipse([fx - 20, fy - 12, fx + 24, fy + 24], fill=(234, 88, 12))
        d.ellipse([fx - 10, fy - 4, fx + 12, fy + 16], fill=GOLD)
    return im


def art_ebola_drc(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (216, 232, 220))
    _grad_v(im, (224, 238, 228), (194, 218, 202))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.68), w, h], fill=(98, 134, 92))
    # WHO tent + red cross + evacuation ambulance
    d.polygon([(46, int(h * 0.72)), (82, 28), (222, 28), (258, int(h * 0.72))], fill=(252, 252, 252), outline=(140, 150, 160), width=2)
    d.rectangle([144, 44, 160, 82], fill=CRIMSON)
    d.rectangle([133, 55, 171, 71], fill=CRIMSON)
    d.rounded_rectangle([296, 52, 412, int(h * 0.74)], radius=5, fill=(248, 250, 252), outline=(96, 106, 118), width=2)
    d.rectangle([308, 60, 354, 72], fill=NAVY)
    d.ellipse([310, int(h * 0.68), 332, int(h * 0.88)], fill=(30, 41, 59))
    d.ellipse([378, int(h * 0.68), 400, int(h * 0.88)], fill=(30, 41, 59))
    return im


# ---------------------------------------------------------------------------
# World Map Projection & Pins
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
    (1, 100.3, 40.9, CRIMSON),       # Jiuquan Shenzhou-24
    (2, 127.0, 37.6, CRIMSON),       # Seoul / Taipei chips
    (3, 56.5, 26.2, AMBER),          # Strait of Hormuz
    (4, 159.9, -9.4, EMERALD),       # Honiara Solomons
    (5, -74.0, 40.7, GLOBAL_SLATE),  # UNODC NY / Global
    (6, -0.1, 51.5, NAVY),           # UK Ofgem
    (7, 42.9, 14.8, AMBER),          # Hodeidah / Red Sea
    (8, 106.8, -6.6, CRIMSON),       # West Java pit
    (9, 90.4, 23.8, CRIMSON),        # Dhaka Bangladesh
    (10, 49.5, 53.2, NAVY),          # Samara Russia
    (11, 29.8, 1.6, AFRICA_PLUM),    # Ituri DRC
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
        d.line([(int(px * SCALE), my * SCALE + 4), (int(px * SCALE), (my + mh) * SCALE - 4)], fill=(204, 218, 232), width=2)
    for lat in (-40, 0, 40):
        _, py = _proj_1x(0, lat, mx, my, mw, mh)
        d.line([(mx * SCALE + 4, int(py * SCALE)), ((mx + mw) * SCALE - 4, int(py * SCALE))], fill=(204, 218, 232), width=2)

    for poly_pts in WORLD_POLYGONS:
        d.polygon(
            [(int(round(_proj_1x(lon, lat, mx, my, mw, mh)[0] * SCALE)), int(round(_proj_1x(lon, lat, mx, my, mw, mh)[1] * SCALE))) for lon, lat in poly_pts],
            fill=LAND,
            outline=LAND_EDGE,
        )

    coords = []
    for num, lon, lat, col in PINS:
        px, py = _proj_1x(lon, lat, mx, my, mw, mh)
        for pnum, ox, oy in coords:
            dist = math.hypot(px - ox, py - oy)
            assert dist >= 13.0, f"Pins {num} and {pnum} too close: {dist:.1f}px"
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
# Curated 35 Verified Wednesday 25 November 2026 Stories Across 7 Regions
# ---------------------------------------------------------------------------
KPIS = [
    ("1st", "foreign astronaut reaches China's Tiangong station", CRIMSON),
    ("-6.2%", "Kospi close on sell curb; SoftBank drops ~15%", CRIMSON),
    ("2", "tankers hit mines & burn in Hormuz, IRGC says", AMBER),
    ("47,000", "women killed by partner or kin (5/hr), UN says", NAVY),
    ("26", "miners trapped in flooded 100m West Java pit", TEAL),
    ("+36%", "Bangladesh garment wage lifted to Tk 17,500", EMERALD),
]

LEADS = [
    LeadArticle(
        1, "ASIA", "LIFTOFF", CRIMSON, "CONFIRMED", "JIUQUAN, CHINA · SPACE",
        "Shenzhou-24 flies Pakistan's 1st astronaut to Tiangong",
        "Long March-2F lifts off at 00:18 UTC carrying Tang Hongbo, Wu Yi and payload specialist Zeeshan Ali to dock.",
        "XINHUA · AA · REUTERS", art_shenzhou24,
    ),
    LeadArticle(
        2, "ASIA", "SELL-OFF", CRIMSON, "CONFIRMED", "SEOUL · TAIPEI · TOKYO",
        "Asia's chip stocks crash on AI doubts",
        "Kospi plunges 6.2% (sell curb), SK Hynix -11.1%, Samsung -9.9%, Taiex -4.8%, SoftBank -15%, Nikkei -2.8%.",
        "AL JAZEERA · AFP · REUTERS", art_chips_crash,
    ),
    LeadArticle(
        3, "ME", "WAR AT SEA", AMBER, "CLAIM", "STRAIT OF HORMUZ · GULF",
        "Two oil tankers hit mines and burn, Iran says",
        "IRGC Navy claims vessels took an 'unauthorised route' in Strait early Wednesday; no independent confirmation yet.",
        "IRIB · REUTERS · ARAB NEWS", art_hormuz_tankers,
    ),
]

CARDS = [
    CardArticle(4, "OCEANIA", "OFFICIAL", "CANBERRA, AUSTRALIA", "Australia & Solomons sign security treaty", "No foreign bases allowed; A$740m aid & easier visas. DFAT · ABC", art_solomons_pact),
    CardArticle(5, "GLOBAL", "OFFICIAL", "UNITED NATIONS", "UN: five women an hour killed by partner/kin", "47,000 in 2025; Africa 2.9/100k highest. UNODC · UN Women", art_unodc_femicide),
    CardArticle(6, "EUROPE", "OFFICIAL", "LONDON, UK", "UK energy bills to jump 26% on gas shock", "Ofgem cap set to rise £1,723 -> £2,166 (~20m homes). Ofgem · AFP", art_uk_energy),
    CardArticle(7, "ME", "OFFICIAL", "HODEIDAH · RAS TANURA", "Coalition bombs Hodeidah, downs 4 drones", "Strikes follow Tue Riyadh hit; Houthis warn Jeddah. Reuters · AJ", art_hodeidah_drones),
    CardArticle(8, "ASIA", "OFFICIAL", "BOGOR, INDONESIA", "26 trapped in flooded West Java gold pit", "Overflowing river swamped 100m illegal shaft. WashPost · FMT", art_west_java),
    CardArticle(9, "ASIA", "OFFICIAL", "DHAKA, BANGLADESH", "Garment workers win 36% minimum wage rise", "Floor raised from Tk 12,500 to Tk 17,500/mo. Prothom Alo · AFP", art_dhaka_wage),
    CardArticle(10, "EUROPE", "REPORTED", "SAMARA, RUSSIA", "Ukrainian drones hit two oil refineries", "Blazes at Syzran & Kuibyshev; Putin vows answer. Kyiv Ind. · F24", art_samara_refineries),
    CardArticle(11, "AFRICA", "OFFICIAL", "ITURI, DR CONGO", "WHO pulls teams out of Congo Ebola clinic", "Akwe clinic sheltered 3 days amid fighting; 5,775 dead. WHO · AJ", art_ebola_drc),
]

BRIEFS_COLS: list[list[tuple[int, str, str, str]]] = [
    [
        (12, "OCEANIA", "CANBERRA", "Oct CPI jumps to 4.9% 3-yr high, beating forecasts"),
        (13, "ASIA", "DOHA", "Sooryavanshi, 15, smashes fastest List A 204 off 53b"),
        (14, "OCEANIA", "CANBERRA", "Parliament apologises to LGBTQ military veterans"),
        (15, "OCEANIA", "HOBART", "Flinders Is. bushfire forces emergency boat rescues"),
        (16, "EUROPE", "LONDON", "Review finds Met Police still institutionally racist"),
        (17, "EUROPE", "LONDON", "Tube strike hits Circle & Piccadilly from 10:00 UTC"),
        (18, "EUROPE", "BRUSSELS", "EU hosts Balkans summit; weighs €210B Russia assets"),
        (19, "EUROPE", "DARMSTADT", "ESA Hera reveals first close-up images of Dimorphos"),
        (20, "EUROPE", "GENEVA", "FIDE World Chess: Gukesh & Sindarov draw Game 1"),
        (21, "ME", "GAZA CITY", "Israeli strikes kill at least 4 in Shati camp despite truce"),
        (22, "ME", "TEHRAN", "Iran warns winter gas rationing as cold wave hits"),
        (23, "ASIA", "SHANGHAI", "City officials pledge loyalty amid Chen Jining probe"),
    ],
    [
        (24, "ASIA", "SEOUL", "Births jump 12.2% YoY; deal averts subway strike"),
        (25, "ASIA", "TAIPEI", "BBC Verify traces China-linked deepfakes in Taiwan"),
        (26, "AFRICA", "KHARTOUM", "Sudan rejects Ethiopia peace talks offer amid clashes"),
        (27, "AFRICA", "GAUTENG", "Johannesburg sets Level-2 water curbs in grid crisis"),
        (28, "AMERICAS", "WASHINGTON", "USTR readies 16-nation Section 301 capacity tariffs"),
        (29, "AMERICAS", "WASHINGTON", "NATO chief Rutte holds Mar-a-Lago talks with Trump"),
        (30, "AMERICAS", "MIDDLETOWN", "US Army to detonate 5t degraded lead azide in Iowa"),
        (31, "AMERICAS", "CHICAGO", "81.5m Thanksgiving holiday travelers face storm delays"),
        (32, "AMERICAS", "BRASÍLIA", "Brazil permanently recalls ambassador to Argentina"),
        (33, "AMERICAS", "CARTAGENA", "Police storm supermarket to free Colombia hostages"),
        (34, "ASIA", "JAKARTA", "OECD chief Cormann meets Prabowo on accession"),
        (35, "GLOBAL", "MARKETS", "Gold slips ~$3,545 (-8% Nov) as dollar & Fed bets jump"),
    ],
]


def compute_region_counts() -> dict[str, int]:
    counts = {k: 0 for k, _l, _c in REGION_META}
    seen = []
    for l in LEADS:
        counts[l.region] += 1
        seen.append(l.num)
    for c in CARDS:
        counts[c.region] += 1
        seen.append(c.num)
    for col in BRIEFS_COLS:
        for n, reg, _city, _txt in col:
            counts[reg] += 1
            seen.append(n)
    assert seen == list(range(1, 36)), f"Story numbers mismatch: {seen}"
    assert sum(counts.values()) == 35
    return counts


def render() -> None:
    counts = compute_region_counts()
    hi = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), PAPER)
    dh = ImageDraw.Draw(hi)

    # Top Folio & Double Masthead Rules
    dh.rectangle([0, 0, WIDTH * SCALE, 20 * SCALE], fill=RULE_DARK)
    dh.line([14 * SCALE, 84 * SCALE, 1010 * SCALE, 84 * SCALE], fill=RULE_DARK, width=2)

    # Full-width Colored Region Proportion Bar (y: 86..101, x: 14..1010 = 996px)
    rx, rem_w = 14, 996
    bar_segs = []
    for idx, (rk, rlbl, rcol) in enumerate(REGION_META):
        cnt = counts[rk]
        sw = rem_w if idx == len(REGION_META) - 1 else round(996 * cnt / 35)
        bar_segs.append((f"{rlbl} {cnt}", rx, sw, rcol))
        dh.rectangle([rx * SCALE, 86 * SCALE, (rx + sw) * SCALE, 101 * SCALE], fill=rcol)
        rx += sw
        rem_w -= sw

    # UTC Chronological Ticker (y: 104..121)
    dh.rectangle([14 * SCALE, 104 * SCALE, 1010 * SCALE, 121 * SCALE], fill=PAPER_WARM)
    dh.rectangle([14 * SCALE, 104 * SCALE, 108 * SCALE, 121 * SCALE], fill=RULE_DARK)
    dh.line([14 * SCALE, 121 * SCALE, 1010 * SCALE, 121 * SCALE], fill=RULE_DARK, width=2)

    # 6 Hairline KPI Columns (y: 124..166)
    kpi_w = 166
    for i in range(1, 6):
        kx = (14 + i * kpi_w) * SCALE
        dh.line([kx, 128 * SCALE, kx, 162 * SCALE], fill=RULE_LIGHT, width=2)
    dh.line([14 * SCALE, 167 * SCALE, 1010 * SCALE, 167 * SCALE], fill=RULE_LIGHT, width=2)

    # 3 Full-Bleed Hero Art Panels (y: 171..271, h=100, lw=322, gap=15)
    lw, lgap = 322, 15
    for idx, lead in enumerate(LEADS):
        lx, ly = 14 + idx * (lw + lgap), 171
        art = lead.drawer(lw * SCALE, 100 * SCALE)
        hi.paste(art, (lx * SCALE, ly * SCALE))
        # Subtle clean tag rectangle below artwork
        tb_w = 62
        dh.rectangle([lx * SCALE, (ly + 104) * SCALE, (lx + tb_w) * SCALE, (ly + 117) * SCALE], fill=lead.tag_col)
        # Small corner badge top-left inside art
        dh.rounded_rectangle([(lx + 6) * SCALE, (ly + 6) * SCALE, (lx + 112) * SCALE, (ly + 20) * SCALE], radius=3, fill=(14, 18, 28))
        # Bottom-left circle number inside hero art
        dh.ellipse([(lx + 6) * SCALE, (ly + 76) * SCALE, (lx + 24) * SCALE, (ly + 94) * SCALE], fill=lead.tag_col, outline=(255, 255, 255), width=2)
    dh.line([14 * SCALE, 382 * SCALE, 1010 * SCALE, 382 * SCALE], fill=RULE_DARK, width=3)

    # 8 Full-Bleed Mid Cards (2 rows x 4 cols: y=406..676, cw=240, ch=132, vgap=8)
    cw, ch, cgap = 240, 132, 12
    for idx, card in enumerate(CARDS):
        col, row = idx % 4, idx // 4
        cx, cy = 14 + col * (cw + cgap), 406 + row * (ch + 8)
        art = card.drawer(cw * SCALE, 56 * SCALE)
        hi.paste(art, (cx * SCALE, cy * SCALE))
        # Bottom-left circle badge inside art (clean, unobtrusive)
        dh.ellipse([(cx + 5) * SCALE, (cy + 36) * SCALE, (cx + 21) * SCALE, (cy + 52) * SCALE], fill=REGION_COLORS[card.region], outline=(255, 255, 255), width=2)
        dh.line([cx * SCALE, (cy + ch) * SCALE, (cx + cw) * SCALE, (cy + ch) * SCALE], fill=RULE_LIGHT, width=2)
    dh.line([14 * SCALE, 682 * SCALE, 1010 * SCALE, 682 * SCALE], fill=RULE_DARK, width=3)

    # Bottom Atlas (x=14..316, y=704..892) + Legend
    mx, my, mw, mh = 14, 704, 302, 188
    draw_map_surface(hi, mx, my, mw, mh)

    # Date Check Strip (y: 938..982) + Footer Sources (y: 984..1024)
    dh.line([14 * SCALE, 936 * SCALE, 1010 * SCALE, 936 * SCALE], fill=RULE_DARK, width=2)
    dh.rectangle([14 * SCALE, 940 * SCALE, 1010 * SCALE, 982 * SCALE], fill=PAPER_WARM)
    dh.rectangle([14 * SCALE, 940 * SCALE, 18 * SCALE, 982 * SCALE], fill=CRIMSON)
    dh.rectangle([0, 1002 * SCALE, WIDTH * SCALE, HEIGHT * SCALE], fill=RULE_DARK)

    # Downsample 2x artwork cleanly
    img = hi.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    # 1x Sharp Typography Layer
    draw.text((14, 4), "THE WORLD IN ONE DAY", font=F_TOPBAR, fill=(255, 255, 255))
    top_r = "35 STORIES · ALL FROM WEDNESDAY 25 NOVEMBER 2026"
    draw.text((1010 - draw.textbbox((0, 0), top_r, font=F_TOPBAR)[2], 4), top_r, font=F_TOPBAR, fill=GOLD)

    mast = "Wednesday 25 November 2026"
    mb = draw.textbbox((0, 0), mast, font=F_MAST)
    assert mb[2] - mb[0] < 996
    draw.text(((WIDTH - (mb[2] - mb[0])) // 2, 16), mast, font=F_MAST, fill=INK)

    deck = "Pakistan's first astronaut reaches Tiangong  ·  Asia's chip stocks crash on AI doubts  ·  Tankers burn in Hormuz, Iran says"
    dkb = draw.textbbox((0, 0), deck, font=F_DECK)
    assert dkb[2] - dkb[0] <= 996
    draw.text(((WIDTH - (dkb[2] - dkb[0])) // 2, 70), deck, font=F_DECK, fill=SLATE)

    # Full-width Region Bar labels (fit guaranteed)
    for txt, sx, sw, _col in bar_segs:
        show = txt if draw.textbbox((0, 0), txt, font=F_REG_BAR)[2] <= sw - 6 else txt.replace("MIDDLE EAST", "M. EAST")
        tb = draw.textbbox((0, 0), show, font=F_REG_BAR)
        assert tb[2] - tb[0] <= sw - 4, f"Region overflow {show}: {tb[2]-tb[0]} > {sw}"
        draw.text((sx + (sw - (tb[2] - tb[0])) // 2, 88), show, font=F_REG_BAR, fill=(255, 255, 255))

    # UTC Timeline labels
    draw.text((20, 107), "THE DAY IN UTC", font=F_UTC_LBL, fill=GOLD)
    utc_slots = [
        ("00:18", "Shenzhou-24 liftoff"),
        ("00:30", "Aus CPI hits 4.9%"),
        ("03:56", "Crew docks Tiangong"),
        ("05:30", "Taiex closes -4.8%"),
        ("06:30", "Kospi -6.2% curb"),
        ("10:00", "Tube strike starts"),
    ]
    ux = 114
    uw = (1006 - 114) // len(utc_slots)
    for ts, ds in utc_slots:
        draw.text((ux, 107), ts, font=F_UTC_LBL, fill=CRIMSON)
        tw = draw.textbbox((0, 0), ts, font=F_UTC_LBL)[2]
        draw.text((ux + tw + 4, 107), ds, font=F_UTC_TXT, fill=INK)
        ux += uw

    # 6 KPI Stats
    for i, (knum, ktxt, kcol) in enumerate(KPIS):
        kx = 20 + i * kpi_w
        draw.text((kx, 126), knum, font=F_KPI_NUM, fill=kcol)
        draw_text_lines(draw, kx, 147, ktxt, F_KPI_TXT, SLATE, kpi_w - 14, 10, 2)

    # 3 Hero Artwork Inner Data Overlays + Headlines
    for idx, lead in enumerate(LEADS):
        lx, ly = 14 + idx * (lw + lgap), 171
        # Top-left scene pill
        pill_txt = ["00:18 UTC · TIANGONG", "ASIA CLOSE · WED 25", "STRAIT OF HORMUZ"][idx]
        draw.text((lx + 10, ly + 7), pill_txt, font=F_ART_LBL, fill=(255, 255, 255))
        # Circle number
        nb = draw.textbbox((0, 0), str(lead.num), font=F_PIN)
        draw.text((lx + 15 - (nb[2] - nb[0]) // 2, ly + 79), str(lead.num), font=F_PIN, fill=(255, 255, 255))

        if idx == 1:
            # Embedded Financial Times market plunge scorecard inside Hero #2
            tx0 = lx + lw - 108
            rows_mkt = [
                ("KOSPI", "-6.2%"), ("TAIEX", "-4.8%"), ("NIKKEI", "-2.8%"),
                ("HYNIX", "-11.1%"), ("SAMSUNG", "-9.9%"), ("SOFTBANK", "-15%"),
            ]
            for r_i, (sym, chg) in enumerate(rows_mkt):
                ry = ly + 11 + r_i * 13
                draw.text((tx0, ry), sym, font=F_ART_LBL, fill=(203, 213, 225))
                cb = draw.textbbox((0, 0), chg, font=F_ART_LBL)
                draw.text((lx + lw - 10 - (cb[2] - cb[0]), ry), chg, font=F_ART_LBL, fill=(248, 113, 113))
        elif idx == 2:
            draw.text((lx + 158, ly + 10), "IRAN", font=F_ART_LBL, fill=INK)
            draw.text((lx + 244, ly + 86), "OMAN", font=F_ART_LBL, fill=INK)
            draw.text((lx + 96, ly + 86), "NAVAL MINE CLAIM", font=F_ART_LBL, fill=(255, 255, 255))

        # Status badge + tag below art
        tb_b = draw.textbbox((0, 0), lead.tag_lbl, font=F_LEAD_TAG)
        draw.text((lx + (62 - (tb_b[2] - tb_b[0])) // 2, ly + 105), lead.tag_lbl, font=F_LEAD_TAG, fill=(255, 255, 255))
        draw.text((lx + 68, ly + 105), lead.place_line, font=F_LEAD_TAG, fill=MUTED)
        draw_status_box(draw, lx + lw, ly + 104, lead.status)

        ny = draw_text_lines(draw, lx, ly + 121, lead.headline, F_LEAD_TITLE, INK, lw, 19, 2)
        draw_text_lines(draw, lx, ny + 3, lead.summary, F_LEAD_BODY, SLATE, lw, 12, 3)
        draw.text((lx, ly + 198), lead.sources, font=F_LEAD_SRC, fill=MUTED)

    # Section strip 2 + Inline HOW SURE Legend
    draw.text((14, 387), "ALSO ON WEDNESDAY 25 NOVEMBER", font=F_SEC_HDR, fill=INK)
    hx = 356
    draw.text((hx, 388), "HOW SURE:", font=F_CARD_TAG, fill=MUTED)
    hx += 52
    for st_lbl, st_desc in [
        ("OFFICIAL", "gov / agency statement"),
        ("CONFIRMED", "2+ major outlets"),
        ("REPORTED", "single wire / outlet"),
        ("CLAIM", "one side, unverified"),
    ]:
        bg, fg = STATUS_COLORS[st_lbl]
        bw = draw.textbbox((0, 0), st_lbl, font=F_STATUS)[2] + 6
        draw.rectangle([hx, 387, hx + bw, 399], fill=bg, outline=fg, width=1)
        draw.text((hx + 3, 388), st_lbl, font=F_STATUS, fill=fg)
        hx += bw + 4
        dw = draw.textbbox((0, 0), st_desc, font=F_CARD_TAG)[2]
        draw.text((hx, 388), st_desc, font=F_CARD_TAG, fill=SLATE)
        hx += dw + 10

    # 8 Mid Cards Artwork Micro-Charts & Typography
    for idx, card in enumerate(CARDS):
        col, row = idx % 4, idx // 4
        cx, cy = 14 + col * (cw + cgap), 406 + row * (ch + 8)
        nt = str(card.num)
        nb = draw.textbbox((0, 0), nt, font=F_PIN)
        draw.text((cx + 13 - (nb[2] - nb[0]) // 2, cy + 38), nt, font=F_PIN, fill=(255, 255, 255))

        if card.num == 4:
            draw.text((cx + 100, cy + 39), "NO BASES", font=F_ART_LBL, fill=NAVY)
        elif card.num == 5:
            draw.text((cx + 12, cy + 8), "47,000", font=F_ART_BIG, fill=(248, 113, 113))
            draw.text((cx + 12, cy + 28), "5 KILLED / HR", font=F_ART_LBL, fill=GOLD)
            for ri, rname in enumerate(["AF 2.9", "AM 1.4", "OC 1.1", "AS 0.6", "EU 0.5"]):
                draw.text((cx + 102, cy + 16 + ri * 7), rname, font=ft("sans_bold", 6), fill=(226, 232, 240))
        elif card.num == 6:
            draw.text((cx + 122, cy + 10), "+26%", font=F_ART_BIG, fill=CRIMSON)
            draw.text((cx + 122, cy + 30), "£1,723 -> £2,166", font=F_ART_LBL, fill=NAVY)
        elif card.num == 7:
            draw.text((cx + 10, cy + 6), "4 DRONES DOWNED", font=F_ART_LBL, fill=GOLD)
        elif card.num == 8:
            draw.text((cx + 104, cy + 40), "100m PIT · 26 TRAPPED", font=F_ART_LBL, fill=(255, 255, 255))
        elif card.num == 9:
            draw.text((cx + 12, cy + 8), "+36%", font=F_ART_BIG, fill=EMERALD)
            draw.text((cx + 114, cy + 6), "Tk 17,500", font=F_ART_LBL, fill=EMERALD)
        elif card.num == 10:
            draw.text((cx + 10, cy + 6), "SYZRAN & KUIBYSHEV", font=F_ART_LBL, fill=GOLD)
        elif card.num == 11:
            draw.text((cx + 10, cy + 6), "AKWE CLINIC · 5,775 DEAD", font=F_ART_LBL, fill=CRIMSON)

        draw.text((cx, cy + 59), card.place_line, font=F_CARD_TAG, fill=REGION_COLORS[card.region])
        draw_status_box(draw, cx + cw, cy + 58, card.status)
        ny = draw_text_lines(draw, cx, cy + 72, card.headline, F_CARD_TITLE, INK, cw, 14, 2)
        draw_text_lines(draw, cx, ny + 2, card.summary, F_CARD_BODY, SLATE, cw, 10, 2)

    # Bottom Atlas & 24 Crisp Briefs Section
    draw.text((14, 687), "WHERE IT HAPPENED · PINS = STORIES 1–11", font=F_SEC_HDR, fill=INK)
    draw.text((334, 687), "IN BRIEF · 24 MORE VERIFIED WEDNESDAY 25 NOV STORIES", font=F_SEC_HDR, fill=INK)
    draw_map_pin_nums(draw, mx, my, mw, mh)

    # Region legend below map (2 clean rows across x=14..316)
    rx0, ry0 = mx, 898
    for idx, (rk, rlbl, rcol) in enumerate(REGION_META):
        col_i = idx % 4
        row_i = idx // 4
        lx = rx0 + col_i * 76
        ly = ry0 + row_i * 15
        draw.rectangle([lx, ly + 2, lx + 8, ly + 10], fill=rcol)
        short_lbl = rlbl.replace("MIDDLE EAST", "M. East").title() if rlbl != "OCEANIA" else "Oceania"
        draw.text((lx + 11, ly), short_lbl, font=F_CARD_BODY, fill=INK)

    # 2 Wide Brief Columns (#12-#23 and #24-#35, x=334..1010, cw=332, gap=12, 12 rows x 19px = 228px)
    br_w = 332
    for cidx, items in enumerate(BRIEFS_COLS):
        bx = 334 + cidx * (br_w + 12)
        for ridx, (num, reg, city, txt) in enumerate(items):
            by = 706 + ridx * 19
            draw.text((bx, by), str(num), font=F_BRIEF_NUM, fill=REGION_COLORS[reg])
            cs = f"{city} "
            draw.text((bx + 18, by), cs, font=F_BRIEF_CITY, fill=INK)
            cw_px = draw.textbbox((0, 0), cs, font=F_BRIEF_CITY)[2]
            tx = bx + 18 + cw_px
            tw = draw.textbbox((0, 0), txt, font=F_BRIEF_TXT)[2]
            assert tx + tw <= bx + br_w, f"Brief #{num} overflow: {tx + tw} > {bx + br_w} | {txt}"
            draw.text((tx, by), txt, font=F_BRIEF_TXT, fill=SLATE)

    # Date Check Strip
    draw.text((24, 944), "DATE CHECK:", font=F_DATE_BOLD, fill=CRIMSON)
    dc_txt = (
        "Every story here broke or developed Wed 25 Nov 2026 (UTC). Left out as prior days: Huang's Nvidia comeback, leaked Russia war dead & Anmer Hall break-in (Mon 23 Nov); "
        "initial Riyadh PIF Tower strike, Brooklyn Huawei verdict & CAS Senegal ruling (Tue 24 Nov); COP31 collapse & 186-drone Kyiv strike (Sun 22 Nov)."
    )
    draw_text_lines(draw, 94, 943, dc_txt, F_DATE_TXT, INK, 908, 12, 3)

    # Sources & Bottom Bar
    draw.text(
        (14, 987),
        "SOURCES: REUTERS · AP · AL JAZEERA · AFP · BBC · XINHUA · WHO · UNODC · DFAT · OFGEM · ABS · ESA · FIDE · US ARMY · PROTHOM ALO",
        font=F_CARD_TAG,
        fill=SLATE,
    )
    art_note = "Original code art · no photos"
    draw.text((1010 - draw.textbbox((0, 0), art_note, font=F_CARD_TAG)[2], 987), art_note, font=F_CARD_TAG, fill=MUTED)
    draw.text((14, 1006), "THE WORLD IN ONE DAY · BUILT FOR MAKE.FUN", font=F_TOPBAR, fill=(226, 232, 240))
    bot_r = "WEDNESDAY 25 NOVEMBER 2026 · ONE DAY, ONE PAGE"
    draw.text((1010 - draw.textbbox((0, 0), bot_r, font=F_TOPBAR)[2], 1006), bot_r, font=F_TOPBAR, fill=GOLD)

    img.save(OUT_PATH, format="PNG", optimize=True)
    print(f"Generated v5 {OUT_PATH}: {os.path.getsize(OUT_PATH)} bytes")


if __name__ == "__main__":
    render()
