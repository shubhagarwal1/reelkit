---
name: asset-casting
description: >-
  Harvest hi-res, license-safe photos from the open web (Wikimedia Commons + Openverse, no API
  keys) and curate them like a casting director. Use when a reel needs real photography (crowds,
  events, people, venues) and you have no client footage. Produces a per-reel curated folder with
  a license manifest ready for attribution.
---

# Asset harvest & casting

Treat stock sourcing as **casting a movie**, not keyword search: write a shot-list per reel,
harvest wide, then review montages and reject like a director.

## 1. Harvest

`scripts/harvest_assets.py` — edit the `SHOTLIST` dict (one list of specific, cinematic queries
per reel), then run. It queries **Wikimedia Commons** (API, `iiurlwidth=3200` thumbs) and
**Openverse** (`license_type=commercial`) — both keyless — keeps only images ≥1600px wide,
downloads biggest-first, and writes a `manifest.json` per reel with `source / page / license /
dimensions` for every file.

Query craft: describe the FRAME, not the topic — "marathon runner finishing arms raised", not
"marathon". Add a second targeted round (`*_r2` keys) after the first casting review to fill gaps.

## 2. Casting review

Montage each reel's raw folder into contact sheets and READ them. Reject:

- **Recognizable public figures** (politicians surface constantly in "conference/summit" queries).
- **Third-party event branding** — race banners, sponsor walls, betting logos, branded podiums.
- **Logo apparel** on foreground subjects.
- **Wrong-context matches** (religious festivals for "festival", statues/cranes for people
  queries) — Commons search is literal-minded.
- Anything below the reel's grade: flat light, motion junk, watermarks.

Keep 10–15 per reel, rename to a stable scheme (`fest_01.jpg`…), copy into
`assets/curated/<reel>/` with a filtered manifest.

## 3. Use in reels

- **Downscale for render weight**: headless Chromium decodes every page load per worker — copy the
  picks used by a reel into its dir at ~900px. Keep total image/background count <40 per page.
- Preload used images (hidden `<img>`) so the renderer's decode-wait actually covers them.
- Grade in CSS, subtly: `saturate(1.06)` on color photos; never force grayscale on hero photos —
  it reads as a quality drop, not a style.
- **Attribution**: CC0/PD need nothing; CC BY / CC BY-SA require credit — carry the manifest
  through to delivery and put credits in the post caption/description.
