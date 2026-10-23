#!/usr/bin/env python3
"""Build docs/index.html — ONE self-contained file.

Everything the page needs is baked in at build time: the numbers parsed out of the README's
`<!--stats:start-->` marker and a set of ASCII animations read from assets/frames/. The result
makes no network requests at all, so it works on GitHub Pages, on any static host, and by
double-clicking the file from disk.

    python3 tools/build_site.py
    python3 tools/build_site.py --max-frames-bytes 20000 --out /tmp/terminal.html
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
README = os.path.join(ROOT, "README.md")
TEMPLATE = os.path.join(HERE, "site_template.html")
FRAMES_DIR = os.path.join(ROOT, "assets", "frames")
OUT = os.path.join(ROOT, "docs", "index.html")

# The page is a single file, so every extra animation costs bytes on every load. Anything above
# this threshold is still available in assets/frames and through the animated SVG hero.
DEFAULT_MAX_FRAME_BYTES = 40_000


def read_numbers():
    text = open(README, encoding="utf-8").read()
    block = re.search(r"<!--stats:start-->(.*?)<!--stats:end-->", text, re.S)
    if not block:
        raise SystemExit("README is missing the <!--stats:start-->…<!--stats:end--> marker")
    m = re.search(r"(\d+)\s+merged\s+·\s+(\d+)\s+repos\s+·\s+(\d+)\s+open", block.group(1))
    if not m:
        raise SystemExit(f"could not parse numbers from the stats marker: {block.group(1)!r}")
    checked = re.search(r"checked\s+([^<]+?)\s*$", block.group(1))
    return {
        "merged": int(m.group(1)),
        "repos": int(m.group(2)),
        "open": int(m.group(3)),
        "checked": checked.group(1) if checked else "",
    }


def read_frames(max_bytes):
    frames, skipped = {}, []
    for name in sorted(os.listdir(FRAMES_DIR)):
        if not name.endswith(".frames.txt"):
            continue
        path = os.path.join(FRAMES_DIR, name)
        size = os.path.getsize(path)
        if size > max_bytes:
            skipped.append((name.split(".")[0], size))
            continue
        frames[name[: -len(".frames.txt")]] = open(path, encoding="utf-8").read()
    return frames, skipped


def build(max_frame_bytes=DEFAULT_MAX_FRAME_BYTES, out=OUT):
    numbers = read_numbers()
    frames, skipped = read_frames(max_frame_bytes)
    if not frames:
        raise SystemExit(f"no frames under {max_frame_bytes} bytes — raise --max-frames-bytes")

    data = dict(numbers, frames=frames)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # a literal </script> inside the payload would close the tag early
    payload = payload.replace("</", "<\\/")

    template = open(TEMPLATE, encoding="utf-8").read()
    if template.count("__DATA__") != 1:
        raise SystemExit(f"template must contain exactly one __DATA__ placeholder, found {template.count('__DATA__')}")
    html = template.replace("__DATA__", payload)

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out, len(html), numbers, sorted(frames), skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-frames-bytes", type=int, default=DEFAULT_MAX_FRAME_BYTES)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    out, size, numbers, names, skipped = build(args.max_frames_bytes, args.out)
    print(f"{out}: {size/1024:.1f} KB, self-contained (0 fetches)")
    print(f"numbers baked: {numbers['merged']} merged / {numbers['repos']} repos / {numbers['open']} open"
          f"{' · checked ' + numbers['checked'] if numbers['checked'] else ''}")
    print(f"animations baked: {len(names)} — {', '.join(names)}")
    if skipped:
        print(f"left out (over {args.max_frames_bytes/1024:.0f} KB): "
              + ", ".join(f"{n} {s/1024:.0f}KB" for n, s in skipped))


if __name__ == "__main__":
    main()
