#!/usr/bin/env python3
"""Build assets/tui.svg — a terminal window that plays the stored ASCII loop.

Frames come from assets/rick.frames.txt (no network at build or view time).
Animation is CSS keyframes, one rule, negative per-frame delay; GitHub serves
SVGs as images, where CSS animation runs and scripts do not.

    python3 tools/build_tui_svg.py
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES_FILE = os.path.join(ROOT, "assets", "rick.frames.txt")
OUT_FILE = os.path.join(ROOT, "assets", "tui.svg")
SEP = "==="

FONT = 12
CELL_W = 7.2          # advance width of the monospace cell at FONT px
LINE_H = 14
PAD = 16
CHROME_H = 30
PROMPT_H = 22
BG = "#0d1117"
FG = "#7ee787"
DIM = "#8b949e"
FRAME_BG = "#010409"


def load(path):
    raw = open(path, encoding="utf-8").read()
    return [f.strip("\n").split("\n") for f in raw.split(SEP) if f.strip()]


def build(frames, fps=12.9):
    w = max(len(l) for f in frames for l in f)
    h = max(len(f) for f in frames)
    art_w, art_h = w * CELL_W, h * LINE_H
    width = art_w + PAD * 2
    height = art_h + CHROME_H + PROMPT_H + PAD * 2
    period = len(frames) / fps
    step = 100.0 / len(frames)

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" '
        f'aria-label="Terminal playing an ASCII animation of Rick Astley, {len(frames)} frames, stored locally">'
    )
    out.append(
        "<style>"
        f".f{{opacity:0;animation:blink {period:.3f}s steps(1,end) infinite}}"
        f".f:first-of-type{{opacity:1}}"
        f"@media (prefers-reduced-motion: reduce){{.f{{animation:none}}.f:first-of-type{{opacity:1}}}}"
        f"@keyframes blink{{0%{{opacity:1}}{step:.3f}%{{opacity:0}}100%{{opacity:0}}}}"
        "text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,monospace;"
        f"font-size:{FONT}px;white-space:pre}}"
        "</style>"
    )
    # window
    out.append(f'<rect width="{width:.0f}" height="{height:.0f}" rx="10" fill="{BG}"/>')
    out.append(f'<rect x="0.5" y="0.5" width="{width-1:.0f}" height="{height-1:.0f}" rx="10" fill="none" stroke="#30363d"/>')
    # title bar
    out.append(f'<rect width="{width:.0f}" height="{CHROME_H}" rx="10" fill="#161b22"/>')
    out.append(f'<rect y="{CHROME_H-10}" width="{width:.0f}" height="10" fill="#161b22"/>')
    for i, colour in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        out.append(f'<circle cx="{PAD + i*16}" cy="{CHROME_H/2}" r="5" fill="{colour}"/>')
    out.append(
        f'<text x="{width/2:.0f}" y="{CHROME_H/2 + 4:.0f}" fill="{DIM}" text-anchor="middle" font-size="11">'
        f'rick.frames.txt — {len(frames)} frames — played locally, no network</text>'
    )
    # prompt
    py = CHROME_H + PAD + 2
    out.append(f'<text x="{PAD}" y="{py:.0f}" fill="{FG}">$ curl ascii.live/rick</text>')
    # art
    top = CHROME_H + PROMPT_H + PAD
    out.append(f'<rect x="{PAD-4}" y="{top-4}" width="{art_w+8:.0f}" height="{art_h+8:.0f}" rx="6" fill="{FRAME_BG}"/>')
    for idx, frame in enumerate(frames):
        delay = -(idx * period / len(frames))
        out.append(f'<g class="f" style="animation-delay:{delay:.4f}s">')
        out.append(f'<text x="{PAD}" y="{top + LINE_H - 3:.0f}" fill="{FG}" xml:space="preserve">')
        for row, line in enumerate(frame):
            dy = 0 if row == 0 else LINE_H
            out.append(f'<tspan x="{PAD}" dy="{dy}">{html.escape(line) or " "}</tspan>')
        out.append("</text></g>")
    out.append("</svg>")
    return "\n".join(out), len(frames), period, width, height


def main():
    frames = load(FRAMES_FILE)
    svg, n, period, w, h = build(frames)
    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    open(OUT_FILE, "w", encoding="utf-8").write(svg)
    print(f"{OUT_FILE}: {n} frames, {period:.2f}s loop, {w:.0f}x{h:.0f}, {len(svg)/1024:.1f} KB")


if __name__ == "__main__":
    main()
