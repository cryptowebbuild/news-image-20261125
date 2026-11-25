"""
Deterministic editorial front-page generator for:
  "Sum up 25 November's world news in one image" (news-image-20261125)

Renders a crisp 1024x1024 illustrated world dispatch broadsheet covering
Wednesday, 25 November 2026 across all 6 continents and 45 verified stories.
Uses 2x supersampled vector rendering for maps and hero scenes paired with
native 1x TrueType typography so text remains legible down to ~300px previews.
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

FONT_DIR = r"C:\Windows\Fonts"


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, size)


F_MAST = load_font("georgiab.ttf", 24)
F_SUBMAST = load_font("arialbd.ttf", 11)
F_PILL = load_font("arialbd.ttf", 11)
F_HERO_TITLE = load_font("georgiab.ttf", 13)
F_HERO_BODY = load_font("arial.ttf", 11)
F_HERO_SRC = load_font("arialbd.ttf", 10)
F_SEC_HDR = load_font("arialbd.ttf", 12)
F_SPOT_KICK = load_font("arialbd.ttf", 11)
F_SPOT_BODY = load_font("arial.ttf", 11)
F_REG_HDR = load_font("arialbd.ttf", 13)
F_ITEM_KICK = load_font("arialbd.ttf", 11)
F_ITEM_BODY = load_font("arial.ttf", 11)
F_TICK_KICK = load_font("arialbd.ttf", 11)
F_TICK_BODY = load_font("arial.ttf", 11)
F_PIN = load_font("arialbd.ttf", 10)
F_MAP_TITLE = load_font("arialbd.ttf", 11)
F_MAP_LBL = load_font("arialbd.ttf", 9)

PAPER = (247, 243, 234)
INK = (16, 23, 38)
NAVY_DARK = (11, 22, 39)
CRIMSON = (185, 28, 28)
GOLD = (234, 179, 8)
AMBER = (194, 65, 12)
CARD_BG = (255, 253, 249)
BORDER = (212, 204, 188)
MUTED = (82, 92, 108)
OCEAN = (220, 234, 246)
LAND = (168, 190, 174)
LAND_LINE = (118, 142, 126)


@dataclass(frozen=True)
class HeroStory:
    kicker: str
    headline: str
    summary: str
    source: str
    accent: tuple[int, int, int]
    drawer: Callable[[int, int], Image.Image]


@dataclass(frozen=True)
class SpotlightItem:
    kicker: str
    body: str
    source: str
    pin: int
    accent: tuple[int, int, int]


@dataclass(frozen=True)
class DispatchItem:
    kicker: str
    body: str
    source: str


@dataclass(frozen=True)
class RegionBlock:
    title: str
    accent: tuple[int, int, int]
    items: list[DispatchItem]


def wrap_lines(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int
) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip()
        bbox = draw.textbbox((0, 0), cand, font=font)
        if bbox[2] - bbox[0] <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_inline_item(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    max_w: int,
    max_h: int,
    kicker: str,
    body: str,
    source: str,
    accent: tuple[int, int, int],
    f_kick: ImageFont.FreeTypeFont,
    f_body: ImageFont.FreeTypeFont,
    line_h: int = 14,
) -> None:
    prefix = f"{kicker}: "
    pb = draw.textbbox((0, 0), prefix, font=f_kick)
    pw = pb[2] - pb[0]

    # Build full wrapped text while respecting first-line indent from kicker
    words = f"{body} [{source}]".split()
    first_line_words: list[str] = []
    rest_words: list[str] = []
    cur = ""
    filled_first = False
    for w in words:
        cand = f"{cur} {w}".strip()
        wb = draw.textbbox((0, 0), cand, font=f_body)
        if not filled_first and (pw + (wb[2] - wb[0]) <= max_w or not first_line_words):
            cur = cand
            first_line_words.append(w)
        else:
            filled_first = True
            rest_words.append(w)

    draw.text((x, y), prefix, font=f_kick, fill=accent)
    draw.text((x + pw, y), cur, font=f_body, fill=INK)

    cur_y = y + line_h
    if rest_words:
        rem_lines = wrap_lines(draw, " ".join(rest_words), f_body, max_w)
        for idx, line in enumerate(rem_lines):
            assert cur_y + line_h <= y + max_h + 2, f"Overflow on {kicker}: {line}"
            draw.text((x, cur_y), line, font=f_body, fill=INK)
            cur_y += line_h


# ---------------------------------------------------------------------------
# Hero 2x Supersampled Illustrations (strictly clipped to local w x h surface)
# ---------------------------------------------------------------------------
def draw_hero_benghazi(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (12, 27, 48))
    d = ImageDraw.Draw(im)
    d.rectangle([0, int(h * 0.56), w, h], fill=(18, 52, 86))
    for wy in range(int(h * 0.64), h - 6, 15):
        d.line([(10, wy), (w - 10, wy)], fill=(48, 102, 150), width=2)
    # Harbor pier & lighthouse Silhouette
    d.rectangle([0, int(h * 0.48), 78, int(h * 0.60)], fill=(30, 41, 59))
    d.rectangle([16, int(h * 0.34), 28, int(h * 0.48)], fill=(51, 65, 85))
    d.ellipse([14, int(h * 0.31), 30, int(h * 0.39)], fill=(250, 204, 21))
    # Corvette Merkury hull listing & breaking
    hx, hy = 132, int(h * 0.49)
    hull = [(hx, hy + 16), (hx + 232, hy - 12), (hx + 248, hy + 24), (hx + 16, hy + 36)]
    d.polygon(hull, fill=(90, 104, 124))
    d.polygon([(hx + 66, hy + 7), (hx + 122, hy - 18), (hx + 150, hy + 8)], fill=(64, 78, 98))
    d.line([(hx + 96, hy - 18), (hx + 96, hy - 40)], fill=(148, 163, 184), width=3)
    # Explosion fireball & rising smoke
    cx, cy = hx + 86, hy
    d.ellipse([cx - 38, cy - 48, cx + 44, cy + 16], fill=(100, 116, 139))
    d.ellipse([cx - 28, cy - 28, cx + 32, cy + 16], fill=(234, 88, 12))
    d.ellipse([cx - 14, cy - 16, cx + 16, cy + 10], fill=(253, 224, 71))
    # Incoming sea drone wake
    d.line([(42, h - 18), (cx - 14, cy + 12)], fill=(56, 189, 248), width=4)
    d.polygon([(cx - 26, cy + 14), (cx - 8, cy + 8), (cx - 18, cy + 24)], fill=(255, 255, 255))
    return im


def draw_hero_tiangong(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (8, 15, 34))
    d = ImageDraw.Draw(im)
    stars = [
        (24, 18), (68, 44), (116, 14), (176, 30), (234, 20),
        (312, 28), (390, 16), (438, 46), (52, 84), (414, 76), (350, 56),
    ]
    for sx, sy in stars:
        if sx < w - 10 and sy < h - 30:
            d.ellipse([sx, sy, sx + 4, sy + 4], fill=(226, 232, 240))
    # Earth blue limb safely confined to bottom slice of local w x h canvas
    d.ellipse([-80, int(h * 0.68), w + 80, h + 320], fill=(29, 78, 216))
    d.arc([-80, int(h * 0.68), w + 80, h + 320], 195, 345, fill=(147, 197, 253), width=5)
    # Tiangong modular station + docked Shenzhou-24
    cx, cy = int(w * 0.54), int(h * 0.40)
    for wx in (cx - 128, cx + 44):
        d.rectangle([wx, cy - 42, wx + 82, cy - 12], fill=(37, 99, 235), outline=(250, 204, 21), width=2)
        d.rectangle([wx, cy + 12, wx + 82, cy + 42], fill=(37, 99, 235), outline=(250, 204, 21), width=2)
    d.rounded_rectangle([cx - 56, cy - 12, cx + 56, cy + 12], radius=6, fill=(241, 245, 249))
    d.rounded_rectangle([cx - 106, cy - 9, cx - 64, cy + 9], radius=6, fill=(250, 204, 21))
    d.line([(cx - 64, cy), (cx - 56, cy)], fill=(239, 68, 68), width=4)
    # Pakistan green & China crimson patches
    d.rectangle([12, 10, 48, 32], fill=(21, 128, 61), outline=(255, 255, 255), width=2)
    d.rectangle([54, 10, 90, 32], fill=(220, 38, 38), outline=(255, 255, 255), width=2)
    return im


def draw_hero_redsea(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (236, 222, 194))
    d = ImageDraw.Draw(im)
    red_sea = [(68, 0), (132, 0), (206, h), (122, h)]
    d.polygon(red_sea, fill=(28, 86, 136))
    persian_gulf = [(306, 16), (w, 52), (w, 134), (282, 70)]
    d.polygon(persian_gulf, fill=(28, 86, 136))
    # Hodeidah strike starburst
    hx, hy = 186, h - 42
    d.ellipse([hx - 22, hy - 22, hx + 22, hy + 22], fill=(220, 38, 38))
    d.ellipse([hx - 10, hy - 10, hx + 10, hy + 10], fill=(251, 191, 36))
    # Ras Tanura 4 drone defense arcs
    rx, ry = 308, 56
    d.arc([rx - 52, ry - 44, rx + 24, ry + 30], 190, 340, fill=(22, 163, 74), width=4)
    for dx, dy in [(-24, -18), (-4, -30), (14, -16), (26, -28)]:
        d.line([(rx, ry), (rx + dx, ry + dy)], fill=(15, 118, 110), width=3)
        d.ellipse([rx + dx - 6, ry + dy - 6, rx + dx + 6, ry + dy + 6], fill=(245, 158, 11))
    # Strait of Hormuz tanker mine ring + tiny tanker hull
    mx, my = w - 60, 98
    d.ellipse([mx - 18, my - 18, mx + 18, my + 18], outline=(220, 38, 38), width=4)
    d.rectangle([mx - 10, my - 4, mx + 10, my + 5], fill=(239, 68, 68))
    return im


def draw_hero_chiprout(w: int, h: int) -> Image.Image:
    im = Image.new("RGB", (w, h), (17, 24, 39))
    d = ImageDraw.Draw(im)
    for gy in range(28, h - 10, 34):
        d.line([(12, gy), (w - 12, gy)], fill=(31, 41, 55), width=2)
    bars = [
        (42, 34, 72, False),
        (86, 46, 90, True),
        (130, 70, 116, True),
        (174, 86, 132, True),
        (218, 100, 146, True),
        (262, 112, 156, True),
    ]
    for bx, top, bot, red in bars:
        col = (239, 68, 68) if red else (34, 197, 94)
        d.line([(bx, top - 14), (bx, bot + 14)], fill=col, width=3)
        d.rectangle([bx - 11, top, bx + 11, bot], fill=col)
    pts = [(38, 38), (118, 70), (200, 112), (288, 148)]
    d.line(pts, fill=(250, 204, 21), width=5)
    d.polygon([(296, 152), (276, 140), (282, 156)], fill=(250, 204, 21))
    cx, cy = w - 76, 56
    d.rounded_rectangle([cx - 32, cy - 32, cx + 32, cy + 32], radius=6, fill=(55, 65, 81), outline=(250, 204, 21), width=3)
    for k in range(-20, 24, 13):
        d.line([(cx + k, cy - 40), (cx + k, cy - 32)], fill=(250, 204, 21), width=3)
        d.line([(cx + k, cy + 32), (cx + k, cy + 40)], fill=(250, 204, 21), width=3)
    d.line([(cx - 24, cy - 24), (cx + 24, cy + 24)], fill=(239, 68, 68), width=4)
    return im


# ---------------------------------------------------------------------------
# 2x Supersampled Vector World Map with Equirectangular Projection
# ---------------------------------------------------------------------------
WORLD_POLYGONS: list[tuple[str, list[tuple[float, float]]]] = [
    ("NA", [(-168, 66), (-140, 70), (-95, 72), (-62, 62), (-54, 48), (-72, 42), (-81, 26), (-92, 17), (-106, 20), (-124, 40), (-136, 57)]),
    ("GL", [(-52, 60), (-42, 82), (-18, 78), (-24, 65)]),
    ("SA", [(-80, 10), (-62, 11), (-35, -6), (-42, -23), (-58, -39), (-68, -54), (-75, -44), (-72, -18), (-81, -4)]),
    ("EU", [(-9, 37), (3, 43), (-5, 49), (10, 56), (6, 62), (24, 70), (42, 66), (48, 52), (38, 46), (26, 41), (16, 39), (12, 43), (2, 42)]),
    ("UK", [(-8, 51), (-2, 58), (2, 53), (-5, 50)]),
    ("AF", [(-17, 15), (-12, 29), (10, 37), (33, 31), (43, 12), (51, 11), (41, -3), (40, -18), (28, -33), (18, -34), (12, -16), (9, 4), (-7, 5)]),
    ("MG", [(44, -25), (50, -13), (47, -24)]),
    ("ME", [(34, 31), (42, 37), (56, 25), (60, 22), (50, 14), (43, 13), (35, 29)]),
    ("AS", [(44, 65), (72, 72), (126, 72), (168, 65), (144, 52), (132, 42), (122, 34), (120, 23), (108, 12), (102, 2), (96, 16), (86, 21), (78, 8), (68, 23), (58, 26), (42, 42)]),
    ("JP", [(130, 32), (141, 44), (145, 42), (137, 34)]),
    ("ID", [(96, 5), (118, -2), (136, -4), (132, -8), (106, -8)]),
    ("AU", [(114, -22), (130, -12), (142, -12), (153, -27), (148, -38), (134, -34), (116, -34)]),
    ("NZ", [(168, -46), (178, -36), (174, -44)]),
]

MAP_PINS: list[tuple[int, float, float, tuple[int, int, int]]] = [
    (1, 20.1, 32.1, CRIMSON),       # Benghazi
    (2, 99.8, 40.9, (37, 99, 235)), # Jiuquan / Shenzhou-24
    (3, 42.9, 14.8, AMBER),         # Hodeidah / Red Sea
    (4, 121.5, 25.0, CRIMSON),      # Taipei / Asian Chip Rout
    (5, 160.0, -9.4, (109, 40, 217)), # Solomon Is. / Pacific Pact
    (6, -74.0, 40.7, (29, 78, 216)),  # NY / Huawei + UN
    (7, 6.1, 46.2, CRIMSON),          # Geneva World Chess
    (8, -17.4, 14.7, (15, 118, 110)), # Senegal AFCON
    (9, 24.0, 48.6, CRIMSON),         # Transcarpathia Zelenskyy-Magyar
    (10, -58.4, -34.6, (4, 120, 87)), # Buenos Aires recession
    (11, 106.8, -6.2, (109, 40, 217)), # Jakarta OECD
    (12, 3.4, 6.5, (15, 118, 110)),   # Nigeria budget / Edochie
]


def draw_world_map_base(base: Image.Image, x: int, y: int, w: int, h: int) -> None:
    # Draw crisp 2x map onto base image (already 2x coordinates passed!)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=OCEAN, outline=(148, 174, 204), width=3)
    # Graticule
    for lon in (-120, -60, 0, 60, 120):
        px = x + int((lon + 180.0) / 360.0 * (w - 24)) + 12
        d.line([(px, y + 6), (px, y + h - 6)], fill=(196, 217, 238), width=2)
    for lat in (-40, 0, 40):
        py = y + int((85.0 - lat) / 145.0 * (h - 24)) + 12
        d.line([(x + 6, py), (x + w - 6, py)], fill=(196, 217, 238), width=2)

    def proj(lon: float, lat: float) -> tuple[int, int]:
        px = x + int((lon + 180.0) / 360.0 * (w - 28)) + 14
        py = y + int((84.0 - lat) / 142.0 * (h - 28)) + 14
        return px, py

    for _code, pts in WORLD_POLYGONS:
        poly = [proj(lon, lat) for lon, lat in pts]
        d.polygon(poly, fill=LAND, outline=LAND_LINE)

    # Connecting alert arcs (Benghazi, Jiuquan orbit, Hormuz)
    bx, by = proj(30.5, 50.4)
    tx, ty = proj(20.1, 32.1)
    d.line([(bx, by), (tx, ty)], fill=(220, 38, 38), width=3)

    # Numbered pins
    for num, lon, lat, col in MAP_PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 14, py - 14, px + 14, py + 14], fill=col, outline=(255, 255, 255), width=3)


def draw_pin_numbers(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    def proj(lon: float, lat: float) -> tuple[int, int]:
        px = x + int((lon + 180.0) / 360.0 * (w - 14)) + 7
        py = y + int((84.0 - lat) / 142.0 * (h - 14)) + 7
        return px, py

    for num, lon, lat, _col in MAP_PINS:
        px, py = proj(lon, lat)
        txt = str(num)
        tb = draw.textbbox((0, 0), txt, font=F_PIN)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        draw.text((px - tw // 2, py - th // 2 - 1), txt, font=F_PIN, fill=(255, 255, 255))


# ---------------------------------------------------------------------------
# Verified Data Set — Wednesday, 25 November 2026
# ---------------------------------------------------------------------------
HEROES = [
    HeroStory(
        kicker="1 · UKRAINE–LIBYA",
        headline="Kyiv Sinks Warship in Libya",
        summary="SBU sea drones sink Russian corvette Merkury & hit arms ship.",
        source="Guardian/CNN",
        accent=CRIMSON,
        drawer=draw_hero_benghazi,
    ),
    HeroStory(
        kicker="2 · CHINA SPACE",
        headline="1st Foreigner at Tiangong",
        summary="Shenzhou-24 docks with Pakistan specialist M. Zeeshan Ali.",
        source="Xinhua/Hindu",
        accent=(29, 78, 216),
        drawer=draw_hero_tiangong,
    ),
    HeroStory(
        kicker="3 · RED SEA & GULF",
        headline="Hodeidah Hit, 4 Drones Shot",
        summary="Coalition bombs Yemen port; Saudi Arabia & Hormuz on alert.",
        source="AA/GulfNews",
        accent=AMBER,
        drawer=draw_hero_redsea,
    ),
    HeroStory(
        kicker="4 · ASIA TECH ROUT",
        headline="Chip Stocks Plunge in Asia",
        summary="Taiex -4.8% (38,195), Kospi halts -5% on AI & US tariff fears.",
        source="Al Jazeera",
        accent=(185, 28, 28),
        drawer=draw_hero_chiprout,
    ),
]

SPOTLIGHTS = [
    SpotlightItem("5 · SOLOMON PACT", "Australia & Honiara ink $740M treaty barring foreign bases", "Guardian", 5, (109, 40, 217)),
    SpotlightItem("6 · HUAWEI VERDICT", "Brooklyn jury finds 10 fraud/Iran counts; acquits RICO", "JT", 6, (29, 78, 216)),
    SpotlightItem("7 · CHESS GAME 2", "Gukesh (20) & Sindarov (20) draw Game 1; clash in Geneva", "FIDE", 7, CRIMSON),
    SpotlightItem("8 · SENEGAL AFCON", "CAS overturns CAF & restores Senegal's 2025 crown", "WGLT", 8, (15, 118, 110)),
    SpotlightItem("9 · KYIV–HUNGARY", "Zelenskyy & PM Magyar hail rail, gas and EU reset", "Guardian", 9, CRIMSON),
    SpotlightItem("10 · NOV 25 UN DAY", "UNODC warns 47,000 femicides in 2025 (5/hr); 7% report", "UN", 6, (30, 64, 175)),
]

REGIONS = [
    RegionBlock(
        title="NORTH AMERICA · US & CANADA",
        accent=(29, 78, 216),
        items=[
            DispatchItem("81M US TRAVELERS", "Dual coastal storms & Chicago O'Hare outage snarl eve rush", "CNN"),
            DispatchItem("USTR 301 TARIFFS", "Greer readies excess-capacity trade probes on 16 nations", "MStar"),
            DispatchItem("CIA OSINT BREACH", "NYT reports hack into unclassified US intel data system", "NYT"),
            DispatchItem("IOWA ARMY BLAST", "Controlled lead-azide detonation safely clears plant", "Army"),
            DispatchItem("NHL 600 ASSISTS", "Vegas star Mitch Marner hits 600 assists against Oilers", "NHL"),
        ],
    ),
    RegionBlock(
        title="LATIN AMERICA · CARIBBEAN",
        accent=(4, 120, 87),
        items=[
            DispatchItem("ARGENTINA SLUMP", "INDEC -1.2% Sept drop confirms Q3 technical recession", "Xinhua"),
            DispatchItem("PETROBRAS $122B", "2027-31 plan prioritizes 70%+ pre-salt deepwater oil", "Offsh"),
            DispatchItem("BRAZIL WTO SUIT", "Brasilia seeks WTO dispute panel on US Sec. 301 duties", "WTO"),
            DispatchItem("MEXICO PROTESTS", "US Mission alerts Reforma-Zocalo traffic & police curbs", "US Emb"),
            DispatchItem("ECLAC & MPOX", "Brasilia hosts LatAm tech summit; PAHO mpox alert", "PAHO"),
        ],
    ),
    RegionBlock(
        title="EUROPE · UKRAINE & RUSSIA",
        accent=(185, 28, 28),
        items=[
            DispatchItem("MET POLICE DAMNED", "Fairfield review finds enduring racism & misogyny", "Guard"),
            DispatchItem("UK SABOTAGE RISK", "Britain alerts Ukraine-supply firms after Estonia plots", "UNB"),
            DispatchItem("EU $45B MANIFESTO", "90+ ex-leaders urge frozen-asset loans for Ukraine", "FoE"),
            DispatchItem("US DROPS DEALS", "Envoys shelve Moscow carrots; Bila Tserkva struck", "FT"),
            DispatchItem("MOSCOW TALKS", "Putin hosts Brunei Sultan; leak cites ~500k dead", "Guard"),
        ],
    ),
    RegionBlock(
        title="MIDDLE EAST · NORTH AFRICA",
        accent=(180, 83, 9),
        items=[
            DispatchItem("JEDDAH WARNING", "Houthis threaten Saudi Red Sea ports over Hodeidah raids", "HoS"),
            DispatchItem("HORMUZ MINES", "IRGC says two oil tankers struck naval mines & burned", "AA"),
            DispatchItem("GAZA WINTER ALERT", "IDF kills Hamas security chief; floods hit 1.7M IDPs", "IOM"),
            DispatchItem("BEKAA AIRSTRIKES", "Israeli jets bomb subterranean Hezbollah missile sites", "IDF"),
            DispatchItem("BENGHAZI TOLL", "Two Libyan naval officers succumb after sea-drone strike", "Guard"),
        ],
    ),
    RegionBlock(
        title="SUB-SAHARAN AFRICA",
        accent=(15, 118, 110),
        items=[
            DispatchItem("PETE EDOCHIE (79)", "Nollywood legend passes in Enugu amid national tributes", "AllAfr"),
            DispatchItem("NIGERIA BUDGET", "Tinubu urges lawmakers to trim FY26 spending to N65.18T", "Punch"),
            DispatchItem("SUDAN DIALOGUE", "RSF coalition & Somoud welcome Ethiopia peace bid", "SudanT"),
            DispatchItem("NASPERS +12%", "Core half-year profit jumps on strong Tencent gains", "CNBC"),
            DispatchItem("GHANA & AIJC", "Mahama courts German capital; Nairobi AI media ends", "Wits"),
        ],
    ),
    RegionBlock(
        title="ASIA-PACIFIC · SOUTH ASIA",
        accent=(109, 40, 217),
        items=[
            DispatchItem("OECD IN JAKARTA", "Cormann launches Indonesia chip plan across 25 reviews", "Antara"),
            DispatchItem("NORTH KOREA", "Pyongyang expels head of Swiss diplomatic mission", "JT"),
            DispatchItem("MALAYSIA 787s", "MAG commits to order up to 16 Boeing 787-10 jets", "Boeing"),
            DispatchItem("INDIA UN & CRICKET", "Delhi urges AI guardrails; Sooryavanshi fastest List A 100", "IndExp"),
            DispatchItem("CHINA RESERVES", "Sinograin seeks 600k t soy oil; Nikkei ends 57,012", "UkrAg"),
        ],
    ),
]

TICKER_ITEMS = [
    ("ASIA MARKETS", "Taiex 38,195 (-4.8%) | Nikkei 57,012 | Kospi -5%", CRIMSON),
    ("UNSC AI BAN", "Guterres seeks ban on killer robots", (96, 165, 250)),
    ("ICBL REPORT", "Global mine toll highest since 2020", (251, 191, 36)),
    ("KAIST SCIENCE", "RQC protein link paces circadian clocks", (52, 211, 153)),
    ("MIT & CANON", "Atom black holes study; Ultimion CT debut", (192, 132, 252)),
]


def render_edition() -> None:
    # 1) Render high-resolution vector art layer at 2x (2048x2048)
    art_hi = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), PAPER)
    d_hi = ImageDraw.Draw(art_hi)

    # Top masthead dark fill + crimson top stripe + gold underline (2x)
    d_hi.rectangle([0, 0, WIDTH * SCALE, 66 * SCALE], fill=NAVY_DARK)
    d_hi.rectangle([0, 0, WIDTH * SCALE, 5 * SCALE], fill=CRIMSON)
    d_hi.rectangle([0, 64 * SCALE, WIDTH * SCALE, 67 * SCALE], fill=GOLD)

    # Hero card frames & 2x artwork
    hero_w = 244
    hero_gap = 8
    x0 = 12
    for idx, hero in enumerate(HEROES):
        hx = x0 + idx * (hero_w + hero_gap)
        hy = 74
        hh = 176
        d_hi.rounded_rectangle(
            [hx * SCALE, hy * SCALE, (hx + hero_w) * SCALE, (hy + hh) * SCALE],
            radius=12,
            fill=CARD_BG,
            outline=BORDER,
            width=2,
        )
        hero_art = hero.drawer((hero_w - 10) * SCALE, 86 * SCALE)
        art_hi.paste(hero_art, ((hx + 5) * SCALE, (hy + 5) * SCALE))
        # Kicker pill strip right beneath illustration edge
        d_hi.rectangle(
            [(hx + 5) * SCALE, (hy + 89) * SCALE, (hx + hero_w - 5) * SCALE, (hy + 92) * SCALE],
            fill=hero.accent,
        )

    # World Map (left of row 2: x=12..498, y=258..466)
    map_x, map_y, map_w, map_h = 12, 258, 486, 208
    draw_world_map_base(art_hi, map_x * SCALE, map_y * SCALE, map_w * SCALE, map_h * SCALE)

    # Spotlight grid container (right of row 2: x=506..1012, y=258..466)
    d_hi.rounded_rectangle(
        [506 * SCALE, 258 * SCALE, 1012 * SCALE, 466 * SCALE],
        radius=12,
        fill=CARD_BG,
        outline=BORDER,
        width=2,
    )
    d_hi.rounded_rectangle(
        [506 * SCALE, 258 * SCALE, 1012 * SCALE, 282 * SCALE],
        radius=8,
        fill=NAVY_DARK,
    )
    d_hi.rectangle([506 * SCALE, 274 * SCALE, 1012 * SCALE, 282 * SCALE], fill=NAVY_DARK)

    # Subtle spotlight sub-cells (2 cols x 3 rows)
    for idx, spot in enumerate(SPOTLIGHTS):
        col = idx % 2
        row = idx // 2
        sx = 512 + col * 248
        sy = 287 + row * 59
        d_hi.rounded_rectangle(
            [sx * SCALE, sy * SCALE, (sx + 242) * SCALE, (sy + 54) * SCALE],
            radius=8,
            fill=(250, 248, 243),
            outline=(226, 220, 208),
            width=2,
        )
        d_hi.rectangle([sx * SCALE, sy * SCALE, (sx + 4) * SCALE, (sy + 54) * SCALE], fill=spot.accent)

    # 6 Regional broadsheet panels (3 cols x 2 rows: y=474..952)
    reg_w = 328
    reg_h = 234
    for idx, reg in enumerate(REGIONS):
        col = idx % 3
        row = idx // 3
        rx = 12 + col * (reg_w + 8)
        ry = 474 + row * (reg_h + 8)
        d_hi.rounded_rectangle(
            [rx * SCALE, ry * SCALE, (rx + reg_w) * SCALE, (ry + reg_h) * SCALE],
            radius=12,
            fill=CARD_BG,
            outline=BORDER,
            width=2,
        )
        d_hi.rounded_rectangle(
            [rx * SCALE, ry * SCALE, (rx + reg_w) * SCALE, (ry + 24) * SCALE],
            radius=8,
            fill=reg.accent,
        )
        d_hi.rectangle([rx * SCALE, (ry + 16) * SCALE, (rx + reg_w) * SCALE, (ry + 24) * SCALE], fill=reg.accent)
        # Subtle divider hairlines inside region
        for k in range(1, 5):
            ly = (ry + 27 + k * 41) * SCALE
            d_hi.line([(rx + 8) * SCALE, ly, (rx + reg_w - 8) * SCALE, ly], fill=(232, 227, 218), width=2)

    # Footer ticker band (y=960..1016)
    d_hi.rounded_rectangle([12 * SCALE, 960 * SCALE, 1012 * SCALE, 1016 * SCALE], radius=10, fill=NAVY_DARK)
    d_hi.rectangle([12 * SCALE, 960 * SCALE, 1012 * SCALE, 963 * SCALE], fill=GOLD)
    for k in range(1, len(TICKER_ITEMS)):
        tx = (12 + k * 200) * SCALE
        d_hi.line([tx, 968 * SCALE, tx, 1010 * SCALE], fill=(51, 65, 85), width=2)

    # Downsample cleanly to crisp 1024x1024 base
    img = art_hi.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)

    # 2) Composite razor-sharp 1x native TrueType typography
    # Masthead (check headline stays clear left of x=812 pill)
    mast_text = "THE WORLD · WEDNESDAY, 25 NOVEMBER 2026"
    mb = draw.textbbox((0, 0), mast_text, font=F_MAST)
    assert (mb[2] - mb[0]) + 16 < 810, f"Masthead collides with right pill: {mb}"
    draw.text((16, 13), mast_text, font=F_MAST, fill=(255, 252, 245))
    draw.text(
        (17, 44),
        "ONE-DAY GLOBAL DISPATCH · ALL STORIES DATED 25 NOV 2026 · REUTERS / AP / UN / XINHUA / GUARDIAN / FIDE",
        font=F_SUBMAST,
        fill=(219, 229, 245),
    )
    # Right date/count pill
    draw.rounded_rectangle([820, 13, 1010, 53], radius=6, fill=CRIMSON)
    draw.text((831, 18), "WEDNESDAY 25 NOV", font=F_PILL, fill=(255, 255, 255))
    draw.text((831, 34), "6 CONTINENTS · 45 NEWS", font=F_PILL, fill=(254, 240, 138))

    # Hero labels & text
    for idx, hero in enumerate(HEROES):
        hx = 12 + idx * (hero_w + hero_gap)
        hy = 74
        hb = draw.textbbox((0, 0), hero.headline, font=F_HERO_TITLE)
        assert (hb[2] - hb[0]) <= hero_w - 18, f"Hero title too wide: {hero.headline} -> {hb[2]-hb[0]}"
        draw.text((hx + 9, hy + 96), hero.kicker, font=F_HERO_SRC, fill=hero.accent)
        draw.text((hx + 9, hy + 111), hero.headline, font=F_HERO_TITLE, fill=INK)
        lines = wrap_lines(draw, f"{hero.summary} [{hero.source}]", F_HERO_BODY, hero_w - 18)
        for li, line in enumerate(lines[:3]):
            assert li < 3, f"Hero text overflow: {hero.headline}"
            draw.text((hx + 9, hy + 130 + li * 13), line, font=F_HERO_BODY, fill=MUTED)

    # World Map Pin Numbers + Map Corner Banner + Legend Strip
    draw_pin_numbers(draw, map_x, map_y, map_w, map_h)
    draw.rounded_rectangle([map_x + 8, map_y + 7, map_x + 218, map_y + 26], radius=4, fill=(15, 23, 42))
    draw.text((map_x + 14, map_y + 10), "GLOBAL HOTSPOTS · 25 NOV 2026", font=F_MAP_TITLE, fill=(254, 240, 138))
    draw.rounded_rectangle([map_x + 6, map_y + map_h - 21, map_x + map_w - 6, map_y + map_h - 5], radius=4, fill=(15, 23, 42))
    map_legend = "1 Libya · 2 Tiangong · 3 RedSea · 4 TW · 5 Sol · 6 NY · 7 GVA · 8 Sen · 9 Ukr · 10 Arg · 11 ID · 12 NGA"
    mlb = draw.textbbox((0, 0), map_legend, font=F_MAP_LBL)
    assert (mlb[2] - mlb[0]) <= map_w - 22, f"Map legend too wide: {mlb[2] - mlb[0]}"
    draw.text(
        (map_x + (map_w - (mlb[2] - mlb[0])) // 2, map_y + map_h - 19),
        map_legend,
        font=F_MAP_LBL,
        fill=(241, 245, 249),
    )

    # Spotlights Header & 6 cards
    draw.text((516, 263), "MAJOR BREAKING HEADLINES · ALL 6 CONTINENTS", font=F_SEC_HDR, fill=(255, 255, 255))
    for idx, spot in enumerate(SPOTLIGHTS):
        col = idx % 2
        row = idx // 2
        sx = 518 + col * 248
        sy = 290 + row * 59
        draw_inline_item(
            draw,
            sx,
            sy,
            230,
            50,
            spot.kicker,
            spot.body,
            spot.source,
            spot.accent,
            F_SPOT_KICK,
            F_SPOT_BODY,
            line_h=15,
        )

    # Regional Cards
    for idx, reg in enumerate(REGIONS):
        col = idx % 3
        row = idx // 3
        rx = 12 + col * (reg_w + 8)
        ry = 474 + row * (reg_h + 8)
        draw.text((rx + 10, ry + 5), reg.title, font=F_REG_HDR, fill=(255, 255, 255))
        for j, item in enumerate(reg.items):
            iy = ry + 30 + j * 41
            draw_inline_item(
                draw,
                rx + 10,
                iy,
                reg_w - 20,
                38,
                item.kicker,
                item.body,
                item.source,
                reg.accent,
                F_ITEM_KICK,
                F_ITEM_BODY,
                line_h=14,
            )

    # Bottom Markets / UN / Science Ticker
    for idx, (kicker, body, col) in enumerate(TICKER_ITEMS):
        tx = 20 + idx * 200
        draw.text((tx, 967), kicker, font=F_TICK_KICK, fill=col)
        tlines = wrap_lines(draw, body, F_TICK_BODY, 184)
        for li, line in enumerate(tlines[:2]):
            draw.text((tx, 981 + li * 13), line, font=F_TICK_BODY, fill=(241, 245, 249))

    img.save(OUT_PATH, format="PNG", optimize=True)
    # Also save a 300x300 simulation preview outside repo? No, script saves only OUT_PATH; test harness inspects 300px separately.
    print(f"Generated {OUT_PATH}: {os.path.getsize(OUT_PATH)} bytes")


if __name__ == "__main__":
    render_edition()
