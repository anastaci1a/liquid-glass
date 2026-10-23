const fs=require('fs'),p='/mnt/user/live/projects/localica/localica-docs-publish/docs/liquid-glass/experiments/browser.cjs';let s=fs.readFileSync(p,'utf8');
s=s.replace("shape:'pill',background:'grid',depth:1", "shape:'pill',background:'lines',ink:'light',depth:1");
s=s.replace("const errors=[];page.on('pageerror',e=>errors.push(e.message));", "const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('crash',()=>errors.push('Renderer process crashed'));");
s=s.replace("check('Phone layout fits; no-WebGL fallback retains working controls',{});",`const phoneInfo=await phone.evaluate(()=>glassLab.settle());assert.equal(phoneInfo.viewWidth,520);assert(phoneInfo.renderSize[0]*phoneInfo.renderSize[1]<=960*400);
  await phone.click('#right');const phoneEdge=await phone.evaluate(()=>glassLab.settle());assert(Math.abs(phoneEdge.geometry.x+phoneEdge.geometry.w/2-(480+260-32))<.1);
  check('Phone layout fits; no-WebGL fallback retains working controls',{});
  await page.emulateMedia({reducedMotion:'reduce'});
  await configure({depth:2,band:.8,blur:5,tint:.3,trim:.5,weight:2,shine:1,shadow:.3,damping:35,shape:'circle',model:'1',background:'text',ink:'dark',reduce:false,hideLabel:true,source:true});
  await page.click('#reset');await settle();
  const reset=await page.evaluate(()=>Object.fromEntries([...document.querySelectorAll('input,select')].map(e=>[e.id,e.type==='checkbox'?e.checked:e.value])));
  assert.deepEqual(reset,{model:'0',shape:'pill',background:'lines',ink:'light',depth:'1',band:'0.55',blur:'0',tint:'0.02',trim:'0.12',weight:'1.6',shine:'0.35',shadow:'0.1',damping:'8',reduce:true,hideLabel:false,source:false});
  assert.equal(await page.locator('#menu').getAttribute('aria-pressed'),'false');
  await page.emulateMedia({reducedMotion:'no-preference'});
  check('Reset restores every control and the system Reduced Motion preference',{});
  for(let i=0;i<40;i++){
    await configure({shape:['panel','circle','pill'][i%3],model:String(i%2),blur:i%6});
    await page.click('#menu');await page.evaluate(()=>glassLab.advance(160));
  }
  assert.equal(await page.evaluate(()=>glassLab.error()),0);
  for(let i=0;i<3;i++){
    await page.evaluate(()=>glassLab.lose());await page.waitForFunction(()=>!glassLab.info().gpu);
    await page.evaluate(()=>glassLab.restore());await page.waitForFunction(()=>glassLab.info().gpu);
  }
  check('Repeated morph/model changes and three context recoveries remain functional',{});
  await page.click('#reset');await settle();await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  // Actual contact/recovery sequence, captured from this renderer.
  fs.mkdirSync(path.join(out,'pressure'),{recursive:true});
  await page.locator('#scene').scrollIntoViewIfNeeded();box=await page.locator('#scene').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();
  for(let i=0;i<60;i++){
    if(i<25)await page.mouse.move(box.x+box.width/2+(box.width/2+45)*i/24,box.y+box.height/2);
    if(i===32)await page.mouse.up();
    await page.evaluate(()=>glassLab.advance(1000/30));
    await page.locator('#stage').screenshot({path:path.join(out,'pressure',String(i).padStart(3,'0')+'.png')});
  }
`);
fs.writeFileSync(p,s);
