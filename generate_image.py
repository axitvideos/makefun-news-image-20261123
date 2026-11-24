#!/usr/bin/env python3
"""Draw the front page of 23 November 2026 in one 1024x1024 PNG.

Layout, in my own words: a newspaper masthead up top, the date line
under it, then six story cards in two columns and three rows. Every
card has a small flat-colour picture strip, a coloured section label,
a bold headline and a two-line summary. Nothing is read from disk
except the DejaVu fonts that ship with the system; the picture is
fully deterministic, so running this twice gives identical bytes.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 28
GAP = 14

PAPER = (250, 244, 231)
INK = (26, 26, 26)
SOFT_INK = (74, 74, 74)
RULE = (26, 26, 26)
CARD_LINE = (196, 186, 168)
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_BOLD = lambda s: load_font("DejaVuSerif-Bold.ttf", s)
SANS_BOLD = lambda s: load_font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: load_font("DejaVuSans.ttf", s)


def draw_tag(draw, x, y, text, fill, chip=None):
    """A short label; with chip, a solid rounded block sits behind it."""
    font = SANS_BOLD(20)
    if chip is not None:
        tw = draw.textlength(text, font=font)
        draw.rounded_rectangle([x - 6, y - 3, x + tw + 8, y + 27],
                               radius=4, fill=chip)
    draw.text((x, y), text, font=font, fill=fill)


def wrap(draw, text, font, width):
    """Split text into lines that fit inside width pixels."""
    """Split text into lines that fit inside width pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        current = ""
        for word in words:
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=font) <= width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def fit_lines(draw, text, width, start_size, min_size, max_lines):
    """Largest font size (bold) that wraps the text into max_lines."""
    size = start_size
    while size > min_size:
        font = SANS_BOLD(size)
        lines = wrap(draw, text, font, width)
        if len(lines) <= max_lines:
            return font, lines
        size -= 2
    return SANS_BOLD(min_size), wrap(draw, text, SANS_BOLD(min_size), width)


# ---------------------------------------------------------------- pictures
# Each painter draws one flat-colour strip inside (x0, y0, x1, y1).

def paint_tankers(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(16, 28, 52))
    sea_y = y0 + (y1 - y0) * 2 // 3
    draw.rectangle([x0, sea_y, x1, y1], fill=(24, 52, 84))
    for cx in range(x0 + 14, x1 - 10, 26):
        draw.ellipse([cx, sea_y + 12, cx + 9, sea_y + 17], fill=(120, 160, 200))
    hulls = [(x0 + 12, 120), (x0 + 160, 150), (x0 + 340, 120)]
    for hx, hw in hulls:
        draw.rectangle([hx, sea_y - 14, hx + hw, sea_y + 8], fill=(122, 122, 116))
        draw.rectangle([hx + hw // 3, sea_y - 30, hx + hw // 3 + 34, sea_y - 14],
                       fill=(96, 96, 92))
    # flames on the middle tanker
    fx = x0 + 160 + 150 // 2
    draw.polygon([(fx - 26, sea_y - 12), (fx, sea_y - 52), (fx + 26, sea_y - 12)],
                 fill=(255, 122, 26))
    draw.polygon([(fx - 13, sea_y - 12), (fx, sea_y - 38), (fx + 13, sea_y - 12)],
                 fill=(255, 214, 64))
    draw.ellipse([fx - 34, sea_y - 66, fx - 6, sea_y - 44], fill=(120, 120, 118))
    draw.ellipse([fx - 8, sea_y - 74, fx + 22, sea_y - 50], fill=(140, 140, 138))
    draw.text((x0 + 12, y0 + 8), "3 TANKERS HIT", font=SANS_BOLD(20),
              fill=WHITE)


def paint_warship(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(10, 34, 48))
    sea_y = y0 + (y1 - y0) * 3 // 5
    draw.rectangle([x0, sea_y, x1, y1], fill=(18, 58, 74))
    # frigate silhouette
    draw.polygon([(x0 + 90, sea_y - 6), (x0 + 400, sea_y - 6),
                  (x0 + 372, sea_y + 22), (x0 + 118, sea_y + 22)],
                 fill=(88, 92, 96))
    draw.rectangle([x0 + 210, sea_y - 34, x0 + 300, sea_y - 6], fill=(70, 74, 78))
    draw.rectangle([x0 + 250, sea_y - 58, x0 + 258, sea_y - 34], fill=(70, 74, 78))
    # explosion at the bow
    bx, by = x0 + 96, sea_y - 14
    draw.polygon([(bx - 26, by + 8), (bx - 6, by - 26), (bx + 8, by - 2),
                  (bx + 26, by - 22), (bx + 14, by + 8)], fill=(255, 170, 30))
    draw.polygon([(bx - 12, by + 8), (bx, by - 14), (bx + 12, by + 8)],
                 fill=(255, 226, 110))
    # drones overhead
    for dx, dy in [(x0 + 130, y0 + 16), (x0 + 200, y0 + 30), (x0 + 330, y0 + 14)]:
        draw.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(235, 235, 235))
    draw.text((x1 - 132, y0 + 8), "BENGHAZI", font=SANS_BOLD(20), fill=WHITE)


def paint_kyiv(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(214, 206, 192))
    base = y1 - 8
    draw.rectangle([x0 + 22, base - 46, x0 + 118, base], fill=(104, 110, 122))
    draw.rectangle([x0 + 138, base - 66, x0 + 236, base], fill=(88, 94, 106))
    # broken tower with a slanted, sheared-off top
    draw.polygon([(x0 + 258, base), (x0 + 258, base - 78), (x0 + 356, base - 96),
                  (x0 + 356, base)], fill=(70, 76, 88))
    for wx in (x0 + 40, x0 + 72, x0 + 156, x0 + 188, x0 + 280, x0 + 316):
        draw.rectangle([wx, base - 34, wx + 14, base - 20], fill=(38, 44, 58))
    draw.ellipse([x0 + 380, y0 + 12, x0 + 404, y0 + 36], fill=(150, 148, 142))
    draw.ellipse([x0 + 398, y0 + 22, x0 + 428, y0 + 52], fill=(168, 166, 160))
    draw_tag(draw, x0 + 12, y0 + 8, "12 DEAD", WHITE, chip=(178, 32, 28))


def paint_climate(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(14, 96, 92))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = 34
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(146, 196, 178))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(230, 240, 236), width=3)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 200, 340,
             fill=(230, 240, 236), width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=(230, 240, 236), width=2)
    draw.line([cx - r + 8, cy - r + 6, cx + r - 8, cy + r - 6],
              fill=(206, 52, 44), width=6)
    draw.line([cx - r + 8, cy + r - 6, cx + r - 8, cy - r + 6],
              fill=(206, 52, 44), width=6)
    draw.text((x1 - 118, y0 + 8), "NO DEAL", font=SANS_BOLD(20), fill=WHITE)


def paint_mountains(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(238, 226, 200))
    draw.ellipse([x1 - 92, y0 + 10, x1 - 48, y0 + 54], fill=(232, 158, 62))
    draw.polygon([(x0 + 10, y1), (x0 + 150, y0 + 22), (x0 + 290, y1)],
                 fill=(84, 106, 132))
    draw.polygon([(x0 + 130, y0 + 34), (x0 + 150, y0 + 22), (x0 + 170, y0 + 34),
                  (x0 + 158, y0 + 42), (x0 + 142, y0 + 42)], fill=WHITE)
    draw.polygon([(x0 + 190, y1), (x0 + 330, y0 + 30), (x0 + 470, y1)],
                 fill=(62, 82, 106))
    draw.polygon([(x0 + 312, y0 + 40), (x0 + 330, y0 + 30), (x0 + 348, y0 + 40),
                  (x0 + 338, y0 + 48), (x0 + 322, y0 + 48)], fill=WHITE)
    draw.text((x0 + 12, y0 + 8), "$1.62BN AID", font=SANS_BOLD(20),
              fill=(146, 106, 20))


def paint_factory(draw, x0, y0, x1, y1):
    draw.rectangle([x0, y0, x1, y1], fill=(240, 222, 178))
    base = y1 - 6
    draw.rectangle([x0 + 24, base - 52, x0 + 330, base], fill=(122, 92, 52))
    for i in range(4):
        sx = x0 + 24 + i * 78
        draw.polygon([(sx, base - 52), (sx + 39, base - 78), (sx + 78, base - 52)],
                     fill=(92, 66, 34))
    draw.rectangle([x0 + 360, base - 84, x0 + 384, base], fill=(74, 54, 30))
    draw.ellipse([x0 + 392, y0 + 6, x0 + 420, y0 + 30], fill=(150, 146, 140))
    draw.ellipse([x0 + 412, y0 + 18, x0 + 444, y0 + 46], fill=(168, 164, 158))
    for fx in (x0 + 63, x0 + 141, x0 + 219, x0 + 297):
        draw.polygon([(fx - 10, base - 52), (fx, base - 72), (fx + 10, base - 52)],
                     fill=(255, 122, 26))
    draw_tag(draw, x0 + 12, y0 + 8, "24 DEAD", WHITE, chip=(178, 32, 28))


PAINTERS = {
    "tankers": paint_tankers,
    "warship": paint_warship,
    "kyiv": paint_kyiv,
    "climate": paint_climate,
    "mountains": paint_mountains,
    "factory": paint_factory,
}

STORIES = [
    dict(picture="tankers", accent=(178, 32, 28),
         kicker="THE GULF  ·  STRAIT OF HORMUZ",
         headline="THREE TANKERS ABLAZE IN HORMUZ",
         deck="Iran's Guard says mines set three oil tankers ablaze as the "
              "US oil blockade hits day 130."),
    dict(picture="warship", accent=(30, 44, 84),
         kicker="LIBYA  ·  BENGHAZI",
         headline="UKRAINE SINKS RUSSIAN WARSHIP",
         deck="Zelensky confirms naval drones struck the Russian corvette "
              "Mercury off Benghazi."),
    dict(picture="kyiv", accent=(30, 44, 84),
         kicker="UKRAINE  ·  KYIV REGION",
         headline="KYIV TOLL RISES TO 12",
         deck="Russian strikes kill 12 across the Kyiv region; a 79-year-old "
              "is pulled alive from rubble."),
    dict(picture="climate", accent=(14, 96, 92),
         kicker="CLIMATE  ·  AFTER COP31",
         headline="WHAT NEXT AFTER THE COLLAPSE",
         deck="The longest UN climate summit ends with no deal; calls grow "
              "to reform the talks."),
    dict(picture="mountains", accent=(146, 106, 20),
         kicker="SOUTH ASIA  ·  NEPAL AID",
         headline="INDIA GIVES NEPAL $1.62BN",
         deck="Modi announces a flood-recovery package for Nepal after talks "
              "with PM Shah in New Delhi."),
    dict(picture="factory", accent=(178, 32, 28),
         kicker="INDONESIA  ·  CIKANDE",
         headline="FACTORY FIRE: 24 DEAD, 30 MISSING",
         deck="The toll reaches 24 at the burned candy factory in Cikande; "
              "dozens are still missing."),
]


def draw_masthead(draw):
    title = "THE WORLD TODAY"
    font = SERIF_BOLD(62)
    tw = draw.textlength(title, font=font)
    draw.text(((PAGE - tw) / 2, 16), title, font=font, fill=INK)
    draw.line([MARGIN, 96, PAGE - MARGIN, 96], fill=RULE, width=3)
    date_font = SANS_BOLD(24)
    date_text = "MONDAY, 23 NOVEMBER 2026  ·  SIX STORIES, ONE DAY"
    dw = draw.textlength(date_text, font=date_font)
    draw.text(((PAGE - dw) / 2, 106), date_text, font=date_font, fill=INK)
    draw.line([MARGIN, 140, PAGE - MARGIN, 140], fill=RULE, width=3)


def draw_card(draw, story, x0, y0, width, height):
    x1, y1 = x0 + width, y0 + height
    draw.rectangle([x0, y0, x1, y1], outline=CARD_LINE, width=2)
    pic_h = 92
    PAINTERS[story["picture"]](draw, x0 + 2, y0 + 2, x1 - 2, y0 + pic_h)
    text_x = x0 + 14
    text_w = width - 28
    kicker_font = SANS_BOLD(17)
    draw.text((text_x, y0 + pic_h + 12), story["kicker"],
              font=kicker_font, fill=story["accent"])
    head_font, head_lines = fit_lines(draw, story["headline"], text_w,
                                      start_size=30, min_size=23, max_lines=2)
    hy = y0 + pic_h + 38
    for line in head_lines:
        draw.text((text_x, hy), line, font=head_font, fill=INK)
        hy += head_font.size + 4
    deck_font = SANS(19)
    deck_lines = wrap(draw, story["deck"], deck_font, text_w)
    if len(deck_lines) > 2:  # shrink one step rather than ever cutting words
        deck_font = SANS(17)
        deck_lines = wrap(draw, story["deck"], deck_font, text_w)[:2]
    else:
        deck_lines = deck_lines[:2]
    dy = hy + 6
    for line in deck_lines:
        draw.text((text_x, dy), line, font=deck_font, fill=SOFT_INK)
        dy += 23 if deck_font.size == 17 else 24


def draw_footer(draw):
    note = ("Sources: AP · Reuters · BBC · Just Security · BusinessWorld  —  "
            "All six stories happened or were first reported on 23 November 2026.")
    font = SANS(15)
    draw.text((MARGIN, 988), note, font=font, fill=SOFT_INK)


def build(out_path):
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    grid_top = 154
    grid_bottom = 976
    col_w = (PAGE - 2 * MARGIN - GAP) // 2
    row_h = (grid_bottom - grid_top - 2 * GAP) // 3
    for i, story in enumerate(STORIES):
        row, col = divmod(i, 2)
        x0 = MARGIN + col * (col_w + GAP)
        y0 = grid_top + row * (row_h + GAP)
        draw_card(draw, story, x0, y0, col_w, row_h)
    draw_footer(draw)
    img.save(out_path, format="PNG", optimize=True)


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    here = os.path.dirname(os.path.abspath(__file__))
    if not os.path.isabs(out_path):
        out_path = os.path.join(here, out_path)
    build(out_path)
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({size} bytes)")


if __name__ == "__main__":
    main()
