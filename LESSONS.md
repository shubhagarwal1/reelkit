# LESSONS — append-only fixes the skills must not relearn

This file is the plugin's memory. Every time a render fails and you fix it, add a one-line rule
here. Both skills tell Claude to read this before starting. Newest at the bottom.

## Audio
- **Never reuse an ffmpeg filter label.** Sidechain + amix on the same `[vo]` label is invalid and
  the stream silently drops → inaudible voice. Use `asplit=2[v1][v2]` to duplicate first.
- **Fill silent holes.** A demucs instrumental is silent wherever the original was voice-only.
  Loop/tile the densest section to cover the full duration, or the music drops out mid-reel.
- **Audio length must equal video length.** If the mix is shorter, `-shortest` clips your end card.
  Trim/pad the mix to the exact `duration`.
- **Gentle ducking, not hard.** Sidechain at ratio ~2.2 + makeup gain keeps the song present under
  dialogue. Hard ducking makes lines "lose the song completely."
- **Verify the song is actually the song.** Cross-correlate a candidate track against the reference
  before trusting it; a random MP3 correlates ~0 (noise).
- **Ad-libs live in the vocals stem.** The verse is the long take (0–11s); outro ad-libs are the
  short staccato bursts after. Pull them from `vocals.wav` and replace at original timestamps.

## Person matte (rembg)
- **Force CPU on macOS:** CoreML model-save fails. Set `ONNXRUNTIME_EXECUTION_PROVIDERS=CPUExecutionProvider`
  and `new_session('u2net_human_seg', providers=['CPUExecutionProvider'])`.
- **One matte per shot, not per frame.** Per-frame rembg is ~3s/frame (~35 min/reel, often dies).
  Matte a representative frame; for stills, matte the source then apply the SAME Ken-Burns move so
  the matte tracks the zoom. ~8 inferences ≈ 30s.
- **Split front vs behind text.** Putting ALL text behind hides lower-third captions behind the body.
  Big words/title go behind; captions/footers draw in front AFTER compositing.

## Encoding
- **Grain kills compression.** Film grain at CRF 18 ballooned a 30s reel to ~98 MB. Re-encode the
  final mux at CRF 23 (still clean) → ~12 MB.

## Motion-graphics rendering
- **Render serially on low RAM.** One headless Chromium at a time (8 GB limit). Kill stray Chromium
  between films, wipe `frames/` after each to free disk, recompress finals >60 MB.
- **Wait for readiness.** Renderer must wait for `window.__ready`, `document.fonts.ready`, and image
  decode, then 2× rAF after each `__seek`, or frames capture mid-layout.
- **Supersample for motion blur.** Render at fps×2, blend with `tmix=frames=2` → real motion blur.
- **`window.__seek` must call `tl.seek(t, false)`.** GSAP's `seek()` SUPPRESSES callbacks by default, so any `onUpdate`-driven value (animated counters, dynamic text) silently freezes at its initial value across every rendered frame. Pass `false` (don't-suppress) so callbacks fire per-frame. Property tweens render fine either way — only callback-driven animation breaks, so it's easy to miss until you watch the output.
- **The screenshot is ~86% of render time** (measured: 1446ms PNG vs 32ms seek + 164ms rAF per frame @1080×1920). **Write JPEG q92, not PNG** → ~2.7× faster (535ms), invisible after grade+grain. 720×1280 is another ~2×. This is the #1 speed lever.

## Quality / craft
- **Lighting & angle are capture-time, not post.** You can't relight flat footage — specify it in the
  generation prompt (cinematography skill). Score takes with `score_shots.py`; keep the best-lit/framed.
- **Lift the black floor in every grade** — raw output read muddy/underexposed on some films. Mood
  presets in build_edit.py and the mograph grade both raise blacks.
- **Made-for-social basics matter as much as the visuals:** hook on frame 1, keep text inside the
  safe area (platform UI covers edges), burn sound-off captions, end on a brand lock + CTA + sting,
  and put a music bed under SFX-only mograph (biggest perceived-quality lift).

## Environment
- macOS has no `timeout` command by default — don't wrap commands in it.
- zsh does not word-split unquoted `$var` in `for` loops, and errors on empty globs; pass explicit
  values or guard globs.

## GSAP timeline / ghost bleed
- **Hard-clear every text container after its exit.** Overlapping in/out word tweens re-stamp
  "exited" text (an in-tween ending after the out-tween resurrects it), and parallel render
  workers reuse stateful pages that cache it. Child tweens can't override a parent's opacity, so
  after each exit add `tl.set(container, {opacity:0}, afterExitTime)` — belt-and-braces on top of
  `overwrite:"auto"` on exits.
- **`fromTo` needs `immediateRender:false`.** A `fromTo` with visible from-vars paints at t=0 and
  bleeds over every earlier scene (two independent builds hit this: a giant blurred headline and a
  gray flash washing all pre-drop scenes). Any `fromTo`/`from` scheduled mid-timeline gets
  `immediateRender:false`.
- **`window.__seek` arrow must have braces:** `(t)=>{ tl.time(t) }`. The brace-less form returns
  the timeline and can hang the renderer's evaluate.
- **Counters must be seek-safe.** Drive rolling numbers from timeline progress (frame-stepped
  `textContent` inside an onUpdate on a tween that the seek replays), never from wall-clock or
  accumulators — parallel workers seek non-contiguous frames.
- **Verify from the RENDERED mp4, not the preview.** `ffmpeg -ss T -i out.mp4 -frames:v 1` at
  scene boundaries and holds. Static previews on a fresh page hide state bugs; and what looks like
  a ghost in one frame may be a legitimate motion-blurred exit — check t±0.6s before "fixing" it.

## Music & beats
- **Music first, script in bars, re-lock to the real grid.** Scripts written at a nominal BPM
  transfer cleanly to the real track if every time is bar-addressed; re-lock cuts/cues to librosa
  beat times (downbeats = every 4th beat) and document the mapping in the file header.
- **ffprobe duration on mp3s lies.** A bed source died decoding at 23.8s of a "60s" file
  ("invalid new backstep"). Always ffprobe the CUT WAV; if short, bar-loop extend (append the
  span between two late downbeats with a ~10ms crossfade) and re-extract beats — a clean loop
  matched linear extrapolation within 7ms, so no cue re-lock was needed.
- **Beat-hops need meaning and one voice.** Held-text hops land on strong beats with a `thunk`;
  when two lines bounce over the same window, only ONE fires cues or every tap doubles.
- **Elastic ease on text reads as wobble.** Use `back.out(1.5)` for word rises; save elastic for
  props, if anything.

## Readability & holds
- **28–34s, ~2 bars/scene, every message ≥2s.** A 15s "dense" cut read as unwatchable; re-timing
  the same content to 2 bars/scene fixed it without any redesign.
- **Dead-still holds.** Perpetual float/drift during holds smears under tmix motion blur and reads
  as "quality dropping". Motion belongs to entrances/exits/beat-hops only.
- **Preview readability by shooting t AND t+1.8** for each key line — if the second still doesn't
  show the same settled frame, the hold is too short.
- **Don't force grayscale on hero photos** — it reads as degradation, not art direction. Full
  color, `saturate(1.06)`, real spread.

## Multi-agent production
- **One reel = one agent = one directory.** Builders get script + brief + base rig + their own
  music/beats/assets; they never touch sibling dirs.
- **Builders preview, the parent renders.** Agents self-verify with shot.js contact sheets
  (`DONE errs=[]` + a director-style read of the stills); full renders run serially in the parent
  — and NOBODY `pkill`s Chromium while sibling agents run (it kills their browsers mid-preview).
- **Downscale curated photos into the reel dir (~900px)** and preload them as hidden `<img>`;
  hi-res originals multiply per-worker decode time for zero visible gain at 1080×1920.
- **A killed batch resumes cheaply**: frames are per-reel, so wipe the partial `frames/` and
  re-run only the unfinished reels.

## Environment (more)
- **zsh doesn't word-split `$var` in `for` loops** — a space-separated times string passed to
  `ffmpeg -ss` arrives as one arg. Wrap batch loops in `bash -c` or use arrays.
