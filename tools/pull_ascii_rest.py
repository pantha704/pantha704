#!/usr/bin/env python3
"""Pull animated pieces from ascii.rest (MIT) and write them as frame files.

ascii.rest ships each piece as a tiny procedural module — a function of time returning one frame of
text. So the only way to get frames is to run it, which this does through node.

    python3 tools/pull_ascii_rest.py campfire black-hole --frames 24
    python3 tools/pull_ascii_rest.py --list          # every piece the site advertises

Writes assets/frames/<name>.frames.txt in the same "===" separated format the rest of the pool uses.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FRAMES_DIR = os.path.join(ROOT, "assets", "frames")
BASE = "https://ascii.rest"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ascii-pool-puller/1.0)"}

NODE_HARNESS = r"""
import { pathToFileURL } from "url";
const [file, count] = [process.argv[2], parseInt(process.argv[3], 10)];
const mod = await import(pathToFileURL(file).href);
const meta = mod.meta || {};
let fn = mod.default;
const inner = fn();
const f = typeof inner === "function" ? inner : fn;
const out = [];
for (let i = 0; i < count; i++) out.push(String(f(i / (meta.fps || 30))));
process.stdout.write(JSON.stringify({ meta, frames: out }));
"""


def fetch(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")


def list_pieces():
    html = fetch(f"{BASE}/")
    names = sorted(set(re.findall(r'piece="([a-z0-9][a-z0-9-]*)"', html)))
    return names


def pull(name, count, out_dir=FRAMES_DIR):
    src = fetch(f"{BASE}/pieces/{name}.js")
    with tempfile.TemporaryDirectory() as tmp:
        mod = os.path.join(tmp, f"{name}.js")
        open(mod, "w", encoding="utf-8").write(src)
        harness = os.path.join(tmp, "h.mjs")
        open(harness, "w", encoding="utf-8").write(NODE_HARNESS)
        res = subprocess.run(
            ["node", harness, mod, str(count)], capture_output=True, text=True, timeout=120
        )
    if res.returncode != 0:
        raise RuntimeError(f"{name}: node failed — {res.stderr.strip()[:300]}")
    payload = json.loads(res.stdout)
    frames = [f.rstrip("\n").split("\n") for f in payload["frames"]]
    if not frames:
        raise RuntimeError(f"{name}: no frames")
    rows = max(len(f) for f in frames)
    frames = [f + [""] * (rows - len(f)) for f in frames]
    body = "\n===\n".join("\n".join(f) for f in frames) + "\n"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.frames.txt")
    open(path, "w", encoding="utf-8").write(body)
    meta = payload["meta"]
    cols = max(len(l) for f in frames for l in f)
    return path, meta, len(frames), rows, cols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--frames", type=int, default=24)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        names = list_pieces()
        print(f"{len(names)} pieces on ascii.rest")
        print(" ".join(names))
        return
    if not args.names:
        ap.error("give at least one piece name, or --list")

    for name in args.names:
        try:
            path, meta, n, rows, cols = pull(name, args.frames)
            print(
                f"  {name:16s} {n:3d}f  {rows:3d}x{cols:<3d} {meta.get('category','?'):10s} "
                f"{meta.get('note','')[:44]}"
            )
        except Exception as exc:  # noqa: BLE001 - report and keep going
            print(f"  {name:16s} FAILED: {exc}")


if __name__ == "__main__":
    main()
