const {chromium}=require('playwright');
const {pathToFileURL}=require('url');
const path=require('path'),fs=require('fs'),assert=require('assert');
(async()=>{
 const browser=await chromium.launch({args:['--no-sandbox']});
 try{
  const page=await browser.newPage(),checks=[];
  for(const width of [390,1280])for(const name of ['index','outline-review']){
   await page.setViewportSize({width,height:900});
   await page.goto(pathToFileURL(path.resolve(__dirname,'../../../guide/site/research/experiments/clear-play-02',name+'.html')).href);
   await page.evaluate(()=>document.fonts.ready);
   await page.locator('main img').evaluateAll(images=>Promise.all(images.map(i=>i.decode())));
   const result=await page.evaluate(()=>({
    overflow:document.documentElement.scrollWidth>innerWidth,
    images:[...document.querySelectorAll('main img')].map(i=>({loaded:i.complete&&i.naturalWidth>0})),
    math:document.querySelectorAll('.katex').length,
    errors:document.querySelectorAll('.katex-error').length
   }));
   assert(!result.overflow);assert(result.images.every(i=>i.loaded));assert(result.math>0&&!result.errors);
   checks.push({width,name,...result});
  }
  fs.writeFileSync(path.join(__dirname,'website-check.json'),JSON.stringify({status:'PASS',checks},null,2)+'\n');
  console.log('PASS desktop/mobile figures and typeset equations');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
