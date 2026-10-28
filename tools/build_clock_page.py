#!/usr/bin/env python3
"""Build clock.html — a live ASCII clock and calendar in the visitor's own timezone.

Why this page exists: the README images are SVG inside <img>, proxied through GitHub's camo. No
JavaScript runs there and no client headers reach us, so the profile can only ever show the
server's clock at fetch time. A page we serve ourselves can do the real thing — read the visitor's
timezone from Intl, tick every second, and draw the calendar for their month.

    python3 tools/build_clock_page.py [--out /home/ubuntu/tui-server/clock.html]
"""
import argparse
import os

DEFAULT_OUT = "/home/ubuntu/tui-server/clock.html"

PAGE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ascii clock · your time</title>
<style>
  :root { --bg:#0d1117; --panel:#161b22; --line:#30363d; --fg:#7ee787; --dim:#8b949e; --accent:#79c0ff; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:14px/1.45 ui-monospace,SFMono-Regular,"DejaVu Sans Mono",Menlo,Consolas,monospace; }
  .wrap { max-width:1000px; margin:0 auto; padding:28px 22px 60px; }
  .bar { display:flex; justify-content:space-between; gap:14px; flex-wrap:wrap; color:var(--dim);
         font-size:11.5px; border:1px solid var(--line); border-bottom:none;
         border-radius:8px 8px 0 0; background:var(--panel); padding:8px 12px; }
  .bar b { color:var(--fg); font-weight:600; }
  .pane { border:1px solid var(--line); border-radius:0 0 8px 8px; background:#010409; padding:22px 18px; }
  pre { margin:0; font:inherit; line-height:1.05; white-space:pre; overflow-x:auto; }
  #clock { color:var(--fg); text-shadow:0 0 12px rgba(126,231,135,.18); }
  #clock .colon { animation:blink 1s steps(1,end) infinite; }
  @keyframes blink { 0%{opacity:1} 50%{opacity:.15} 100%{opacity:.15} }
  @media (prefers-reduced-motion: reduce) { #clock .colon { animation:none; } }
  h2 { font-size:11px; letter-spacing:1.1px; text-transform:uppercase; color:var(--dim);
       font-weight:600; margin:26px 0 10px; }
  #cal { color:var(--fg); }
  #cal .today { color:#0d1117; background:var(--fg); border-radius:3px; }
  #cal .head { color:var(--accent); }
  #cal .dim { color:var(--dim); }
  .foot { color:var(--dim); font-size:11px; margin-top:18px; line-height:1.7; }
  .foot code { color:var(--fg); }
  .kv { display:flex; gap:22px; flex-wrap:wrap; color:var(--dim); font-size:11.5px; margin-top:12px; }
  .kv b { color:var(--fg); }
</style>
</head><body>
<div class="wrap">
  <div class="bar">
    <span><b id="tz">…</b> <span id="off"></span></span>
    <span id="stamp">…</span>
  </div>
  <div class="pane">
    <pre id="clock"></pre>
    <div class="kv">
      <span>kolkata <b id="kol">…</b></span>
      <span>utc <b id="utc">…</b></span>
      <span>day <b id="day">…</b></span>
    </div>
  </div>

  <h2>this month, where you are</h2>
  <pre id="cal"></pre>

  <div class="foot">
    Rendered by your browser from <code>Intl.DateTimeFormat()</code> — the timezone is read from
    your own device, nothing is sent anywhere. The profile README cannot do this: its images are
    SVG inside <code>&lt;img&gt;</code>, fetched through GitHub's proxy, so they can only ever show
    the server's clock at the moment the page loaded.
  </div>
</div>

<script>
const G = {
  "0": ["████", "█  █", "█  █", "█  █", "████"],
  "1": ["   █", "   █", "   █", "   █", "   █"],
  "2": ["████", "   █", "████", "█   ", "████"],
  "3": ["████", "   █", "████", "   █", "████"],
  "4": ["█  █", "█  █", "████", "   █", "   █"],
  "5": ["████", "█   ", "████", "   █", "████"],
  "6": ["████", "█   ", "████", "█  █", "████"],
  "7": ["████", "   █", "   █", "   █", "   █"],
  "8": ["████", "█  █", "████", "█  █", "████"],
  "9": ["████", "█  █", "████", "   █", "████"],
  ":": ["    ", " ██ ", "    ", " ██ ", "    "],
  " ": ["    ", "    ", "    ", "    ", "    "],
};

function bigText(str) {
  const rows = ["", "", "", "", ""];
  for (const ch of str) {
    const g = G[ch] || G[" "];
    for (let r = 0; r < 5; r++) rows[r] += g[r] + " ";
  }
  return rows.join("\n");
}

function pad(n) { return String(n).padStart(2, "0"); }

const fmtTime = (tz) => new Intl.DateTimeFormat("en-GB", {
  hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false, timeZone: tz,
});
const fmtDate = (tz) => new Intl.DateTimeFormat("en-GB", {
  day: "2-digit", month: "short", year: "numeric", timeZone: tz,
});

function offsetLabel(tz, date) {
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: tz, timeZoneName: "shortOffset" })
    .formatToParts(date);
  const t = parts.find(p => p.type === "timeZoneName");
  return t ? t.value.replace("GMT", "UTC") : "";
}

function renderCalendar(now, tz) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: tz, year: "numeric", month: "numeric", day: "numeric", weekday: "short",
  }).formatToParts(now);
  const get = (t) => parts.find(p => p.type === t)?.value;
  const year = +get("year"), month = +get("month") - 1, today = +get("day");

  const monthName = new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: tz })
    .format(now);

  // first weekday of the month, in the visitor's timezone
  const first = new Date(Date.UTC(year, month, 1, 12));
  const wdIndex = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
  const startIdx = wdIndex[new Intl.DateTimeFormat("en-US", { timeZone: tz, weekday: "short" }).format(first)];
  const daysInMonth = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();

  const lines = [];
  lines.push("  " + monthName);
  lines.push("  " + "─".repeat(28));
  lines.push("  su  mo  tu  we  th  fr  sa");
  let row = "  " + "    ".repeat(startIdx);
  for (let d = 1; d <= daysInMonth; d++) {
    const cell = (d === today) ? "[" + pad(d) + "]" : " " + pad(d) + " ";
    row += cell;
    if ((startIdx + d) % 7 === 0) { lines.push(row.replace(/\s+$/, "")); row = "  "; }
  }
  if (row.trim()) lines.push(row.replace(/\s+$/, ""));
  return lines.join("\n");
}

function tick() {
  const now = new Date();
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;

  const t = fmtTime(tz).format(now).replace(/:/g, ":");   // hh:mm:ss
  document.getElementById("clock").textContent = bigText(t);

  document.getElementById("tz").textContent = tz;
  document.getElementById("off").textContent = offsetLabel(tz, now);
  document.getElementById("stamp").textContent = fmtDate(tz).format(now) + " · " + fmtTime(tz).format(now);

  document.getElementById("kol").textContent = fmtTime("Asia/Kolkata").format(now) + " IST";
  document.getElementById("utc").textContent = fmtTime("UTC").format(now);
  document.getElementById("day").textContent =
    new Intl.DateTimeFormat("en-GB", { weekday: "long", timeZone: tz }).format(now);

  const cal = renderCalendar(now, tz);
  // highlight today inside the calendar text without innerHTML
  const calEl = document.getElementById("cal");
  calEl.textContent = cal;
}
tick();
setInterval(tick, 1000);
</script>
</body></html>
"""


def build(out=DEFAULT_OUT):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(PAGE)
    print(f"{out}: {len(PAGE)/1024:.0f} KB")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
