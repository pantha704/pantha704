# Where the animations come from

Every animation in `assets/frames/` was recorded from a live source and rebuilt into an SVG by
`tools/build_tui_svg.py`. Nothing is hand-drawn here.

| Source | What it is | License | How we take it |
| --- | --- | --- | --- |
| [ascii.live](https://ascii.live) · [hugomd/ascii-live](https://github.com/hugomd/ascii-live) | The original: ~93 animations served as a terminal stream | **GPL-3.0** | `tools/capture_frames.py <name>` — the frames are Go programs, so each one is played and recorded |
| [ascii.rest](https://ascii.rest) | 240 pieces, each a tiny procedural module | **MIT** | `tools/pull_ascii_rest.py <name>` — imports the module, samples it over time |

## ascii.live is GPL-3.0 — the repo has no licence

Worth knowing, not worth panicking about: the majority of the pool is GPL-3.0 art, and this repo
carries no `LICENSE` file at all. Redistributing those frames without a licence that permits it is
the gap. Two clean fixes, either is fine:

1. add `LICENSE` = GPL-3.0 (simplest, matches the dominant source), or
2. keep the repo unlicensed and treat the frames as local-only — but they are committed, so this
   one is only honest if the frames come out.

The ascii.rest pieces added later are MIT, which asks for attribution and nothing else — this file
is that attribution.

## Sources checked and not used

| Source | Why not |
| --- | --- |
| [ascii.theater](https://ascii.theater) (MSCHF) | Full films streamed as ASCII. Copyright status is exactly as dubious as it looks |
| [gabe565/ascii-movie](https://github.com/gabe565/ascii-movie) | Star Wars over SSH/telnet, GPL-3.0 — a 12-minute linear movie, not a loop |
| [16colo.rs](https://16colo.rs) | The ANSI/ASCII artpack archive, 1990s → today, ~4.5 GB, has a real API. Static art in CP437 with colours, not animation — wrong shape for this slot, right shape for a gallery |
| [ascii-magic.com](https://www.ascii-magic.com/ascii) | 734 animated pieces, MIT, but the assets are behind a JS bundle with no stable per-piece URL. Needs browser capture |
| [asciiart.eu/animations](https://asciiart.eu/animations) | Fire, plasma, matrix rain, starfield — all canvas toys driven by JS, no frame text to take |
| [addyosmani/firew0rks](https://github.com/addyosmani/firew0rks) | MIT and directly usable (150 numbered `.txt` frames per animation), but ~46 KB per frame — would need downsampling before it fits the canvas |
