#!/usr/bin/env python3
"""Build the green terminal-style link chips: assets/links/<name>.svg

GitHub owns the colour of anchor text — a README can't style <a> — so a green *link* has to be an
image wrapped in a link. These chips use the same palette and font as the hero, which keeps the top
row of the profile looking like part of the terminal.

    python3 tools/build_link_chips.py
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "links")

FONT = 13
CHAR_W = 7.85           # advance of the monospace cell at FONT px
PAD_X = 12
H = 28
BG = "#161b22"
BORDER = "#30363d"
FG = "#7ee787"

CHIPS = ["resume", "mail", "x"]


def chip(label):
    w = round(len(label) * CHAR_W + PAD_X * 2)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" '
        f'viewBox="0 0 {w} {H}" role="img" aria-label="{html.escape(label)}">'
        "<style>"
        "text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,"
        f"monospace;font-size:{FONT}px}}"
        "</style>"
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{H-1}" rx="6" fill="{BG}" '
        f'stroke="{BORDER}"/>'
        f'<text x="{w/2:.1f}" y="{H/2 + 4.5:.1f}" fill="{FG}" text-anchor="middle">'
        f"{html.escape(label)}</text>"
        "</svg>"
    )


def main():
    os.makedirs(OUT, exist_ok=True)
    for label in CHIPS:
        path = os.path.join(OUT, f"{label}.svg")
        svg = chip(label)
        open(path, "w", encoding="utf-8").write(svg)
        print(f"{path}: {len(svg)} bytes")


if __name__ == "__main__":
    main()
