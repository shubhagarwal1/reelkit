#!/usr/bin/env python3
"""Beat grid + energy for a music file (analysis or bed prep).
  python3 extract_beats.py <audio> [--cut out.wav --start S --dur D]
Prints tempo / beat times / RMS; with --cut, writes a bed WAV starting at the
first energetic bar >= --start and re-extracts beats from the CUT file into
<out>.beats.json ({src, start_in_src, tempo, beats}). ALWAYS ffprobe the cut
WAV afterwards — corrupt mp3 sources decode short (see LESSONS.md).
"""
import json, sys, argparse
import numpy as np, librosa, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument('audio'); ap.add_argument('--cut'); ap.add_argument('--start', type=float, default=0.0)
ap.add_argument('--dur', type=float, default=35.0)
a = ap.parse_args()

y, sr = librosa.load(a.audio, sr=22050, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
tempo = float(np.atleast_1d(tempo)[0])
rms = librosa.feature.rms(y=y)[0]
print(f'tempo {tempo:.1f} BPM  beats {len(beats)}  dur {len(y)/sr:.1f}s  rms mean {rms.mean():.4f}')
print('first8', [round(float(b),3) for b in beats[:8]])

if a.cut:
    # start at the first beat >= --start where local RMS clears 70% of the track mean
    hop = 512; thr = 0.7 * rms.mean()
    t0 = a.start
    for b in beats:
        if b < a.start: continue
        i = int(b * sr / hop)
        if rms[i:i+8].mean() >= thr: t0 = float(b); break
    yf, srf = librosa.load(a.audio, sr=48000, mono=False, offset=t0, duration=a.dur)
    if yf.ndim == 1: yf = np.stack([yf, yf])
    sf.write(a.cut, yf.T, srf)
    yc, src_ = librosa.load(a.cut, sr=22050, mono=True)
    tc, bc = librosa.beat.beat_track(y=yc, sr=src_, units='time')
    grid = {'src': a.audio, 'start_in_src': round(t0,3),
            'tempo': round(float(np.atleast_1d(tc)[0]),1),
            'beats': [round(float(b),3) for b in bc]}
    out = a.cut.rsplit('.',1)[0] + '.beats.json'
    json.dump(grid, open(out,'w'))
    print(f'cut {a.cut} from {t0:.2f}s  ({len(yc)/src_:.1f}s decoded)  grid -> {out}')
