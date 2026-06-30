#!/usr/bin/env python3
"""reelkit sound-off captions — transcribe a video and burn styled captions for muted viewing.

~80% of social video is watched on mute, so captions are a quality multiplier. Transcribes with
faster-whisper (already a dep), writes an SRT, and burns it with ffmpeg as bold, high-contrast
text sitting inside the bottom safe area (clear of platform UI).

Usage:  python3 captions.py <in.mp4> <out.mp4> [--safe-bottom 0.18] [--color #FFFFFF]
"""
import sys, os, subprocess, argparse

def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--safe-bottom', type=float, default=0.18, help='fraction of height kept clear at the bottom')
    ap.add_argument('--color', default='#FFFFFF')
    ap.add_argument('--model', default='base')
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device='cpu', compute_type='int8')
    segs, _ = model.transcribe(a.inp, word_timestamps=False)

    srt = os.path.splitext(a.out)[0] + '.srt'
    with open(srt, 'w') as f:
        for i, s in enumerate(segs, 1):
            f.write(f"{i}\n{ts(s.start)} --> {ts(s.end)}\n{s.text.strip()}\n\n")

    # height to push captions up into the safe area
    H = int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=height', '-of', 'csv=p=0', a.inp],
        capture_output=True, text=True).stdout.strip() or 1280)
    margin = int(H * a.safe_bottom)
    hexc = a.color.lstrip('#')
    primary = f"&H00{hexc[4:6]}{hexc[2:4]}{hexc[0:2]}"   # ASS is &HAABBGGRR
    style = (f"FontName=Arial,Bold=1,Fontsize=22,PrimaryColour={primary},"
             f"BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV={margin}")
    srt_esc = srt.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', a.inp,
        '-vf', f"subtitles='{srt_esc}':force_style='{style}'",
        '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'copy', a.out], check=True)
    print('CAPTIONED ->', a.out)

if __name__ == '__main__':
    main()
