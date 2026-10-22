#!/usr/bin/env python3
"""Refresh the live numbers in the profile: hero SVGs + the README footer line.

Run daily by .github/workflows/refresh-stats.yml, or by hand:

    python3 tools/refresh_stats.py
    python3 tools/refresh_stats.py --dry-run      # show what would change

Numbers come straight from the GitHub API (merged PRs into repositories this account does
not own, plus open PRs), so the README cannot claim anything the API will not confirm.
"""
import argparse
import datetime
import importlib.util
import os
import re
import sys
from types import ModuleType

try:
    from zoneinfo import ZoneInfo

    IST = ZoneInfo("Asia/Kolkata")
except Exception:                                  # no tzdata on the runner
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
README = os.path.join(ROOT, "README.md")
BUILDER = os.path.join(HERE, "build_hero_svg.py")

START = "<!--stats:start-->"
END = "<!--stats:end-->"
UPSTREAM_START = "<!--upstream:start-->"
UPSTREAM_END = "<!--upstream:end-->"


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_hero_svg", BUILDER)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load {BUILDER}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--include-private",
        action="store_true",
        help="count merges into private repositories too (résumé numbers, not the public README)",
    )
    args = ap.parse_args()

    builder = load_builder()
    merged, repos = builder.count("merged", args.include_private)
    opened, _ = builder.count("open", args.include_private)

    stamp = datetime.datetime.now(IST).strftime("%d %b %Y")
    footer = f"{START}<code>{merged} merged · {repos} repos · {opened} open · checked {stamp}</code>{END}"
    summary = f"{UPSTREAM_START}{merged} merged · {repos} repositories · {opened} open{UPSTREAM_END}"

    text = open(README, encoding="utf-8").read()
    blocks = [
        (START, END, footer, "footer"),
        (UPSTREAM_START, UPSTREAM_END, summary, "upstream summary"),
    ]
    for a, b, _, label in blocks:
        if a not in text or b not in text:
            raise SystemExit(f"README has no {a} … {b} block to update ({label})")

    updated = text
    for a, b, replacement, _ in blocks:
        updated = re.compile(re.escape(a) + r".*?" + re.escape(b), re.S).sub(
            lambda _m, r=replacement: r, updated
        )
    changed = updated != text

    if args.dry_run:
        print(f"numbers : {merged} merged / {repos} repos / {opened} open")
        print(f"footer  : {footer}")
        print(f"summary : {summary}")
        print(f"README  : {'would change' if changed else 'already current'}")
        return

    for name, theme in (("hero-dark.svg", builder.DARK), ("hero-light.svg", builder.LIGHT)):
        path = os.path.join(ROOT, "assets", name)
        open(path, "w", encoding="utf-8").write(builder.build(theme, merged, repos, opened))
        print(f"rebuilt {path}")

    if changed:
        open(README, "w", encoding="utf-8").write(updated)
        print(f"README -> {merged} merged · {repos} repositories · {opened} open · checked {stamp}")
    else:
        print("README already current")


if __name__ == "__main__":
    main()
