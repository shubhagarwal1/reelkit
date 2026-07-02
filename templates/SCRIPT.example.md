# USE CASE 5 — COLLEGE FEST · "FEST MODE"
Slug: `collegefest-festmode` · 9:16 · 1080×1920 · 60fps · **32.0s** · **150 BPM**

> **BEAT MATH (all timings below use this grid).**
> 150 BPM → beat = **0.4s**, bar (4/4) = **1.6s**. Reel = **20 bars = 32.0s**.
> Downbeats: 0.0, 1.6, 3.2, 4.8, 6.4, 8.0, 9.6, 11.2, 12.8, 14.4, **16.0 (THE DROP)**, 17.6, 19.2, 20.8, 22.4, 24.0, 25.6, 27.2, 28.8, 30.4.
> All times in this doc are seconds on this nominal grid. When the final licensed track is chosen, extract real downbeats with librosa and re-lock every cue by bar index (bar numbers are given for every scene) — do NOT re-lock by seconds.

---

## 1 · CONCEPT

**Use case:** College fest, concert night. 10,000 students, DJ set, confetti cannons.
**Character:** Rhea, final-year student. Last fest ever. She's IN the pit.
**Problem (old world):** 400 Instagram stories vanish in 24h. The official aftermovie drops a month later. Rhea appears in exactly **zero** of the official photos she can find. Her biggest night has no proof.
**Samaro magic:** One QR on the LED wall between sets → she scans, takes one selfie → **before the encore ends** her phone buzzes with HER photos from the pit. No login. No app install. Straight gallery link on WhatsApp. The fest committee gets a no-login 4K gallery, and 10,000 students sharing their own faces means next year's fest sells itself.
**One-line story:** *The fest that finds you before the encore ends.*
**Why out-of-the-box:** The reel BEHAVES like the fest — scene cuts are drop-synced strobe cuts (capped for legibility), the bass drop physically detonates the gallery into a face-mosaic, and **the QR code is a character**: it walks in like a headliner, bounces on the beat, and takes the selfie. Sticker/scrapbook energy (rotated mono tags, coral tape strips) rides on top of the strict brand system — maximal, but clean.

---

## 2 · MUSIC DIRECTION

- **Genre/energy:** aggressive-clean phonk / EDM-trap hybrid, 140–160 BPM. Dark verse (charcoal scenes) → riser bar → filthy but musical drop (climax) → groove outro. Needs: a real 2-bar riser before bar 11, and a hard sub+snare hit on the drop.
- **Nominal grid: 150 BPM** (bar = 1.6s). Reference tracks (license equivalents from the music library; match energy + structure, then re-lock grid):
  1. **Kordhell — "Murder In My Mind"** · 152 BPM — the drive/menace of the verses, drop weight.
  2. **Dxrk ダーク — "RAVE"** · 140 BPM — the clean, spacious phonk groove for the resolve act.
  3. **INTERWORLD — "METAMORPHOSIS"** · 162 BPM (feels 81 half-time) — the riser→drop architecture we want at bars 9–11.
- **Where the drop lands:** **bar 11 downbeat = 16.0s** — the climax mosaic detonation. Second (smaller) drop at **30.4s** for the logo coral-slam.
- **SFX blend:** music bed loudnorm to −14 LUFS; accents duck the bed −3 dB via sidechain during the riser (14.4→16.0) so the `riser` + `drop` layers read as part of the track. `thunk` beat-taps only on strong pulses (every other beat, 0.8s apart at this tempo). Swoosh budget: **3**, at act boundaries only (9.6, 20.8, 28.8). Rich layered drop (boom g1.0 + boom+12ms g0.6 + hit g0.58) used exactly twice: 16.0 and 30.4.

---

## 3 · GRADE / COLOR PLAN

| Scene | Bars | Canvas | Coral usage |
|---|---|---|---|
| S1 HOOK | 1–2 | **charcoal** `#0A0A0A` + radial vignette | none (withhold) |
| S2 OLD WORLD | 3–4 | charcoal | one coral "24h" ring only |
| S3 ZERO | 5–6 | charcoal, photo wall at 45% opacity grayscale | coral **"0"** — first big coral moment |
| S4 QR | 7–8 | charcoal (LED-wall black) | QR eyes + sticker tag coral |
| S5 SELFIE | 9–10 | **paper** `#F6F5F3` (hard flip on 12.8) | selfie ring + scan line coral |
| S6 CLIMAX | 11–13 | paper base, 2-frame charcoal strobe inversions on 16.0/16.8/17.6 | coral brackets on every found face; coral is EVERYWHERE here — this is the "found" meaning at max |
| S7 PROOF | 14–16 | paper | notification "347", WhatsApp accent chips |
| S8 END+CTA | 17–20 | charcoal (17–18) → paper (19–20) | "prove it." + coral S lockup |

**Photo treatment:** all crowd/pit photos graded **charcoal duotone** (desaturate −70%, lift blacks +6, coral-tinted highlights ≤8%) in build scenes; **full color, saturation 1.06, contrast 1.03** the instant they're "found" (S6 onward) — found = color, lost = mono. This rule is the grade's story.
**Texture:** 3% fractal grain multiply + soft radial vignette on every scene (kit default `#grain` + `#vig`).
**Strobe legibility rule:** each strobe = exactly 2 frames (33ms) of inverted canvas, never during a text entrance, max 3 per reel, all inside S6.

---

## 4 · SCENE-BY-SCENE BREAKDOWN

Stage: 1080×1920. All positions absolute px unless noted. Every container hard-cleared (`opacity:0`) after exit.

### S1 · HOOK — "10,000 students. one night." — bars 1–2 (0.0 → 3.2s) · charcoal

Layout:
- `#festwall` (NEW primitive `ledWall`): full-bleed charcoal with 6 horizontal LED scanlines (2px, `#1c1c1c`) at y = 300/560/820/1080/1340/1600, and a faint stage-glow radial (`rgba(255,90,31,0.04)` 900px at 50%/70%). Sets "concert night" without footage.
- `#hk1` big condensed slam, Inter 800, **150px**, letter-spacing −0.045em, paper color, centered, **top:640px**: "10,000 students."
- `#hk2` Instrument Serif italic **112px**, paper, centered, **top:830px**: "one night."
- `#hk3` mono overline, 26px, 6px letterspacing, uppercase, `#6E6E6E`, centered, **top:560px**: "CONCERT NIGHT · MAIN STAGE"

Timeline:
- 0.00 — `#festwall` fades in 0.3s (power2.out); scanlines flicker via 2 quick opacity dips at 0.10/0.22.
- 0.40 — `#hk3` overline: fade+rise 18px, 0.4s.
- 0.80 (beat 3) — `#hk1` **bigSlam** (NEW primitive: popIn variant, scale 1.55→1 + skewX 6→0 + blur 8→0, back.out(1.8), dur 0.5, word stagger 0.05).
- 1.20 (beat 4) — `#hk2` **wavyIn** (stagger 0.08, dur 0.6) — pulled a beat earlier so both lines read ≥2s.
- 1.5→2.8 — hold, dead-still except beatWave on `#hk2` words at 2.4 (amp 14, one pulse only).
- 2.80 — `#hk1` **slideOut** left (2.0s read ✓); 3.00 — `#hk2` **wavyOut** (1.8s hold + 0.4s exit travel ≈ 2.0s visible, conveyor overlap under S2's cards arriving from the right); 3.00 — `#hk3` fade 0.25s. `#festwall` STAYS.

Sound:
- 0.00 `sub_boom` g0.5 (cold-open thump, under music intro)
- 0.80 `hit` g0.55 (slam lands)
- 1.20 `glass` g0.40 ("one night." rises)
- 2.40 `thunk` g0.32 (beat-hop tap)

### S2 · OLD WORLD — stories vanish, aftermovie ghosts — bars 3–4 (3.2 → 6.4s) · charcoal

Layout:
- `#storyrow`: 5 Instagram-story cards (`.pcard` restyle: 168×288px, border-radius 20px, 3px `#2a2a2a` ring, grayscale pit photos), left-to-right at x = 60/258/456/654/852, **top:520px**. Each has a coral progress bar (top inset 10px, 4px tall) already at 96%.
- `#ring24`: coral ring badge (`#badge` restyle: 120px circle, mono 700 30px "24h", coral border 6px, transparent fill), **left:830px top:440px**, rotate −8°.
- `#old1` big type, Inter 800 **96px**, paper, left-aligned **left:90px top:1000px**: "400 stories." line 2 `.lt` (weight 300): "gone in 24h."
- `#old2` mono sticker (NEW primitive `stickerTag`: paper chip, charcoal mono 26px text, padding 12/24, border-radius 10px, rotate −4°, hard shadow 0 10px 24px rgba(0,0,0,0.5)), **left:90px top:1360px**: "AFTERMOVIE ETA: 34 DAYS"

Timeline:
- 3.20 (bar 3) — story cards **slideIn** as cards (x from 560, blur 5→0, power4.out, 0.5s, stagger 0.06).
- 3.60 — `#ring24` **popIn** (back.out(3), 0.4s) + one 1.06 pulse at 4.0.
- 4.00 (beat) — `#old1` **slideIn** (stagger 0.05).
- 4.40→4.90 — the KILL: all 5 story cards drain — progress bars snap to 100% then each card does z-recede+blur exit (scale 0.9, blur 6, opacity 0, power2.in 0.35s, stagger 0.07, order left→right). They vanish like stories.
- 4.80 (bar 4) — `#old2` sticker **popIn** (single-element, back.out(2.4), 0.45s).
- 4.8→6.1 — hold, still; `#old1` beatWave one pulse at 5.6 (amp 12).
- 6.10 — `#old1` **slideOut**; 6.25 — `#ring24` fade 0.25s; 6.85 — `#old2` z-recede exit (sticker reads 4.80→6.85 = 2.05s ✓; it sits at top:1360, clear of S3's wall and of `#z1`, which enters 7.0 at top:880).

Sound:
- 3.20 `latch` g0.60 (cards arrive)
- 3.60 `blip` g0.40 (24h ring)
- 4.00 `hit` g0.45 ("400 stories." lands)
- 4.40–4.85 `pop` ×5, g 0.34/0.32/0.30/0.28/0.26, at 4.40/4.47/4.54/4.61/4.68 (stories dying, decaying gains)
- 4.80 `thunk` g0.32 (sticker slap)

### S3 · ZERO — buried in everyone's photos, found in none — bars 5–6 (6.4 → 9.6s) · charcoal

Layout:
- `#wall` (existing photo-wall rig): 5×4 grid, left/right inset 70px, **top:196px**, gap 18px — 20 grayscale pit/crowd tiles at opacity 0.45. `#wshade` radial shade on top.
- `#z1` centered, **top:880px**, Instrument Serif italic **84px** paper: "official photos of you:"
- `#z0` centered, **top:1010px**, Inter 800 **300px** letter-spacing −0.05em **coral**: "0"

Timeline:
- 6.40 (bar 5) — wall tiles pop in (scale 0.7→1, y 26→0, back.out(1.6), 0.42s, stagger 0.016); `#wshade` fade to 1 over 0.7s from 6.6.
- 7.00 — `#z1` **wavyIn** (stagger 0.06).
- 7.60 (beat) — `#z0` **bigSlam** (scale 1.6→1, blur snap) — first coral. On landing, the whole wall dims to opacity 0.28 over 0.3s (the zero erases her from the crowd).
- 7.6→9.1 — hold ≥1.5s on the composed frame (z1 already held from 7.0 → combined message readable 2.1s). `#z0` beat-hops at 8.0 and 8.8 (amp 16, y only).
- 9.10 — `#z1` **wavyOut**, `#z0` scales to 0.9 + blur 6 + fade 0.35s; wall+shade fade 0.4s.

Sound:
- 6.40 `tile` g0.40 (wall builds — one cue, not per-tile)
- 7.00 `glass` g0.38
- 7.60 `noise_hit` g0.60 (the "0" gut-punch)
- 8.00 `thunk` g0.32 · 8.80 `thunk` g0.30

### S4 · THE QR IS THE HEADLINER — bars 7–8 (9.6 → 12.8s) · charcoal (LED wall)

The act break. Between sets, the LED wall goes black — then one QR walks on like an artist.

Layout:
- `#festwall` persists; add `#ledframe`: thin `#2a2a2a` 3px rect, **left:190px top:520px, 700×700px**, radius 24px — the LED wall panel.
- `#qr` (NEW primitive `qrChar`): 520×520px QR code (SVG, paper modules on transparent, the three finder "eyes" **coral**), centered in `#ledframe` (left:280px top:610px). It is a CHARACTER — it breathes and bounces.
- `#qrtag` stickerTag, mono 26px, coral chip/paper text, rotate 3°, **left:395px top:1180px**: "SCAN BETWEEN SETS"
- `#qr1` centered **top:1400px**, Inter 800 **88px** paper: "one QR." `.lt` light suffix: " that's it."

Timeline:
- 9.60 (bar 7, ACT 1→2) — screen "power-cut": `#festwall` scanlines flare once (opacity 1→0.2, 0.12s); `#ledframe` draws in (scaleX 0→1, 0.3s, power3.out).
- 9.90 — `#qr` **3D card entrance**: rotateX −70→0, y 60→0, blur 8→0, scale 0.85→1, back.out(1.5), 0.6s — it steps onto the stage.
- 10.40 — the three coral eyes pop sequentially (scale 0→1, back.out(3), 0.25s each, at 10.40/10.50/10.60).
- 10.80 — `#qrtag` popIn; 11.20 (bar 8) — `#qr1` **slideIn** (stagger 0.05).
- 10.8→12.4 — hold: `#qr` bounces on strong pulses at 11.2 and 12.0 (y −20, squash scaleY 0.96 on land, 0.3s — headliner jump; NOT drifting between hops).
- 12.40 — `#qr1` slideOut, `#qrtag` fade 0.25s. `#qr` does NOT exit — it flies: 12.55→12.85 `#qr` scales 1→0.32 while moving to left:750px top:120px (power3.inOut) becoming the corner "scanned" chip of S5, then fades 0.2s under the paper flip.

Sound:
- 9.60 `swoosh` g0.62 (**ACT BOUNDARY 1/3**) + `sub_boom` g0.35 (power-cut)
- 9.90 `latch` g0.65 (QR lands)
- 10.40/10.50/10.60 `blip` g0.36/0.34/0.32 (eyes)
- 11.20 `thunk` g0.34 · 12.00 `thunk` g0.34 (QR bounces)
- 12.55 `camera_focus` g0.45 (QR captured → into the phone)

### S5 · SELFIE → SCAN (riser) — bars 9–10 (12.8 → 16.0s) · PAPER

Layout (existing phone rig):
- 12.80 hard canvas flip charcoal→paper (`#bgdark` opacity 1→0 in 0.25s — a light-slam, not a fade story).
- `#phone` (existing, 600×1200, centered left:50% top:50%): inside it `#selfie` (330px circle, coral ring, at 40% height), `#scan` line, `#fbkA` brackets, `#caplabel`.
- `#s5tag` stickerTag rotate −3°, **left:120px top:250px**, mono 26px: "NO APP · NO LOGIN"

Timeline:
- 12.80 (bar 9) — `#phone` 3D entrance: rotateX −70→0, y 40→0, back.out(1.5), 0.7s.
- 13.30 — `#selfie` fades in blurred (blur 16→6, scale 0.86→1, 0.5s).
- 13.60 — `#s5tag` popIn.
- 14.00 — `#scan` sweep: top 22%→62%, 0.7s, power2.inOut; opacity out 0.2s at 14.7.
- 14.40 (bar 10) — **RISER STARTS** (music + `riser` SFX). `#selfie` micro-shakes: x ±3px at 60fps-safe 0.08s intervals from 15.2→15.9 (tension), still blurred at 4px.
- 15.60→15.97 — pre-drop VOID: everything except the phone dims to 40% (0.2s); one white 2-frame flash at 15.97.
- The face-lock itself happens ON the drop = S6 frame 0.

Sound:
- 12.80 `swoosh` — NO. (Budget: act boundary was 9.6.) Instead: 12.80 `hit` g0.50 (paper slam)
- 12.80 `latch` g0.55 (phone lands, +0.05s at 12.85)
- 13.30 `glass` g0.40 (selfie appears)
- 13.60 `pop` g0.34 (sticker)
- 14.00 `shutter` g0.45 (scan starts) · 14.70 `click` g0.30 (scan ends)
- 14.40 `riser` g0.80 (1.6s riser into the drop; duck bed −3dB 14.4→16.0)

### S6 · **CLIMAX — THE DROP / FOUND-FACE MOSAIC** — bars 11–13 (16.0 → 20.8s) · paper + strobe

Full spec in §5. Summary: at 16.0 the selfie SNAPS sharp, brackets lock, and the screen detonates into a 3×5 mosaic of full-color found faces, coral brackets popping corner-to-corner on every beat, 3 strobe inversions on downbeats.

### S7 · PROOF — everyone's phone buzzes before the encore — bars 14–16 (20.8 → 25.6s) · paper

Layout:
- `#notif` (existing notification card, 900px wide, **left:90px top:906px**): icon ✦, "SAMARO · now", h3: "**347** new photos of you ✦" (coral numerals), sub: "from the pit · tap to open".
- `#wa` (existing WhatsApp-style dark card, 720px wide, **left:180px top:1200px**, rotate 2°): green dot header "Fest Squad 🎪", row: "bro the gallery has EVERYONE 😭🔥", row with link chip mono coral: "samaro.ai/g/fest24".
- `#pr1` centered **top:420px**, Inter 800 **86px** ink: "before the encore" line2 serif italic coral 86px: "ends."
- `#pr2` mono overline centered **top:640px** 26px `#8A8A86`: "NO LOGIN · NO APP · STRAIGHT TO WHATSAPP"
- `#pr3` stickerTag rotate −3°, **left:600px top:1560px**, charcoal chip/paper text: "COMMITTEE: 4K GALLERY, ZERO OPS"

Timeline:
- 20.80 (bar 14, ACT 2→3) — mosaic collapses (see §5); `#pr1` **wavyIn** (stagger 0.07).
- 21.40 — `#pr2` fade+rise 0.4s.
- 22.40 (bar 15) — `#notif` entrance: y 64→0, scale 0.94→1, blur 4→0, back.out(2.2), 0.55s; icon spins in (rotate −30→0, back.out(3)).
- 23.20 — `#wa` slides up (y 80→0, blur→0, power4.out, 0.5s).
- 23.60 (beat) — `#pr3` popIn (the B2B whisper — small, 26px; entering a beat earlier buys it a 1.85s read + exit travel ≈ 2s visible).
- Holds: `#pr1` readable 20.8→25.2 (4.4s), notif 22.4→25.2 (2.8s), wa 23.2→25.2 (2.0s). `#pr1` beatWave at 22.4/23.2/24.0 (amp 13). Cards dead-still.
- 25.20 — `#pr1` wavyOut, `#pr2` fade; 25.30 — `#notif`+`#wa` z-recede+blur exit 0.4s; 25.45 — `#pr3` fade 0.2s.

Sound:
- 20.80 `swoosh` g0.62 (**ACT BOUNDARY 2/3**)
- 22.40 `ui_confirm` g0.70 (THE buzz — the most meaningful cue in the reel)
- 23.20 `ding` g0.45 (WhatsApp lands)
- 23.60 `pop` g0.32 (committee sticker)
- 22.4/23.2/24.0 `thunk` g0.30 each (beat-hops)

### S8 · END LINE + ENDCARD — bars 17–20 (25.6 → 32.0s) · charcoal → paper

Layout A (25.6→28.8, charcoal):
- `#end1` left-aligned **left:90px top:760px**, Inter 800 **118px** paper: "you were there."
- `#end2` left-aligned **left:90px top:920px**, Inter **118px**: weight 300 paper "now " + serif italic **coral** "prove it."

Timeline A:
- 25.60 (bar 17) — `#bgdark` to 1 in 0.3s; `#end1` **slideIn** (stagger 0.05, dur 0.55).
- 26.40 (beat) — `#end2` **slideIn** (stagger 0.06); "prove it." final word gets a 1.06 scale pulse at 27.2.
- Hold 26.4→28.4 (≥2s), beatWave on `#end2` at 27.2/28.0 (amp 12).
- 28.45 — both **slideOut** left; `#bgdark` to 0 over 0.4s at 28.55.

Layout B — ENDCARD (28.8→32.0, paper): full spec §6.

Sound:
- 25.60 `hit` g0.46 ("you were there." lands)
- 26.40 `glass` g0.50 ("prove it.")
- 27.2/28.0 `thunk` g0.30
- 28.80 `swoosh` g0.60 (**ACT BOUNDARY 3/3**, into lockup)
- Endcard cues in §6.

---

## 5 · CLIMAX SPEC — frame-by-frame (drop at 16.000s, bar 11; 60fps → frame 960)

The device: **blur→SNAP-sharp + coral brackets + drop**, scaled up into a mosaic detonation. Grid geometry: 3 cols × 5 rows; tiles 331×355px; x origins 30/378/726; y origins 60/436/812/1188/1564; gap 17px. 15 tiles = 15 full-color pit photos of "found" people; tile r2c2 (x:378 y:812, dead center) is RHEA.

| Time (s) | Frame | Event |
|---|---|---|
| 15.967 | 958 | 2-frame white pre-flash (paper #FFF overlay, opacity 0.9) |
| **16.000** | **960** | **DROP** (boom g1.0 + boom@16.012 g0.6 + hit g0.58). `#selfie` blur 4→0 SNAP in 4 frames, scale→1.06; `#fbkA` brackets slam on (scale 1.5→1, back.out(3.2), 0.3s). STROBE 1: frames 960–961 canvas inverts to charcoal, text/brackets stay coral+paper (legible). |
| 16.10–16.30 | 966–978 | Phone shatters outward: `#phone` scales 1→1.9 + blur 10 + opacity→0 (power2.in). Behind it the mosaic base (paper) is revealed. |
| 16.20 | 972 | Tiles 1–3 (row 3, center row first: r2c2 RHEA, then r2c1, r2c3) pop: scale 0.6→1, blur 6→0, back.out(2.1), 0.30s, 0.05s apart. Rhea's tile gets `.fbk` coral brackets snapping from scale 1.4→1 the instant it lands. `latch` g0.55. |
| 16.40 | 984 | (beat) Tiles r1c1+r3c3 pop; brackets JUMP from Rhea's tile to r1c1 (brackets are ONE element that teleports corner-to-corner, 0 tween — hard cut, that's the pop). `latch` g0.50 + `thunk` g0.30. |
| 16.80 | 1008 | (downbeat, bar 11.5) Tiles r1c3+r3c1 pop; brackets jump to r3c1. STROBE 2 (frames 1008–1009). `noise_hit` g0.45. |
| 17.20 | 1032 | (beat) Tiles r0c2+r4c2 pop; brackets jump to r4c2. `latch` g0.46. |
| 17.60 | 1056 | (bar 12) Tiles r0c1+r0c3 pop; brackets jump to r0c3. STROBE 3 (frames 1056–1057, LAST strobe). `noise_hit` g0.45. |
| 18.00 | 1080 | (beat) Tiles r4c1+r4c3 pop — **grid complete, 15/15**. Brackets jump HOME to Rhea (r2c2) and stay. `latch` g0.44. |
| 18.20 | 1092 | `#cl1` counter slams center **top:60px→ overlays on a charcoal chip 560×120px left:260px**: mono 700 44px coral, ticking "12 → 347 FOUND" (counter counts in 10 frames). `count` g0.5 at 18.20, `ding` g0.42 at 18.40 when it locks at 347. |
| 18.4→20.3 | 1104–1218 | **HOLD ~1.9s** — full mosaic + brackets on Rhea + "347 FOUND" chip. Tiles dead-still (motion-blur pass). Brackets do a 1.06 breath-pulse at 19.2 (bar 13 downbeat, `thunk` g0.32) — nothing else moves. |
| 20.30 | 1218 | Non-Rhea tiles z-recede (scale 0.92, blur 5, opacity 0, 0.4s, stagger 0.02 radial from center). |
| 20.60 | 1236 | Rhea's tile + brackets + chip scale to 0.8, fly to top-center (x:540 y:180) and fade 0.25s — she's "banked". Clean handoff to S7 at 20.8. |

Rules honored: exactly 3 strobes, all 2 frames; every bracket jump is beat-locked (0.4s grid); one rich drop; text hold ≥1.9s on the completed frame.

---

## 6 · ENDCARD SPEC (28.8 → 32.0s, paper) — exact px

Identical lockup geometry to the platform reel (system endcard):
- `#slogo`: coral cursive S, **left:50% top:812px**, translate(−50%,−50%), **322×382px**, object-fit contain.
- Line 1 `#lk4`: Instrument Serif italic **74px** ink, centered, **top:1120px**: "find yourself today."
- Line 2 `#lk3`: JetBrains Mono 500 **38px**, letter-spacing 0.08em, **coral**, centered, **top:1244px**: "events.samaro.ai"
- (≤2 text lines besides logo — spec-compliant.)

Timeline:
- 28.80 — `#slogo` in: scale 0.72→1, blur 10→0, 0.36s power3.out.
- 29.00→29.36 — **color-shutter flick**: swap src through variants [1,2,6,5,10,8,9,3] every 0.045s; `click` g0.5 per swap (8 ticks).
- **30.40 (bar 20 downbeat)** — SLAM to coral S_00: scale 1.18→1 back.out(2.2) 0.44s + **rich drop #2** (boom g0.95 + boom+12ms g0.57 + hit g0.55).
- 30.60 — `#lk4` slideIn (stagger 0.05, dur 0.58) + `chime` g0.36.
- 31.05 — `#lk3` slideIn (stagger 0.03, dur 0.5).
- 30.9→32.0 — logo micro-breath scale 1→1.012 (sine.inOut); hold to 32.0. END.

---

## 7 · COPY DECK (every on-screen line)

| ID | Line | Style note |
|---|---|---|
| hk3 | CONCERT NIGHT · MAIN STAGE | mono overline |
| hk1 | 10,000 students. | 150px slam |
| hk2 | one night. | serif italic |
| old1 | 400 stories. gone in 24h. | "gone in 24h" weight 300 |
| old2 | AFTERMOVIE ETA: 34 DAYS | mono sticker |
| ring24 | 24h | coral ring |
| z1 | official photos of you: | serif italic |
| z0 | 0 | 300px coral |
| qrtag | SCAN BETWEEN SETS | mono sticker, coral chip |
| qr1 | one QR. that's it. | "that's it." weight 300 |
| s5tag | NO APP · NO LOGIN | mono sticker |
| caplabel | AI Face Search | phone caption (existing) |
| cl1 | 347 FOUND | mono coral counter chip |
| pr1 | before the encore *ends.* | "ends." serif italic coral |
| pr2 | NO LOGIN · NO APP · STRAIGHT TO WHATSAPP | mono overline |
| notif h3 | 347 new photos of you ✦ | coral numerals |
| notif sub | from the pit · tap to open | |
| wa row | bro the gallery has EVERYONE 😭🔥 | WhatsApp voice, Gen-Z |
| wa link | samaro.ai/g/fest24 | mono coral chip |
| pr3 | COMMITTEE: 4K GALLERY, ZERO OPS | mono sticker |
| end1 | you were there. | 118px paper |
| end2 | now *prove it.* | "prove it." serif italic coral |
| lk4 | find yourself today. | endcard serif |
| lk3 | events.samaro.ai | endcard mono coral |

Tone check: no corporate words, everything ≤6 words per visual line, "prove it." is the mic-drop.

---

## 8 · ASSET LIST

**Exists (kit):**
- iPhone frame CSS, notification card, WhatsApp-style dark card, photo-wall grid, `.fbk` coral brackets, `.line/.big` type system, grain+vignette, `#bgdark`.
- S_00..S_10 logo variants (color shutter). selfie.png (works as Rhea's selfie — reframe/crop square).
- SFX manifest families: latch, glass, chime, ui_confirm, click, thunk, noise_hit, sub_boom, riser, swoosh, shutter, ding, pop, camera_focus, tile, blip, count. Bed pipeline (loudnorm −14 LUFS).
- 54 wedding photos — usable as FALLBACK for mosaic tiles only with the heavy charcoal-duotone grade (build scenes); NOT ideal for the full-color climax.

**Must build / collect:**
1. **~20 concert/pit/crowd photos** (CC0 — Unsplash/Pexels: "concert crowd phone lights", "festival confetti", "dj crowd") → grade per §3; 15 needed full-color for the mosaic, incl. one young-woman shot for Rhea's tile (or reuse selfie.png subject). Check `assets/harvest/curated` first.
2. **`qrChar` primitive** — SVG QR (encode `events.samaro.ai/g/fest24`), paper modules, coral finder eyes as separately animatable nodes; bounce/squash tween.
3. **`ledWall` primitive** — charcoal bg + 6 scanlines + stage-glow radial + flicker helper.
4. **`bigSlam` primitive** — popIn variant: scale 1.55→1, skewX 6→0, blur 8→0, back.out(1.8).
5. **`stickerTag` component** — CSS chip (paper or coral fill, mono text, rotation prop, hard shadow).
6. **`mosaicBurst` rig** — 3×5 tile grid per §5 geometry + a single teleporting `.fbk` bracket element + counter chip with GSAP number tween.
7. **`strobeCut` helper** — 2-frame full-canvas inversion overlay, guarded so it never overlaps a text entrance (assert in code).
8. **5 Instagram-story cards** — restyled `.pcard` (168×288, coral progress bar).
9. **Licensed 150BPM-region phonk track** per §2 + librosa downbeat extraction + cue re-lock by bar index.

---

## 9 · CHARACTER SPEC

**Rhea, 21, final-year, front row of the pit.** We never need her "acted" — she exists as:
- **selfie.png** (existing) cropped to the coral-ring circle in S5 — the selfie IS the character introduction.
- **Her mosaic tile** (r2c2, §5): one full-color crowd photo of a young woman mid-scream/hands-up (harvest list item 1); the coral brackets belong to HER — every bracket jump in the climax starts and ends on her tile.
- **Her voice** in the WhatsApp card copy ("bro the gallery has EVERYONE 😭🔥") — Gen-Z register, no brand voice leakage.
- Coral = Rhea. Anywhere coral appears (0, QR eyes, ring, brackets, "prove it.") it means *her being found*. Never decorative — this is the brief's accent law and this reel's emotional spine.

**Secondary character: the QR.** Treated as a headliner (S4): walks on with a 3D card entrance, coral eyes blink on sequentially, bounces on downbeats like it's jumping to the drop, then dives into the phone to take the selfie. It reappears conceptually as the link chip in the WhatsApp card — the QR kept its promise.
