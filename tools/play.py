#!/usr/bin/env python3
"""Play a stored ASCII loop in your terminal. No network, no dependencies.

    python3 tools/play.py                 # random animation each run
    python3 tools/play.py --name rick     # a specific one
    python3 tools/play.py --list          # what is stored
    python3 tools/play.py --fps 8         # slower
    python3 tools/play.py --once          # one pass, then exit

Keys: q quit · space pause · f faster · s slower · n next (random again)
"""
import argparse
import os
import random
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES_DIR = os.path.join(ROOT, "assets", "frames")
SEP = "==="
ESC = "\x1b"


def stored():
    if not os.path.isdir(FRAMES_DIR):
        return []
    return sorted(
        f[: -len(".frames.txt")] for f in os.listdir(FRAMES_DIR) if f.endswith(".frames.txt")
    )


def load(name):
    raw = open(os.path.join(FRAMES_DIR, f"{name}.frames.txt"), encoding="utf-8").read()
    frames = [f.strip("\n").split("\n") for f in raw.split(SEP)]
    frames = [f for f in frames if any(line.strip() for line in f)]
    if not frames:
        sys.exit(f"no frames for {name}")
    return frames


def size_of(frames):
    h = max(len(f) for f in frames)
    w = max(len(line) for f in frames for line in f)
    return w, h


def render(frame, w, h, rows, cols, name, paused, fps):
    out = [f"{ESC}[H"]
    pad_left = max(0, (cols - w) // 2)
    out.append(" " * pad_left + f"{ESC}[7m ascii.live/{name} {ESC}[0m")
    out.append("")
    for line in frame[:h]:
        out.append(" " * pad_left + line)
    for _ in range(h - len(frame)):
        out.append("")
    status = "paused" if paused else f"{fps:g} fps"
    out.append("")
    out.append(
        " " * pad_left + f"{ESC}[2mq quit · space pause · f/s speed · n next · {status}{ESC}[0m"
    )
    sys.stdout.write("\n".join(out) + f"{ESC}[J")
    sys.stdout.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--fps", type=float, default=12.9)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    names = stored()
    if args.list:
        for n in names:
            print(n)
        return
    if not names:
        sys.exit(f"no frames in {FRAMES_DIR} — run tools/capture_frames.py first")

    name = args.name if args.name else random.choice(names)
    if name not in names:
        sys.exit(f"{name} not stored; available: {', '.join(names)}")
    frames = load(name)
    w, h = size_of(frames)
    fps = args.fps

    if not sys.stdout.isatty():
        # non-interactive: emit frames so the output can be piped or diffed
        for f in frames:
            print("\n".join(f))
            print(SEP)
        return

    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    sys.stdout.write(f"{ESC}[?1049h{ESC}[?25l")  # alt screen, hide cursor
    paused = False
    try:
        tty.setcbreak(fd)
        i = 0
        while True:
            if not paused:
                cols, rows = shutil.get_terminal_size()
                render(frames[i % len(frames)], w, h, rows, cols, name, paused, fps)
                i += 1
            if sys.stdin in __import__("select").select([sys.stdin], [], [], 1.0 / fps)[0]:
                key = sys.stdin.read(1)
                if key in ("q", "Q", "\x03", "\x1b"):
                    break
                if key == " ":
                    paused = not paused
                if key == "f":
                    fps = min(60, fps * 1.25)
                if key == "s":
                    fps = max(1, fps / 1.25)
                if key == "n":
                    name = random.choice(names)
                    frames = load(name)
                    w, h = size_of(frames)
                    i = 0
            if args.once and i >= len(frames):
                break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write(f"{ESC}[?25h{ESC}[?1049l")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
