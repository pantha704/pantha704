### pratham jaiswal

`systems & automation` · `rust` · `typescript` · `python` · `go`

[resume](./resume/Pratham-Jaiswal-Resume.pdf) · [detailed](./resume/Pratham-Jaiswal-Resume-detailed.pdf) · [mail](mailto:pratham.jaiswal2004@gmail.com) · [linkedin](https://www.linkedin.com/in/pantha704) · [x](https://twitter.com/pantha704)

[![pratham@kolkata — a terminal cycling through profile, upstream work, projects, stack and the ascii terminal](./assets/hero.svg)](https://pantha704.github.io/pantha704/)

<table>
<tr>
<td valign="top">

<kbd>~/profile</kbd><br>
<kbd>├─ README.md</kbd><br>
<kbd>├─ upstream/</kbd><br>
<kbd>├─ projects/</kbd><br>
<kbd>├─ stack.md</kbd><br>
<kbd>└─ terminal.md</kbd><br>
<br>
<sub>↑ folders<br>click a path →</sub>

</td>
<td valign="top">

<details open>
<summary><kbd>~/profile/README.md</kbd> — automation + vulnerability reporting</summary>

- systems and automation engineer. day job is automation and vulnerability reporting at **braid-forbes**; the rest is upstream compiler, tooling and frontend work.
- b.tech, sister nivedita university, 2023–2027 (ISC science, 85%, 2023).
- kolkata, india. open to systems, devtools and infrastructure work — [mail](mailto:pratham.jaiswal2004@gmail.com) is fastest.

</details>

<details>
<summary><kbd>~/upstream/</kbd> — <!--upstream:start-->19 merged · 10 repositories · 14 open<!--upstream:end--></summary>

| repository | pr | what changed |
| --- | --- | --- |
| [rust-lang/rustc_codegen_cranelift](https://github.com/rust-lang/rustc_codegen_cranelift/pull/1625) | `#1625` | CI runner disk exhaustion broke abi-cafe tests — ported the cleanup workflow |
| [CCExtractor/ccextractor](https://github.com/CCExtractor/ccextractor/pull/2378) | `#2378` | tx3g subtitle times wrong on the FFmpeg MP4 path — demuxer trusted a shared timing pointer |
| [google-deepmind/open_spiel](https://github.com/google-deepmind/open_spiel/pull/1455) | `#1455` | legacy TensorFlow 1.x deep-RL examples → PyTorch |
| [pytorch/ao](https://github.com/pytorch/ao/pull/3709) | `#3709` | documented `FqnToConfig` and MoE parameter quantization |
| [CircuitVerse/cv-frontend-vue](https://github.com/CircuitVerse/cv-frontend-vue/pulls?q=is%3Apr+author%3Apantha704+is%3Amerged) | `×6` | dropped jQuery from engine/setup/minimap, ported four modules to TypeScript |
| [Bijoy99roy/scheduler](https://github.com/Bijoy99roy/scheduler/pull/7) | `#7` `#13` | telemetry + retry, persistent queue storage |

<sub>Every link here opens without an account, and the counts include only repositories a visitor can open. Private client work — Razorpay payment flow, video quality scoring, Android release tooling — is excluded.</sub>

**in flight** — [rust-clippy](https://github.com/rust-lang/rust-clippy/pull/16375) `#16375` type-based checks in `arithmetic_side_effects` · [wagtail](https://github.com/wagtail/wagtail/pull/13708) `#13708` `#13709` comment textarea overflow, tooltip styles · [gatsby](https://github.com/gatsbyjs/gatsby/pull/39703) `#39703` `assetPrefix` in manifest icon paths · [scancode-toolkit](https://github.com/aboutcode-org/scancode-toolkit/pull/4765) `#4765` `#4766` OSGi/.bnd parsing, authenticated Git deps

</details>

<details>
<summary><kbd>~/projects/</kbd> — 5 shipped</summary>

| project | stack | what it is |
| --- | --- | --- |
| [Perfume Store](https://github.com/pantha704/perfume-store) | TypeScript · Next.js | production commerce system — catalogue, admin console, dispatch, India Post integration, 60+ reviewed PRs |
| [Homeworker](https://github.com/pantha704/home-worker) | Python | local-first pipeline: PDF and image input to reviewable A4 notes in licensed handwriting typefaces |
| FlowForge | Next.js · Upstash QStash | serverless automation separating frontend events from durable background jobs |
| [MacFolio](https://mac-folio-three.vercel.app) | React · Zustand · GSAP | macOS simulation in the browser — draggable, resizable windows with window-manager state |
| Turbin3 · Solana | Rust · Anchor | Q4 '25 Builder + Q1 '26 Accelerate — NFT marketplaces, staking, vaults, escrow, AMMs |

</details>

<details>
<summary><kbd>~/stack.md</kbd> — what I reach for</summary>

`rust` (compiler internals) · `typescript` · `python` · `go` · `solidity` · `next.js` · `react` · `node` · `anchor` · `prisma` · `postgresql` · `redis` · `docker` · `linux` · `github actions` · `n8n` · `monday.com` · `playwright`

</details>

<details>
<summary><kbd>~/terminal.md</kbd> — the animation</summary>

![a random ascii animation — different on every load](http://57.131.133.151:8080/tui.svg)

Frames captured once from [ascii.live's animation list](https://ascii.live/list) into [`assets/frames/`](assets/frames); the server picks a random one per request, so a reload gets a different animation. GitHub strips `<script>`, `<iframe>` and inline SVG from READMEs, so this pane folds open instead of swapping. The same frames play locally:

```bash
python3 tools/play.py            # random animation each run
python3 tools/play.py --name nyan
python3 tools/play.py --list
```

Capture any of ascii.live's ninety-odd animations with `python3 tools/capture_frames.py <name>`; rebuild the panels with `python3 tools/build_tui_svg.py --all` and `python3 tools/build_hero_svg.py`.

</details>

</td>
</tr>
</table>

---

<sub><!--stats:start--><code>19 merged · 10 repos · 14 open · checked 23 Oct 2026</code><!--stats:end--> — the hero above and these numbers are rebuilt daily from the GitHub API by <a href="tools/refresh_stats.py">tools/refresh_stats.py</a>. The hero cycles the five panes on its own; click a path in the pane to unfold that folder.</sub>
