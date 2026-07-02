// Quick preview: screenshot given times + report page errors. node shot.js <html> <outdir> t1 t2 ...
const { chromium } = require('playwright');
const path=require('path'), fs=require('fs');
const [,,html,outdir,...ts]=process.argv;
(async()=>{
  const errs=[];
  const browser=await chromium.launch({args:['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']});
  const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
  page.on('pageerror',e=>errs.push(String(e)));
  page.on('console',m=>{ if(m.type()==='error') errs.push('console:'+m.text()); });
  await page.goto('file://'+path.resolve(html),{waitUntil:'domcontentloaded'});
  await page.waitForFunction('window.__ready===true',{timeout:20000});
  await page.evaluate(async()=>{await Promise.race([document.fonts.ready,new Promise(r=>setTimeout(r,5000))]);
    await Promise.all(Array.from(document.images).map(i=>i.complete?0:i.decode().catch(()=>{})));});
  fs.mkdirSync(outdir,{recursive:true});
  for(const t of ts){ await page.evaluate(x=>window.__seek(x),+t);
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    await page.screenshot({path:path.join(outdir,'s_'+t+'.png')}); }
  await browser.close();
  console.log('DONE errs='+JSON.stringify(errs));
})();
