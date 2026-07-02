#!/bin/bash
# ============================================================================
# gen_sfx_v2.sh — Richer, deterministic, license-clean SFX kit (ffmpeg only).
#
# Synthesizes MANY variations per category so a reel can fire dozens of the
# same TYPE without an audible repeat. Everything is:
#   - 48 kHz stereo, normalized to ~-1 dBFS
#   - short one-shots (no music bed)
#   - fully DETERMINISTIC (fixed params, no per-run randomness)
#
# Output: sfx/synth/<category>/<category>_<n>.wav
# These augment the existing CC0 mp3 families in sfx/genuine/* (never replace).
#
# Usage:  bash sfx/gen_sfx_v2.sh
# ============================================================================
set -e
ROOT="${1:-$(pwd)}"   # run from your project root (writes to <root>/sfx/synth)
S="$ROOT/sfx/synth"
SR=48000

# Peak-normalize to ~-1 dBFS, force 48k stereo. Two pass: measure peak, apply makeup
# gain, then a brick-wall limiter as safety. Deterministic (gain derived from input).
norm() {
  local maxdb gain
  maxdb=$(ffmpeg -i "$1" -af volumedetect -f null - 2>&1 | grep -oE 'max_volume: -?[0-9.]+' | grep -oE '\-?[0-9.]+$')
  [ -z "$maxdb" ] && maxdb=0
  # target peak = -1 dBFS
  gain=$(printf '%.3f' "$(echo "(-1) - (${maxdb})" | bc -l)")
  ffmpeg -y -i "$1" -af \
    "aresample=${SR},volume=${gain}dB,alimiter=limit=0.93,aformat=sample_fmts=s16:channel_layouts=stereo" \
    -ac 2 -ar ${SR} "$2" -loglevel error
  rm -f "$1"
}

mk() { mkdir -p "$S/$1"; }

# calc(expr) -> float with guaranteed leading zero (bc emits ".40", ffmpeg needs "0.400")
calc() { printf '%.4f' "$(echo "$1" | bc -l)"; }

# tone(out, freq, dur, decay, hp)  — decaying sine "blip/key/tone"
tone() {
  local out="$1" f="$2" d="$3" dec="$4" hp="${5:-20}"
  ffmpeg -y -f lavfi -i "sine=frequency=${f}:duration=${d}" \
    -af "volume='exp(-t*${dec})':eval=frame,highpass=f=${hp},afade=t=in:st=0:d=0.002" \
    "${out}.tmp.wav" -loglevel error
  norm "${out}.tmp.wav" "${out}"
}

# noiseburst(out, color, dur, atk, dec, bpf, bpw, hp) — filtered noise one-shot
noiseburst() {
  local out="$1" col="$2" d="$3" atk="$4" dec="$5" bpf="$6" bpw="$7" hp="${8:-60}"
  ffmpeg -y -f lavfi -i "anoisesrc=color=${col}:d=${d}:a=0.85" \
    -af "volume='(min(t/${atk},1))*(exp(-(max(0,t-${atk}))*${dec}))':eval=frame,bandpass=f=${bpf}:width_type=h:w=${bpw},highpass=f=${hp}" \
    "${out}.tmp.wav" -loglevel error
  norm "${out}.tmp.wav" "${out}"
}

# chirp(out, f0, f1, dur, mode)  — linear sine sweep; mode=up|down shapes envelope
chirp() {
  local out="$1" f0="$2" f1="$3" d="$4" mode="$5" lp="${6:-20000}"
  local env
  if [ "$mode" = "up" ]; then env="min(1,t/${d})"; else env="max(0,1-t/${d})"; fi
  ffmpeg -y -f lavfi \
    -i "aevalsrc='0.8*sin(2*PI*(${f0}*t + (${f1}-${f0})*t*t/(2*${d})))':d=${d}:s=${SR}" \
    -af "volume='${env}':eval=frame,lowpass=f=${lp},afade=t=in:st=0:d=0.004,afade=t=out:st=$(calc "$d-0.03"):d=0.03" \
    "${out}.tmp.wav" -loglevel error
  norm "${out}.tmp.wav" "${out}"
}

# thump(out, f, dur, dec, noisehp) — low sine body + click transient (impact/thunk/boom)
thump() {
  local out="$1" f="$2" d="$3" dec="$4" nhp="$5"
  ffmpeg -y -f lavfi -i "sine=frequency=${f}:duration=${d}" -f lavfi -i "anoisesrc=d=0.08:a=0.9" \
    -filter_complex \
    "[0:a]volume='exp(-t*${dec})':eval=frame[a];[1:a]volume='exp(-t*60)':eval=frame,highpass=f=${nhp}[b];[a][b]amix=inputs=2:normalize=0" \
    "${out}.tmp.wav" -loglevel error
  norm "${out}.tmp.wav" "${out}"
}

# two-tone(out, f1, f2, dur, dec) — interval ping (chime/glass/ui_confirm)
twotone() {
  local out="$1" f1="$2" f2="$3" d="$4" dec="$5"
  ffmpeg -y -f lavfi -i "sine=frequency=${f1}:duration=${d}" -f lavfi -i "sine=frequency=${f2}:duration=${d}" \
    -filter_complex \
    "[0:a]volume='exp(-t*${dec})':eval=frame[a];[1:a]volume='exp(-t*${dec})*0.7':eval=frame,adelay=0|0[b];[a][b]amix=inputs=2:normalize=0,highpass=f=200,afade=t=in:st=0:d=0.003" \
    "${out}.tmp.wav" -loglevel error
  norm "${out}.tmp.wav" "${out}"
}

echo ">> generating v2 kit into $S"

# ---------------------------------------------------------------------------
# CLICK — crisp soft UI click (mid transient). 8 variations.
mk click
CF=(1600 1750 1500 1850 1680 1550 1900 1620)
for i in 0 1 2 3 4 5 6 7; do
  noiseburst "$S/click/click_${i}.wav" white 0.05 0.001 $((90 + i*4)) "${CF[$i]}" 1200 700
done

# TICK — tiny high counter tick (very short). 8 variations.
mk tick
TF=(2200 2350 2500 2100 2650 2300 2450 2550)
for i in 0 1 2 3 4 5 6 7; do
  tone "$S/tick/tick_${i}.wav" "${TF[$i]}" 0.035 110 1200
done

# KEY — soft mechanical key press (body + click). 8 variations.
mk key
KF=(420 460 400 480 440 500 380 520)
for i in 0 1 2 3 4 5 6 7; do
  thump "$S/key/key_${i}.wav" "${KF[$i]}" 0.07 70 900
done

# BLIP — short digital sine blip. 8 variations.
mk blip
BF=(880 988 1047 784 1175 932 1319 740)
for i in 0 1 2 3 4 5 6 7; do
  tone "$S/blip/blip_${i}.wav" "${BF[$i]}" 0.09 40 300
done

# DIGITAL — gated stutter noise (data / glitch texture). 8 variations.
mk digital
DG_BPF=(1800 2200 1500 2600 2000 1300 2400 1700)
DG_GATE=(0.040 0.030 0.050 0.025 0.045 0.035 0.028 0.038)
for i in 0 1 2 3 4 5 6 7; do
  ffmpeg -y -f lavfi -i "anoisesrc=color=white:d=0.30:a=0.9" \
    -af "volume='(lt(mod(t,${DG_GATE[$i]}),${DG_GATE[$i]}/2))*0.9':eval=frame,highpass=f=700,bandpass=f=${DG_BPF[$i]}:w=2400" \
    "$S/digital/digital_${i}.wav.tmp.wav" -loglevel error
  norm "$S/digital/digital_${i}.wav.tmp.wav" "$S/digital/digital_${i}.wav"
done

# SWOOSH_UP — rising pitch: swept sine (low->high) + band-passed noise. 6 variations.
# Pitch motion comes from the sine sweep (filter freqs can't be time-varying in ffmpeg).
mk swoosh_up
SU_BPF=(1400 1800 1200 2000 1600 1500)
SU_F0=(300 350 280 380 320 340)
SU_F1=(2200 2600 2000 2800 2400 2300)
for i in 0 1 2 3 4 5; do
  d=$(calc "0.40 + $i*0.04")
  ffmpeg -y \
    -f lavfi -i "anoisesrc=color=pink:d=${d}:a=0.85" \
    -f lavfi -i "aevalsrc='0.6*sin(2*PI*(${SU_F0[$i]}*t + (${SU_F1[$i]}-${SU_F0[$i]})*t*t/(2*${d})))':d=${d}:s=${SR}" \
    -filter_complex "[0:a]volume='min(t/${d},1)*0.7':eval=frame,bandpass=f=${SU_BPF[$i]}:width_type=h:w=2600,highpass=f=350[n];[1:a]volume='min(t/${d},1)':eval=frame[s];[n][s]amix=inputs=2:normalize=0,afade=t=out:st=$(calc "$d-0.05"):d=0.05" \
    "$S/swoosh_up/swoosh_up_${i}.wav.tmp.wav" -loglevel error
  norm "$S/swoosh_up/swoosh_up_${i}.wav.tmp.wav" "$S/swoosh_up/swoosh_up_${i}.wav"
done

# SWOOSH_DOWN — falling pitch: swept sine (high->low) + band-passed noise. 6 variations.
mk swoosh_down
SD_BPF=(2800 3200 2400 3000 2600 2900)
SD_F0=(2400 2800 2200 3000 2600 2500)
SD_F1=(360 420 320 460 400 380)
for i in 0 1 2 3 4 5; do
  d=$(calc "0.42 + $i*0.04")
  ffmpeg -y \
    -f lavfi -i "anoisesrc=color=pink:d=${d}:a=0.85" \
    -f lavfi -i "aevalsrc='0.6*sin(2*PI*(${SD_F0[$i]}*t + (${SD_F1[$i]}-${SD_F0[$i]})*t*t/(2*${d})))':d=${d}:s=${SR}" \
    -filter_complex "[0:a]volume='max(0,1-t/${d})*0.7':eval=frame,bandpass=f=${SD_BPF[$i]}:width_type=h:w=2600,highpass=f=300[n];[1:a]volume='max(0,1-t/${d})':eval=frame[s];[n][s]amix=inputs=2:normalize=0,afade=t=in:st=0:d=0.03" \
    "$S/swoosh_down/swoosh_down_${i}.wav.tmp.wav" -loglevel error
  norm "$S/swoosh_down/swoosh_down_${i}.wav.tmp.wav" "$S/swoosh_down/swoosh_down_${i}.wav"
done

# TRANSITION_WHOOSH — full swell+fall whoosh for scene cuts. 6 variations.
mk transition_whoosh
TW_BPF=(1600 2000 1400 2200 1800 1500)
for i in 0 1 2 3 4 5; do
  d=$(calc "0.55 + $i*0.05")
  pk=$(calc "$d*0.45")
  ffmpeg -y -f lavfi -i "anoisesrc=color=pink:d=${d}:a=0.85" \
    -af "volume='(min(t/0.12,1))*(max(0,1-(t-${pk})/(${d}-${pk})))':eval=frame,bandpass=f=${TW_BPF[$i]}:width_type=h:w=1800,highpass=f=220" \
    "$S/transition_whoosh/transition_whoosh_${i}.wav.tmp.wav" -loglevel error
  norm "$S/transition_whoosh/transition_whoosh_${i}.wav.tmp.wav" "$S/transition_whoosh/transition_whoosh_${i}.wav"
done

# THUNK / WOODBLOCK — short woody knock. 8 variations.
mk thunk
THF=(180 210 160 240 195 220 170 200)
for i in 0 1 2 3 4 5 6 7; do
  thump "$S/thunk/thunk_${i}.wav" "${THF[$i]}" 0.12 38 1100
done

# GLASS — bright glassy ping interval. 8 variations.
mk glass
GA=(1568 1760 1976 1318 2093 1480 2349 1245)
GB=(2349 2637 2960 1976 3136 2217 3520 1865)
for i in 0 1 2 3 4 5 6 7; do
  twotone "$S/glass/glass_${i}.wav" "${GA[$i]}" "${GB[$i]}" 0.45 12
done

# CHIME — warm bell two-tone (success/notify). 8 variations.
mk chime
CA=(523 587 659 698 784 880 466 622)
CB=(784 880 988 1047 1175 1319 698 932)
for i in 0 1 2 3 4 5 6 7; do
  twotone "$S/chime/chime_${i}.wav" "${CA[$i]}" "${CB[$i]}" 0.6 8
done

# UI_CONFIRM — soft pleasant confirm (rising two-tone). 8 variations.
mk ui_confirm
UA=(660 700 620 740 680 720 640 760)
UB=(990 1050 930 1110 1020 1080 960 1140)
for i in 0 1 2 3 4 5 6 7; do
  twotone "$S/ui_confirm/ui_confirm_${i}.wav" "${UA[$i]}" "${UB[$i]}" 0.32 14
done

# LATCH — mechanical snap/latch (click + tiny body). 8 variations.
mk latch
LF=(900 980 840 1040 920 1000 880 960)
for i in 0 1 2 3 4 5 6 7; do
  thump "$S/latch/latch_${i}.wav" "${LF[$i]}" 0.05 95 1400
done

# CAMERA_FOCUS — soft double-beep focus confirm. 6 variations.
mk camera_focus
CFA=(1500 1600 1400 1700 1550 1650)
for i in 0 1 2 3 4 5; do
  f="${CFA[$i]}"
  ffmpeg -y -f lavfi -i "sine=frequency=${f}:duration=0.18" \
    -af "volume='(lt(mod(t,0.09),0.045))*exp(-mod(t,0.09)*40)':eval=frame,highpass=f=800,afade=t=in:st=0:d=0.002" \
    "$S/camera_focus/camera_focus_${i}.wav.tmp.wav" -loglevel error
  norm "$S/camera_focus/camera_focus_${i}.wav.tmp.wav" "$S/camera_focus/camera_focus_${i}.wav"
done

# RISER (short) — quick 0.6-0.9s builds. 4 variations.
mk riser_short
RS_D=(0.6 0.7 0.8 0.9)
RS_F1=(180 200 220 240)
RS_F2=(1600 1800 2000 2200)
for i in 0 1 2 3; do
  d="${RS_D[$i]}"
  ffmpeg -y -f lavfi \
    -i "aevalsrc='0.5*sin(2*PI*(${RS_F1[$i]}*t + (${RS_F2[$i]}-${RS_F1[$i]})*t*t/(2*${d})))':d=${d}:s=${SR}" \
    -f lavfi -i "anoisesrc=color=white:d=${d}:a=0.5" \
    -filter_complex "[0:a]volume='min(1,t/${d})':eval=frame[a];[1:a]volume='min(1,t/${d})*0.6':eval=frame,highpass=f=1500[b];[a][b]amix=inputs=2:normalize=0,afade=t=out:st=$(calc "$d-0.06"):d=0.06" \
    "$S/riser_short/riser_short_${i}.wav.tmp.wav" -loglevel error
  norm "$S/riser_short/riser_short_${i}.wav.tmp.wav" "$S/riser_short/riser_short_${i}.wav"
done

# RISER (long) — 1.4-2.0s builds. 4 variations.
mk riser_long
RL_D=(1.4 1.6 1.8 2.0)
for i in 0 1 2 3; do
  d="${RL_D[$i]}"
  ffmpeg -y -f lavfi \
    -i "aevalsrc='0.5*sin(2*PI*(200*t + 1600*t*t/(2*${d})))':d=${d}:s=${SR}" \
    -f lavfi -i "anoisesrc=color=white:d=${d}:a=0.5" \
    -filter_complex "[0:a]volume='min(1,t/${d})':eval=frame[a];[1:a]volume='min(1,t/${d})*0.6':eval=frame,highpass=f=1400[b];[a][b]amix=inputs=2:normalize=0,afade=t=out:st=$(calc "$d-0.08"):d=0.08" \
    "$S/riser_long/riser_long_${i}.wav.tmp.wav" -loglevel error
  norm "$S/riser_long/riser_long_${i}.wav.tmp.wav" "$S/riser_long/riser_long_${i}.wav"
done

# SUB_BOOM — deep sub drop for reveals. 6 variations.
mk sub_boom
SB_F0=(140 150 130 160 145 135)
SB_F1=(34 38 30 40 36 32)
for i in 0 1 2 3 4 5; do
  chirp "$S/sub_boom/sub_boom_${i}.wav" "${SB_F0[$i]}" "${SB_F1[$i]}" 0.9 down 180
done

# NOISE_HIT — bright filtered noise smack (cut accent). 8 variations.
mk noise_hit
NH_BPF=(2000 2400 1800 2800 2200 1600 2600 1900)
for i in 0 1 2 3 4 5 6 7; do
  noiseburst "$S/noise_hit/noise_hit_${i}.wav" white 0.18 0.001 $((28 + i*2)) "${NH_BPF[$i]}" 2600 800
done

# POP — short rounded pop (UI element appear). 8 variations.
mk pop
PF=(520 580 460 640 540 600 500 660)
for i in 0 1 2 3 4 5 6 7; do
  tone "$S/pop/pop_${i}.wav" "${PF[$i]}" 0.06 55 200
done

echo "SFX_V2_DONE"
find "$S" -name '*.wav' | wc -l
