#!/bin/bash
# FAST build: parallel JPEG frames (render_par.js) + fast x264. Tunable via env.
#   bash build_fast.sh <dir>            # default SS=2 WORKERS=4 CRF=18 PRESET=faster
#   SS=1 bash build_fast.sh launchPO    # DRAFT (no motion-blur supersample, fastest)
#   SS=3 CRF=17 PRESET=slow bash build_fast.sh launchPO   # FINAL quality
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"; cd "$ROOT"
DIR="${1:-launchPO}"
W=1080; H=1920; FPS="${FPS:-30}"
SS="${SS:-2}"; WORKERS="${WORKERS:-4}"; CRF="${CRF:-18}"; PRESET="${PRESET:-faster}"; JPEG_Q="${JPEG_Q:-90}"
W8=$(printf '1 %.0s' $(seq 1 $SS))     # tmix weights: SS ones
T0=$(date +%s)
echo "[1/4] frames (SS=$SS workers=$WORKERS jpeg q$JPEG_Q)…"
JPEG_Q=$JPEG_Q node render_par.js "$DIR/index.html" "$DIR/frames" $W $H $FPS $SS $WORKERS
echo "[2/4] audio…"
MUSIC="$DIR/music.wav" node build_audio.js "$DIR/index.html" "$DIR/audio.wav"
echo "[3/4] motion-blur + encode (crf$CRF $PRESET)…"
if [ "$SS" -gt 1 ]; then VF="tmix=frames=${SS}:weights='${W8}',fps=${FPS},format=yuv420p"; else VF="format=yuv420p"; fi
ffmpeg -y -framerate $((FPS*SS)) -i "$DIR/frames/%05d.jpg" -vf "$VF" \
  -c:v libx264 -crf $CRF -preset $PRESET "$DIR/silent.mp4" -loglevel error
echo "[4/4] mux…"
ffmpeg -y -i "$DIR/silent.mp4" -i "$DIR/audio.wav" -c:v copy -c:a aac -b:a 256k -shortest \
  "$DIR/REEL.mp4" -loglevel error
echo "DONE -> $DIR/REEL.mp4  in $(( $(date +%s)-T0 ))s"
