#!/usr/bin/env python3
"""Capture an ascii.live animation into a stored frame file.

    python3 tools/capture_frames.py rick parrot donut --seconds 10
    python3 tools/capture_frames.py --all --seconds 8

Writes assets/frames/<name>.frames.txt (frames separated by a line of ===).
Loop detection: the shortest repeat distance where frame 0 matches exactly.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "assets", "frames")
SEP = "==="
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
LIST_URL = "https://ascii.live/list"


def available():
    with urllib.request.urlopen(LIST_URL, timeout=15) as r:
        data = json.load(r)
    return [n for n in data.get("frames", []) if n != "frames"]


def fetch(name, seconds):
    proc = subprocess.run(
        ["curl", "-s", "--max-time", str(seconds), f"https://ascii.live/{name}"],
        capture_output=True,
    )
    return proc.stdout.decode("utf-8", "replace")


def parse(raw):
    frames = []
    for part in raw.split("\x1b[2J\x1b[H"):
        text = ANSI.sub("", part)
        lines = text.split("\n")
        # Only trailing blanks go: leading blank lines carry the art's vertical position, and
        # trimming them makes frames of different heights jump when they're played back.
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            continue
        frames.append([l.rstrip() for l in lines])
    deduped = []
    for f in frames:
        if not deduped or deduped[-1] != f:
            deduped.append(f)
    return normalise(deduped)


def normalise(frames, min_rows=5):
    """Pad every frame to the same height (bottom) and width (right), so a moving sprite stays
    where it belongs instead of sliding up as soon as a frame is shorter than its neighbours."""
    if not frames:
        return frames
    rows = max(max(len(f) for f in frames), min_rows)
    cols = max(max((len(l) for l in f), default=0) for f in frames)
    return [f + [""] * (rows - len(f)) for f in frames]


def loop_length(frames):
    if len(frames) < 6:
        return len(frames)
    sigs = ["".join(l.strip() for l in f) for f in frames]
    for L in range(4, len(frames)):
        if difflib.SequenceMatcher(None, sigs[0], sigs[L]).ratio() > 0.999:
            if all(
                difflib.SequenceMatcher(None, sigs[i], sigs[i + L]).ratio() > 0.995
                for i in range(0, min(L, len(sigs) - L), max(1, L // 4))
            ):
                return L
    return len(frames)


def capture(name, seconds=10):
    frames = parse(fetch(name, seconds))
    if not frames:
        return None
    n = loop_length(frames)
    loop = frames[:n]
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{name}.frames.txt")
    open(path, "w", encoding="utf-8").write("\n===\n".join("\n".join(f) for f in loop) + "\n")
    return n, len(loop[0]), max(len(l) for l in loop[0]), os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seconds", type=float, default=10)
    args = ap.parse_args()

    names = available() if args.all else args.names
    if not names:
        ap.error("give names or --all")
    print(f"{len(names)} to capture")
    for name in names:
        try:
            res = capture(name, args.seconds)
        except Exception as e:                                   # noqa: BLE001
            print(f"  {name:20s} FAILED {e}")
            continue
        if not res:
            print(f"  {name:20s} no frames")
            continue
        n, h, w, size = res
        print(f"  {name:20s} {n:3d} frames  {w}x{h}  {size/1024:.0f} KB")


if __name__ == "__main__":
    main()
