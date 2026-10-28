#!/usr/bin/env python3
"""Build audit.html — every animation in the pool, playing, with its verdict.

The page is served by tui-server at /audit and points at /animations/<name>.svg, which is the same
self-animating SVG the README uses. No JS needed for the motion: the CSS keyframes live inside the
SVG, so an <img> plays it.

    python3 tools/build_audit_page.py [--out /path/audit.html]
"""
import argparse
import glob
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ANIM = os.path.join(ROOT, "assets", "animations")
AUDIT = os.path.join(ROOT, "assets", "audit.json")
DEFAULT_OUT = "/home/ubuntu/tui-server/audit.html"

ORDER = ["REMOVED", "DROP", "BORDERLINE", "NEW", "KEEP"]
LABEL = {
    "REMOVED": "removed",
    "DROP": "drop",
    "BORDERLINE": "borderline",
    "NEW": "new",
    "KEEP": "keep",
}
BLURB = {
    "REMOVED": "Taken out of the pool. Kept here only so the decision is on the record.",
    "DROP": "Should come out: broken captures, specks, text banners, noise, or a green smear.",
    "BORDERLINE": "Abstract or sparse. Not wrong, just not obviously anything.",
    "NEW": "Captured after the audit — playing, but not judged yet.",
    "KEEP": "Reads as a subject at README size. These are what a visitor should get.",
}


def build(out=DEFAULT_OUT):
    """Render the page to `out` and return (path, total, counts)."""
    audit = json.load(open(AUDIT, encoding="utf-8"))
    present = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ANIM, "*.svg"))}
    names = sorted(set(audit) | present)

    buckets = {k: [] for k in ORDER}
    for name in names:
        meta = audit.get(name)
        if meta is None:
            meta = {"verdict": "NEW", "why": "captured after the audit — not judged yet"}
        verdict = meta["verdict"] if meta["verdict"] in buckets else "KEEP"
        # a REMOVED entry has no SVG any more; everything else must actually exist to play
        if verdict != "REMOVED" and name not in present:
            continue
        buckets[verdict].append((name, meta))

    total = sum(len(v) for v in buckets.values())
    counts = " · ".join(f"{len(buckets[k])} {LABEL[k]}" for k in ORDER if buckets[k])

    sections = []
    for key in ORDER:
        items = buckets[key]
        if not items:
            continue
        cards = []
        for name, meta in items:
            if key == "REMOVED":
                art = '<div class="gone">removed</div>'
            else:
                art = (
                    f'<img src="/animations/{name}.svg" alt="{html.escape(name)}" '
                    'width="680" height="420" loading="lazy">'
                )
            cards.append(
                f"""      <figure class="card v-{key.lower()}">
        {art}
        <figcaption>
          <span class="name">{html.escape(name)}</span>
          <span class="meta">{meta.get('frames','?')}f · {meta.get('rows','?')}×{meta.get('cols','?')} · {meta.get('ink','?')}% ink</span>
          <span class="why">{html.escape(meta.get('why',''))}</span>
        </figcaption>
      </figure>"""
            )
        sections.append(
            f"""    <section id="{key.lower()}">
      <h2><span class="pill v-{key.lower()}">{LABEL[key]}</span> {len(items)}
        <small>{html.escape(BLURB[key])}</small></h2>
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </section>"""
        )

    nav = " ".join(
        f'<a href="#{k.lower()}">{LABEL[k]} <b>{len(buckets[k])}</b></a>' for k in ORDER if buckets[k]
    )

    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ascii pool · audit</title>
<style>
  :root {{ --bg:#0d1117; --panel:#161b22; --line:#30363d; --fg:#c9d1d9; --dim:#8b949e;
           --green:#7ee787; --red:#f85149; --amber:#d29922; --blue:#79c0ff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
          font:14px/1.5 ui-monospace,SFMono-Regular,"DejaVu Sans Mono",Menlo,Consolas,monospace; }}
  header.top {{ position:sticky; top:0; z-index:5; background:rgba(13,17,23,.92);
                backdrop-filter:blur(6px); border-bottom:1px solid var(--line);
                padding:14px 22px; }}
  h1 {{ font-size:15px; margin:0 0 6px; font-weight:600; letter-spacing:.2px; }}
  h1 span {{ color:var(--dim); font-weight:400; }}
  nav a {{ color:var(--dim); text-decoration:none; margin-right:16px; font-size:12px;
           border-bottom:1px solid transparent; padding-bottom:2px; }}
  nav a:hover {{ color:var(--green); border-color:var(--green); }}
  nav b {{ color:var(--fg); }}
  main {{ padding:26px 22px 80px; max-width:1500px; margin:0 auto; }}
  section {{ margin:0 0 42px; }}
  h2 {{ font-size:13px; text-transform:uppercase; letter-spacing:1px; color:var(--dim);
        display:flex; align-items:center; gap:10px; margin:0 0 14px; font-weight:600; }}
  h2 small {{ text-transform:none; letter-spacing:0; color:var(--dim); font-weight:400;
              font-size:11px; opacity:.75; }}
  .pill {{ font-size:10px; padding:2px 8px; border-radius:20px; color:#0d1117; font-weight:700;
           letter-spacing:.5px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:16px; }}
  .card {{ margin:0; background:var(--panel); border:1px solid var(--line); border-radius:8px;
           overflow:hidden; }}
  .card img {{ width:100%; height:auto; display:block; background:#010409; }}
  .gone {{ aspect-ratio:680/420; display:grid; place-items:center; color:var(--dim);
           background:repeating-linear-gradient(45deg,#0f141b,#0f141b 10px,#12181f 10px,#12181f 20px);
           font-size:12px; letter-spacing:2px; text-transform:uppercase; }}
  figcaption {{ padding:9px 11px 11px; display:flex; flex-direction:column; gap:3px;
                border-top:1px solid var(--line); }}
  .name {{ color:var(--green); font-size:12.5px; }}
  .meta {{ color:var(--dim); font-size:10.5px; }}
  .why {{ color:var(--fg); font-size:11px; opacity:.85; margin-top:3px; }}
  .v-removed {{ border-color:#5c1f1f; }}
  .v-drop {{ border-color:#4a2a12; }}
  .v-borderline {{ border-color:#4a3a12; }}
  .v-new {{ border-color:#1f3a5c; }}
  .v-keep {{ border-color:#1d3a24; }}
  .pill.v-removed {{ background:var(--red); }}
  .pill.v-drop {{ background:#db6d28; }}
  .pill.v-borderline {{ background:var(--amber); }}
  .pill.v-new {{ background:var(--blue); }}
  .pill.v-keep {{ background:var(--green); }}
</style>
</head><body>
<header class="top">
  <h1>ascii pool <span>· {total} animations · each one playing at 680×420, the size a visitor sees</span></h1>
  <nav>{nav}</nav>
</header>
<main>
{chr(10).join(sections)}
</main>
</body></html>
"""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    print(f"{out}: {len(page)/1024:.0f} KB, {total} animations ({counts})")
    return out, total, counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
