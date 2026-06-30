#!/bin/bash
# Build Samaro "Living Invites" (Film C): supersampled frames -> motion-blur silent mp4 -> + audio.
# Run from the project root (so build_audio.js finds sfx/manifest.json).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
W=1080; H=1920; FPS=30; SS=2
echo "[1/4] frames (${W}x${H} x${SS})…"
node render2.js launch12/index.html launch12/frames $W $H $FPS $SS
echo "[2/4] audio…"
node build_audio.js launch12/index.html launch12/audio.wav
echo "[3/4] motion-blur silent video…"
# Grade: warm-filmic master (duotone->colour handled in HTML via CSS). Order: grade -> grain -> vignette.
ffmpeg -y -framerate $((FPS*SS)) -i launch12/frames/%05d.png \
  -vf "tmix=frames=${SS}:weights='1 1',fps=${FPS},eq=contrast=1.08:brightness=0.02:saturation=1.02:gamma_r=1.04:gamma_b=0.96,curves=all='0/0 0.25/0.22 0.5/0.5 0.75/0.78 1/1',noise=alls=12:allf=t+u,vignette=PI/4.5,format=yuv420p" \
  -c:v libx264 -crf 17 -preset slow launch12/silent.mp4 -loglevel error
echo "[4/4] mux…"
ffmpeg -y -i launch12/silent.mp4 -i launch12/audio.wav -c:v copy -c:a aac -b:a 192k -shortest \
  launch12/Samaro-Invites-LivingInvitations.mp4 -loglevel error
echo "DONE -> launch12/Samaro-Invites-LivingInvitations.mp4"
ffprobe -v error -show_entries format=duration:stream=width,height -of default=noprint_wrappers=1 launch12/Samaro-Invites-LivingInvitations.mp4
