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
node ${CLAUDE_PLUGIN_ROOT}/scripts/render_mograph.js <film>/index.html <film>/frames 1080 1920 30 1
```
Render a couple of frames or a low-ss pass and READ them. Fix layout/timing in the HTML.

**3. Full render** at supersample 2 (true motion blur):
```
node ${CLAUDE_PLUGIN_ROOT}/scripts/render_mograph.js <film>/index.html <film>/frames 1080 1920 30 2
```
Renders at fps×ss; ffmpeg later blends every `ss` frames (`tmix`) into real motion blur.

**4. Build the sound-design track** (no music bed — pure SFX from a CC0 manifest):
```
node ${CLAUDE_PLUGIN_ROOT}/scripts/build_audio.js <film>/index.html <film>/audio.wav
```
Reads `window.__audio` cues, resolves each `type` through `sfx/manifest.json`, applies per-hit
pitch + pan so repeats never sound identical, over a subtle ambient bed. Requires a `sfx/`
folder with `manifest.json` at the working root (ship your own CC0 SFX library).

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

## Why it looks expensive
- **Deterministic stepping** (`__seek` per frame), not screen-recording → frame-perfect, machine-independent.
- **Supersample + tmix** → genuine motion blur you can't fake in a single render.
- **Filmic grade + grain + vignette** on top, identical across every film → one house style.

## Requirements
`ffmpeg`, Node with `playwright` (run `npx playwright install chromium` once), a `sfx/manifest.json`.

## Read this before you start
`${CLAUDE_PLUGIN_ROOT}/LESSONS.md` — RAM/serial-render limits, frame cleanup, >60MB recompress,
font/image readiness gotchas. Append new fixes you discover.
