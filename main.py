#!/usr/bin/env python3
"""THE WORLD - front page for Monday 23 November 2026.

Pure standard library: a hand-written 5x7 bitmap font, an RGB pixel buffer and a
hand-written PNG encoder (struct + zlib). Deterministic, no network, no clock.
"""
import os
import struct
import zlib

W = H = 1024
PAPER = (244, 239, 226)
INK = (20, 18, 16)
RED = (158, 22, 28)
GREY = (92, 88, 80)

# ---------------------------------------------------------------- font ----
_G = {}


def _def(ch, *rows):
    _G[ch] = rows


_def("A", ".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
_def("B", "####.", "#...#", "#...#", "####.", "#...#", "#...#", "####.")
_def("C", ".###.", "#...#", "#....", "#....", "#....", "#...#", ".###.")
_def("D", "####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####.")
_def("E", "#####", "#....", "#....", "####.", "#....", "#....", "#####")
_def("F", "#####", "#....", "#....", "####.", "#....", "#....", "#....")
_def("G", ".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###.")
_def("H", "#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#")
_def("I", ".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###.")
_def("J", "..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##..")
_def("K", "#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#")
_def("L", "#....", "#....", "#....", "#....", "#....", "#....", "#####")
_def("M", "#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#")
_def("N", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#")
_def("O", ".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
_def("P", "####.", "#...#", "#...#", "####.", "#....", "#....", "#....")
_def("Q", ".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#")
_def("R", "####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#")
_def("S", ".####", "#....", "#....", ".###.", "....#", "....#", "####.")
_def("T", "#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#..")
_def("U", "#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###.")
_def("V", "#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#..")
_def("W", "#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#")
_def("X", "#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#")
_def("Y", "#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#..")
_def("Z", "#####", "....#", "...#.", "..#..", ".#...", "#....", "#####")
_def("0", ".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###.")
_def("1", "..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###.")
_def("2", ".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####")
_def("3", "####.", "....#", "....#", ".###.", "....#", "....#", "####.")
_def("4", "...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#.")
_def("5", "#####", "#....", "####.", "....#", "....#", "#...#", ".###.")
_def("6", ".###.", "#....", "#....", "####.", "#...#", "#...#", ".###.")
_def("7", "#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#...")
_def("8", ".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###.")
_def("9", ".###.", "#...#", "#...#", ".####", "....#", "....#", ".###.")
_def(".", ".....", ".....", ".....", ".....", ".....", ".##..", ".##..")
_def(",", ".....", ".....", ".....", ".....", ".##..", ".##..", ".#...")
_def(";", ".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#...")
_def(":", ".....", ".##..", ".##..", ".....", ".##..", ".##..", ".....")
_def("!", "..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#..")
_def("?", ".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#..")
_def("'", "..#..", "..#..", ".#...", ".....", ".....", ".....", ".....")
_def("-", ".....", ".....", ".....", "#####", ".....", ".....", ".....")
_def("(", "...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#.")
_def(")", ".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#...")
_def("%", "##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##")
_def("&", ".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#")
_def("/", "....#", "....#", "...#.", "..#..", ".#...", "#....", "#....")
_def("·", ".....", ".....", ".....", "..#..", ".....", ".....", ".....")
_def(" ", *["....."] * 7)

# ------------------------------------------------------------- canvas -----
buf = bytearray(bytes(PAPER) * (W * H))


def rect(x, y, w, h, col):
    x0, x1 = max(0, x), min(W, x + w)
    y0, y1 = max(0, y), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(col) * (x1 - x0)
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        buf[o:o + len(row)] = row


def text_w(s, sc):
    return len(s) * 6 * sc - sc if s else 0


def text(x, y, s, sc, col=INK, bold=False):
    """Draw upper-cased text; return x after the last glyph."""
    for ch in s.upper():
        g = _G.get(ch, _G["?"])
        for r, row in enumerate(g):
            c = 0
            while c < 5:
                if row[c] == "#":
                    c2 = c
                    while c2 < 5 and row[c2] == "#":
                        c2 += 1
                    rect(x + c * sc, y + r * sc, (c2 - c) * sc + (1 if bold else 0) * max(1, sc // 2),
                         sc, col)
                    c = c2
                else:
                    c += 1
        x += 6 * sc
    return x - sc


def wrap(s, sc, width):
    maxc = (width + sc) // (6 * sc)
    lines, cur = [], ""
    for word in s.split():
        t = word if not cur else cur + " " + word
        if len(t) <= maxc:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, sc, width, col=INK, bold=False, lead=None):
    lead = lead or 8 * sc + max(1, sc // 2)
    for ln in wrap(s, sc, width):
        text(x, y, ln, sc, col, bold)
        y += lead
    return y


def para_h(s, sc, width, lead=None):
    lead = lead or 8 * sc + max(1, sc // 2)
    return len(wrap(s, sc, width)) * lead


def tag(x, y, s, sc):
    """Red chip with paper-coloured text; returns chip width."""
    w = text_w(s, sc) + 4 * sc
    rect(x, y, w, tag_h(sc), RED)
    text(x + 2 * sc, y + sc, s, sc, PAPER, True)
    return w


def tag_h(sc):
    return 9 * sc


# ------------------------------------------------------------ content -----
HERO = ("TECH - LEAD",
        "Nvidia brings back Jensen Huang as chief executive",
        "The board reinstated Huang with immediate effect in an extraordinary "
        "reversal under pressure from President Donald Trump. Shares jumped "
        "about 30% on the news.")

STORIES = [
    ("WAR", "Ukraine says its sea drones sank a Russian warship off Libya",
     "Zelenskyy hailed an 'exemplary operation'; a Russian cargo ship was also hit in the Baltic."),
    ("CLIMATE", "COP31 collapses with no deal on fossil fuels",
     "The UN summit ended with no approved agreement after the draft dropped fossil-fuel phase-out language."),
    ("USA", "Democrats take largest House majority since 1992",
     "Chuck Hubbard unseated Virginia Foxx in North Carolina, sealing the biggest majority in 34 years."),
    ("USA", "Democrats fire starting gun on the 2028 White House race",
     "Party officials revealed details of the 2028 presidential primary schedule."),
    ("UK - EUROPE", "Burnham defends EU reset deal in the Commons",
     "The prime minister promised 'no banging on about Europe' as MPs pressed him on a referendum."),
    ("MARKETS", "Bitcoin rebounds from a two-year low",
     "Bitcoin bounced after a weekend plunge to its lowest in two years as Wall Street futures recovered."),
    ("MIDDLE EAST - ASIA", "Houthis claim strike on Saudi oil refinery",
     "Rebels said they hit a major refinery on the Red Sea coast. Bangladesh vowed to arrest Sheikh Hasina if she returns."),
    ("SPORT", "2031 Women's World Cup goes to four hosts",
     "FIFA approved the joint US, Mexico, Costa Rica and Jamaica bid; the UK was confirmed as host for 2035."),
]

FOOTER = ("Also on 23 November: flights grounded in Belgium as workers strike over "
          "austerity · dozens missing after an Indonesia candy-factory fire · "
          "Iran warns of a response to any attack amid a naval blockade.")
SOURCES = "Sources: BBC, Al Jazeera, Daily Mirror, Economic Times, CoinDesk."

# ------------------------------------------------------------- layout -----
M = 24
CW = W - 2 * M


def build():
    # masthead
    s = 7
    mw = text_w("THE WORLD", s)
    text(M + (CW - mw) // 2, 10, "THE WORLD", s, INK, True)
    rect(M, 68, CW, 4, INK)
    rect(M, 75, CW, 2, INK)
    # date band
    rect(M, 82, CW, 46, RED)
    d = "MONDAY 23 NOVEMBER 2026"
    ds = 5
    dw = text_w(d, ds)
    text(M + (CW - dw) // 2, 82 + (46 - 7 * ds) // 2, d, ds, PAPER, True)

    # hero
    y = 138
    tag(M, y, HERO[0], 3)
    y += tag_h(3) + 10
    hs = 5
    y = para(M, y, HERO[1], hs, CW, INK, True, lead=8 * hs + 3)
    y += 4
    y = para(M, y, HERO[2], 3, CW, INK, False, lead=8 * 3 + 1)
    y += 6
    rect(M, y, CW, 4, RED)
    y += 10

    # grid
    gap = 28
    colw = (CW - gap) // 2
    hsz, ssz = 3, 2
    top = y
    rows = [STORIES[i:i + 2] for i in range(0, 8, 2)]
    flines = len(wrap(FOOTER, 2, CW - 16))
    fh = 8 + flines * 16 + 4 + 14 + 8          # strip height from its content
    footer_top = H - 8 - fh                    # strip ends 8 px above the edge
    # measure
    heights = []
    for pair in rows:
        h = 0
        for (t, hd, sm) in pair:
            hh = tag_h(2) + 4 + para_h(hd, hsz, colw, 8 * hsz) + 4 + para_h(sm, ssz, colw, 8 * ssz + 1)
            h = max(h, hh)
        heights.append(h)
    total = sum(heights)
    pad = (footer_top - 14 - top - total) // (len(rows) - 1)  # even spacing between rows
    for ri, pair in enumerate(rows):
        for ci, (t, hd, sm) in enumerate(pair):
            x = M + ci * (colw + gap)
            yy = y
            tag(x, yy, t, 2)
            yy += tag_h(2) + 4
            yy = para(x, yy, hd, hsz, colw, INK, True, lead=8 * hsz)
            yy += 4
            yy = para(x, yy, sm, ssz, colw, GREY if False else INK, False, lead=8 * ssz + 1)
        y += heights[ri]
        if ri < len(rows) - 1:
            y += pad // 2
            rect(M, y, CW, 2, INK)
            y += pad - pad // 2
    # vertical divider
    rect(M + colw + gap // 2 - 1, top, 2, y - top, INK)
    grid_end = y

    # footer strip
    fy = footer_top
    rect(M, fy - 6, CW, 4, INK)
    rect(M, fy, CW, fh, INK)
    fy2 = para(M + 8, fy + 8, FOOTER, 2, CW - 16, PAPER, False, lead=16)
    text(M + 8, fy2 + 4, SOURCES, 2, (214, 204, 184), False)
    return grid_end, fy + fh


# ---------------------------------------------------------------- png -----
def png_bytes():
    raw = bytearray()
    stride = W * 3
    for yy in range(H):
        raw.append(0)
        raw += buf[yy * stride:(yy + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", comp)
            + chunk(b"IEND", b""))


def main():
    ge, fe = build()
    out = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    os.chmod(path, 0o644)


if __name__ == "__main__":
    main()
