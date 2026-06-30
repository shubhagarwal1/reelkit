// Parametrized deterministic renderer with motion-blur supersampling.
// Usage: node render2.js <html> <outdir> <W> <H> <fps> <ss>
// Renders at fps*ss; ffmpeg later blends every <ss> frames (tmix) -> true motion blur.
const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');

const [,, htmlArg='index.html', outArg='frames', wArg='1080', hArg='1920', fpsArg='30', ssArg='3'] = process.argv;
const W=+wArg, H=+hArg, FPS=+fpsArg, SS=+ssArg;
const OUT = path.resolve(outArg);
const SRCFPS = FPS*SS;

(async () => {
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport:{width:W,height:H}, deviceScaleFactor:1 });
  await page.goto('file://'+path.resolve(htmlArg), { waitUntil:'networkidle' });
  await page.waitForFunction('window.__ready === true');
  await page.evaluate(async () => { await document.fonts.ready;
    await Promise.all(Array.from(document.images).map(i=>i.complete?0:i.decode().catch(()=>{}))); });
  const duration = await page.evaluate('window.__duration');
  const total = Math.ceil(duration * SRCFPS);
  console.log(`render ${W}x${H} dur=${duration}s out=${FPS}fps ss=${SS} (src ${SRCFPS}fps) frames=${total}`);
  const t0 = Date.now();
  for (let i=0;i<total;i++){
    const t = i / SRCFPS;
    await page.evaluate((t)=>window.__seek(t), t);
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    // JPEG q92 instead of PNG: ~2.7x faster to encode at this size, invisible after grade+grain.
    await page.screenshot({ path: path.join(OUT, String(i).padStart(5,'0')+'.jpg'), type:'jpeg', quality:92, clip:{x:0,y:0,width:W,height:H} });
    if (i%60===0 && i){ const el=(Date.now()-t0)/1000;
      console.log(`  ${i}/${total}  ${(el/i).toFixed(2)}s/frame  eta ${Math.round((total-i)*el/i)}s`); }
  }
  await browser.close();
  const el = (Date.now()-t0)/1000;
  console.log(`FRAMES_DONE ${total}`);
  console.log(`STATS  frames=${total}  res=${W}x${H}  ss=${SS}  elapsed=${Math.floor(el/60)}m${Math.round(el%60)}s  rate=${(el/total).toFixed(2)}s/frame`);
})();
