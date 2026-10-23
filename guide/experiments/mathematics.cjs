// Published equations must render locally and remain usable on narrow screens.
const {chromium}=require('playwright');
const assert=require('node:assert/strict'),path=require('node:path');
const {pathToFileURL}=require('node:url');
(async()=>{
  const browser=await chromium.launch({args:['--no-sandbox']});
  try {
    const page=await browser.newPage();
    const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    let equations=0;
    for(const width of [1280,390])for(const name of ['geometric-optics','model','recreation-models','specification','optics','reconstruction','mathematics']){
      await page.setViewportSize({width,height:950});
      await page.goto(pathToFileURL(path.resolve(__dirname,'../site',name+'.html')).href);
      await page.evaluate(()=>document.fonts.ready);
      const n=await page.locator('.display-math .katex').count();
      assert(n>0,name+' has no rendered equations');
      assert.equal(await page.locator('.katex-error').count(),0);
      assert(await page.locator('.katex-html').evaluateAll(list=>list.every(e=>!e.textContent.includes('_'))),'Literal programming underscores reached visible mathematics');
      if(['model','geometric-optics','recreation-models'].includes(name))assert(await page.locator('.katex .mfrac').count()>2,name+' needs actual typeset fractions');
      if(name==='mathematics')assert((await page.locator('.katex-html').allTextContents()).some(t=>t.includes('∇')),'Gradient notation is missing');
      assert.equal(await page.locator('.display-math math').count(),n,'Every equation needs accessible MathML');
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),name+' overflows at '+width);
      assert(await page.evaluate(()=>document.fonts.check('16px KaTeX_Main')),'Local math fonts unavailable');
      equations+=n;
    }
    assert.deepEqual(errors,[]);
    console.log('PASS '+equations+' equation views: local KaTeX, MathML and desktop/mobile layout');
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
