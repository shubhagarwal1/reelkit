// Pure sound-design mixer (NO music bed). Reads window.__audio + __duration from
// index.html, resolves event types through sfx/manifest.json (genuine CC0 sounds),
// and mixes one audio.wav. Each cue is delayed to its time, round-robins through the
// type's samples, and gets a per-hit PITCH shift so nothing repeats linearly:
//   - tile  : ascending pentatonic riffle across a cascade
//   - others: small deterministic jitter so repeats never sound identical
// Usage: node build_audio.js [index.html] [audio.wav]
const { chromium } = require('playwright');
const { spawnSync } = require('child_process');
const path = require('path'), fs = require('fs');

const HTML = process.argv[2] || 'index.html';
const OUT  = process.argv[3] || 'audio.wav';
const manifest = JSON.parse(fs.readFileSync(path.resolve('sfx/manifest.json'),'utf8'));

// Expressive cue names used in the timelines -> real sample families in the manifest.
// (Without this, names like "click"/"tick"/"confirm" silently dropped to silence.)
// NOTE: tick/click/glitch etc. now resolve to their OWN dedicated synth families
// (added in the v2 kit) for crisper distinction, but every legacy name still resolves.
const ALIAS = {
  // legacy cue names (preserve existing reels' contract) ----------------------
  subdrop:'sub_boom', // deep low hit on a reveal/drop (was impact; sub_boom is purpose-built)
  tick:'tick',        // tiny high counter tick (own family now)
  typing:'type', key:'key',
  glitch:'digital',   // digital stutter (own family now; falls into buzz family timbrally)
  confirm:'ding', success:'ding',
  click:'click',      // crisp UI click (own family now)
  dropdown:'swoosh_down', panel:'whoosh', swipe:'swoosh_up', // panel/menu motion
  cam:'shutter', capture:'shutter',
  // new expressive aliases for the v2 categories ------------------------------
  blip:'blip', digital:'digital',
  swoosh:'transition_whoosh', transition:'transition_whoosh',
  thunk:'thunk', woodblock:'thunk', knock:'thunk',
  glass:'glass', chime:'chime', bell:'chime',
  ui_confirm:'ui_confirm', notify:'ui_confirm',
  latch:'latch', snap:'latch', toggle:'latch',
  camera_focus:'camera_focus', focus:'camera_focus',
  boom:'sub_boom', drop:'sub_boom',
  hit:'noise_hit', accent:'noise_hit', smack:'noise_hit',
  riser_up:'riser_short', build:'riser_long',
};
// resolve through the alias chain (max a few hops) until we hit a manifest family.
const resolve = (t) => {
  let cur = t, hops = 0;
  while (!manifest[cur] && ALIAS[cur] && hops++ < 5) cur = ALIAS[cur];
  return manifest[cur] ? cur : (ALIAS[t] || t);
};

// per-type levels (genuine SFX carry the track; a subtle ambient bed fills the gaps)
const GAIN = { type:0.46, whoosh:0.74, buzz:0.58, tile:0.56, shutter:0.80,
               ding:0.64, pop:0.62, impact:0.82, riser:0.60, count:0.34,
               // v2 families
               click:0.52, tick:0.40, key:0.46, blip:0.48, digital:0.54,
               swoosh_up:0.70, swoosh_down:0.70, transition_whoosh:0.74,
               thunk:0.66, glass:0.58, chime:0.62, ui_confirm:0.56,
               latch:0.54, camera_focus:0.60, riser_short:0.58, riser_long:0.60,
               sub_boom:0.84, noise_hit:0.74 };
const AMB_VOL = 0.72;   // trims the -20 LUFS bed to present-but-subtle texture (NOT a song)

// ---- per-hit PITCH (deterministic, seeded by cue counter n) -----------------
// Widened from the old ±7% jitter to a richer, longer non-repeating cycle so even
// a reused sample sounds distinct. Tonal families (tile/glass/chime/blip) riffle
// up a pentatonic; weighty families (riser/impact/sub_boom) stay near unity.
const PENT = [0,2,4,7,9,12,9,7,4,2];           // pentatonic up-and-down (semitones)
// 13-long coprime-ish jitter cycle (±~9%): never realigns with the file round-robin
const JIT  = [1.00,1.05,0.95,1.08,0.93,1.03,0.97,1.06,0.92,1.04,0.96,1.07,0.94];
const TONAL = new Set(['tile','glass','chime','blip','ding','ui_confirm','pop']);
const WEIGHTY = new Set(['riser','riser_short','riser_long','impact','sub_boom','noise_hit','thunk']);
function pitchFor(type, n){
  if (TONAL.has(type)) return Math.pow(2, PENT[n % PENT.length]/12);   // riffle
  if (WEIGHTY.has(type)) return [1.0,0.98,1.02,0.97,1.03][n%5];         // keep weight
  return JIT[n % JIT.length];
}
// ---- per-hit STEREO PAN (deterministic) -------------------------------------
// Subtle alternating placement so successive same-type hits separate spatially.
// Returns gains for L/R (constant-power-ish). Weighty/low content stays centered.
const PAN = [0.0, 0.28, -0.22, 0.18, -0.30, 0.12, -0.16, 0.24, -0.10, 0.20, -0.26, 0.08];
function panFor(type, n){
  if (WEIGHTY.has(type)) return 0;            // keep low end mono/centered
  return PAN[n % PAN.length];                  // -1 = hard L, +1 = hard R
}

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://'+path.resolve(HTML), { waitUntil:'networkidle' });
  await p.waitForFunction('window.__ready===true');
  const events  = await p.evaluate('window.__audio');
  const duration = await p.evaluate('window.__duration');
  await b.close();
  console.log(`${events.length} cues, dur=${duration}s (no bed — pure sound design)`);

  const counters = {};   // per-type hit index (drives pitch/pan cycles)
  const recent   = {};   // per-type ring buffer of recently used sample indices
  const inputs = [];
  const parts  = [];
  const labels = [];

  // Deterministic anti-repeat picker. For a family of `len` samples, never reuse
  // a sample that's in the last N picks for this type. Walk forward from a
  // counter-seeded start until we find one outside the recent window; if the
  // family is too small to avoid all recents, fall back to the least-recent.
  function pickIndex(type, len, n){
    const N = Math.min(len - 1, 4);               // forbid the last up-to-4 picks
    const used = recent[type] || (recent[type] = []);
    if (len <= 1) return 0;
    let idx = -1;
    for (let step = 0; step < len; step++){
      const cand = (n + step) % len;              // deterministic, seeded by n
      if (!used.includes(cand)) { idx = cand; break; }
    }
    if (idx < 0) idx = (n + 1) % len;             // family smaller than window
    if (idx === used[used.length - 1] && len > 1) // hard guarantee: not back-to-back
      idx = (idx + 1) % len;
    used.push(idx);
    if (used.length > N) used.shift();
    return idx;
  }

  // input 0 = continuous ambient bed (looped/trimmed to duration, subtle, faded)
  const ambFile = Array.isArray(manifest.ambient) ? manifest.ambient[0] : manifest.ambient;
  inputs.push(path.resolve(ambFile));
  // loudnorm gives the bed a consistent, present level (so silence is truly filled),
  // then AMB_VOL trims it to "subtle texture" rather than "song".
  parts.push(`[0:a]aresample=48000,aloop=loop=-1:size=2e9,atrim=0:${duration},` +
             `loudnorm=I=-20:TP=-3:LRA=7,` +
             `afade=t=in:st=0:d=0.8,afade=t=out:st=${(duration-1.4).toFixed(2)}:d=1.4,` +
             `volume=${AMB_VOL}[bed]`);
  labels.push('[bed]');

  events.forEach((e, i) => {
    const type  = resolve(e.type);
    const files = manifest[type];
    if (!files) { console.warn('no manifest entry for', e.type, '->', type); return; }
    const list = Array.isArray(files) ? files : [files];
    const n = (counters[type] = (counters[type]||0)); counters[type]++;
    const fi = pickIndex(type, list.length, n);     // anti-repeat sample choice
    const file = list[fi];
    const idx = inputs.length;
    inputs.push(path.resolve(file));
    const ms = Math.max(0, Math.round(e.t*1000));
    const g  = (GAIN[type] ?? 0.6) * (e.g ?? 1);
    const p  = pitchFor(type, n);
    const sr = Math.round(48000 * p);
    // per-hit stereo pan -> equal-power L/R gains (pan in [-1,1])
    const pan = panFor(type, n);
    const ang = (pan + 1) * Math.PI / 4;            // 0->left .. PI/2->right
    const gl = (Math.cos(ang) * Math.SQRT2).toFixed(3);
    const gr = (Math.sin(ang) * Math.SQRT2).toFixed(3);
    // normalize -> pitch-shift -> resample -> per-channel pan gains -> delay -> level
    parts.push(`[${idx}:a]aresample=48000,asetrate=${sr},aresample=48000,` +
               `aformat=channel_layouts=stereo,` +
               `pan=stereo|c0=${gl}*c0|c1=${gr}*c1,` +
               `adelay=${ms}|${ms},volume=${g.toFixed(3)}[s${i}]`);
    labels.push(`[s${i}]`);
  });

  // Optional music bed + endcard sting (env MUSIC / STING, or argv[4] / argv[5]).
  // The bed loops under the SFX as a present-but-subordinate layer; the sting is a one-shot
  // brand stab dropped ~1.5s before the end (over the endcard).
  const MUSIC = process.argv[4] || process.env.MUSIC;
  const STING = process.argv[5] || process.env.STING;
  if (MUSIC) {
    const mi = inputs.length; inputs.push(path.resolve(MUSIC));
    parts.push(`[${mi}:a]aresample=48000,aloop=loop=-1:size=2e9,atrim=0:${duration},` +
               `loudnorm=I=-18:TP=-3:LRA=8,afade=t=in:st=0:d=0.5,` +
               `afade=t=out:st=${(duration-1.4).toFixed(2)}:d=1.4,volume=0.6[music]`);
    labels.push('[music]');
  }
  if (STING) {
    const si = inputs.length; inputs.push(path.resolve(STING));
    const at = Math.max(0, Math.round((duration - 1.5) * 1000));
    parts.push(`[${si}:a]aresample=48000,adelay=${at}|${at},volume=0.9[sting]`);
    labels.push('[sting]');
  }

  parts.push(`${labels.join('')}amix=inputs=${labels.length}:normalize=0:duration=longest,` +
             `volume=0.92,alimiter=level=disabled:limit=0.97,apad,atrim=0:${duration},` +
             `aformat=sample_fmts=s16:channel_layouts=stereo[out]`);

  const args = [];
  inputs.forEach(f => { args.push('-i', f); });
  args.push('-filter_complex', parts.join(';'), '-map','[out]', '-ar','48000','-c:a','pcm_s16le','-y', OUT);
  console.log('ffmpeg inputs:', inputs.length);
  const r = spawnSync('ffmpeg', args, { stdio:['ignore','ignore','inherit'] });
  if (r.status !== 0) { console.error('ffmpeg failed'); process.exit(1); }
  console.log('AUDIO_DONE', OUT);
})();
