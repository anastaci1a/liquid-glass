const fs=require('fs'),http=require('http'),path=require('path'),{chromium}=require('/workspace/docs/liquid-glass/node_modules/playwright');
(async()=>{
 const root='/workspace/docs/liquid-glass/site',requests=[];
 const server=http.createServer((req,res)=>{const name=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const file=path.resolve(root,'.'+name);if(!file.startsWith(root+'/')||!fs.existsSync(file)){res.writeHead(404);res.end();return;}res.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'application/javascript','.png':'image/png','.gif':'image/gif','.mp4':'video/mp4'})[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res);});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch({executablePath:'/browsers/chromium-1248/chrome-linux64/chrome',args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1280,height:950}});
 page.on('request',r=>requests.push(new URL(r.url()).pathname));await page.route(/\.(gif|mp4)(\?|$)/,r=>r.abort());
 await page.goto('http://127.0.0.1:'+server.address().port+'/liquid-glass/reconstruction.html',{waitUntil:'networkidle'});
 const report={scope:'Initial fresh desktop page, all details closed; GIF/MP4 attempts are intercepted and aborted to measure intent without downloading large captures.',counts:Object.fromEntries(['png','gif','mp4'].map(ext=>[ext,requests.filter(p=>p.endsWith('.'+ext)).length])),requests,closedDetails:await page.locator('details:not([open])').count(),bytes:await page.evaluate(()=>performance.getEntriesByType('resource').reduce((sum,r)=>sum+r.transferSize,0))};
 fs.writeFileSync('/evidence/extended/media-network-baseline.json',JSON.stringify(report,null,2)+'\n');console.log(report);await browser.close();await new Promise(r=>server.close(r));
})().catch(e=>{console.error(e);process.exit(1)});
