// The dedicated five-pass review must expose exact-pair wipe controls.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url'),{chromium}=require('playwright');
const guide=path.resolve(__dirname,'..'),url=pathToFileURL(path.join(guide,'site/outline-review.html')).href;
(async()=>{
 const browser=await chromium.launch({args:['--no-sandbox']});
 try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const metadata=JSON.parse(fs.readFileSync(path.join(guide,'outline-comparison-panels.json')));
  for(const width of [1280,390]){
   await page.setViewportSize({width,height:950});await page.goto(url);
   assert.equal(await page.locator('details[data-pass]').count(),5);
   assert.equal(await page.locator('img[data-comparison-top]').count(),Object.keys(metadata).length+4);
   const image=page.locator('img[data-comparison-top]').first();await image.evaluate(i=>(i.closest(".comparison")||i).scrollIntoView());await image.evaluate(i=>i.decode());
   const figure=page.locator('.comparison').first(),handle=figure.getByRole('slider'),frame=figure.locator('.comparison-frame');
   await handle.waitFor({state:'visible'});const ratio=await frame.evaluate(e=>e.style.aspectRatio.split('/').map(Number));const dims=await image.evaluate(i=>[(i.naturalWidth-2)/2,i.naturalHeight-38]);assert(Math.abs(ratio[0]/ratio[1]-dims[0]/dims[1])<1e-12);assert.equal(await handle.getAttribute('aria-valuenow'),'50');
   assert.match(await handle.getAttribute('aria-valuetext'),/Apple reference.*Outline proposal/);
   await handle.focus();await page.keyboard.press('Home');assert.equal(await handle.getAttribute('aria-valuenow'),'0');
   await page.keyboard.press('End');assert.equal(await handle.getAttribute('aria-valuenow'),'100');
   await page.keyboard.press('Home');await page.keyboard.press('Shift+ArrowRight');assert.equal(await handle.getAttribute('aria-valuenow'),'10');
   const b=await frame.boundingBox();await page.mouse.move(b.x+b.width*.1,b.y+b.height/2);await page.mouse.down();await page.mouse.move(b.x+b.width*.75,b.y+b.height/2,{steps:5});await page.mouse.up();assert.equal(await handle.getAttribute('aria-valuenow'),'75');
   await figure.getByRole('button',{name:'Side by side'}).click();assert(await image.isVisible());
   await figure.getByRole('button',{name:'Wipe',exact:true}).click();assert.equal(await handle.getAttribute('aria-valuenow'),'50');
   await figure.getByRole('button',{name:/Fullscreen/}).click();assert(await page.locator('dialog').isVisible());await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.querySelector('dialog').open);await page.waitForFunction(()=>document.activeElement?.classList.contains('image-expand'));assert(await figure.getByRole('button',{name:/Fullscreen/}).evaluate(b=>b===document.activeElement));
   const before=page.locator('details').filter({has:page.locator('summary',{hasText:'Starting model versus final proposal'})}).first();await before.evaluate(d=>d.open=true);
   const start=before.locator('img').first();await start.evaluate(i=>(i.closest(".comparison")||i).scrollIntoView());await start.evaluate(async i=>{while(!i.src)await new Promise(requestAnimationFrame);await i.decode();});
   await before.getByRole('slider').first().waitFor();assert.match(await before.getByRole('slider').first().getAttribute('aria-valuetext'),/Starting model.*Outline proposal/);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   for(const n of [1,2,3,4,5]){const d=page.locator(`details[data-pass="${n}"]`);await d.evaluate(x=>x.open=true);const child=d.locator('details').first();await child.evaluate(x=>x.open=true);const img=child.locator('img').first();await img.evaluate(i=>(i.closest(".comparison")||i).scrollIntoView());await img.evaluate(async i=>{while(!i.src)await new Promise(requestAnimationFrame);await i.decode();});await child.getByRole('slider').first().waitFor();}
  }
  const mobile=await browser.newContext({viewport:{width:390,height:950},hasTouch:true,isMobile:true}),touch=await mobile.newPage();await touch.goto(url);await touch.locator('img[data-comparison-top]').first().evaluate(i=>(i.closest('.comparison')||i).scrollIntoView());await touch.locator('img[data-comparison-top]').first().evaluate(i=>i.decode());const f=touch.locator('.comparison-frame').first();await f.scrollIntoViewIfNeeded();const b=await f.boundingBox(),cdp=await mobile.newCDPSession(touch),y=b.y+b.height/2;
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:b.x+b.width*.5,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:b.x+b.width*.7,y}]});await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});assert.equal(await touch.getByRole('slider').first().getAttribute('aria-valuenow'),'70');await mobile.close();
  assert.deepEqual(errors,[]);console.log('PASS five-pass wipe page: desktop/mobile, pointer/touch/keyboard, labels, fullscreen, all pass disclosures and native aspect ratios');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
