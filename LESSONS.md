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
