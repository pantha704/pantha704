#!/usr/bin/env python3
"""Generate a calendar animation that is always the current month, with today marked.

One frame per day of the year, each a full month grid with that day bracketed. Frames run
Jan 1 -> Dec 31 and the server rotates the list so today's frame comes first when it builds the
SVG — so the animation starts on today and rolls forward instead of showing a frozen snapshot.

Every cell is exactly four characters (" 29 " or "[29]"), so no frame is wider than another and
the marking never shifts the grid.

    python3 tools/build_calendar_frames.py
"""
import calendar
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "frames", "calendar.frames.txt")

YEAR = 2026
WEEK = ["su", "mo", "tu", "we", "th", "fr", "sa"]
ROWS = 11          # fixed height so the canvas never jumps between frames


def frame(year, month, today):
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
    title = f"{calendar.month_name[month].lower()} {year}"
    lines = [
        "",
        "  " + title.center(28),
        "  " + "─" * 28,
        "  " + "".join(f"{d:>4}" for d in WEEK),
    ]
    for week in weeks:
        cells = []
        for day in week:
            if day == 0:
                cells.append("    ")
            elif day == today:
                cells.append(f"[{day:>2}]")
            else:
                cells.append(f"{day:>4}")
        lines.append(("  " + "".join(cells)).rstrip())
    while len(lines) < ROWS:
        lines.append("")
    return lines


def main():
    frames = []
    for month in range(1, 13):
        for day in range(1, calendar.monthrange(YEAR, month)[1] + 1):
            frames.append(frame(YEAR, month, day))

    body = "\n===\n".join("\n".join(f) for f in frames) + "\n"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(body)
    widths = {max(len(line) for line in f) for f in frames}
    heights = {len(f) for f in frames}
    print(f"{OUT}: {len(frames)} frames, heights {heights}, widths {widths}, {len(body)/1024:.0f} KB")


if __name__ == "__main__":
    main()
