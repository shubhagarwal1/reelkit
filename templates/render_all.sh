#!/bin/bash
# Render all 9 campaign films STRICTLY SERIALLY (one Chromium at a time — 8GB RAM limit).
# Clean frames+silent after each, copy final mp4 to Desktop folder, recompress >60MB. Retry-once.
cd /Users/shubh/Desktop/samaro-platform-reel
DEST=/Users/shubh/Desktop/motioneditsamaro/new; mkdir -p "$DEST"
log(){ echo "[$(date +%H:%M:%S)] $*"; }

FILMS="${FILMS:-10 11 12 13 14 15 16 17 18}"  # override via FILMS env to resume

for n in $FILMS; do
  D="launch$n"
  log "===== $D : render attempt 1 ====="
  rm -f $D/frames/*.png $D/frames/*.jpg 2>/dev/null || true
  pkill -9 -f render2.js 2>/dev/null; pkill -9 -f chrome-headless-shell 2>/dev/null; sleep 1
  OK=0
  if bash $D/build.sh; then OK=1; fi
  if [ "$OK" -ne 1 ]; then
    log "$D attempt 1 FAILED — retrying once"
    rm -f $D/frames/*.png 2>/dev/null || true
    pkill -9 -f render2.js 2>/dev/null; pkill -9 -f chrome-headless-shell 2>/dev/null; sleep 2
    if bash $D/build.sh; then OK=1; fi
  fi

  # locate the final mp4 (any .mp4 in dir that isn't silent.mp4), newest first
  MP4=$(ls -t $D/*.mp4 2>/dev/null | grep -v '/silent\.mp4$' | head -1)
  if [ "$OK" -eq 1 ] && [ -s "$MP4" ]; then
    SZ=$(stat -f%z "$MP4")
    if [ "$SZ" -gt 60000000 ]; then
      log "$D recompressing ($((SZ/1048576))MB)…"
      ffmpeg -y -i "$MP4" -c:v libx264 -crf 20 -preset medium -c:a copy "$D/.small.mp4" -loglevel error \
        && mv "$D/.small.mp4" "$MP4" && log "$D -> $(($(stat -f%z "$MP4")/1048576))MB"
    fi
    cp "$MP4" "$DEST/" && log "COPIED $(basename "$MP4") ($(($(stat -f%z "$MP4")/1048576))MB)"
  else
    log "!!!! $D FAILED both attempts — no mp4 copied"
  fi

  # clean scratch to free disk before next film
  rm -f $D/frames/*.png $D/frames/*.jpg $D/silent.mp4 2>/dev/null || true
  log "$D scratch cleaned. disk: $(df -h . | tail -1 | awk '{print $4}') free"
done

log "RENDER_ALL_DONE"
ls -la "$DEST"