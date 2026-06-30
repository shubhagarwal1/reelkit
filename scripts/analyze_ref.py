#!/usr/bin/env python3
"""reelkit reference analyzer — deconstruct a reference video/song into a reusable recipe.

Runs three passes and writes <out>/recipe.json plus stems:
  1. demucs         -> vocals.wav + no_vocals.wav (instrumental bed, clean ad-libs)
  2. librosa        -> tempo (BPM), beat grid, downbeat spacing, a beat-snapped cut grid
  3. faster-whisper -> word-level transcript of any talking-head clip(s) (optional)

The recipe is the thing the skill reuses next time so it never re-measures a known
reference. Usage:
  python3 analyze_ref.py <reference.mp4|wav> <out_dir> [--vo clipA.mp4 clipB.mp4 ...]
"""
import json, os, sys, subprocess, argparse

def run(cmd):
    print('+', ' '.join(cmd)); subprocess.run(cmd, check=True)

def extract_audio(src, dst):
    run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src,
         '-vn', '-ac', '2', '-ar', '44100', dst])

def separate(audio, out_dir):
    # demucs two-stems: vocals vs everything-else (the instrumental bed)
    run([sys.executable, '-m', 'demucs', '--two-stems=vocals', '-o',
         os.path.join(out_dir, 'sep'), audio])
    base = os.path.splitext(os.path.basename(audio))[0]
    d = os.path.join(out_dir, 'sep', 'htdemucs', base)
    return os.path.join(d, 'vocals.wav'), os.path.join(d, 'no_vocals.wav')

def beats(audio):
    import librosa, numpy as np
    y, sr = librosa.load(audio, mono=True)
    tempo, beat_f = librosa.beat.beat_track(y=y, sr=sr)
    bt = librosa.frames_to_time(beat_f, sr=sr).tolist()
    tempo = float(np.atleast_1d(tempo)[0])
    beat = 60.0 / tempo if tempo else 0.5
    bar = beat * 4                       # 4/4 downbeat spacing
    dur = float(librosa.get_duration(y=y, sr=sr))
    # a clean beat-snapped cut grid: a downbeat every `bar` seconds from t=0
    grid = [round(i * bar, 3) for i in range(int(dur / bar) + 1)]
    return {'tempo_bpm': round(tempo, 2), 'beat_sec': round(beat, 3),
            'bar_sec': round(bar, 3), 'duration_sec': round(dur, 3),
            'beat_times': [round(t, 3) for t in bt], 'cut_grid': grid}

def transcribe(clip, out_dir):
    from faster_whisper import WhisperModel
    wav = os.path.join(out_dir, 'vo_' + os.path.splitext(os.path.basename(clip))[0] + '.wav')
    extract_audio(clip, wav)
    model = WhisperModel('base', device='cpu', compute_type='int8')
    segs, _ = model.transcribe(wav, word_timestamps=True)
    words = [{'t': w.word.strip(), 'a': round(w.start, 2), 'b': round(w.end, 2)}
             for s in segs for w in (s.words or [])]
    return {'clip': os.path.basename(clip), 'words': words}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('reference'); ap.add_argument('out_dir')
    ap.add_argument('--vo', nargs='*', default=[], help='talking-head clips to transcribe')
    ap.add_argument('--no-sep', action='store_true', help='skip demucs')
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    audio = os.path.join(a.out_dir, 'ref_audio.wav')
    extract_audio(a.reference, audio)

    recipe = {'reference': os.path.basename(a.reference)}
    recipe['rhythm'] = beats(audio)
    if not a.no_sep:
        v, nv = separate(audio, a.out_dir)
        recipe['stems'] = {'vocals': v, 'instrumental': nv}
    if a.vo:
        recipe['voice'] = [transcribe(c, a.out_dir) for c in a.vo]

    out = os.path.join(a.out_dir, 'recipe.json')
    json.dump(recipe, open(out, 'w'), indent=2)
    print('RECIPE ->', out)
    print(json.dumps(recipe.get('rhythm', {}), indent=2))

if __name__ == '__main__':
    main()
