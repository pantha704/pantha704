#!/usr/bin/env python3
"""Build terminal-window SVGs from stored frame files. No network.

    python3 tools/build_tui_svg.py --name rick          # -> assets/tui.svg
    python3 tools/build_tui_svg.py --random             # random animation -> assets/tui.svg
    python3 tools/build_tui_svg.py --all                # every eligible animation -> assets/animations/
    python3 tools/build_tui_svg.py --name nyan --out /tmp/nyan.svg

Animation is CSS keyframes with a negative per-frame delay. The first frame carries a static
opacity so renderers that ignore CSS animation still show a picture instead of an empty box.
"""
import argparse
import html
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES_DIR = os.path.join(ROOT, "assets", "frames")
DEFAULT_OUT = os.path.join(ROOT, "assets", "tui.svg")
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

MAX_COLS = 100        # keep the README image sane
MAX_ROWS = 60
MAX_FRAMES = 130


def frames_path(name):
    return os.path.join(FRAMES_DIR, f"{name}.frames.txt")


def available():
    if not os.path.isdir(FRAMES_DIR):
        return []
    return sorted(
        f[: -len(".frames.txt")] for f in os.listdir(FRAMES_DIR) if f.endswith(".frames.txt")
    )


def load(name):
    raw = open(frames_path(name), encoding="utf-8").read()
    return [f.strip("\n").split("\n") for f in raw.split(SEP) if f.strip()]


def eligible(name):
    try:
        frames = load(name)
    except OSError:
        return False
    cols = max(len(l) for f in frames for l in f)
    rows = max(len(f) for f in frames)
    return cols <= MAX_COLS and rows <= MAX_ROWS and len(frames) <= MAX_FRAMES


def build(name, frames, fps=12.9):
    cols = max(len(l) for f in frames for l in f)
    rows = max(len(f) for f in frames)
    art_w, art_h = cols * CELL_W, rows * LINE_H
    width = art_w + PAD * 2
    height = art_h + CHROME_H + PROMPT_H + PAD * 2
    period = len(frames) / fps
    step = 100.0 / len(frames)

    o = []
    o.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}" role="img" '
        f'aria-label="Terminal playing an ASCII animation of {html.escape(name)}">'
    )
    o.append(
        "<style>"
        f".f{{opacity:0;animation:blink {period:.3f}s steps(1,end) infinite}}"
        f".f:first-of-type{{opacity:1}}"
        f"@keyframes blink{{0%{{opacity:1}}{step:.3f}%{{opacity:0}}100%{{opacity:0}}}}"
        "@media (prefers-reduced-motion: reduce){.f{animation:none}.f:first-of-type{opacity:1}}"
        "text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,monospace;"
        f"font-size:{FONT}px;white-space:pre}}"
        "</style>"
    )
    o.append(f'<rect width="{width:.0f}" height="{height:.0f}" rx="10" fill="{BG}"/>')
    o.append(
        f'<rect x="0.5" y="0.5" width="{width-1:.0f}" height="{height-1:.0f}" rx="10" '
        f'fill="none" stroke="#30363d"/>'
    )
    o.append(f'<rect width="{width:.0f}" height="{CHROME_H}" rx="10" fill="#161b22"/>')
    o.append(f'<rect y="{CHROME_H-10}" width="{width:.0f}" height="10" fill="#161b22"/>')
    for i, colour in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{PAD + i*16}" cy="{CHROME_H/2}" r="5" fill="{colour}"/>')
    o.append(
        f'<text x="{width/2:.0f}" y="{CHROME_H/2 + 4:.0f}" fill="{DIM}" text-anchor="middle" '
        f'font-size="11">ascii.live/{html.escape(name)}</text>'
    )
    o.append(
        f'<text x="{PAD}" y="{CHROME_H + PAD + 2:.0f}" fill="{FG}">'
        f'$ curl ascii.live/{html.escape(name)}</text>'
    )
    top = CHROME_H + PROMPT_H + PAD
    o.append(
        f'<rect x="{PAD-4}" y="{top-4}" width="{art_w+8:.0f}" height="{art_h+8:.0f}" rx="6" '
        f'fill="{FRAME_BG}"/>'
    )
    for idx, frame in enumerate(frames):
        delay = -(idx * period / len(frames))
        o.append(f'<g class="f" style="animation-delay:{delay:.4f}s">')
        o.append(f'<text x="{PAD}" y="{top + LINE_H - 3:.0f}" fill="{FG}" xml:space="preserve">')
        for row, line in enumerate(frame):
            dy = 0 if row == 0 else LINE_H
            o.append(f'<tspan x="{PAD}" dy="{dy}">{html.escape(line) or " "}</tspan>')
        o.append("</text></g>")
    o.append("</svg>")
    return "\n".join(o), cols, rows, period


def write(name, out):
    frames = load(name)
    svg, cols, rows, period = build(name, frames)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(svg)
    print(
        f"{out}: {name} | {len(frames)} frames | {period:.2f}s | {cols}x{rows} | "
        f"{len(svg)/1024:.0f} KB"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--random", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()

    pool = [n for n in available() if eligible(n)]
    if not pool:
        raise SystemExit(f"no eligible frames in {FRAMES_DIR} — run tools/capture_frames.py first")

    if args.all:
        out_dir = os.path.join(ROOT, "assets", "animations")
        for n in pool:
            write(n, os.path.join(out_dir, f"{n}.svg"))
        print(f"{len(pool)} animations -> {out_dir}")
        return

    if args.random:
        if args.seed is not None:
            random.seed(args.seed)
        name = random.choice(pool)
    elif args.name:
        name = args.name
        if name not in pool:
            raise SystemExit(f"{name} not eligible or not captured; pool: {', '.join(pool)}")
    else:
        raise SystemExit("pass --name, --random or --all")

    write(name, args.out)


if __name__ == "__main__":
    main()
