---
name: reel-mograph
description: >-
  Render a code-driven motion-graphics film (animated typography / kinetic UI / brand graphics)
  with no real footage. Use when the user wants a campaign/feature/launch film built from
  animation rather than clips. Authors a GSAP timeline in an HTML page, renders it frame-by-frame
  through headless Chromium with motion-blur supersampling, builds a sound-design track from an
  SFX manifest, then grades + muxes with ffmpeg. Can batch-render many films serially.
---

# Motion-graphics film

Build films that are *drawn in code*, not filmed. Deterministic, frame-perfect, buttery.
Each film is one self-contained HTML page; the renderer steps it frame by frame.

## When to use
- Animated typography, kinetic feature explainers, brand/launch films, logo reels.
- No real footage needed (or only stills used as graphic elements).
If the user has real video clips of a person/product, use **reel-liveaction** instead.

## Pipeline (run in order)

**1. Author the film as an HTML page.** Copy `templates/mograph.index.html` to
`<film>/index.html`. It MUST expose four globals the renderer drives:
- `window.__duration` — film length in seconds
- `window.__seek(t)`  — set the GSAP timeline to exactly time `t` (use `tl.seek(t)` / `tl.pause()`)
- `window.__ready`    — set `true` once fonts + images are loaded
- `window.__audio`    — array of `{type, t, g?}` sound cues (type resolves via sfx manifest)
Animate with GSAP. Keep everything full-bleed (no dead margins). Drive lines/words on the beat.

**2. Preview before rendering** (cheap sanity check):
```
node ${CLAUDE_PLUGIN_ROOT}/scripts/shot.js <film>/index.html /tmp/pv 1.8 4.8 7.5 ...
```
Screenshot 10–14 timestamps covering every scene + climax + endcard; it prints `DONE errs=[...]`
which MUST be `[]`. Montage the stills into a contact sheet and READ it like a director: layout,
readability (shoot t and t+1.8 for key lines — same settled frame = long-enough hold), no ghost
text, endcard spacing. Iterate here — it's ~100× cheaper than a render.

**3. Full render** at supersample 2 (true motion blur):
```
node ${CLAUDE_PLUGIN_ROOT}/scripts/render_mograph.js <film>/index.html <film>/frames 1080 1920 30 2
```
Renders at fps×ss; ffmpeg later blends every `ss` frames (`tmix`) into real motion blur.
**Faster:** use `render_par.js <...> <workers>` to split frames across N pages (~N× speedup; the
default worker count is RAM-aware). Both print a `STATS` line (frames, elapsed, s/frame) when done.
See the README "Parallel rendering" section for the per-RAM concurrency budget and running multiple
films across sessions/machines (each film is independent — split via the `FILMS` env in render_all.sh).

**4. Build the sound-design track** (no music bed — pure SFX from a CC0 manifest):
```
node ${CLAUDE_PLUGIN_ROOT}/scripts/build_audio.js <film>/index.html <film>/audio.wav
```
Reads `window.__audio` cues, resolves each `type` through `sfx/manifest.json`, applies per-hit
pitch + pan so repeats never sound identical, over a subtle ambient bed. For **beat-locked reels**
pass `MUSIC_BED=<track>` — the track becomes the bed itself (prominent, cues sit on its beats,
master loudnormed to −14 LUFS). No SFX library? `scripts/gen_sfx.sh` synthesizes a deterministic,
license-clean kit with ffmpeg alone (`templates/sfx.manifest.example.json` shows the manifest shape).

**5. Grade + mux** (one ffmpeg pass — see `templates/mograph.build.sh`):
```
ffmpeg -y -framerate 60 -i <film>/frames/%05d.png \
  -vf "tmix=frames=2:weights='1 1',fps=30,eq=...,curves=...,noise=...,vignette=PI/4.5,format=yuv420p" \
  -c:v libx264 -crf 17 -preset slow <film>/silent.mp4
ffmpeg -y -i <film>/silent.mp4 -i <film>/audio.wav -c:v copy -c:a aac -b:a 192k -shortest <film>/<name>.mp4
```

**6. Batch many films** — render STRICTLY SERIALLY (one Chromium at a time on low-RAM machines).
Adapt `templates/render_all.sh`: loop films, kill stray Chromium between each, wipe `frames/`
after each to free disk, recompress anything >60 MB, copy finals to the delivery folder, retry once.

## Quality checklist — apply to EVERY film

Load `skills/cinematography` for the look and `templates/brandkit.json` for the brand system.
For 30s campaign reels, load `skills/reel-scripting` FIRST (music-first beat grid, bar-addressed
script, motion vocabulary, sound budget) and `skills/asset-casting` if real photos are needed. Then:
- **Hook (first ~1.5s):** biggest word/number/image on frame 1 — no slow fade-in. Social videos win in the first second.
- **Safe margins:** keep all text inside `brandkit.safe_area` (top 10% / bottom 18% / sides) — platform UI covers the edges.
- **Sound-off captions:** most viewers are muted → burn captions with `scripts/captions.py` (sits in the bottom safe area).
- **Endcard + CTA:** end on the brand lock — logo + tagline + CTA ("link in bio") + an audio **sting**.
- **Music bed:** SFX-only feels thin. Pass `MUSIC=bed.mp3 STING=sting.wav` to the build → a beat-matched bed under the SFX + a closing stab. (Biggest perceived-quality lift.)
- **Exposure floor:** the build grade lifts blacks so nothing reads muddy/underexposed.
- **Typography & motion:** one type pairing, strong size/weight hierarchy; physics easing + stagger + parallax depth (not flat moves).
- **Brand consistency:** same palette/type/logo across all films so they read as one campaign.

## Why it looks expensive
- **Deterministic stepping** (`__seek` per frame), not screen-recording → frame-perfect, machine-independent.
- **Supersample + tmix** → genuine motion blur you can't fake in a single render.
- **Filmic grade + grain + vignette** on top, identical across every film → one house style.

## Requirements
`ffmpeg`, Node with `playwright` (run `npx playwright install chromium` once), a `sfx/manifest.json`.

## Read this before you start
`${CLAUDE_PLUGIN_ROOT}/LESSONS.md` — RAM/serial-render limits, frame cleanup, >60MB recompress,
font/image readiness gotchas. Append new fixes you discover.
