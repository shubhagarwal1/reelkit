---
name: cinematography
description: >-
  Lighting, camera-angle, lens, and mood vocabulary for video. Use whenever generating or
  selecting footage, or grading a reel — it makes generation prompts specify real DP language
  (Rembrandt key, golden hour, low hero angle, shallow DoF) instead of flat defaults, drives
  shot-selection scoring, and maps a brand mood to a concrete lighting + grade recipe. Both
  reel-liveaction and reel-mograph load this for the look.
---

# Cinematography playbook

Lighting and camera angle are decided at **capture/generation**, not in post. So this skill acts
at three points: (1) it shapes footage-generation prompts, (2) it gives the rubric for picking the
best take, (3) it maps mood → grade. Never accept "flat, eye-level, evenly-lit" — always specify.

## Lighting (pick one key + optional rim/practical)
- **Rembrandt** — 45° key, small triangle of light under the far eye. Portrait default; looks expensive.
- **Butterfly/beauty** — key above and front; soft, flattering, glamour.
- **Rim / kicker** — backlight separates subject from background; add for depth on dark sets.
- **High-key** — bright, low-contrast, minimal shadow → upbeat, clean, commercial.
- **Low-key** — single hard source, deep shadows → dramatic, premium, moody.
- **Golden hour** — warm, low, soft sun → romantic/luxury (weddings). **Blue hour** → calm, cinematic.
- **Motivated practicals** — lamps/candles/windows *in frame* as the source → realism + warmth.
Rule: soft light = flattering/calm, hard light = dramatic/edgy. State direction (key-from-left), quality (soft/hard), and color temp (warm 3200K / neutral / cool 5600K).

## Camera angle & framing
- **Eye-level** neutral · **low/hero** (camera below, looking up) = power/aspiration · **high** = vulnerability/overview · **Dutch tilt** = tension/energy.
- **Scale:** ECU (emotion) → CU → medium → wide (context). **Vary scale across a reel** — never all the same.
- **Framing:** rule-of-thirds, eyes on the upper third, correct **headroom**, **lead room** in the look direction. OTS for connection.

## Lens / depth / movement
- **Shallow DoF** (f/1.8, 85mm) → subject pops, background melts = premium. **Deep** (wide, f/8) → context.
- **Movement:** slow **push-in** (intimacy/build), **pull-out** (reveal/scale), **orbit** (hero), subtle **handheld** (energy/realism). Avoid static unless deliberate.

## Mood → recipe (use to fill a generation prompt AND pick the grade)
| Brand mood | Lighting | Angle/lens | Grade preset |
|---|---|---|---|
| Luxury wedding | golden-hour soft key + rim | low hero, 85mm shallow DoF, slow push | `warm-golden` |
| Premium/editorial | low-key hard key + practicals | eye-level CU, shallow DoF | `moody-teal` |
| Bright/friendly product | high-key soft | medium, slight low angle | `clean` |
| Nostalgic/memory | window light, warm | medium, handheld | `vintage` |

## How to use it
- **Generating footage** (Veo/Kling/Runway): write the prompt as `[subject] · [lighting] · [angle+lens] · [movement] · [mood]`. e.g. *"bride and groom, golden-hour soft key with warm rim light, low hero angle, 85mm shallow depth of field, slow push-in, romantic luxury."* Camera-control params on the model (if any) set the move.
- **Selecting takes** — score candidates with `scripts/score_shots.py` (exposure, sharpness, face framing) or hand frames to Claude with this rubric; keep the best-lit, best-framed, drop the rest.
- **Grading** — pass the mood's `grade` preset to `build_edit.py` (see grade presets in that script / the reel skills).

Grade presets (ffmpeg, also in build_edit.py): `warm-golden`, `moody-teal`, `clean`, `vintage`, `noir`.
