---
name: reel-scripting
description: >-
  Music-first, beat-locked production scripting for motion-graphics reels — and the multi-agent
  workflow for building several reels in parallel without quality loss. Use BEFORE reel-mograph
  when the job is a campaign (one or more 30s reels): pick the track, extract the real beat grid,
  write a bar-addressed production script per reel, then build each reel in an isolated dir with
  preview-only self-verification and render centrally.
---

# Beat-locked scripting & multi-reel production

The single biggest quality lever we found: **pick the music first, script to its bars, lock every
cut and cue to real beat times.** A reel scripted "by feel" and scored afterwards always reads
loose; a bar-addressed script re-locked to a librosa grid reads like an edit.

## 1. Music-first workflow

1. Gather candidate tracks, analyze all of them (`scripts/extract_beats.py <mp3>` → tempo, beat
   times, RMS energy). Pick per reel by energy arc, not genre labels.
2. Cut a working bed (`music.wav`, ~duration+3s) starting at an energetic bar; re-extract beats
   from the CUT file and save `beats.json` (`{src, start_in_src, tempo, beats:[...]}`).
3. **Verify the WAV's decoded duration with ffprobe** — source mp3s can be corrupt partway and
   header duration lies. If short, bar-loop extend: append the segment between two late downbeats
   with a ~10ms crossfade, then re-extract beats (a clean loop lands within ~10ms of linear
   extrapolation, so cues usually survive).
4. Downbeats = every 4th beat from `beats[0]` (confirm by ear/energy). Scene cuts go ON downbeats;
   entrances on beats/half-beats; the drop on the act-3 downbeat.

## 2. The script system (one BRIEF, N SCRIPTs)

Write one shared **BRIEF.md** (brand system, motion vocabulary, sound families, pacing standard)
and one **SCRIPT.md per reel** that complies with it. A SCRIPT.md must contain — exhaustively:
concept · music direction (BPM + where the drop lands) · grade/color plan · scene-by-scene with
time ranges **in bars+seconds**, exact px layouts (1080×1920), every entrance/hold/exit by
vocabulary name, every sound cue with time+gain · climax spec frame-by-frame · endcard px spec ·
copy deck · asset list · character. Bar-addressed times let you re-lock the whole script to any
real grid later.

**Motion vocabulary** (name the moves; scripts reference them):
`slideIn/slideOut` (words in from right / out to left, power4 — conveyor logic), `wavyIn/wavyOut`
(word-by-word rise, back.out(1.5) — NEVER elastic on text), `popIn` (scale .42→1, back.out(2.4)),
3D card entrances (rotateX/z + blur→sharp), `beatWave` (held text hops 12–17px on strong beats
with a `thunk` tap — give the hop meaning, don't decorate), color-shutter logo (flick 8–10 tint
variants ~45ms apart with click ticks → SLAM brand color on a drop).

**Pacing standard:** 28–34s total, ~2 bars per scene, ≤8 scenes, one idea per scene, every message
readable ≥2s, elements DEAD-STILL during holds (the tmix motion-blur pass smears any drift).
Arc: build → climax on the drop → proof → endcard (logo + one tagline + URL, nothing else).

**Sound budget:** max 3 swooshes (act boundaries only); rich drop = boom(1.0) + boom+12ms(0.6) +
hit(0.58), used at THE climax and logo-lock only; thunks only via beat-hops; every cue must have a
visible cause on screen.

## 3. Multi-reel build (parallel agents, serial renders)

When building N reels, give each its own agent and directory — never share state:

- Each builder gets: its SCRIPT.md, the BRIEF, a proven base rig HTML to copy patterns from, its
  own `reel_x/` dir with `music.wav` + `beats.json`, and its curated asset folder.
- First job: **re-lock** every bar-addressed time in the script to the real `beats.json` grid and
  document the mapping in a file-header comment.
- Builders are **preview-only**: verify with `scripts/shot.js` (screenshot N timestamps, must print
  `DONE errs=[]`), montage the stills into a contact sheet, and READ it like a director —
  layout px, ≥2s readability (shoot t and t+1.8 for key lines), no ghost text, climax frame,
  endcard spacing. Iterate until it passes.
- Builders must NEVER run the full renderer and NEVER `pkill` Chromium (it kills sibling agents'
  browsers). The parent reviews every contact sheet itself, then renders **serially**, one reel at
  a time, wiping `frames/` between runs.
- Final QA is done on the **rendered mp4** (`ffmpeg -ss T -i out.mp4 -frames:v 1`), never only the
  preview — stateful render pages and overlapping tweens produce artifacts previews can't show.

## Read this before you start
`${CLAUDE_PLUGIN_ROOT}/LESSONS.md` — ghost-bleed rules, seek-safe counters, corrupt-bed fix,
readability lessons. Append new fixes you discover.
