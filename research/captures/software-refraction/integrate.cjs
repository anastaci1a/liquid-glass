const fs=require('fs'),r='/mnt/user/live/projects/localica/localica-docs-publish/docs/liquid-glass/';
let s=fs.readFileSync(r+'lab.js','utf8');
s=s.replace("const canvas = $('scene'), fallback = $('fallback'), foreground = $('foreground');","const canvas = $('scene'), fallback = $('fallback'), foreground = $('foreground');\n  const software = createSoftwareLens(fallback);\n  let rendererReason = ''; ");
s=s.replace("if(new URLSearchParams(location.search).has('fallback'))return false;","if(new URLSearchParams(location.search).has('fallback')){rendererReason='Software rendering requested by the URL.';return false;}");
s=s.replace('if(!gl)return false;',"if(!gl){rendererReason='This browser did not provide a WebGL2 context.';return false;}");
s=s.replace("lost=false;fallback.hidden=true;$('status').textContent='WebGL2 · background refraction';return true;","lost=false;fallback.hidden=true;rendererReason='';$('retry').hidden=true;$('rendererNote').textContent='';$('status').textContent='WebGL2 · background refraction';return true;");
s=s.replace("}catch(error){console.warn('Glass lab fallback:',error.message);return false;}","}catch(error){rendererReason='WebGL initialization failed: '+error.message;console.warn('Glass lab software renderer:',error.message);return false;}");
s=s.replace('    upload();wake();','    software.setSource(textureCanvas);upload();wake();');
const a=s.indexOf('  function drawFallback(g){'),b=s.indexOf('  function draw(){',a);
s=s.slice(0,a)+`  function drawFallback(g,v){
    fallback.hidden=false;
    software.draw({g,v,viewWidth,model:+$('model').value,coordinates:$('background').value==='coordinates',
      lightInk:$('ink').value==='light',sourceOnly:$('source').checked,held:clamp(-state.z/.3,0,1)});
    $('status').textContent='Software · background refraction';
    $('rendererNote').textContent=rendererReason;
    $('retry').hidden=false;
  }
`+s.slice(b);
s=s.replace('}else drawFallback(g);','}else drawFallback(g,v);');
s=s.replace("canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;draw();});","canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();lost=true;rendererReason='The WebGL context was lost; software rendering is active.';draw();});");
s=s.replace("canvas.addEventListener('webglcontextrestored',()=>{gpu=initGL();upload();wake();});",`canvas.addEventListener('webglcontextrestored',()=>{gpu=initGL();upload();wake();});
  $('retry').onclick=()=>{
    const url=new URL(location.href);url.searchParams.delete('fallback');history.replaceState(null,'',url);
    if(lost){contextControl?.restoreContext();return;}
    gpu=initGL();upload();wake();
  };`);
s=s.replace('gpu:gpu&&!lost,frames,uploads,','gpu:gpu&&!lost,renderer:gpu&&!lost?\'webgl\':\'software\',reason:rendererReason,software:software.info(),frames,uploads,');
s=s.replace("pixels(points){if(!gpu||lost)throw Error('No WebGL');draw();",'pixels(points){draw();if(!gpu||lost)return software.pixels(points,viewWidth);');
fs.writeFileSync(r+'lab.js',s);
s=fs.readFileSync(r+'lab.html','utf8').replace('<script src="lab.js" defer>', '<script src="software.js" defer></script><script src="lab.js" defer>');
s=s.replace('<p id="instructions">','<div class="renderer-help"><span id="rendererNote"></span><button id="retry" hidden>Retry WebGL</button></div>\n<p id="instructions">');
s=s.replace('If WebGL is unavailable, the fallback demonstrates motion only. Use <a href="?fallback=1">motion-only mode</a> if your browser cannot run the shader.','When WebGL is unavailable, <a href="?fallback=1">software rendering</a> applies the same inverse maps at a lower resolution. Both renderers sample the background; their performance depends on the device.');fs.writeFileSync(r+'lab.html',s);
s=fs.readFileSync(r+'lab.css','utf8');s+='\n.renderer-help{display:flex;align-items:center;gap:12px;font-size:11px;color:var(--muted);margin-top:8px}.renderer-help:has(#retry[hidden]){display:none}#retry{flex-shrink:0;min-height:34px;padding:6px 10px;font-size:11px}#retry[hidden]{display:none}\n';fs.writeFileSync(r+'lab.css',s);
s=fs.readFileSync(r+'site.cjs','utf8').replace("['lab.html','lab.js','lab.css','guide.css']","['lab.html','lab.js','software.js','lab.css','guide.css']");fs.writeFileSync(r+'site.cjs',s);
