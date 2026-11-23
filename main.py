#!/usr/bin/env python3
"""The World in One Page -- Monday 23 November 2026.

Draws a one-page newspaper front page summing up the world's news of
Monday 23 November 2026 as a single 1024x1024 PNG, using nothing but the
Python standard library: a hand-built 5x7 bitmap typeface, flat geometric
artwork, and a small PNG encoder (zlib + struct). No network, no files
read, no randomness: two runs write byte for byte the same file.

Layout: masthead, four illustrated leads (2x2), a big-numbers strip, a
weekend-to-Monday timeline, seven small panels (one slot is the world
map with numbered pins), 37 one-line briefs in three columns, and a
date-check footer. 48 stories across 7 regions, every one first
reported 22-23 November 2026.

Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

SIDE = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (20, 20, 20)
WHITE = (255, 255, 255)
PANEL = (255, 255, 255)
PANEL2 = (239, 231, 211)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
GOLD = (196, 144, 2)
GREY = (107, 107, 107)
DARKBLUE = (16, 42, 67)
SKY = (174, 205, 226)
SEA = (46, 111, 164)
SAND = (226, 205, 158)
GREEN = (46, 125, 50)
ORANGE = (217, 119, 6)
LIGHTGREY = (210, 210, 200)

# ---------------------------------------------------------------- png out


def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, width, height, rgb):
    raw = b"".join(b"\x00" + rgb[y * width * 3:(y + 1) * width * 3]
                   for y in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)


# ------------------------------------------------------------------ canvas


class Canvas:
    def __init__(self, side):
        self.side = side
        self.px = bytearray(PAPER * (side * side))

    def _set(self, x, y, colour):
        if 0 <= x < self.side and 0 <= y < self.side:
            i = (y * self.side + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.side, x + w), min(self.side, y + h)
        for yy in range(y0, y1):
            base = (yy * self.side + x0) * 3
            self.px[base:(base + (x1 - x0) * 3)] = bytes(colour) * (x1 - x0)

    def hline(self, x, y, w, colour):
        self.rect(x, y, w, 1, colour)

    def vline(self, x, y, h, colour):
        self.rect(x, y, 1, h, colour)

    def border(self, x, y, w, h, colour, t=1):
        self.rect(x, y, w, t, colour)
        self.rect(x, y + h - t, w, t, colour)
        self.rect(x, y, t, h, colour)
        self.rect(x + w - t, y, t, h, colour)

    def circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self._set(xx, yy, colour)

    def disc(self, cx, cy, r, colour):
        self.circle(cx, cy, r, colour)

    def ring(self, cx, cy, r, colour, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self._set(xx, yy, colour)

    def tri(self, x0, y0, x1, y1, x2, y2, colour):
        xs = sorted([x0, x1, x2])
        ys = sorted([y0, y1, y2])
        for yy in range(ys[0], ys[2] + 1):
            row = []
            for xa, ya, xb, yb in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                  (x2, y2, x0, y0)):
                if ya == yb:
                    continue
                if min(ya, yb) <= yy <= max(ya, yb):
                    row.append(xa + (xb - xa) * (yy - ya) / (yb - ya))
            if len(row) >= 2:
                for xx in range(int(min(row)), int(max(row)) + 1):
                    self._set(xx, yy, colour)

    def poly(self, pts, colour):
        ys = sorted(p[1] for p in pts)
        for yy in range(ys[0], ys[-1] + 1):
            row = []
            n = len(pts)
            for i in range(n):
                xa, ya = pts[i]
                xb, yb = pts[(i + 1) % n]
                if ya == yb:
                    continue
                if min(ya, yb) <= yy <= max(ya, yb):
                    row.append(xa + (xb - xa) * (yy - ya) / (yb - ya))
            row.sort()
            for k in range(0, len(row) - 1, 2):
                for xx in range(int(row[k]), int(row[k + 1]) + 1):
                    self._set(xx, yy, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            self._set(round(x0 + dx * i / steps), round(y0 + dy * i / steps),
                      colour)


# ------------------------------------------------------------- 5x7 typeface
# Five cells wide, seven rows tall per glyph; uppercase only. Written
# from scratch for this page: "#" is ink, "." is blank.


FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("###  ", "#  # ", "#   #", "#   #", "#   #", "#  # ", "###  "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": (" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", "#    "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "#    "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "(": ("   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"),
    ")": ("##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "),
    "%": ("#   #", "#  # ", "    #", "   # ", "  #  ", " #  #", "#   #"),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", " ### ", "     ", " ### ", "     ", "     "),
    "&": (" ##  ", "#  # ", "# #  ", " #   ", "# # #", "#  # ", " ## #"),
    "*": ("     ", "# # #", " ### ", "#####", " ### ", "# # #", "     "),
    "#": (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
    "<": ("   # ", "  #  ", " #   ", "#    ", " #   ", "  #  ", "   # "),
    ">": (" #   ", "  #  ", "   # ", "    #", "   # ", "  #  ", " #   "),
    "[": (" ### ", " #   ", " #   ", " #   ", " #   ", " #   ", " ### "),
    "]": (" ### ", "   # ", "   # ", "   # ", "   # ", "   # ", " ### "),
}

BLANK = ("     ",) * 7


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, scale, colour, text):
    pen = x
    for ch in text.upper():
        glyph = FONT.get(ch, BLANK)
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "#":
                    cv.rect(pen + col * scale, y + row * scale,
                            scale, scale, colour)
        pen += 6 * scale


def draw_centred(cv, centre, y, scale, colour, text):
    draw_text(cv, centre - text_width(text, scale) // 2, y, scale, colour,
              text)


def wrap_lines(text, scale, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, scale, colour, text, max_w, max_lines, leading):
    lines = wrap_lines(text, scale, max_w)[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * leading, scale, colour, ln)
    return len(lines)

# ------------------------------------------------------------ lead artwork
# Four flat scenes, one per lead, each fitted to the art strip it gets.


def art_hormuz(cv, x, y, w, h):
    cv.rect(x, y, w, h, DARKBLUE)
    cv.disc(x + 330, y + 20, 12, ORANGE)
    cv.rect(x, y + h - 26, w, 26, SEA)
    cv.rect(x + 52, y + h - 48, 150, 22, INK)
    cv.rect(x + 52, y + h - 54, 26, 8, INK)
    cv.rect(x + 178, y + h - 62, 10, 16, INK)
    cv.rect(x + 52, y + h - 30, 150, 3, WHITE)
    cv.line(x + 90, y + 8, x + 130, y + h - 48, GOLD)
    cv.line(x + 150, y + 4, x + 185, y + h - 48, GOLD)
    cv.disc(x + 130, y + h - 48, 6, GOLD)
    cv.disc(x + 185, y + h - 48, 6, GOLD)
    for wx in range(x + 14, x + w - 20, 34):
        cv.line(wx, y + h - 12, wx + 16, y + h - 12, WHITE)


def art_cop31(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + w // 2, y + h // 2 + 4, 26, GREEN)
    cv.rect(x + w // 2 - 26, y + h // 2 - 4, 52, 5, GREEN)
    cv.rect(x + w // 2 - 14, y + h // 2 - 16, 12, 8, SAND)
    cv.rect(x + w // 2 + 6, y + h // 2 + 8, 14, 7, SAND)
    cv.line(x + w // 2 - 20, y + h // 2 - 24, x + w // 2 + 4,
            y + h // 2 - 2, RED)
    cv.line(x + w // 2 + 4, y + h // 2 - 2, x + w // 2 - 8,
            y + h // 2 + 22, RED)
    cv.line(x + w // 2 - 30, y + h // 2 - 30, x + w // 2 + 30,
            y + h // 2 + 30, RED)
    cv.line(x + w // 2 + 30, y + h // 2 - 30, x + w // 2 - 30,
            y + h // 2 + 30, RED)
    cv.rect(x + 16, y + h - 14, w - 32, 3, INK)


def art_ships(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 24, w, 24, SEA)
    cv.rect(x + 60, y + h - 46, 170, 20, INK)
    cv.rect(x + 220, y + h - 62, 8, 18, INK)
    cv.rect(x + 96, y + h - 54, 22, 8, INK)
    cx, cy = x + 320, y + 26
    for dx, dy in ((0, -16), (11, -11), (16, 0), (11, 11), (0, 16),
                   (-11, 11), (-16, 0), (-11, -11)):
        cv.line(cx, cy, cx + dx, cy + dy, ORANGE)
    cv.disc(cx, cy, 8, GOLD)
    cv.disc(cx - 34, cy + 10, 7, LIGHTGREY)
    cv.disc(cx - 22, cy + 16, 9, LIGHTGREY)
    for wx in range(x + 14, x + w - 20, 34):
        cv.line(wx, y + h - 10, wx + 16, y + h - 10, WHITE)


def art_nepal(cv, x, y, w, h):
    cv.rect(x, y, w, h, SKY)
    cv.disc(x + 330, y + 16, 12, GOLD)
    cv.tri(x + 20, y + h, x + 90, y + 8, x + 160, y + h, TEAL)
    cv.tri(x + 110, y + h, x + 180, y + 22, x + 250, y + h, BLUE)
    cv.tri(x + 76, y + 20, x + 90, y + 8, x + 104, y + 20, WHITE)
    cv.tri(x + 168, y + 32, x + 180, y + 22, x + 192, y + 32, WHITE)
    cv.rect(x + w - 120, y + h - 34, 96, 34, SAND)
    cv.disc(x + w - 72, y + h - 34, 20, RED)
    cv.rect(x + w - 120, y + h - 34, 96, 4, INK)
    cv.rect(x + 24, y + h - 40, 8, 40, RED)
    cv.tri(x + 24, y + h - 52, x + 40, y + h - 40, x + 24, y + h - 28, RED)
    cv.tri(x + 24, y + h - 28, x + 40, y + h - 16, x + 24, y + h - 4, RED)


# -------------------------------------------------------------------- data
# 48 stories, every one first reported 22-23 November 2026. Leads 1-4,
# small panels 5-11, one-line briefs 12-48 (<=27 chars at scale 2).

LEADS = [
    ("MIDDLE EAST", RED, art_hormuz,
     "IRAN HITS US BASES IN BAHRAIN",
     "IRGC missiles and drones hit Al-Riffa and Awali. Bahrain: a "
     "site burned, two hurt. 25 tankers hit in a week."),
    ("CLIMATE", TEAL, art_cop31,
     "CLIMATE TALKS COLLAPSE",
     "COP31 ends with no deal in Antalya. The draft left out "
     "fossil fuels; the EU and UK said no. Longest COP ever."),
    ("UKRAINE WAR", BLUE, art_ships,
     "RUSSIAN WARSHIP SUNK IN LIBYA",
     "Sea drones sink corvette Merkury at Benghazi at dawn. Sparta II "
     "burns in the Baltic; 16 crew rescued."),
    ("ASIA", GOLD, art_nepal,
     "NEPAL PM MEETS MODI IN DELHI",
     "Balendra Shah holds bilateral talks in Delhi on his 22-23 Nov "
     "state visit. Trade, energy and border on the table."),
]

SMALL = [
    ("ASIA", "CANDY FACTORY FIRE",
     "3 DEAD, 36 MISSING IN CIKANDE."),
    ("AMERICAS", "DEMOCRATS: 258 SEATS",
     "BIGGEST SINCE 1992, LARGEST EVER."),
    ("MARKETS", "KOSPI: FUND ON STANDBY",
     "SEOUL -5.2% FRIDAY. FUND READY."),
    ("SPORT", "INDIA 720/9D RECORD",
     "HIGHEST TEST TOTAL IN NZ. DAY 4."),
    ("SPORT", "VERSTAPPEN WINS VEGAS",
     "BEATS NORRIS BY 0.5S. PIASTRI 3RD."),
    ("AFRICA", "SOUTH SUDAN: 24 DEAD",
     "SPLA-IO KILLED 24, AFP SAYS."),
    ("AFRICA", "EBOLA FIGHT HIT BY WAR",
     "WHO: WAR BLOCKS EBOLA RESPONSE."),
]

BRIEFS = [
    ("MIDDLE EAST", [
        "12 TANKERS HIT IN HORMUZ",
        "13 HOUTHI MISSILE DOWNED",
        "14 DRONE DOWNED OVER QESHM",
        "15 EISENKOT SLAMS SETTLERS",
        "16 NETANYAHU TALKS FAIL",
    ]),
    ("EUROPE", [
        "17 NATO: 'EVERY INCH' VOW",
        "18 14 MISSING IN KYIV BLAST",
        "19 1 DEAD, 9 HURT IN DNIPRO",
        "20 DNI: PUTIN NOT A FRIEND",
        "21 LISBON MARCHES ON PRICES",
        "22 TURKEY PROTESTS TV RAIDS",
        "23 POLAND: RAPPER PLOT",
    ]),
    ("ASIA", [
        "24 KOREA MINISTER QUITS",
        "25 KOTA BUS CRASH: 9 DEAD",
        "26 MP WADKUTE DIES IN DELHI",
        "27 SHAH'S RS 4,000-CR PUSH",
        "28 MODI OPENS AI CENTRE",
        "29 MYANMAR SLAMS ASEAN MOVE",
        "30 PAKISTAN HOPES IRAN DEAL",
    ]),
    ("AMERICAS", [
        "31 DELTA HALTED IN ATLANTA",
        "32 ICE DETAIN 2 IN SEATTLE",
        "33 FBI PROBES DATA BREACH",
        "34 BESSENT PRESSES NVIDIA",
        "35 TRUMP HOSTS COIN DINNER",
        "36 METCALF EJECTED IN NFL",
    ]),
    ("AFRICA", [
        "37 BENGHAZI DRONE PROBE",
        "38 WHO WARNS ON EBOLA FIGHT",
    ]),
    ("MARKETS", [
        "39 S+P -9.3% IN 7 SESSIONS",
        "40 NVIDIA -47.5% FROM PEAK",
        "41 BITCOIN BEAR: 412 DAYS",
        "42 CHINA EASES MARGIN 80%",
        "43 TAIWAN CURBS SHORT SALES",
    ]),
    ("SPORT", [
        "44 LIVERPOOL ROUT MAN UTD",
        "45 INDIA WIN ODI SERIES 3-2",
        "46 ANUPAMA KEEPS CROWN",
        "47 PRINCESS KATE 'HEAL'",
        "48 TOM JACKSON, ESPN VOICE",
    ]),
]

NUMBERS = [
    ("258", "HOUSE SEATS"),
    ("25", "TANKERS HIT"),
    ("36", "MISSING IN JAVA"),
    ("720", "INDIA'S RECORD"),
    ("0", "COP31 DEAL"),
    ("-5.2%", "KOSPI FRIDAY"),
]

TIMELINE = [
    ("SAT EVE", "IRAN HITS BAHRAIN"),
    ("SUN AM", "MERKURY SUNK IN LIBYA"),
    ("SUN PM", "COP31: NO DEAL"),
    ("SUN EVE", "SPARTA II TOWED OUT"),
    ("MON AM", "NEPAL PM MEETS MODI"),
]

# Rough world map polygons (equirectangular, 229 x 70 box).
MAP_LAND = [
    [(8, 18), (30, 8), (55, 10), (62, 18), (52, 26), (40, 30), (28, 34),
     (14, 28)],
    [(48, 42), (62, 44), (66, 54), (58, 66), (50, 58)],
    [(108, 12), (128, 8), (136, 16), (126, 22), (112, 20)],
    [(108, 34), (126, 32), (138, 40), (132, 56), (118, 58), (108, 46)],
    [(138, 10), (185, 6), (205, 14), (200, 28), (175, 34), (160, 30),
     (145, 22)],
    [(190, 52), (208, 50), (212, 58), (196, 60)],
]
# Numbered pins: (story, x, y). Others: small dots.
MAP_PINS = [(1, 180, 40), (2, 128, 16), (3, 118, 38), (4, 166, 22)]
MAP_DOTS = [(196, 44), (196, 20), (214, 62), (30, 22), (58, 52),
            (118, 46), (150, 20)]


# ------------------------------------------------------------------- panels


def badge(cv, x, y, num, colour):
    cv.rect(x, y, 20, 20, colour)
    draw_centred(cv, x + 10, y + 3, 2, WHITE, str(num))


def lead_panel(cv, x, y, w, h, num, region, colour, art, headline,
               caption):
    cv.rect(x, y, w, h, PANEL)
    cv.border(x, y, w, h, INK, 2)
    art(cv, x + 2, y + 2, w - 4, 56)
    badge(cv, x + 8, y + 8, num, colour)
    tw = text_width(region, 2)
    cv.rect(x + w - 14 - tw, y + 6, tw + 8, 18, INK)
    draw_text(cv, x + w - 10 - tw, y + 10, 2, WHITE, region)
    draw_wrapped(cv, x + 10, y + 66, 4, INK, headline, w - 20, 2, 29)
    draw_wrapped(cv, x + 10, y + 126, 2, INK, caption, w - 20, 3, 14)


def small_panel(cv, x, y, w, h, num, region, headline, caption):
    cv.rect(x, y, w, h, PANEL)
    cv.border(x, y, w, h, INK, 1)
    cv.rect(x, y, w, 22, PANEL2)
    draw_text(cv, x + 6, y + 4, 2, RED, str(num))
    draw_text(cv, x + 30, y + 4, 2, INK, region)
    draw_wrapped(cv, x + 8, y + 28, 3, INK, headline, w - 16, 2, 21)
    draw_wrapped(cv, x + 8, y + 72, 2, GREY, caption, w - 16, 2, 13)


def map_panel(cv, x, y, w, h):
    cv.rect(x, y, w, h, (214, 230, 240))
    cv.border(x, y, w, h, INK, 1)
    draw_text(cv, x + 6, y + 4, 2, INK, "WHERE IT HAPPENED")
    ox, oy = x + 8, y + 24
    for pts in MAP_LAND:
        cv.poly([(ox + px, oy + py) for px, py in pts], GREEN)
    for dx, dy in MAP_DOTS:
        cv.disc(ox + dx, oy + dy, 3, RED)
    for num, px, py in MAP_PINS:
        cv.disc(ox + px, oy + py, 10, RED)
        draw_text(cv, ox + px - 3, oy + py - 7, 2, WHITE, str(num))


# -------------------------------------------------------------------- page


def compose():
    cv = Canvas(SIDE)
    # Masthead.
    draw_centred(cv, SIDE // 2, 10, 6, INK, "THE WORLD IN ONE PAGE")
    draw_centred(cv, SIDE // 2, 54, 3, RED,
                 "MONDAY 23 NOVEMBER 2026 - 48 STORIES - 7 REGIONS")
    cv.hline(10, 84, SIDE - 20, INK)
    cv.hline(10, 87, SIDE - 20, INK)
    # Four leads, 2x2.
    lw, lh = 496, 170
    for i, (region, colour, art, headline, caption) in enumerate(LEADS):
        lx = 10 + (i % 2) * (lw + 12)
        ly = 94 + (i // 2) * (lh + 8)
        lead_panel(cv, lx, ly, lw, lh, i + 1, region, colour, art,
                   headline, caption)
    # Big-numbers strip.
    ny = 450
    cv.rect(10, ny, SIDE - 20, 48, PANEL2)
    cv.border(10, ny, SIDE - 20, 48, INK, 1)
    cw = (SIDE - 20) // 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = 10 + i * cw
        draw_centred(cv, cx + cw // 2, ny + 3, 4, RED, num)
        draw_centred(cv, cx + cw // 2, ny + 34, 2, INK, label)
        if i:
            cv.vline(cx, ny + 6, 32, GREY)
    # Timeline strip.
    ty = 502
    cv.rect(10, ty, SIDE - 20, 42, PANEL)
    cv.border(10, ty, SIDE - 20, 42, INK, 1)
    tw = (SIDE - 20) // 5
    for i, (when, what) in enumerate(TIMELINE):
        tx = 10 + i * tw
        draw_text(cv, tx + 8, ty + 4, 2, RED, when)
        draw_wrapped(cv, tx + 8, ty + 19, 2, INK, what, tw - 16, 2, 11)
        if i:
            cv.vline(tx, ty + 5, 32, GREY)
    # Small panels: row A four, row B three + map.
    sw, sh = 245, 100
    for i, (region, headline, caption) in enumerate(SMALL):
        if i < 4:
            sx = 10 + i * (sw + 8)
            sy = 552
        else:
            sx = 10 + (i - 4) * (sw + 8)
            sy = 660
        small_panel(cv, sx, sy, sw, sh, i + 5, region, headline, caption)
    map_panel(cv, 10 + 3 * (sw + 8), 660, sw, sh)
    # Briefs, three columns grouped by region.
    cols = [BRIEFS[0:2], BRIEFS[2:4], BRIEFS[4:7]]
    bx = [10, 348, 686]
    bw = 328
    for ci, groups in enumerate(cols):
        yy = 772
        for region, items in groups:
            draw_text(cv, bx[ci], yy, 2, RED, region)
            yy += 15
            for item in items:
                draw_text(cv, bx[ci], yy, 2, INK, item)
                yy += 14
            yy += 3
    # Footer.
    cv.hline(10, 990, SIDE - 20, INK)
    draw_centred(cv, SIDE // 2, 996, 2, INK,
                 "DATE CHECK: EVERY STORY FIRST REPORTED 22-23 NOV 2026")
    draw_centred(cv, SIDE // 2, 1010, 2, GREY,
                 "48 STORIES, 7 REGIONS - DRAWN WITH PYTHON STDLIB ONLY")
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = compose()
    write_png(os.path.join(out_dir, "entry.png"), SIDE, SIDE, cv.px)


if __name__ == "__main__":
    main()
