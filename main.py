#!/usr/bin/env python3
"""THE WORLD — 23 November 2026.

make.fun bounty: "Sum up 23 November's world news in one image".
Renders a one-page broadsheet-style news summary as PNG, fully offline
and deterministic: no network, no clock, no randomness. stdlib + Pillow only.

Run:  python3 main.py            -> writes world-23-nov-2026.png
Test:  python3 main.py --check   -> renders twice, asserts byte-identical output
"""
import hashlib
import sys
from PIL import Image, ImageDraw, ImageFont

DATE = "Monday, 23 November 2026"
OUT = "world-23-nov-2026.png"
W, H = 1600, 2200
PAPER = (250, 247, 238)
INK = (18, 18, 18)
ACCENT = (158, 27, 27)
MUTED = (90, 88, 82)
RULE = (180, 175, 162)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def story_block(draw, x, y, w, tag, headline, body, head_size=40, body_size=27):
    hf, bf, tf = font(SERIF_B, head_size), font(SERIF, body_size), font(SANS_B, 24)
    # category tag
    tw = draw.textlength(tag, font=tf) + 24
    draw.rounded_rectangle([x, y, x + tw, y + 36], radius=4, fill=ACCENT)
    draw.text((x + 12, y + 5), tag, font=tf, fill=(255, 255, 255))
    y += 52
    for ln in wrap(draw, headline, hf, w):
        draw.text((x, y), ln, font=hf, fill=INK)
        y += head_size + 8
    y += 6
    for ln in wrap(draw, body, bf, w):
        draw.text((x, y), ln, font=bf, fill=(52, 50, 46))
        y += body_size + 9
    return y


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    m = 80  # margin
    # ---- masthead ----
    d.text((m, 48), "THE WORLD", font=font(SERIF_B, 118), fill=INK)
    d.text((m, 178), "IN ONE PAGE", font=font(SANS_B, 34), fill=ACCENT)
    d.text((W - m - d.textlength(DATE, font=font(SANS_B, 34)), 186),
           DATE, font=font(SANS_B, 34), fill=INK)
    d.line([(m, 240), (W - m, 240)], fill=INK, width=4)
    d.line([(m, 248), (W - m, 248)], fill=INK, width=1)

    y = 280
    # ---- hero: Nvidia ----
    y = story_block(
        d, m, y, W - 2 * m, "TECH  ·  LEAD",
        "Nvidia brings back Jensen Huang as chief executive",
        "The board reinstated Huang with immediate effect in an extraordinary "
        "reversal under pressure from President Donald Trump, after revelations "
        "about the chief executive's private life. Shares jumped about 30% on "
        "the news, capping one of the strangest leadership sagas in tech.",
        head_size=56, body_size=30)
    d.line([(m, y + 18), (W - m, y + 18)], fill=RULE, width=2)
    y += 44

    # ---- two-column grid, 8 stories ----
    col_w = (W - 2 * m - 40) // 2
    left = [
        ("WAR", "Ukraine says its sea drones sank a Russian warship off Libya",
         "President Zelenskyy hailed an \u201cexemplary operation\u201d after Kyiv "
         "confirmed the strike. A Russian cargo ship was also hit in the Baltic."),
        ("CLIMATE", "COP31 collapses with no deal on fossil fuels",
         "The UN climate summit ended without an approved agreement after the "
         "draft text dropped language on moving away from fossil fuels."),
        ("USA", "Democrats take largest House majority since 1992",
         "Democrat Chuck Hubbard unseated Republican Virginia Foxx in North "
         "Carolina, sealing the biggest Democratic House majority in 34 years."),
        ("SPORT", "2031 Women's World Cup goes to four hosts",
         "FIFA approved a joint bid from the United States, Mexico, Costa Rica "
         "and Jamaica. The UK was confirmed as host of the 2035 edition."),
    ]
    right = [
        ("USA", "Democrats fire starting gun on the 2028 White House race",
         "Party officials revealed details of the 2028 presidential primary "
         "schedule a year after midterm victories."),
        ("UK  ·  EUROPE", "Burnham defends EU reset deal in the Commons",
         "The prime minister defended the new agreement with the EU, promising "
         "\u201cno banging on about Europe\u201d, as MPs pressed him on a referendum."),
        ("MARKETS", "Bitcoin rebounds from a two-year low",
         "Bitcoin bounced back after a weekend plunge to its lowest in two "
         "years, its second-longest losing streak on record, as Wall Street "
         "futures recovered."),
        ("MIDDLE EAST  ·  ASIA", "Houthis claim strike on Saudi oil refinery",
         "Yemen's Houthi rebels said they attacked a major refinery on Saudi "
         "Arabia's Red Sea coast. Bangladesh vowed to arrest Sheikh Hasina if "
         "she returns from India in December."),
    ]
    ly = ry = y
    for tag, head, body in left:
        ly = story_block(d, m, ly, col_w, tag, head, body) + 34
    for tag, head, body in right:
        ry = story_block(d, m + col_w + 40, ry, col_w, tag, head, body) + 34
    y = max(ly, ry)
    d.line([(m, y), (W - m, y)], fill=RULE, width=2)

    # ---- footer ----
    fy = y + 22
    for ln in wrap(d, "Also on 23 November: flights grounded in Belgium as workers "
                   "strike over austerity  ·  dozens still missing after an "
                   "Indonesia candy-factory fire  ·  Iran warns of a response to "
                   "any attack amid a naval blockade.",
                   font(SERIF, 25), W - 2 * m):
        d.text((m, fy), ln, font=font(SERIF, 25), fill=MUTED)
        fy += 34
    d.text((m, H - 78), "Sources: BBC, Al Jazeera, Daily Mirror, Economic Times, "
           "CoinDesk.", font=font(SANS, 22), fill=MUTED)
    d.text((W - m - d.textlength("THE WORLD — 23 NOV 2026", font=font(SANS_B, 22)), H - 78),
           "THE WORLD — 23 NOV 2026", font=font(SANS_B, 22), fill=MUTED)
    return img


def main():
    img = render()
    img.save(OUT)
    if "--check" in sys.argv:
        img2 = render()
        img2.save("/tmp/world-check.png")
        h1 = hashlib.sha256(open(OUT, "rb").read()).hexdigest()
        h2 = hashlib.sha256(open("/tmp/world-check.png", "rb").read()).hexdigest()
        assert h1 == h2, "non-deterministic render!"
        print(f"OK deterministic  sha256={h1[:16]}…  {OUT}  {W}x{H}")
    else:
        print(f"wrote {OUT}  {W}x{H}")


if __name__ == "__main__":
    main()
