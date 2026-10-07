<p align="center">
  <img src="docs/images/logo.svg" width="72" height="72" alt="BDO Texture AIO mark">
</p>

<h1 align="center">BDO Texture AIO</h1>

<p align="center"><strong>AI upscaling for Black Desert Online world textures.</strong></p>

<p align="center">
  Landscape, buildings, props, NPCs, and optional mounts by default. Opt-in bodies mode<br>
  enhances the bodies you already chose in BDO-AIO. Opt-in player/GPT mode handles<br>
  playable-class <code>p*</code> textures. Results stage for Meta Injector.
</p>

<p align="center">
  <a href="https://github.com/SenjuWoo/BDO-TEX-AIO/actions/workflows/ci.yml"><img src="https://github.com/SenjuWoo/BDO-TEX-AIO/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-c9a227?labelColor=0c0f12" alt="MIT License"></a>
  <a href="https://github.com/SenjuWoo/BDO-TEX-AIO/releases/tag/v1.5.1"><img src="https://img.shields.io/badge/release-v1.5.1-d4af37?labelColor=0c0f12" alt="v1.5.1"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick start</a>
  ·
  <a href="#blank-output-trap">Blank-output trap</a>
  ·
  <a href="#safety-summary">Safety</a>
  ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

Double-click **`START.bat`**. Latest release: [v1.5.1](https://github.com/SenjuWoo/BDO-TEX-AIO/releases/tag/v1.5.1).

This git tree has no application screenshot. The UI is the `START.bat` / `bdo_tex.ps1` console menu.

## Relationship to BDO-AIO (choices always win)

| App | Owns |
| --- | --- |
| **BDO-AIO** | Body / pube / genital / outfit **choices** |
| **BDO-TEX-AIO** (this) | World / environment; optional NPC skins; optional higher-res of the **same** chosen bodies |

This tool:

- **Never** includes playable-class `character/texture/p*` assets unless you opt in (`[G]` / `includePlayerTextures` — for a GPT/texconv pass)
- **By default** skips LODs / SpeedTree **billboards** / impostors (optional high toggle `[L]` / `includeLodBillboards`)
- **Never** overwrites a path already present in `files_to_patch` (AIO, bodies, …)
- **Never** writes into the BDO-AIO install folder
- Writes only `files_to_patch\_bdo_tex_upscale\` (world) and `files_to_patch\_bdo_aio_bodymats\` (bodies mode)

So after you pick bodies in BDO-AIO, TEX will not stomp those choices. Paths AIO (or the bodies layer) already staged are **skipped** at stage time — even in player mode.

## Quick start

1. Install Python 3, Pillow, numpy, and Upscayl (CLI inside the install).
2. Copy `config.example.json` → `config.json` and set `gameDir` to your Black Desert install.
3. Double-click **`START.bat`**, or:

```bat
pip install pillow numpy
python tools\bdo_tex.py status
python tools\bdo_tex.py scan
python tools\body_mats.py status
```

Recommended run order:

```text
1. BDO-AIO          pick + DEPLOY bodies/pubes/outfits
2. BDO-TEX-AIO      this app — [Y] bodies (optional), then world textures
3. PartCutGen       if you use it
4. Meta Injector    once on the game Paz folder
```

TEX can be processed anytime (scan/upscale are self-contained under `work\`), but **stage after AIO deploy** so collision checks see AIO paths and skip them.

## Pipeline

```text
pad00000.meta -> scan -> extract -> upscale -> companions(match) -> pack -> stage
```

| Step | What |
| --- | --- |
| Scan | Eligible colour textures under configured roots |
| Extract | PAZ → PNG (mip 0) |
| Upscale | Upscayl on **RGB only**, alpha re-attached after; every output blank-checked. Or **GPT mode**: export → your own GPT batch → `pack --source gpt` |
| Companions | Resize **existing** `_n`/`_sp`/… that already exist in the archive |
| Pack | DDS + full mips |
| Stage | Only unclaimed world paths → `_bdo_tex_upscale` |

**Companions:** only maps already in `pad00000.meta` for that albedo. Inventing new `_n` fails Meta Injector (not in meta). No ParallaxGen equivalent for BDO.

## GPT / player-texture mode (opt-in)

World textures are the default. Playable-class `character/texture/p*` is BDO-AIO territory, so this tool stays out unless you say otherwise. Press `[G]` (or set `includePlayerTextures: true` in config) to opt them back in for a GPT / external upscaler pass:

```text
[G] player mode on  ->  [1] scan  ->  [2] extract  ->  [A] export -> work\04_swarm_in + gpt-export.zip
     -> send work\gpt-export.zip to GPT / Codex (prompt: "upscale/enhance each PNG,
        keep filenames AND folder structure, return a zip")
     -> drop the returned zip anywhere, [B] prompts for its path
     -> [6] stage  ->  Meta Injector
```

- Zip round-trip: `[A]` also writes `work\gpt-export.zip`; `[B]` accepts the returned zip (`pack --source gpt --zip <file>`, zip-slip guarded) or Enter to keep the old folder flow (`work\05_swarm_out`).
- `texconv.exe` ships in `tools\` — pack uses bundled `dds.py`; texconv is there as an alternative for companion-map encoding if you configure it.
- Stage still skips any path BDO-AIO / BodyMats already claimed — AIO wins.
- Every GPT result is blank-checked before packing; all-black outputs are skipped, never shipped (same guard that caught Upscayl's silent blanks).
- Output format follows each texture's own header (DXT1/DXT5, full mips) — no manual format matching; the GPT PNG just needs to be ≥ the source size.
- Same folder flow works with SwarmUI / ComfyUI (`swarm-export`, `--source swarm`).

## Bodies mode (opt-in, replaces BDO-AIO-BodyMats)

BDO-AIO owns which bodies/pubes/outfits you use. **Bodies mode** only upscales the winner files AIO already staged into `files_to_patch` (layer priority: `_pubic_hair_` > `_genital_` > `_midnight_`), and resizes existing companion maps (`_n`/`_sp`/`_m`/…). It never invents maps and never writes into AIO's folders — the stage target is `files_to_patch\_bdo_aio_bodymats\`.

```text
[X] bodies on  ->  BDO-AIO must already be DEPLOYED
[Y] scan -> process -> stage   (writes _bdo_aio_bodymats only)
```

- Nude skin albedos upscale toward **4096**; other albedos toward **2048**.
- Only **existing** companion maps are resized — no invent (Meta Injector rejects paths not in `pad00000.meta`).
- Same safety rails as the world path: RGB-only upscale with alpha re-attached, blank-output check with LANCZOS fallback, DDS via bundled `dds.py` (no texconv needed).
- The old **BDO-AIO-BodyMats** app is merged into this tool (v1.5.0); run `python tools\body_mats.py status` for the same read-only view.

## Blank-output trap

Measured on this machine (RTX 4080 SUPER, 9800X3D), 150 real BDO textures per config, **every output checked for blankness**:

| Config | 5,187 textures | Output |
| --- | ---: | --- |
| `tile=400` (old default) | ~81 min | valid |
| `tile=auto` | **~54 min** | valid |
| `tile=1024` / `tile=2048` | ~10 min | **blank — all of it** |
| `upscayl-lite`, RGBA input | ~7 min | **blank (146/150)** |
| `upscayl-lite`, RGB input | **~21 min** | valid |

> **upscayl-bin can write a completely empty image, print `🙌 Upscayled Successfully!`, and exit 0.** Nothing in the exit code or the log tells you. Two triggers were reproduced: a large `-t`, and an RGBA input under load. Configs that looked 7× faster were fast because they were producing nothing.

So the pipeline now:

1. **Feeds RGB only.** Alpha is split off before the upscaler and re-attached with Lanczos afterwards. This removes the RGBA trigger *and* is the correct treatment anyway — alpha in these textures is a cutout mask, and an AI model invents soft edges on it.
2. **Blank-checks every output** during the resample pass (free — it is already decoding), retries the failures one at a time at `1:1:1`, and **refuses to write** anything still blank so `pack`/`stage` cannot ship invisible textures.

| Key | Default | Meaning |
| --- | ---: | --- |
| `upscaleBatch` | 256 | PNGs per Upscayl process. **Resume granularity, not a VRAM knob** — VRAM is set by tile and threads, so small batches only pay ~3s of process start-up each |
| `upscaylGpu` | `"0"` | GPU id (`-g`); empty = auto |
| `upscaylTile` | `0` | Tile size (`-t`); `0` = auto. **Do not raise this** — 1024/2048 produce blank images |
| `upscaylThreads` | `"2:4:2"` | load:proc:save (`-j`). Drop to `1:1:1` if blanks appear |

Upscayl uses **Vulkan/ncnn**, not CUDA. If a batch crashes outright (ACCESS_VIOLATION) it retries one file at a time; resume keeps finished raws.

**If it is still too slow:** preset `[P]` → *Fast (lite model)* uses `upscayl-lite-4x` (~21 min instead of ~54) with visibly softer detail. Model choice barely matters otherwise — when output is actually valid, every model lands in the 1.4–2.2 img/s band on this GPU.

## Defaults

- **Roots:** world only (`object/texture`, trees, terrain detail)
- **Character textures:** OFF (menu `[C]` to enable NPC/monster; player `p*` opt-in via `[G]`)
- **Target:** use menu `[P]` presets (playtest 1024, quality 2048, …)

## Menu

| Key | Action |
| --- | --- |
| `1`–`6` | Scan → extract → upscale → companions → pack → stage |
| `7` | Full pipeline |
| `A` | Export PNGs + `gpt-export.zip` for GPT / Codex / SwarmUI / ComfyUI |
| `B` | Pack from returned GPT zip (prompts for path; Enter = swarm folder) |
| `C` | Toggle character/texture (NPC/monster; not player classes) |
| `G` | Toggle player/GPT textures (playable `p*`; opt-in) |
| `X` | Toggle bodies (enhance BDO-AIO choices; **OFF** default) |
| `Y` | Run bodies pipeline: scan → process → stage (after AIO deploy) |
| `L` | Toggle LOD/billboards (**OFF** default; high option, low ROI) |
| `N` | Toggle companion-map matching |
| `P` / `T` / `M` | Preset / target / model |
| `R` | Remove `_bdo_tex_upscale` only |

## Requirements

- Python 3 + Pillow + numpy
- Upscayl (CLI inside the install)
- Meta Injector to apply `files_to_patch`
- Optional: GPT / SwarmUI / ComfyUI for the external-upscaler path

## Config

First run copies `config.example.json` → `config.json`. Set `gameDir` to your Black Desert install. Keep `workDir` as `"work"` (stays next to the app). Bodies mode keys: `bodiesEnabled` (menu `[X]`), `bdoAioRoot`, `skinAlbedoTarget` (4096), `otherAlbedoTarget` (2048), `allowPackFallback` (false), `stageLayerName` (`_bdo_aio_bodymats`), `bodyWorkDir` (`work_body`).

## Safety summary

| Rule | Enforced how |
| --- | --- |
| No player-class textures unless `[G]` opt-in | `texfilter` playable-class block + `includePlayerTextures` |
| AIO paths not overwritten | Stage skips any path owned by another layer |
| No invent materials | Companions = archive siblings only |
| Isolated work | All caches under app `work\` |
| Blank Upscayl/GPT output never ships | RGB-only feed + per-image blank check |

## Honest status

Verified in this tree:

- latest GitHub release **v1.5.1**
- CI (`.github/workflows/ci.yml`) — PowerShell parse + PSScriptAnalyzer, JSON, Python compile
- self-tests in `tools/test_bdo_tex.py` and `tools/test_body_mats.py` (filter rules, collision guard, blank detection, pack skip)
- blank-output timings above are from the author's RTX 4080 SUPER / 9800X3D measurements, not a claim about every GPU

Not claimed:

- a GUI screenshot (console menu only)
- that GPT/Codex upscale quality is verified beyond the blank-check
- that every world texture in a live PAZ has been upscaled in CI

## License

[MIT](LICENSE)
