#!/usr/bin/env python3
"""Harvest hi-res CC/PD photos for the use-case reels from Wikimedia Commons + Openverse.
Casting shot-lists per reel; downloads candidates to assets/harvest/raw/<reel>/ with a
manifest (source, license, dimensions) for later attribution/curation.
Usage: python3 harvest_assets.py [reel ...]   (default: all)
"""
import json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, 'assets', 'harvest', 'raw')
UA = {'User-Agent': 'SamaroReelHarvest/1.0 (shubh@samaro.ai) python-urllib'}
MIN_W = 1600          # accept >=1600 (displayed <=1100px); prefer bigger via sort below
PER_QUERY = 8

SHOTLIST = {
    'marathon': [
        'marathon finish line celebration', 'marathon runner finishing arms raised',
        'marathon runners race street', 'running race bib number runner',
        'marathon start crowd corral', 'city marathon crowd cheering',
    ],
    'corporate': [
        'technology conference keynote stage', 'business conference audience',
        'conference networking people talking', 'award ceremony business event',
        'corporate summit panel discussion', 'conference speaker presentation screen',
    ],
    'fest': [
        'concert crowd hands raised lights', 'music festival confetti stage',
        'dj stage lights crowd night', 'concert crowd phone lights',
        'music festival crowd night stage', 'college festival concert india',
    ],
    'dadi': [
        'indian grandmother smiling', 'elderly indian woman sari portrait',
        'indian wedding elderly woman', 'grandmother india candid',
    ],
    'photographer': [
        'wedding photographer with camera', 'photographer camera closeup working',
        'event photographer shooting', 'camera lens hands photographer',
    ],
    # round 2 — targeted gap-fills after casting review
    'fest_r2': [
        'EDM concert crowd night stage lights', 'confetti drop concert night crowd',
        'crowd silhouette stage lights night', 'nightclub dj mixing turntables',
        'music festival night main stage fireworks', 'concert audience dancing night',
    ],
    'corporate_r2': [
        'gala dinner event round tables', 'corporate awards ceremony trophy stage',
        'conference lanyard badge attendees', 'business team applause event',
    ],
    'marathon_r2': [
        'marathon finisher medal celebrating', 'night run city race lights',
        'runner crossing finish tape', 'marathon crowd spectators cheering runners',
    ],
}

def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def commons_search(query, limit=PER_QUERY):
    q = urllib.parse.quote(query)
    url = ('https://commons.wikimedia.org/w/api.php?action=query&generator=search'
           f'&gsrsearch=filetype:bitmap%20{q}&gsrnamespace=6&gsrlimit={limit*2}'
           '&prop=imageinfo&iiprop=url%7Csize%7Cextmetadata&iiurlwidth=3200&format=json')
    try: data = fetch_json(url)
    except Exception as e: print('  commons ERR', e); return []
    out = []
    for p in (data.get('query', {}).get('pages', {}) or {}).values():
        ii = (p.get('imageinfo') or [{}])[0]
        w, h = ii.get('width', 0), ii.get('height', 0)
        if w < MIN_W or not ii.get('url'): continue
        if not re.search(r'\.(jpe?g|png)$', ii['url'], re.I): continue
        meta = ii.get('extmetadata', {})
        lic = (meta.get('LicenseShortName', {}) or {}).get('value', '?')
        # thumb at 3200 wide if original is giant, else original
        dl = ii.get('thumburl') or ii['url']
        out.append({'src': 'commons', 'title': p.get('title', ''), 'url': dl,
                    'page': ii.get('descriptionurl', ''), 'w': w, 'h': h, 'license': lic})
    return out[:limit]

def openverse_search(query, limit=PER_QUERY):
    q = urllib.parse.quote(query)
    url = (f'https://api.openverse.org/v1/images/?q={q}&page_size={limit*3}'
           '&license_type=commercial&filter_dead=false')
    try: data = fetch_json(url)
    except Exception as e: print('  openverse ERR', e); return []
    out = []
    for r in data.get('results', []):
        w, h = r.get('width') or 0, r.get('height') or 0
        if w < MIN_W: continue
        u = r.get('url', '')
        if not re.search(r'\.(jpe?g|png)(\?|$)', u, re.I): continue
        out.append({'src': 'openverse', 'title': r.get('title', ''), 'url': u,
                    'page': r.get('foreign_landing_url', ''), 'w': w, 'h': h,
                    'license': r.get('license', '?')})
    return out[:limit]

def download(item, dest):
    try:
        req = urllib.request.Request(item['url'], headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, 'wb') as f:
            f.write(r.read())
        return os.path.getsize(dest) > 30000
    except Exception as e:
        print('  dl ERR', e); return False

def main(reels):
    for reel in reels:
        outdir = os.path.join(RAW, reel); os.makedirs(outdir, exist_ok=True)
        manifest, n = [], 0
        print(f'=== {reel} ===')
        for q in SHOTLIST[reel]:
            print(f'  [{q}]')
            cands = commons_search(q) + openverse_search(q)
            cands.sort(key=lambda c: -c['w'])          # biggest first (4K preference)
            got = 0
            for c in cands:
                if got >= 4: break                      # per-query cap after both sources
                ext = '.png' if c['url'].lower().split('?')[0].endswith('png') else '.jpg'
                dest = os.path.join(outdir, f'{reel}_{n:03d}{ext}')
                if download(c, dest):
                    c['file'] = os.path.basename(dest); c['query'] = q
                    manifest.append(c); n += 1; got += 1
                time.sleep(0.4)
        with open(os.path.join(outdir, 'manifest.json'), 'w') as f:
            json.dump(manifest, f, indent=1)
        print(f'  -> {n} files, manifest written')

if __name__ == '__main__':
    reels = sys.argv[1:] or list(SHOTLIST)
    main(reels)
