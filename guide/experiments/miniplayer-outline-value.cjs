const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
const guide=path.resolve(__dirname,'..'),url=pathToFileURL(path.join(guide,'site/miniplayer-outline-value.html')).href;
(async()=>{
 const metadata=JSON.parse(fs.readFileSync(path.join(guide,'outline-value-comparison-panels.json')));
 assert.equal(Object.keys(metadata).length,48);
 const browser=await chromium.launch({executablePath:process.env.LIQ_GLASS_BROWSER_EXECUTABLE,env:process.env.LIQ_GLASS_BROWSER_LIBRARY_PATH?{...process.env,LD_LIBRARY_PATH:process.env.LIQ_GLASS_BROWSER_LIBRARY_PATH}:undefined,args:['--no-sandbox']});
 try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:950});await page.goto(url);
   assert.equal(await page.locator('img[data-comparison-top]').count(),48);
   assert.equal(await page.locator('details[data-hsv]').count(),8);
   const image=page.locator('img[data-comparison-top]').first();await image.evaluate(i=>(i.closest('.comparison')||i).scrollIntoView());await image.evaluate(i=>i.decode());
   const figure=page.locator('.comparison').filter({has:page.locator('img[data-comparison-top]')}).first(),handle=figure.getByRole('slider'),frame=figure.locator('.comparison-frame');await handle.waitFor();
   assert.match(await handle.getAttribute('aria-valuetext'),/Apple reference.*Slightly brighter outline/);
   const ratio=await frame.evaluate(e=>e.style.aspectRatio.split('/').map(Number));const dims=await image.evaluate(i=>[(i.naturalWidth-2)/2,i.naturalHeight-38]);assert(Math.abs(ratio[0]/ratio[1]-dims[0]/dims[1])<1e-12);
   await handle.focus();await page.keyboard.press('Home');assert.equal(await handle.getAttribute('aria-valuenow'),'0');await page.keyboard.press('End');assert.equal(await handle.getAttribute('aria-valuenow'),'100');
   await page.keyboard.press('Home');for(let i=0;i<5;i++)await page.keyboard.press('Shift+ArrowRight');assert.equal(await handle.getAttribute('aria-valuenow'),'50');await frame.scrollIntoViewIfNeeded();
   const b=await frame.boundingBox();await page.mouse.move(b.x+b.width*.5,b.y+b.height/2);await page.mouse.down();await page.mouse.move(b.x+b.width*.7,b.y+b.height/2,{steps:5});await page.mouse.up();assert.equal(await handle.getAttribute('aria-valuenow'),'70');
   await figure.getByRole('button',{name:'Side by side'}).click();assert(await image.isVisible());await figure.getByRole('button',{name:'Wipe',exact:true}).click();
   await figure.getByRole('button',{name:/Fullscreen/}).click();assert(await page.locator('dialog').isVisible());await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('dialog').open);
   for(const id of await page.locator('details[data-hsv]').evaluateAll(ds=>ds.map(d=>d.dataset.hsv))){
    const d=page.locator(`[data-hsv="${id}"]`);await d.evaluate(x=>x.open=true);const img=d.locator('img').first();await img.evaluate(i=>(i.closest('.comparison')||i).scrollIntoView());await img.evaluate(async i=>{while(!i.src)await new Promise(requestAnimationFrame);await i.decode();});await d.getByRole('slider').first().waitFor();
    if(id.endsWith('previous'))assert.match(await d.getByRole('slider').first().getAttribute('aria-valuetext'),/Previous revision/);
   }
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  }
  const ctx=await browser.newContext({viewport:{width:390,height:950},hasTouch:true,isMobile:true});const touch=await ctx.newPage();await touch.goto(url);const img=touch.locator('img[data-comparison-top]').first();await img.evaluate(i=>(i.closest('.comparison')||i).scrollIntoView());await img.evaluate(i=>i.decode());const frame=touch.locator('.comparison').filter({has:touch.locator('img[data-comparison-top]')}).first().locator('.comparison-frame');await frame.scrollIntoViewIfNeeded();const b=await frame.boundingBox(),cdp=await ctx.newCDPSession(touch),y=b.y+b.height/2;
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:b.x+b.width*.5,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:b.x+b.width*.7,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await touch.getByRole('slider').first().getAttribute('aria-valuenow'),'70');await ctx.close();assert.deepEqual(errors,[]);
  console.log('PASS 48 outline-value comparison pairs, native aspect, desktop/mobile, keyboard/pointer/touch, fullscreen and detail disclosures');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});