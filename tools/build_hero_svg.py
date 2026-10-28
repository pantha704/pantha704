#!/usr/bin/env python3
"""Build the profile dashboard hero: assets/hero.svg

Two things make this file unusual:

1. It cycles through five panes by itself — sidebar highlight moves, right pane swaps, status-bar
   path changes — so a still image reads like a terminal being driven. 4s per pane, 20s loop, CSS
   keyframes only: an SVG inside <img> cannot run script, but it does run CSS.

2. It themes itself — light palette by default, dark palette inside
   @media (prefers-color-scheme: dark) — so ONE file can also be wrapped in a link.
   `<a><picture><source>…</picture></a>` gets mangled by GitHub's sanitizer (the <source> is hoisted
   out of the picture and the dark variant is never served); `<a><img></a>` survives intact.

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
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOGIN = "pantha704"

W, H = 920, 402
CHROME = 34
CHAR_W = 7.8          # advance of one character at font-size 13px
STATUS = 28
SIDEBAR = 210
VALUE_X = 118          # offset of a value column from the pane's left edge

SLOT = 4.0             # seconds each pane stays up
PANES = 5
LOOP = SLOT * PANES

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


def panes(merged, repos, opened):
    """(sidebar row that lights up, status-bar path, pane title, [(key, value, colour)…])"""
    return [
        (
            0,
            "~/profile/README.md",
            "pratham@kolkata",
            [
                ("role", "systems & automation engineer", "green"),
                ("now", "automation + vuln reporting @ braid-forbes", "fg"),
                ("based", "kolkata, india", "fg"),
                ("study", "b.tech, sister nivedita university, 2023–2027", "fg"),
                ("status", "open to systems, devtools & infra work", "yellow"),
            ],
        ),
        (
            2,
            "~/profile/upstream/",
            f"~/upstream  —  {merged} merged · {repos} repos · {opened} open",
            [
                ("cranelift", "#1625  ci runner disk exhaustion → cleanup workflow", "fg"),
                ("ccextractor", "#2378  tx3g subtitle timings on the mp4 path", "fg"),
                ("open_spiel", "#1455  tensorflow 1.x deep-rl → pytorch", "fg"),
                ("pytorch/ao", "#3709  FqnToConfig + MoE quantization docs", "fg"),
                ("in flight", "#1711 #1710 · wagtail x2 · gatsby · clippy · scancode x2", "cyan"),
            ],
        ),
        (
            3,
            "~/profile/projects/",
            "~/projects  —  5 shipped",
            [
                ("perfume", "commerce system, catalogue → dispatch, 60+ prs", "fg"),
                ("homeworker", "pdf → reviewable a4 notes, handwriting typefaces", "fg"),
                ("flowforge", "serverless durable background jobs", "fg"),
                ("macfolio", "macos window manager in the browser", "fg"),
                ("turbin3", "solana markets, staking, vaults, escrow, amm", "fg"),
            ],
        ),
        (
            4,
            "~/profile/stack.md",
            "~/stack.md",
            [
                ("languages", "rust · typescript · python · go · solidity", "cyan"),
                ("web", "next.js · react · node · anchor", "fg"),
                ("data", "postgresql · redis · prisma", "fg"),
                ("infra", "docker · linux · github actions · n8n", "fg"),
                ("testing", "playwright", "fg"),
            ],
        ),
        (
            5,
            "~/profile/terminal.md",
            "~/terminal.md",
            [
                ("frames", "17 ascii animations captured locally", "fg"),
                ("hero", "this file — css only, no script allowed", "fg"),
                ("server", "random svg per request, cache-control: no-store", "fg"),
                ("$", "python3 tools/play.py --name badapple", "green"),
            ],
        ),
    ]


def stylesheet():
    light = "".join(f".f-{k}{{fill:{v[0]}}}.s-{k}{{stroke:{v[0]}}}" for k, v in ROLES.items())
    dark = "".join(f".f-{k}{{fill:{v[1]}}}.s-{k}{{stroke:{v[1]}}}" for k, v in ROLES.items())

    # Each pane is up for its own SLOT, then hidden for the rest of the loop. Negative delays put
    # every pane mid-cycle at t=0, so the first painted frame is never blank.
    window = SLOT / LOOP * 100
    keyframes = (
        f"@keyframes show{{0%{{opacity:1}}{window:.2f}%{{opacity:1}}"
        f"{window + 0.01:.2f}%{{opacity:0}}100%{{opacity:0}}}}"
    )
    anim = f".pane,.hl,.path{{opacity:0;animation:show {LOOP:.0f}s infinite}}"
    for n in range(PANES):
        anim += f".p{n}{{animation-delay:{n * SLOT - LOOP:.0f}s}}"

    # the status-bar clock: three stepped layers so the time advances inside an <img>
    anim += (
        ".c-h{opacity:0;animation:ch 86400s steps(1,end) infinite}"
        ".c-m{opacity:0;animation:cm 3600s steps(1,end) infinite}"
        ".c-s{opacity:0;animation:cs 60s steps(1,end) infinite}"
        "@keyframes ch{0%{opacity:1}4.1666667%{opacity:0}100%{opacity:0}}"
        "@keyframes cm{0%{opacity:1}1.6666667%{opacity:0}100%{opacity:0}}"
        "@keyframes cs{0%{opacity:1}1.6666667%{opacity:0}100%{opacity:0}}"
    )

    return (
        "<style>"
        "text{font-family:ui-monospace,SFMono-Regular,'DejaVu Sans Mono',Menlo,Consolas,"
        "monospace;font-size:13px;white-space:pre}"
        + light
        + "@media (prefers-color-scheme: dark){"
        + dark
        + "}"
        + anim
        + keyframes
        + "@media (prefers-reduced-motion: reduce){"
        ".pane,.hl,.path{animation:none;opacity:0}.p0{opacity:1}"
        ".c-h,.c-m,.c-s{animation:none}}"
        "</style>"
    )


def clock_bar(now, x, y):
    """A clock that ticks inside a static <img>.

    Three stepped layers — hours (24 slots over 24h), minutes (60 over 1h), seconds (60 over 1m).
    Each layer starts at the value the server saw when it rendered this file, then advances on its
    own. The inline opacity on the current slot is what a renderer without CSS animation falls back
    to, so the picture is still correct if nothing moves.
    """
    cw = CHAR_W
    o = [f'<text x="{x:.1f}" y="{y}" class="f-green">{now.strftime("%d/%m")}</text>']
    tx = x + 6 * cw
    o.append(f'<text x="{tx + 2 * cw:.1f}" y="{y}" class="f-green">:</text>')
    o.append(f'<text x="{tx + 5 * cw:.1f}" y="{y}" class="f-green">:</text>')

    def layer(cls, count, slot, period, current, fmt, dx):
        out = []
        for k in range(count):
            cur = ";opacity:1" if k == current else ""
            # anchor the layer on the value the server saw: slot k must be visible when the
            # wall clock reads k, which is (k - current) slots after this file is loaded
            delay = ((k - current) * slot) - period
            out.append(
                f'<text x="{tx + dx * cw:.1f}" y="{y}" class="f-green {cls}" '
                f'style="animation-delay:{delay}s{cur}">{fmt(k)}</text>'
            )
        return out

    o += layer("c-h", 24, 3600, 86400, now.hour, lambda k: f"{k:02d}", 0)
    o += layer("c-m", 60, 60, 3600, now.minute, lambda k: f"{k:02d}", 3)
    o += layer("c-s", 60, 1, 60, now.second, lambda k: f"{k:02d}", 6)
    return "".join(o)


def build(merged, repos, opened, stamp=None, now=None):
    data = panes(merged, repos, opened)
    if now is None:
        now = datetime.now(IST)
    if stamp is None:
        stamp = now.strftime("%d/%m %H:%M:%S")
    o = []
    o.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="pratham jaiswal — terminal dashboard cycling through profile, '
        f'{merged} merged pull requests across {repos} upstream repositories, projects, stack and '
        f'the ascii terminal">'
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
        ("~/profile", "dim"),
        ("|- README.md", "green"),
        ("|- upstream/", "fg"),
        ("|- projects/", "fg"),
        ("|- stack.md", "fg"),
        ("`- terminal.md", "fg"),
    ]
    row_y = {i: CHROME + 28 + i * 22 for i in range(len(tree))}
    # highlight first, so the tree text paints over it
    for n, (row, path, title, lines) in enumerate(data):
        o.append(
            f'<rect x="8" y="{row_y[row]-14}" width="{SIDEBAR-16}" height="20" rx="4" '
            f'class="f-sel hl p{n}"/>'
        )
    for label, colour in tree:
        y = row_y[tree.index((label, colour))]
        o.append(f'<text x="16" y="{y}" class="f-{colour}">{html.escape(label)}</text>')
    # panes
    x = SIDEBAR + 26
    for n, (row, path, title, lines) in enumerate(data):
        o.append(f'<g class="pane p{n}">')
        y = CHROME + 34
        o.append(f'<text x="{x}" y="{y}" class="f-cyan" font-size="15">{html.escape(title)}</text>')
        y += 12
        o.append(f'<text x="{x}" y="{y}" class="f-line">{"-" * 52}</text>')
        y += 26
        for key, value, colour in lines:
            o.append(f'<text x="{x}" y="{y}" class="f-dim">{html.escape(key):<11}</text>')
            o.append(
                f'<text x="{x + VALUE_X}" y="{y}" class="f-{colour}">{html.escape(value)}</text>'
            )
            y += 24
        o.append("</g>")
    # status bar
    o.append(f'<rect y="{H-STATUS}" width="{W}" height="{STATUS}" class="f-status_bg"/>')
    o.append(f'<line x1="0" y1="{H-STATUS}" x2="{W}" y2="{H-STATUS}" class="s-line"/>')
    o.append(f'<text x="18" y="{H-STATUS/2 + 4}" class="f-dim">NORMAL</text>')
    for n, (row, path, title, lines) in enumerate(data):
        o.append(
            f'<text x="96" y="{H-STATUS/2 + 4}" class="f-fg path p{n}">{html.escape(path)}</text>'
        )
    o.append(
        f'<text x="{W-335}" y="{H-STATUS/2 + 4}" class="f-dim">utf-8</text>'
        f'<text x="{W-275}" y="{H-STATUS/2 + 4}" class="f-dim">rust</text>'
        f'<text x="{W-222}" y="{H-STATUS/2 + 4}" class="f-dim">ln 1, col 1</text>'
        + clock_bar(now, W - 127, H - STATUS / 2 + 4)
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
    print(f"cycling {PANES} panes, {SLOT:g}s each, {LOOP:g}s loop")


if __name__ == "__main__":
    main()
