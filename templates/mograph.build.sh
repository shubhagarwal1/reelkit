#!/bin/bash
# reelkit motion-graphics build: GSAP page -> supersampled JPEG frames -> motion-blur graded
# silent mp4 -> + sound design (optional music bed) -> optional sound-off captions.
# Usage:  bash mograph.build.sh <film-dir> <output-name.mp4>
#   env: W H FPS SS WORKERS  MUSIC=path/to/bed.mp3  STING=path/to/sting.wav  CAPTIONS=1
# Run from the project root so build_audio.js finds sfx/manifest.json.
set -e
FILM="${1:?film dir}"; OUT="${2:?output name}"
PLUGIN="$(cd "$(dirname "$0")/.." && pwd)"          # reelkit root (scripts/ live here)
W=${W:-1080}; H=${H:-1920}; FPS=${FPS:-30}; SS=${SS:-2}

echo "[1/4] frames (${W}x${H} x${SS}, parallel, JPEG)…"
node "$PLUGIN/scripts/render_par.js" "$FILM/index.html" "$FILM/frames" $W $H $FPS $SS ${WORKERS:-}

echo "[2/4] sound design${MUSIC:+ + music bed}…"
MUSIC="$MUSIC" STING="$STING" node "$PLUGIN/scripts/build_audio.js" "$FILM/index.html" "$FILM/audio.wav" "$MUSIC" "$STING"

echo "[3/4] motion-blur + grade (raised black floor so nothing reads muddy)…"
# tmix blends ss frames -> real motion blur; grade lifts blacks, adds warmth, grain, vignette.
ffmpeg -y -loglevel error -framerate $((FPS*SS)) -i "$FILM/frames/%05d.jpg" \
  -vf "tmix=frames=${SS}:weights='1 1',fps=${FPS},eq=contrast=1.08:brightness=0.03:saturation=1.03:gamma_r=1.04:gamma_b=0.96,curves=all='0/0.03 0.25/0.24 0.5/0.5 0.75/0.78 1/1',noise=alls=10:allf=t+u,vignette=PI/4.5,format=yuv420p" \
  -c:v libx264 -crf 18 -preset slow "$FILM/silent.mp4"

echo "[4/4] mux…"
ffmpeg -y -loglevel error -i "$FILM/silent.mp4" -i "$FILM/audio.wav" \
  -c:v copy -c:a aac -b:a 192k -shortest "$FILM/$OUT"

if [ "${CAPTIONS:-}" = "1" ]; then
  echo "[+] burning sound-off captions…"
  python3 "$PLUGIN/scripts/captions.py" "$FILM/$OUT" "$FILM/captioned-$OUT"
fi

echo "DONE -> $FILM/$OUT"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=noprint_wrappers=1 "$FILM/$OUT"
