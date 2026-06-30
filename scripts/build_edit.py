#!/usr/bin/env python3
# reelkit live-action edit engine: vintage grade + text composited BEHIND the subject
# (rembg person matte), Ken-Burns stills, beat-snapped cuts. Reads an editmap.json.
# Usage: python3 build_edit.py <editmap.json>
#   - asset paths in the editmap resolve relative to the editmap's own folder
#   - output = editmap["output"] (rel to that folder), default "reel.mp4"
import json, os, subprocess, math, shutil, sys, time
import cv2, numpy as np
from rembg import remove, new_session
T0 = time.time()

EDITMAP = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.getcwd(), 'editmap.json')
DIR = os.path.dirname(EDITMAP)
M = json.load(open(EDITMAP))
W, H, FPS = M['width'], M['height'], M['fps']
RED = M.get('RED', '#E01010')
# Fonts: editmap may override (serif/sans). Defaults target macOS — override on other OSes.
SERIF = M.get('serif', '/System/Library/Fonts/Times.ttc')
SANS  = M.get('sans',  '/System/Library/Fonts/Supplemental/Arial Bold.ttf')
WORK = os.path.join(DIR, 'work_edit'); os.makedirs(WORK, exist_ok=True)
# Editable color grade. editmap["grade"] overrides this whole filter string if present.
GRADE = M.get('grade',
         "format=gbrp,curves=r='0/0.05 0.25/0.27 0.5/0.55 0.75/0.81 1/0.99'"
         ":g='0/0.03 0.5/0.49 1/0.96':b='0/0.07 0.5/0.45 1/0.89',"
         "eq=contrast=1.10:saturation=0.76:gamma=0.95:gamma_r=1.03:gamma_b=0.96,"
         "vignette=PI/4.0,gblur=sigma=0.4,noise=alls=8:allf=t,format=yuv420p")
ZEND = {'slowpush': 1.08, 'push': 1.16, 'hold': 1.0}

def ff(args):
    r = subprocess.run(['ffmpeg','-y','-loglevel','error']+args)
    if r.returncode != 0: print('ffmpeg failed:', ' '.join(args)); sys.exit(1)

def esc(t):
    return str(t).replace('\\','\\\\').replace(':','\\:').replace("'","’").replace(',','\\,')
def fit(t, base, factor):
    return min(base, int((0.86*W)/(factor*max(len(str(t)),1))))
def fitBig(t, base):
    return min(base, int((0.92*W)/(0.62*max(len(str(t)),1))))

def bigword(text, sz, y, off, a=None, b=None):
    f = (f"drawtext=fontfile='{SERIF}':text='{esc(text)}':fontcolor={RED}:fontsize={sz}"
         f":x=(w-tw)/2:y={y}:shadowcolor=black@0.55:shadowx=3:shadowy=3")
    if a is not None:
        f += f":enable='between(t,{round(a-off,3)},{round(b-off,3)})'"
    return f

# BEHIND the subject: big top words + title (head/body overlaps the letters)
def text_behind(s):
    off = s['start']; f = []
    for w in s.get('words', []):
        f.append(bigword(w['t'], fitBig(w['t'], 210), '0.06*h', off, w['a'], w['b']))
    if 'title' in s:
        f.append(bigword(s['title']['top'], fitBig(s['title']['top'],210), '0.06*h', off))
        f.append(bigword(s['title']['bottom'], fitBig(s['title']['bottom'],210), 'h-th-0.10*h', off))
    return ','.join(f)

# IN FRONT: lower-third caption build + footer subtitle (sit over the subject)
def text_front(s):
    off = s['start']; f = []
    for w in s.get('capwords', []):
        f.append(bigword(w['t'], fit(w['t'],64,0.60), 'h-th-0.16*h', off, w['a'], w['b']))
    if 'footer' in s:
        ft = s['footer']; fsz = fit(ft['t'],30,0.54)
        f.append(f"drawtext=fontfile='{SANS}':text='{esc(ft['t'])}':fontcolor=white:fontsize={fsz}"
                 f":x=(w-tw)/2:y=h-th-0.10*h:box=1:boxcolor=black@0.5:boxborderw=14"
                 f":enable='between(t,{round(ft['a']-off,3)},{round(ft['b']-off,3)})'")
    return ','.join(f)

os.environ['ONNXRUNTIME_EXECUTION_PROVIDERS'] = 'CPUExecutionProvider'
SESSION = new_session('u2net_human_seg', providers=['CPUExecutionProvider'])
def frame_count(mp4):
    c = cv2.VideoCapture(mp4); n = int(c.get(cv2.CAP_PROP_FRAME_COUNT)); c.release(); return n
def matte_of(img_bgr, ow, oh, blur=2.0):
    # one person matte at output size ow x oh (segment at low-res for speed, upscale + feather)
    small = cv2.resize(img_bgr, (360, 640))
    m = remove(small[:, :, ::-1], session=SESSION, only_mask=True, post_process_mask=True)
    if m.ndim == 3: m = m[:, :, 0]
    m = cv2.resize(m, (ow, oh), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m, (0, 0), blur)
def mid_frame(mp4):
    c = cv2.VideoCapture(mp4); n = int(c.get(cv2.CAP_PROP_FRAME_COUNT))
    c.set(cv2.CAP_PROP_POS_FRAMES, max(n // 2, 0)); ok, fr = c.read(); c.release()
    return fr if ok else None

parts = []
for s in M['segments']:
    sid = '%02d' % s['id']
    dur = round(s['end'] - s['start'], 4)
    src = os.path.join(DIR, s['file'])
    base = os.path.join(WORK, f'base_{sid}.mp4')
    d = max(int(round(dur*FPS)), 1)
    bt = text_behind(s); frt = text_front(s)
    need_matte = bool(s.get('behind') and bt)
    matte_in = None  # ffmpeg input args for the alpha (image-loop or video)
    # ---- pass 1: graded base, NO text (+ build matte source if needed) ----
    if s['type'] == 'video':
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{GRADE}"
        ff(['-ss', str(s.get('in',0)), '-i', src, '-t', str(dur), '-an', '-vf', vf,
            '-r', str(FPS), '-c:v','libx264','-crf','18','-preset','medium', base])
        if need_matte:
            mp = os.path.join(WORK, f'matte_{sid}.png')   # one static matte (subject ~still)
            cv2.imwrite(mp, matte_of(mid_frame(base), W, H))
            matte_in = ['-loop','1','-i', mp]
    else:
        ze = ZEND.get(s.get('move'),1.08); z = f"'1+({ze}-1)*on/{max(d-1,1)}'"
        kb = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
              f"zoompan=z={z}:d={d}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
        ff(['-i', src, '-vf', kb + ',' + GRADE, '-frames:v', str(d), '-r', str(FPS),
            '-c:v','libx264','-crf','18','-preset','medium', base])
        if need_matte:
            # matte the source still, then apply the SAME Ken-Burns move so it tracks the base
            msrc = os.path.join(WORK, f'mattesrc_{sid}.png')
            img = cv2.imread(src); cv2.imwrite(msrc, matte_of(img, img.shape[1], img.shape[0]))
            mvid = os.path.join(WORK, f'matte_{sid}.mp4')
            ff(['-i', msrc, '-vf', kb + ',format=gray', '-frames:v', str(d), '-r', str(FPS),
                '-c:v','libx264','-crf','16','-preset','medium', mvid])
            matte_in = ['-i', mvid]
    # ---- pass 2: behind-text via matte (big words/title), front-text over (caps/footer) ----
    out = os.path.join(WORK, f'seg_{sid}.mp4')
    if need_matte:
        chain = f"[0:v]split=2[a][b];[a]{bt}[bg];[b][1:v]alphamerge[person];[bg][person]overlay=format=auto"
        chain += f",{frt}[out]" if frt else "[out]"
        ff(['-i', base] + matte_in + ['-filter_complex', chain, '-map','[out]','-frames:v',str(d),
            '-r',str(FPS),'-c:v','libx264','-crf','18','-preset','medium', out])
        print(f'seg {s["id"]}: {dur}s  BEHIND  {s["file"]}')
    elif bt or frt:
        chain = ','.join(x for x in [bt, frt] if x)
        ff(['-i', base, '-vf', chain, '-c:v','libx264','-crf','18','-preset','medium', out])
        print(f'seg {s["id"]}: {dur}s  over-text  {s["file"]}')
    else:
        shutil.copyfile(base, out)
        print(f'seg {s["id"]}: {dur}s  no-text  {s["file"]}')
    parts.append(out)

lst = os.path.join(WORK, 'concat.txt')
open(lst,'w').write('\n'.join(f"file '{p}'" for p in parts))
silent = os.path.join(WORK, 'video_silent.mp4')
ff(['-f','concat','-safe','0','-i',lst,'-c','copy', silent])
final = os.path.join(DIR, M.get('output', 'reel.mp4'))
ff(['-i', silent, '-i', os.path.join(DIR, M['audio']),
    '-c:v','libx264','-crf','23','-preset','medium','-pix_fmt','yuv420p',
    '-c:a','aac','-b:a','192k','-shortest', final])
print('DONE ->', final)
el = time.time() - T0
nfr = int(round(M['duration'] * FPS))
mb = os.path.getsize(final) / 1048576
print(f"STATS  segments={len(M['segments'])}  frames={nfr}  res={W}x{H}@{FPS}  "
      f"dur={M['duration']}s  size={mb:.1f}MB  elapsed={int(el//60)}m{int(el%60)}s")
