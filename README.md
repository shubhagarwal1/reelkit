# 🎬 reelkit

Two AI video pipelines packaged as a **Claude Code plugin**. Hand Claude a short per-company
brief + a reference video, and it builds a branded vertical reel — no re-explaining the pipeline
each time. The *method* lives in the plugin; the *content* lives in your brief, so it works for
any brand.

| Skill | Makes | Pipeline |
|---|---|---|
| **reel-liveaction** | Hype/promo reel from real footage, matched to a reference song | demucs + faster-whisper + librosa → editmap → rembg person-matte → ffmpeg compositing |
| **reel-mograph** | Animated typography / feature / launch films (no footage) | GSAP timeline in HTML → headless-Chromium frame stepping → motion-blur supersample → ffmpeg + SFX |

Claude auto-picks **reel-liveaction** when the brief has footage, **reel-mograph** otherwise.

---

## Install

```bash
# 1. system + runtimes
brew install ffmpeg
pip install -r requirements.txt                 # rembg, demucs, librosa, faster-whisper, opencv, soundfile
npm install playwright && npx playwright install chromium

# 2. add the plugin to Claude Code
/plugin marketplace add shubhagarwal1/reelkit
/plugin install reelkit@reelkit-marketplace
```

## Use

```text
# in Claude Code, after filling in templates/brief.example.json:
"build a reel from this brief"
```
That's it. Claude reads the brief, analyzes your reference, authors the edit/animation, renders,
and self-reviews before handing back the MP4.

Run a script directly if you prefer:
```bash
python scripts/analyze_ref.py ref.mp4 work/ --vo clipA.mp4   # reference → recipe + audio stems
python scripts/build_edit.py  my/editmap.json               # editmap → finished live-action reel
node   scripts/render_mograph.js film/index.html film/frames 1080 1920 30 2   # animation → frames
node   scripts/build_audio.js  film/index.html film/audio.wav                 # SFX sound design
```

## What's in the box

```
.claude-plugin/        plugin.json + marketplace.json  (makes it installable)
skills/
  reel-liveaction/     SKILL.md — footage pipeline playbook Claude follows
  reel-mograph/        SKILL.md — motion-graphics playbook
scripts/
  analyze_ref.py       reference → recipe.json (tempo, beat grid, cut grid) + vocal/instrumental stems
  build_edit.py        editmap.json → graded, beat-cut reel with text composited BEHIND the subject
  render_mograph.js    deterministic frame renderer (steps GSAP per frame + motion-blur supersampling)
  build_audio.js       turns timeline cues into a pitched/panned SFX track from an SFX manifest
templates/             editmap schema + worked example, GSAP HTML skeleton, build & batch scripts, brief
recipes/               saved reference analyses — reused, never re-measured
LESSONS.md             append-only fixes — the plugin's memory (read before every run)
```

## How it gets smarter
No training — it **accumulates**. Each analyzed reference is saved to `recipes/` and reused.
Every bug fixed gets one line in `LESSONS.md`, which both skills read first — so the same mistake
never repeats. Commit those two and the plugin improves for everyone.

## Notes
- Defaults to vertical **720×1280@30** (live-action) / **1080×1920@30** (mograph); override in the brief.
- Fonts default to macOS paths — override `serif`/`sans` in the editmap on other OSes.
- Motion-graphics audio needs a `sfx/manifest.json` (your own CC0 SFX library) at the project root.

## Credits
Built with Claude Code. Powered by Meta demucs, faster-whisper, rembg (u2net), librosa, GSAP,
Playwright, and ffmpeg.
