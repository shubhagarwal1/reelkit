# SAMARO USE-CASE REELS — SHARED SYSTEM BRIEF
(Every script MUST follow this system. Scripts are blueprints for our GSAP/HTML → headless-Chromium render pipeline.)

## Brand system
- Canvas: paper `#F6F5F3` (bright) alternating with ink charcoal `#0A0A0A` scenes for tension beats. `#bgdark` radial-vignetted.
- Accent: coral `#FF5A1F` — MEANING ONLY (the "you"/found/CTA moments, badges, brackets). Never decorative.
- Type: Inter (100-900, headlines `-0.045em`, weight 800 big / 300 light), Instrument Serif italic (emotional/lyric lines), JetBrains Mono (labels, URLs, metrics, overline 6px letterspacing uppercase).
- Logo: cursive coral "S" (S_00.png = coral; S_01..S_10 = color variants for the shutter flick).
- Texture: 3% fractal grain multiply + soft radial vignette on every scene.
- Assets available: 54 wedding photos (p_00..p_53, 360px), selfie.png, S-variant logos, iPhone frame CSS, WhatsApp-style dark cards, notification card, photo-wall grid, folder+photo-fan rig.

## Motion language (the reference-ad kinetic style)
- One paused GSAP master timeline; scene cuts LOCKED to bar downbeats.
- Entrance vocabulary (VARY them, never all-slide): `slideIn` (words from right, power4.out, the "zye zye" signature), `wavyIn` (rise word-by-word, back.out(1.5)), `popIn` (scale 0.42→1, back.out(2.4)), 3D card entrances (rotateX/z + blur→sharp, back.out family).
- Exit vocabulary: `slideOut` (words left, conveyor logic — in from right, out to left), `wavyOut` (rise off-frame), z-recede+blur for cards. EVERY container must be hard-cleared (opacity:0) after exit — no ghost bleed.
- Beat-bounce: on strong groove pulses (~0.98s apart) held text hops 12-17px with `thunk` tap synced. Not every sub-beat.
- Climax device: blur→SNAP-sharp reveal + coral corner brackets + drop. Logo endcard: color-shutter flick (8 variants, ~0.045s apart, click ticks) → SLAM to coral on a drop.
- Hold discipline: every message readable ≥2s. ~2 bars (≈3.9s) per scene. Elements DEAD-STILL during holds (motion-blur pass smears anything drifting).

## Sound design system (families in sfx/manifest.json)
- Bed: licensed track as music bed, loudnorm to −14 LUFS, accents ducked under.
- Accent families: `latch` (physical snap), `glass` (delicate), `chime`, `ui_confirm` (notification), `click` (typing/shutter-tick), `thunk` (soft beat-tap), `noise_hit` (impact), `sub_boom` (drop layer), `riser`, `swoosh` (transition — MAX 3 per reel, act boundaries only), `shutter`, `key`, `ding`, `pop`, `camera_focus`, `tile`, `blip`, `count`. AVOID `tick` (beepy).
- Rich drop = layered: boom(g1.0) + boom+12ms(g0.6) + hit(g0.58). Use at THE climax and logo-lock only.
- Every sound must have its own timing, meaning, presence. No spam.

## Pacing / structure standard
- Duration: 28–34s target (Instagram reel sweet spot), 9:16 1080×1920, 60fps.
- Arc: BUILD (problem, tension) → CLIMAX (the Samaro magic moment, on a drop) → RESOLVE (proof, payoff) → CTA endcard (logo shutter → "find yourself today." style one-liner + events.samaro.ai; ≤2 text lines besides logo).
- Beat-grid: pick the track first, extract tempo/bar downbeats (librosa), lock every scene cut + entrance to downbeats. Note BPM and downbeat times in the script.
- The reel must be READABLE: max ~8 scenes, one idea per scene.

## What each SCRIPT.md must contain (be exhaustive — this is the render blueprint)
1. **Concept** — use case, character, the problem, the one-line story, why it's out-of-the-box.
2. **Music direction** — genre/energy/BPM range, 2-3 reference-track suggestions, where the drop must land, how SFX blend with it.
3. **Grade/color** — canvas alternation plan per scene, coral usage map, any photo treatment (color vs b/w, saturation).
4. **Scene-by-scene breakdown** — for EVERY scene: time range (in bars+seconds), layout with EXACT positions (px on 1080×1920), every element, its entrance (which vocabulary word, duration, ease), hold behavior (beat-bounce? float? still?), exit, and every sound cue with timing+gain.
5. **Climax spec** — the exact magic moment, frame by frame.
6. **Endcard spec** — exact px spacing of lockup.
7. **Copy deck** — every on-screen line, checked for tone (short, punchy, human; no corporate fluff).
8. **Asset list** — what must be built/collected (UI mocks, props, photos), what exists already.
9. **Character** — who we follow, how they're visually represented (photos/UI/avatar) given we have wedding photo assets + can mock any UI in HTML/CSS.
