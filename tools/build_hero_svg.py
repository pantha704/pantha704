#!/usr/bin/env python3
"""Build the profile dashboard hero: assets/hero.svg

The SVG themes itself — light palette by default, dark palette inside
@media (prefers-color-scheme: dark) — so ONE file can be wrapped in a link. That matters because
`<a><picture><source>…</picture></a>` gets mangled by GitHub's sanitizer (the <source> is hoisted
out of the picture and the dark variant is never served), while `<a><img></a>` survives intact.

Numbers are queried live from the GitHub API unless overridden:

    python3 tools/build_hero_svg.py
    python3 tools/build_hero_svg.py --merged 19 --repos 10 --open 14
"""
import argparse
import html
import json
import os
import subprocess
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGIN = "pantha704"

W, H = 920, 402
CHROME = 34
STATUS = 28
SIDEBAR = 210

# role: (light, dark)
ROLES = {
    "bg": ("#ffffff", "#0d1117"),
    "panel": ("#f6f8fa", "#161b22"),
    "side": ("#f0f3f6", "#0f141b"),
    "line": ("#d0d7de", "#30363d"),
    "fg": ("#24292f", "#c9d1d9"),
    "dim": ("#57606a", "#8b949e"),
    "green": ("#1a7f37", "#7ee787"),
    "cyan": ("#0969da", "#79c0ff"),
    "yellow": ("#9a6700", "#e3b341"),
    "sel": ("#0969da22", "#1f6feb33"),
    "status_bg": ("#f6f8fa", "#161b22"),
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


_PUBLIC = {}


def is_public(repo):
    """Only count repositories a visitor can actually open — private ones 404 for everyone else,
    and the search API returns them for the owner's token but not for CI's, so an unfiltered
    count would differ between this machine and the daily Action."""
    if repo not in _PUBLIC:
        _PUBLIC[repo] = not gh_json(f"repos/{repo}").get("private", True)
    return _PUBLIC[repo]


def count(state, include_private=False, attempts=3):
    total, repos, page = 0, set(), 1
    while True:
        d = gh_json(
            f"search/issues?q=author:{LOGIN}+type:pr+is:{state}&per_page=100&page={page}"
        )
        items = d.get("items", [])
        # GitHub's search API occasionally answers a state-filtered query with an empty
        # result set while the same query without the state qualifier still returns data.
        if not items and page == 1 and attempts > 1:
            time.sleep(6)
            return count(state, include_private, attempts - 1)
        for it in items:
            repo = it["repository_url"].replace("https://api.github.com/repos/", "")
            if repo.startswith(f"{LOGIN}/"):
                continue
            if not include_private and not is_public(repo):
                continue
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


def stylesheet():
    light = "".join(f".f-{k}{{fill:{v[0]}}}.s-{k}{{stroke:{v[0]}}}" for k, v in ROLES.items())
    dark = "".join(f".f-{k}{{fill:{v[1]}}}.s-{k}{{stroke:{v[1]}}}" for k, v in ROLES.items())
    return (
        "<style>"
        "text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,"
        "monospace;font-size:13px;white-space:pre}"
        + light
        + "@media (prefers-color-scheme: dark){"
        + dark
        + "}"
        "</style>"
    )


def build(merged, repos, opened):
    o = []
    o.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="pratham jaiswal — {merged} merged pull requests across {repos} '
        f'upstream repositories">'
    )
    o.append(stylesheet())
    o.append(f'<rect width="{W}" height="{H}" rx="12" class="f-bg"/>')
    o.append(
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" class="s-line"/>'
    )
    # chrome
    o.append(
        f'<path d="M0 12a12 12 0 0 1 12-12h{W-24}a12 12 0 0 1 12 12v{CHROME-12}H0z" class="f-panel"/>'
    )
    for i, col in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{20 + i*18}" cy="{CHROME/2}" r="5.5" fill="{col}"/>')
    o.append(
        f'<text x="{W/2}" y="{CHROME/2 + 4}" class="f-dim" text-anchor="middle" font-size="12">'
        f'pratham@kolkata — ~/profile</text>'
    )
    o.append(f'<line x1="0" y1="{CHROME}" x2="{W}" y2="{CHROME}" class="s-line"/>')
    # sidebar
    o.append(f'<rect y="{CHROME}" width="{SIDEBAR}" height="{H-CHROME-STATUS}" class="f-side"/>')
    o.append(f'<line x1="{SIDEBAR}" y1="{CHROME}" x2="{SIDEBAR}" y2="{H-STATUS}" class="s-line"/>')
    tree = [
        ("~/profile", "dim", False),
        ("|- README.md", "green", True),
        ("|- upstream/", "fg", False),
        ("|- projects/", "fg", False),
        ("|- stack.md", "fg", False),
        ("`- terminal.md", "fg", False),
    ]
    y = CHROME + 28
    for label, colour, active in tree:
        if active:
            o.append(
                f'<rect x="8" y="{y-14}" width="{SIDEBAR-16}" height="20" rx="4" class="f-sel"/>'
            )
        o.append(f'<text x="16" y="{y}" class="f-{colour}">{html.escape(label)}</text>')
        y += 22
    # main pane
    x = SIDEBAR + 26
    y = CHROME + 34
    o.append(f'<text x="{x}" y="{y}" class="f-cyan" font-size="15">pratham@kolkata</text>')
    y += 12
    o.append(f'<text x="{x}" y="{y}" class="f-line">{"-" * 46}</text>')
    y += 26
    for key, value, colour in rows(merged, repos, opened):
        o.append(f'<text x="{x}" y="{y}" class="f-dim">{html.escape(key):<10}</text>')
        o.append(f'<text x="{x + 110}" y="{y}" class="f-{colour}">{html.escape(value)}</text>')
        y += 24
    # status bar
    o.append(f'<rect y="{H-STATUS}" width="{W}" height="{STATUS}" class="f-status_bg"/>')
    o.append(f'<line x1="0" y1="{H-STATUS}" x2="{W}" y2="{H-STATUS}" class="s-line"/>')
    o.append(
        f'<text x="18" y="{H-STATUS/2 + 4}" class="f-dim">NORMAL</text>'
        f'<text x="96" y="{H-STATUS/2 + 4}" class="f-fg">~/profile/README.md</text>'
        f'<text x="{W-300}" y="{H-STATUS/2 + 4}" class="f-dim">utf-8</text>'
        f'<text x="{W-238}" y="{H-STATUS/2 + 4}" class="f-dim">rust</text>'
        f'<text x="{W-182}" y="{H-STATUS/2 + 4}" class="f-dim">ln 1, col 1</text>'
        f'<text x="{W-80}" y="{H-STATUS/2 + 4}" class="f-green">{merged}/{repos}</text>'
    )
    o.append("</svg>")
    return "\n".join(o)


def write(merged, repos, opened, out=None):
    path = out or os.path.join(ROOT, "assets", "hero.svg")
    svg = build(merged, repos, opened)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(svg)
    return path, len(svg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--merged", type=int)
    ap.add_argument("--repos", type=int)
    ap.add_argument("--open", dest="opened", type=int)
    ap.add_argument(
        "--include-private",
        action="store_true",
        help="count merges into private repositories too (résumé numbers, not the public README)",
    )
    args = ap.parse_args()

    if args.merged and args.repos and args.opened:
        merged, repos, opened = args.merged, args.repos, args.opened
    else:
        merged, repos = count("merged", args.include_private)
        opened, _ = count("open", args.include_private)

    path, size = write(merged, repos, opened)
    print(f"{path}: {size/1024:.1f} KB")
    print(f"numbers baked in: {merged} merged / {repos} repos / {opened} open")


if __name__ == "__main__":
    main()
