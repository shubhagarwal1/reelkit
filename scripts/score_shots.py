#!/usr/bin/env python3
"""reelkit shot scorer — rank candidate clips/images by cinematographic quality, keep the best.

Scores each input on exposure, sharpness, and face framing (rule-of-thirds + headroom), then
prints a ranked list so you select the best-lit, best-composed takes and drop the rest. This is
the cheap CV pass; for finer judgement, hand the top frames to Claude with the cinematography
rubric. Uses only opencv + numpy (already in requirements).

Usage:  python3 score_shots.py <file-or-dir> [more files...]  [--top N]
"""
import sys, os, glob, cv2, numpy as np

FACE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
VID = ('.mp4', '.mov', '.m4v', '.webm'); IMG = ('.png', '.jpg', '.jpeg', '.webp')

def frames(path, n=5):
    if path.lower().endswith(IMG):
        im = cv2.imread(path); return [im] if im is not None else []
    c = cv2.VideoCapture(path); total = int(c.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    out = []
    for i in range(n):
        c.set(cv2.CAP_PROP_POS_FRAMES, int(total * (i + 0.5) / n))
        ok, fr = c.read()
        if ok: out.append(fr)
    c.release(); return out

def exposure(g):
    m = g.mean() / 255.0                       # want ~0.35-0.6
    clip = ((g < 6).mean() + (g > 249).mean()) # fraction crushed/blown
    return max(0, 1 - abs(m - 0.47) / 0.47) * (1 - min(clip * 4, 1))

def sharp(g):
    v = cv2.Laplacian(g, cv2.CV_64F).var()     # focus / detail
    return min(v / 400.0, 1.0)

def framing(g):
    h, w = g.shape
    faces = FACE.detectMultiScale(g, 1.2, 5, minSize=(int(w*0.06), int(w*0.06)))
    if len(faces) == 0:
        return 0.5                              # no face: neutral (could be product/wide)
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    cx, cy = (x + fw / 2) / w, (y + fh / 2) / h
    thirds = 1 - min(abs(cy - 1/3), abs(cy - 2/3)) / 0.33   # eyes near a third line
    headroom = 1 - min(abs(y / h - 0.12) / 0.12, 1)         # a little space above the head
    centered = 1 - min(abs(cx - 0.5) / 0.5, 1) * 0.5        # roughly framed horizontally
    return float(np.clip(0.45 * thirds + 0.3 * headroom + 0.25 * centered, 0, 1))

def score(path):
    fs = frames(path)
    if not fs: return None
    e = s = f = 0
    for fr in fs:
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        e += exposure(g); s += sharp(g); f += framing(g)
    n = len(fs); e, s, f = e/n, s/n, f/n
    total = 0.4 * e + 0.3 * s + 0.3 * f         # exposure weighted highest (lighting)
    return {'file': path, 'score': total, 'exposure': e, 'sharp': s, 'framing': f}

def main():
    args = [a for a in sys.argv[1:] if a != '--top']
    top = 0
    if '--top' in sys.argv:
        top = int(sys.argv[sys.argv.index('--top') + 1]); args = [a for a in args if not a.isdigit()]
    paths = []
    for a in args:
        paths += [a] if os.path.isfile(a) else glob.glob(os.path.join(a, '*'))
    paths = [p for p in paths if p.lower().endswith(VID + IMG)]
    rows = [r for r in (score(p) for p in paths) if r]
    rows.sort(key=lambda r: -r['score'])
    print(f"{'score':>6} {'expo':>5} {'sharp':>5} {'frame':>5}  file")
    for r in rows:
        print(f"{r['score']:6.2f} {r['exposure']:5.2f} {r['sharp']:5.2f} {r['framing']:5.2f}  {os.path.basename(r['file'])}")
    keep = rows[:top] if top else rows
    print('\nKEEP:', ' '.join(os.path.basename(r['file']) for r in keep) or '(none)')

if __name__ == '__main__':
    main()
