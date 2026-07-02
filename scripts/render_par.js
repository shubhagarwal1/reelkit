// Parallel deterministic motion-blur renderer.
// Splits frames across N concurrent headless pages -> big speedup.
// Usage: node render_par.js <html> <outdir> <W> <H> <fps> <ss> <workers>
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs'), os = require('os');

const [,, htmlArg='index.html', outArg='frames', wArg='1080', hArg='1920', fpsArg='30', ssArg='3', wkArg=''] =
  process.argv;
const W=+wArg, H=+hArg, FPS=+fpsArg, SS=+ssArg;
// RAM-aware default: each concurrent page ~1.2GB at 1080x1920. Keep ~2GB headroom.
// Capped by CPU cores too. Override explicitly with the <workers> arg.
const GB = os.totalmem() / 2**30;
const ramCap = Math.max(1, Math.floor((GB - 2) / 1.2));
const WORKERS = +wkArg || Math.max(2, Math.min((os.cpus().length||4)-1, ramCap));
const QUALITY = +(process.env.JPEG_Q || 92);   // 97 for final masters, 90 for drafts
const OUT = path.resolve(outArg);
const SRCFPS = FPS*SS;
const fileURL = 'file://'+path.resolve(htmlArg);

async function makePage(browser){
  const page = await browser.newPage({ viewport:{width:W,height:H}, deviceScaleFactor:1 });
  // domcontentloaded, NOT networkidle — file:// pages with many local images can keep
  // networkidle from ever firing; __ready is the real readiness signal (with a timeout
  // so a broken page fails loudly instead of hanging the whole render).
  await page.goto(fileURL, { waitUntil:'domcontentloaded' });
  await page.waitForFunction('window.__ready === true', { timeout: 20000 });
  // fonts.ready can stall on a bad @font-face — race it against a 5s cap.
  await page.evaluate(async () => {
    await Promise.race([document.fonts.ready, new Promise(r=>setTimeout(r,5000))]);
    await Promise.all(Array.from(document.images).map(i=>i.complete?0:i.decode().catch(()=>{}))); });
  return page;
}

(async () => {
  fs.rmSync(OUT, { recursive:true, force:true });
  fs.mkdirSync(OUT, { recursive:true });
  const browser = await chromium.launch({ args:['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'] });
  const probe = await makePage(browser);
  const duration = await probe.evaluate('window.__duration');
  const total = Math.ceil(duration * SRCFPS);
  await probe.close();
  console.log(`render ${W}x${H} dur=${duration}s ${FPS}fps ss=${SS} (src ${SRCFPS}fps) frames=${total} workers=${WORKERS} (${GB.toFixed(0)}GB RAM)`);

  const t0 = Date.now();
  let next = 0; let done = 0;
  const claim = () => (next < total ? next++ : -1);

  async function worker(id){
    const page = await makePage(browser);
    let i;
    while ((i = claim()) !== -1){
      const t = i / SRCFPS;
      await page.evaluate((t)=>window.__seek(t), t);
      await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
      await page.screenshot({ path: path.join(OUT, String(i).padStart(5,'0')+'.jpg'), type:'jpeg', quality:QUALITY, clip:{x:0,y:0,width:W,height:H} });
      if ((++done) % 120 === 0) { const fps=(done/((Date.now()-t0)/1000)).toFixed(1); console.log(`  ${done}/${total}  (${fps} fps)`); }
    }
    await page.close();
  }

  await Promise.all(Array.from({length:WORKERS}, (_,k)=>worker(k)));
  await browser.close();
  const el = (Date.now()-t0)/1000;
  console.log('FRAMES_DONE '+total);
  console.log(`STATS  frames=${total}  res=${W}x${H}  ss=${SS}  workers=${WORKERS}  elapsed=${Math.floor(el/60)}m${Math.round(el%60)}s  rate=${(el/total).toFixed(2)}s/frame`);
})();
