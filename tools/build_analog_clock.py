#!/usr/bin/env python3
"""An ASCII clock face with hands that tell the real time.

The face is drawn as text; the three hands are SVG lines rotated by SMIL, each starting at the
angle for the moment this file was rendered and then sweeping at its true rate — 360° per minute,
per hour, per twelve hours. So the clock is correct when it is fetched and stays correct for as
long as it is left open, with no JavaScript and no frame sequence.

    python3 tools/build_analog_clock.py [--out path.svg]
"""
import argparse
import math
import os
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

CANVAS_W, CANVAS_H = 680, 420
FONT = 14
CELL_W, CELL_H = 8.4, 16.8

RX, RY = 18.0, 9.0         # radius in character cells; 18*8.4 == 9*16.8, so it is a real circle
COLS, ROWS = 39, 19
CX_CELL, CY_CELL = 19, 9

X0 = (CANVAS_W - COLS * CELL_W) / 2
Y0 = (CANVAS_H - ROWS * CELL_H) / 2
CX = X0 + CX_CELL * CELL_W + CELL_W / 2
CY = Y0 + CY_CELL * CELL_H + CELL_H / 2

R = 148.0
HANDS = {"hour": (0.50 * R, 5.0), "minute": (0.74 * R, 3.4), "second": (0.86 * R, 1.5)}


def face():
    """Rim, hour ticks and the four quarter numbers, drawn in pixel space so the ring is even."""
    grid = [[" "] * COLS for _ in range(ROWS)]
    r_px = RX * CELL_W                       # the circle's radius in pixels

    for y in range(ROWS):
        for x in range(COLS):
            dx = (x - CX_CELL) * CELL_W
            dy = (y - CY_CELL) * CELL_H
            dist = math.hypot(dx, dy)
            if abs(dist - r_px) <= 4.2:
                ang = math.degrees(math.atan2(dy, dx)) % 360
                if ang < 22 or ang >= 338 or 158 <= ang < 202:
                    ch = "-"
                elif 68 <= ang < 112 or 248 <= ang < 292:
                    ch = "|"
                elif 22 <= ang < 68 or 202 <= ang < 248:
                    ch = "\\"
                else:
                    ch = "/"
                grid[y][x] = ch

    def at(angle_deg, radius_px, text):
        a = math.radians(angle_deg - 90)
        x = CX_CELL + (radius_px * math.cos(a)) / CELL_W
        y = CY_CELL + (radius_px * math.sin(a)) / CELL_H
        x = int(round(x - (len(text) - 1) / 2))
        y = int(round(y))
        for i, ch in enumerate(text):
            if 0 <= y < ROWS and 0 <= x + i < COLS:
                grid[y][x + i] = ch

    for hour in range(12):
        at(hour * 30, r_px * 0.86, "·" if hour % 3 else "+")
    for hour, text in {0: "12", 3: "3", 6: "6", 9: "9"}.items():
        at(hour * 30, r_px * 0.66, text)

    grid[CY_CELL][CX_CELL] = "o"
    return ["".join(row) for row in grid]


def build(now=None):
    if now is None:
        now = datetime.now(IST)

    seconds_into_min = now.second + now.microsecond / 1e6
    seconds_into_hour = now.minute * 60 + seconds_into_min
    seconds_into_12h = (now.hour % 12) * 3600 + seconds_into_hour

    rows = face()
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" role="img" '
        f'aria-label="analog clock, {now.strftime("%H:%M:%S")}">',
        "<style>",
        "text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,"
        f"monospace;font-size:{FONT}px;white-space:pre}}",
        ".rim{fill:#8b949e}.num{fill:#7ee787;font-weight:600}.hand{stroke-linecap:round}",
        ".hour{stroke:#7ee787;stroke-width:5}.minute{stroke:#7ee787;stroke-width:3.4}",
        ".second{stroke:#79c0ff;stroke-width:1.5}.cap{fill:#79c0ff}",
        "</style>",
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" fill="#010409"/>',
    ]

    for i, row in enumerate(rows):
        if not row.strip():
            continue
        y = Y0 + (i + 1) * CELL_H
        cls = "num" if any(c.isdigit() for c in row) and row.count("·") < 8 else "rim"
        out.append(
            f'<text x="{X0:.1f}" y="{y:.1f}" class="{cls}" xml:space="preserve">{row}</text>'
        )

    # hands: each rotates at its true rate, starting where it should be for this instant
    for name, (length, _w) in HANDS.items():
        elapsed = {"hour": seconds_into_12h, "minute": seconds_into_hour, "second": seconds_into_min}[name]
        period = {"hour": 43200, "minute": 3600, "second": 60}[name]
        out.append(
            f'<line class="hand {name}" x1="{CX:.1f}" y1="{CY:.1f}" '
            f'x2="{CX:.1f}" y2="{CY - length:.1f}">'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="0 {CX:.1f} {CY:.1f}" to="360 {CX:.1f} {CY:.1f}" '
            f'dur="{period}s" begin="-{elapsed:.2f}s" repeatCount="indefinite"/>'
            f"</line>"
        )

    out.append(f'<circle class="cap" cx="{CX:.1f}" cy="{CY:.1f}" r="4"/>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    svg = build()
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(svg)
        print(f"{a.out}: {len(svg)/1024:.1f} KB")
    else:
        print("\n".join(face()))


if __name__ == "__main__":
    main()
