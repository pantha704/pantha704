#!/usr/bin/env python3
"""Build the profile dashboard hero: assets/hero-dark.svg + assets/hero-light.svg.

Numbers are queried live from the GitHub API unless overridden, so the hero cannot drift
from reality. Regenerate with:

    python3 tools/build_hero_svg.py
    python3 tools/build_hero_svg.py --merged 22 --repos 13 --open 15

READMEs reference these through <picture> + prefers-color-scheme, so the hero follows the
reader's theme instead of fighting it.
"""
import argparse
import html
import json
import os
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGIN = "pantha704"

W, H = 920, 402
CHROME = 34
STATUS = 28
SIDEBAR = 210

DARK = {
    "bg": "#0d1117", "panel": "#161b22", "side": "#0f141b", "line": "#30363d",
    "fg": "#c9d1d9", "dim": "#8b949e", "green": "#7ee787", "cyan": "#79c0ff",
    "yellow": "#e3b341", "status_bg": "#161b22", "sel": "#1f6feb33",
}
LIGHT = {
    "bg": "#ffffff", "panel": "#f6f8fa", "side": "#f0f3f6", "line": "#d0d7de",
    "fg": "#24292f", "dim": "#57606a", "green": "#1a7f37", "cyan": "#0969da",
    "yellow": "#9a6700", "status_bg": "#f6f8fa", "sel": "#0969da22",
}


def _token():
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(key):
            return os.environ[key]
    r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return r.stdout.strip()


def gh_json(path):
    """GitHub API via plain HTTP so the same code runs locally and inside Actions."""
    req = urllib.request.Request(
        f"https://api.github.com/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {_token()}",
            "User-Agent": "profile-readme-stats",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def count(state):
    total, repos, page = 0, set(), 1
    while True:
        d = gh_json(
            f"search/issues?q=author:{LOGIN}+type:pr+is:{state}&per_page=100&page={page}"
        )
        items = d.get("items", [])
        for it in items:
            repo = it["repository_url"].replace("https://api.github.com/repos/", "")
            if not repo.startswith(f"{LOGIN}/"):
                total += 1
                repos.add(repo)
        if len(items) < 100:
            return total, len(repos)
        page += 1


def rows(merged, repos, opened):
    return [
        ("role", "systems & automation engineer", "green"),
        ("now", "automation + vulnerability reporting @ braid-forbes", "fg"),
        ("upstream", f"{merged} merged pull requests across {repos} repositories", "cyan"),
        ("in flight", f"{opened} pull requests open", "fg"),
        ("stack", "rust · typescript · python · go · postgres · docker", "fg"),
        ("status", "open to systems, devtools and infrastructure work", "yellow"),
    ]


def build(theme, merged, repos, opened):
    c = theme
    o = []
    o.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="pratham jaiswal — {merged} merged pull requests across {repos} '
        f'upstream repositories">'
    )
    o.append(
        "<style>text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,"
        "monospace;font-size:13px;white-space:pre}</style>"
    )
    o.append(f'<rect width="{W}" height="{H}" rx="12" fill="{c["bg"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{c["line"]}"/>')
    # chrome
    o.append(f'<path d="M0 12a12 12 0 0 1 12-12h{W-24}a12 12 0 0 1 12 12v{CHROME-12}H0z" fill="{c["panel"]}"/>')
    for i, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{20 + i*18}" cy="{CHROME/2}" r="5.5" fill="{col}"/>')
    o.append(
        f'<text x="{W/2}" y="{CHROME/2 + 4}" fill="{c["dim"]}" text-anchor="middle" font-size="12">'
        f'pratham@kolkata — ~/profile</text>'
    )
    o.append(f'<line x1="0" y1="{CHROME}" x2="{W}" y2="{CHROME}" stroke="{c["line"]}"/>')
    # sidebar
    o.append(f'<rect y="{CHROME}" width="{SIDEBAR}" height="{H-CHROME-STATUS}" fill="{c["side"]}"/>')
    o.append(f'<line x1="{SIDEBAR}" y1="{CHROME}" x2="{SIDEBAR}" y2="{H-STATUS}" stroke="{c["line"]}"/>')
    tree = [
        ("~/profile", "dim", False),
        ("|- README.md", "green", True),
        ("|- upstream/", "fg", False),
        ("|- projects/", "fg", False),
        ("|- stack.md", "fg", False),
        ("`- contact.md", "fg", False),
    ]
    y = CHROME + 28
    for label, colour, active in tree:
        if active:
            o.append(f'<rect x="8" y="{y-14}" width="{SIDEBAR-16}" height="20" rx="4" fill="{c["sel"]}"/>')
        o.append(f'<text x="16" y="{y}" fill="{c[colour]}">{html.escape(label)}</text>')
        y += 22
    # main pane
    x = SIDEBAR + 26
    y = CHROME + 34
    o.append(f'<text x="{x}" y="{y}" fill="{c["cyan"]}" font-size="15">pratham@kolkata</text>')
    y += 12
    o.append(f'<text x="{x}" y="{y}" fill="{c["line"]}">{"-" * 46}</text>')
    y += 26
    for key, value, colour in rows(merged, repos, opened):
        o.append(f'<text x="{x}" y="{y}" fill="{c["dim"]}">{html.escape(key):<10}</text>')
        o.append(f'<text x="{x + 110}" y="{y}" fill="{c[colour]}">{html.escape(value)}</text>')
        y += 24
    # status bar
    o.append(f'<rect y="{H-STATUS}" width="{W}" height="{STATUS}" fill="{c["status_bg"]}"/>')
    o.append(f'<line x1="0" y1="{H-STATUS}" x2="{W}" y2="{H-STATUS}" stroke="{c["line"]}"/>')
    o.append(
        f'<text x="18" y="{H-STATUS/2 + 4}" fill="{c["dim"]}">NORMAL</text>'
        f'<text x="96" y="{H-STATUS/2 + 4}" fill="{c["fg"]}">~/profile/README.md</text>'
        f'<text x="{W-300}" y="{H-STATUS/2 + 4}" fill="{c["dim"]}">utf-8</text>'
        f'<text x="{W-238}" y="{H-STATUS/2 + 4}" fill="{c["dim"]}">rust</text>'
        f'<text x="{W-182}" y="{H-STATUS/2 + 4}" fill="{c["dim"]}">ln 1, col 1</text>'
        f'<text x="{W-80}" y="{H-STATUS/2 + 4}" fill="{c["green"]}">{merged}/{repos}</text>'
    )
    o.append("</svg>")
    return "\n".join(o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--merged", type=int)
    ap.add_argument("--repos", type=int)
    ap.add_argument("--open", dest="opened", type=int)
    args = ap.parse_args()

    if args.merged and args.repos and args.opened:
        merged, repos, opened = args.merged, args.repos, args.opened
    else:
        merged, repos = count("merged")
        opened, _ = count("open")

    for name, theme in (("hero-dark.svg", DARK), ("hero-light.svg", LIGHT)):
        path = os.path.join(ROOT, "assets", name)
        svg = build(theme, merged, repos, opened)
        open(path, "w", encoding="utf-8").write(svg)
        print(f"{path}: {len(svg)/1024:.1f} KB")
    print(f"numbers baked in: {merged} merged / {repos} repos / {opened} open")


if __name__ == "__main__":
    main()
