#!/usr/bin/env python3
"""Rotate assets/tui.svg to a random stored animation.

Run by .github/workflows/rotate-tui.yml on a schedule, or by hand:

    python3 tools/rotate_tui.py
    python3 tools/rotate_tui.py --seed 7      # deterministic, for testing
"""
import argparse
import importlib.util
import os
import random
import sys
from types import ModuleType

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILDER = os.path.join(HERE, "build_tui_svg.py")


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_tui_svg", BUILDER)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {BUILDER}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()

    mod = load_builder()
    pool = [n for n in mod.available() if mod.eligible(n)]
    if not pool:
        raise SystemExit("no eligible animations — run tools/capture_frames.py first")

    if args.seed is not None:
        random.seed(args.seed)
    choice = random.choice(pool)
    mod.write(choice, os.path.join(ROOT, "assets", "tui.svg"))
    print(f"rotated to: {choice} (pool of {len(pool)}: {', '.join(pool)})")


if __name__ == "__main__":
    main()
