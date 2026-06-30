---
name: reel-liveaction
description: >-
  Build a vertical live-action hype/promo reel from real footage + photos, modeled on a
  reference music video. Use when the user has video clips and/or a reference song/video and
  wants a beat-matched, character-driven reel with big kinetic text composited BEHIND the
  subject (text-behind-subject), a cinematic grade, and song + voice both loud. Covers audio
  forensics (demucs/whisper/librosa), person matting (rembg), and ffmpeg compositing.
---

# Live-action promo reel

Turn real footage into a reference-grade music-video edit. The method is fixed; only the
**brief** (footage, reference, copy, brand color) changes per company.

## When to use
- The user has real video clips / photos of a person or product, AND
- wants a punchy vertical reel (Reels/Shorts/TikTok), usually matched to a reference video.
If the user has NO footage and wants animated typography/graphics, use **reel-mograph** instead.

## Pipeline (run in order)

**0. Read the brief.** Expect: footage dir, reference video (optional), brand color (hex),
copy/script lines, aspect (default 720x1280@30), output name. If a `recipes/<ref>.json`
already exists for that reference, reuse it — do NOT re-analyze.

**1. Audio forensics** — only if there's a reference song/video, or talking-head clips.
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/analyze_ref.py <reference.mp4> <work_dir> \
        --vo <talkingclip1.mp4> <talkingclip2.mp4>
```
Produces `recipe.json` (tempo, beat grid, **cut_grid** of downbeats, word timestamps) and
stems: `vocals.wav` (isolated voice — pull ad-libs/outro from here) and `no_vocals.wav`
(clean instrumental bed). **Save the recipe into `recipes/` so it's reused next time.**

**2. Write the editmap.** Author `editmap.json` (schema in `templates/editmap.schema.json`,
example `templates/editmap.example.json`). Rules that make it look good:
- **Snap every cut to `recipe.rhythm.cut_grid`** (downbeats). Crisp sync = on the beat.
- Time each on-screen word to when it's actually said (`words[].a/b` from `recipe.voice`).
- `behind: true` on a segment composites its big words BEHIND the subject (head/body overlaps
  the letters — the signature look). Lower-third captions/footers stay in FRONT automatically.
- Stills get Ken-Burns (`move: push|slowpush|hold`); video segments get `in` (trim start).
- Keep brand color in `RED` (it's just the accent hex, name is legacy).

**3. Build the mix** (loud song AND loud voice — the hard part):
- Bed: loop/trim `no_vocals.wav` to full duration so there are NO silent holes.
- Voice: from talking-head clips or whisper segment; boost to sit ~as loud as the bed.
- Duck the bed under voice with `sidechaincompress` at a GENTLE ratio (~2.2) + makeup gain,
  so the music never fully disappears under dialogue.
- Layer any ad-libs/outro vocal bursts (from `vocals.wav`) back at their original timestamps.
- Finish with `dynaudnorm` + `alimiter`. Target ~-14 dB mean. **Audio length must equal the
  video length** or `-shortest` will clip your end card.

**4. Render** the video and mux:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_edit.py <path/to/editmap.json>
```
It renders a graded base (no text), generates a person matte per behind-segment, composites
text-behind + front, concats all segments, and muxes `editmap.audio`.

**5. Self-review before delivering.** Extract frames at key timestamps and a montage; READ the
images and confirm: text sits behind the subject, words land on the beat, end card survives to
the end, grade is consistent. Fix and re-render if not.

## Quality checklist — apply to EVERY reel

Load `skills/cinematography` and `templates/brandkit.json` first. Then:
- **Lighting & angle (capture-time):** when generating footage, write prompts in DP language —
  `[subject] · [lighting] · [angle+lens] · [movement] · [mood]` (see the cinematography skill).
  You can't relight flat footage in post; specify it at generation.
- **Shot selection:** generate a few takes, score with `python3 scripts/score_shots.py <dir> --top N`
  (exposure + sharpness + face framing), keep the best, drop the rest.
- **Grade by mood:** set `"grade_preset"` in the editmap — `warm-golden | moody-teal | clean | vintage | noir`
  (maps to the cinematography mood table; all lift the black floor so nothing reads muddy).
- **Hook / safe margins / endcard+CTA:** biggest beat on frame 1; keep text in `brandkit.safe_area`;
  end on the brand lock + CTA + the ad-lib/sting.
- **Sound-off captions:** burn with `scripts/captions.py` for muted viewing.
- **Shot variety:** vary scale (wide→medium→ECU) and angle; don't repeat one framing.

## Requirements
`ffmpeg`, Python 3 with `cv2 numpy rembg demucs librosa faster-whisper soundfile`.
rembg on macOS: force CPU — `os.environ['ONNXRUNTIME_EXECUTION_PROVIDERS']='CPUExecutionProvider'`
and `new_session('u2net_human_seg', providers=['CPUExecutionProvider'])` (CoreML save fails).

## Read this before you start
`${CLAUDE_PLUGIN_ROOT}/LESSONS.md` — hard-won fixes (audio-inaudible bug, matte speed, file
size, silent holes). Append any new fix you discover so the skill keeps improving.
