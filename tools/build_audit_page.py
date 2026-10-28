#!/usr/bin/env python3
"""Build audit.html — the whole ascii pool, playing, ordered by source then category.

Two shelves:
  ascii.rest  — procedural pieces, grouped by the category the site gives them
  ascii.live  — the recorded ones, grouped by audit verdict

Motion needs no JS: each card points at /animations/<name>.svg, and the keyframes live inside the
SVG, so an <img> plays it. The only script on the page is the filter box.

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
REST = os.path.join(ROOT, "assets", "ascii-rest.json")
DEFAULT_OUT = "/home/ubuntu/tui-server/audit.html"

VERDICT_ORDER = ["REMOVED", "DROP", "BORDERLINE", "NEW", "KEEP"]
VERDICT_LABEL = {
    "REMOVED": "removed",
    "DROP": "drop",
    "BORDERLINE": "borderline",
    "NEW": "new",
    "KEEP": "keep",
}
VERDICT_BLURB = {
    "REMOVED": "Taken out of the pool. Kept here only so the decision is on the record.",
    "DROP": "Flagged: broken capture, speck, text banner, noise, or a green smear.",
    "BORDERLINE": "Abstract or sparse. Not wrong, just not obviously anything.",
    "NEW": "Recorded after the audit — playing, not judged yet.",
    "KEEP": "Reads as a subject at README size.",
}


def card(name, meta, badge, cls, blurb=""):
    art = (
        f'<img src="/animations/{name}.svg" alt="{html.escape(name)}" '
        'width="680" height="420" loading="lazy">'
    )
    bits = []
    if meta.get("frames"):
        bits.append(f"{meta['frames']}f")
    if meta.get("rows") and meta.get("cols"):
        bits.append(f"{meta['rows']}×{meta['cols']}")
    if meta.get("ink"):
        bits.append(f"{meta['ink']}% ink")
    note = meta.get("note") or blurb
    cat = meta.get("category", "")
    return (
        f'      <figure class="card {cls}" data-name="{html.escape(name.lower())}" '
        f'data-cat="{html.escape(str(cat).lower())}">\n'
        f"        {art}\n"
        f'        <figcaption>\n'
        f'          <span class="row"><span class="name">{html.escape(name)}</span>'
        f'<span class="badge">{html.escape(badge)}</span></span>\n'
        f'          <span class="meta">{" · ".join(bits)}</span>\n'
        f'          <span class="why">{html.escape(note)}</span>\n'
        f"        </figcaption>\n"
        f"      </figure>"
    )


def build(out=DEFAULT_OUT):
    audit = json.load(open(AUDIT, encoding="utf-8"))
    rest = json.load(open(REST, encoding="utf-8")) if os.path.exists(REST) else {}
    present = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ANIM, "*.svg"))}

    rest_files = {v["file"]: (k, v) for k, v in rest.items() if v.get("file") in present}
    live = sorted(n for n in present if n not in rest_files)

    # ---- shelf 1: ascii.rest, grouped by category -------------------------------------------
    by_cat = {}
    for fname, (_piece, meta) in rest_files.items():
        by_cat.setdefault(meta.get("category", "misc"), []).append((fname, meta))
    cats = sorted(by_cat.items(), key=lambda kv: (-len(kv[1]), kv[0]))

    rest_sections = []
    for cat, items in cats:
        items.sort(key=lambda kv: kv[0])
        cards = "\n".join(card(n, m, "rest", "v-rest", f"ascii.rest · {cat}") for n, m in items)
        anchor = cat.replace(" ", "-")
        rest_sections.append(
            f'    <section class="sub" id="cat-{anchor}">\n'
            f'      <h3>{html.escape(cat)} <span class="count">{len(items)}</span></h3>\n'
            f'      <div class="grid">\n{cards}\n      </div>\n'
            f"    </section>"
        )

    # ---- shelf 2: ascii.live, grouped by verdict --------------------------------------------
    buckets = {k: [] for k in VERDICT_ORDER}
    for name in live:
        meta = audit.get(name) or {"verdict": "NEW", "why": "not judged yet"}
        v = meta.get("verdict", "NEW")
        buckets[v if v in buckets else "NEW"].append((name, meta))

    live_sections = []
    for v in VERDICT_ORDER:
        items = buckets[v]
        if not items:
            continue
        items.sort(key=lambda kv: kv[0])
        cards = "\n".join(
            card(n, m, VERDICT_LABEL[v], f"v-{v.lower()}", m.get("why", "")) for n, m in items
        )
        live_sections.append(
            f'    <section class="sub" id="v-{v.lower()}">\n'
            f'      <h3><span class="pill v-{v.lower()}">{VERDICT_LABEL[v]}</span> '
            f'<span class="count">{len(items)}</span> '
            f"<small>{html.escape(VERDICT_BLURB[v])}</small></h3>\n"
            f'      <div class="grid">\n{cards}\n      </div>\n'
            f"    </section>"
        )

    total = len(present)
    rest_n = len(rest_files)
    live_n = len(live)
    cat_nav = " ".join(
        f'<a href="#cat-{c.replace(" ", "-")}">{html.escape(c)} <b>{len(i)}</b></a>' for c, i in cats
    )
    verdict_nav = " ".join(
        f'<a href="#v-{v.lower()}">{VERDICT_LABEL[v]} <b>{len(buckets[v])}</b></a>'
        for v in VERDICT_ORDER
        if buckets[v]
    )

    page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ascii pool · {total} animations</title>
<style>
  :root {{ --bg:#0d1117; --panel:#161b22; --line:#30363d; --fg:#c9d1d9; --dim:#8b949e;
           --green:#7ee787; --red:#f85149; --amber:#d29922; --blue:#79c0ff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
          font:14px/1.5 ui-monospace,SFMono-Regular,"DejaVu Sans Mono",Menlo,Consolas,monospace; }}
  header.top {{ position:sticky; top:0; z-index:9; background:rgba(13,17,23,.94);
                backdrop-filter:blur(8px); border-bottom:1px solid var(--line); padding:12px 22px 10px; }}
  h1 {{ font-size:15px; margin:0 0 8px; font-weight:600; letter-spacing:.2px; }}
  h1 span {{ color:var(--dim); font-weight:400; }}
  #q {{ width:100%; max-width:420px; background:#010409; border:1px solid var(--line); color:var(--fg);
        border-radius:6px; padding:7px 10px; font:12px ui-monospace,monospace; margin:0 0 8px; }}
  #q:focus {{ outline:none; border-color:var(--green); }}
  .navrow {{ display:flex; flex-wrap:wrap; gap:4px 14px; font-size:12px; margin-top:5px; }}
  .navrow a {{ color:var(--dim); text-decoration:none; border-bottom:1px solid transparent; }}
  .navrow a:hover {{ color:var(--green); border-color:var(--green); }}
  .navrow b {{ color:var(--fg); font-weight:600; }}
  .tag {{ color:#484f58; }}
  main {{ max-width:1560px; margin:0 auto; }}
  .shelf {{ border-top:1px solid var(--line); padding:22px; }}
  .shelfhead {{ display:flex; align-items:baseline; gap:12px; margin:0 0 6px; flex-wrap:wrap; }}
  .shelfhead h2 {{ font-size:17px; margin:0; letter-spacing:.3px; }}
  .shelfhead .src {{ color:var(--dim); font-size:11.5px; }}
  .shelfhead .src a {{ color:var(--blue); text-decoration:none; }}
  section.sub {{ margin:0 0 32px; }}
  h3 {{ font-size:12px; text-transform:uppercase; letter-spacing:1.1px; color:var(--dim);
        display:flex; align-items:center; gap:9px; margin:18px 0 12px; font-weight:600; }}
  h3 small {{ text-transform:none; letter-spacing:0; font-weight:400; font-size:11px; opacity:.7; }}
  .count {{ color:var(--fg); background:#21262d; border:1px solid var(--line); border-radius:20px;
            padding:0 8px; font-size:10.5px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:14px; }}
  .card {{ margin:0; background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow:hidden; }}
  .card img {{ width:100%; height:auto; display:block; background:#010409; }}
  figcaption {{ padding:9px 11px 11px; display:flex; flex-direction:column; gap:3px;
                border-top:1px solid var(--line); }}
  .row {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
  .name {{ color:var(--green); font-size:12.5px; }}
  .badge {{ font-size:9.5px; color:var(--dim); border:1px solid var(--line); border-radius:20px; padding:1px 7px; }}
  .meta {{ color:var(--dim); font-size:10.5px; }}
  .why {{ color:var(--fg); font-size:11px; opacity:.82; }}
  .v-removed {{ border-color:#5c1f1f; }} .v-drop {{ border-color:#4a2a12; }}
  .v-borderline {{ border-color:#4a3a12; }} .v-new {{ border-color:#1f3a5c; }}
  .v-keep {{ border-color:#1d3a24; }} .v-rest {{ border-color:#2b2540; }}
  .pill {{ font-size:10px; padding:2px 8px; border-radius:20px; color:#0d1117; font-weight:700; letter-spacing:.5px; }}
  .pill.v-removed {{ background:var(--red); }} .pill.v-drop {{ background:#db6d28; }}
  .pill.v-borderline {{ background:var(--amber); }} .pill.v-new {{ background:var(--blue); }}
  .pill.v-keep {{ background:var(--green); }}
  .hidden {{ display:none !important; }}
  .empty {{ color:var(--dim); padding:30px 22px; font-size:12px; }}
</style>
</head><body>
<header class="top">
  <h1>ascii pool <span>· {total} animations · playing at 680×420, the size a visitor sees</span></h1>
  <input id="q" type="search" placeholder="filter by name or category…" autocomplete="off">
  <div class="navrow">
    <a href="#shelf-rest">ascii.rest <b>{rest_n}</b></a>
    <a href="#shelf-live">ascii.live <b>{live_n}</b></a>
  </div>
  <div class="navrow"><span class="tag">rest:</span> {cat_nav}</div>
  <div class="navrow"><span class="tag">live:</span> {verdict_nav}</div>
</header>
<main>
  <div class="shelf" id="shelf-rest">
    <div class="shelfhead">
      <h2>ascii.rest</h2>
      <span class="src">{rest_n} pieces · MIT · pulled with <code>tools/pull_ascii_rest.py</code></span>
    </div>
{chr(10).join(rest_sections)}
  </div>

  <div class="shelf" id="shelf-live">
    <div class="shelfhead">
      <h2>ascii.live</h2>
      <span class="src">{live_n} recorded from the terminal stream · GPL-3.0 · captured with <code>tools/capture_frames.py</code></span>
    </div>
{chr(10).join(live_sections)}
  </div>
</main>
<script>
  const q = document.getElementById('q');
  const cards = [...document.querySelectorAll('.card')];
  const sections = [...document.querySelectorAll('section.sub')];
  q.addEventListener('input', () => {{
    const t = q.value.trim().toLowerCase();
    let shown = 0;
    for (const c of cards) {{
      const hit = !t || c.dataset.name.includes(t) || (c.dataset.cat || '').includes(t);
      c.classList.toggle('hidden', !hit);
      if (hit) shown++;
    }}
    for (const s of sections) {{
      const any = [...s.querySelectorAll('.card')].some(c => !c.classList.contains('hidden'));
      s.classList.toggle('hidden', !any);
    }}
    document.querySelectorAll('.empty').forEach(e => e.remove());
    if (!shown) {{
      const p = document.createElement('div');
      p.className = 'empty';
      p.textContent = 'nothing matches that';
      document.querySelector('main').appendChild(p);
    }}
  }});
</script>
</body></html>
"""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(page)
    print(
        f"{out}: {len(page)/1024:.0f} KB · {total} animations · "
        f"rest {rest_n} in {len(cats)} categories · live {live_n}"
    )
    return out, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
