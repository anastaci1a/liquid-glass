const fs=require('fs');const root='/mnt/user/live/projects/localica/localica-docs-publish/docs/liquid-glass/';
let h=fs.readFileSync(root+'lab.html','utf8').replace('Background refraction, surface geometry and motion.<br>An experimental renderer, not an exact model of Apple’s material.','Interactive demonstration of background refraction through a movable lens. Controls adjust its shape, optical properties and motion.');fs.writeFileSync(root+'lab.html',h);
let s=fs.readFileSync(root+'lab.js','utf8');
s=s.replace('let lastGeometry, wall = 0;','let lastGeometry, wall = 0, viewWidth = W;\n  const viewLeft = () => (W-viewWidth)/2;\n  const bounds = width => [viewLeft()+32+width/2, W-viewLeft()-32-width/2];');
s=s.replace('uniform vec2 resolution, center, halfSize;','uniform vec2 resolution, center, halfSize;\n  uniform float viewWidth;');
s=s.replace('vec3 original=source(p);','p.x=(p.x-480.)*viewWidth/960.+480.;\n    vec3 original=source(p);');
s=s.replace('preserveDrawingBuffer:false','preserveDrawingBuffer:false,powerPreference:\'low-power\'');
s=s.replace("'backdrop','resolution','center'","'backdrop','resolution','viewWidth','center'");
s=s.replace("if(mode==='grid'||mode==='coordinates'){",`if(mode==='lines'){
      // Original static artwork; generated only when the backdrop is selected.
      const g=bg.createLinearGradient(0,0,W,H*.3);
      [[0,'#172a48'],[.22,'#22676f'],[.45,'#62679e'],[.67,'#ac777d'],[.85,'#bd936b'],[1,'#4d567e']].forEach(([p,c])=>g.addColorStop(p,c));
      bg.fillStyle=g;bg.fillRect(0,0,W,H);
      const shade=bg.createLinearGradient(0,0,0,H);shade.addColorStop(0,'#080e2600');shade.addColorStop(1,'#080e2670');bg.fillStyle=shade;bg.fillRect(0,0,W,H);
      // Fine vertical lines expose horizontal refraction without an animated scene.
      for(let x=12;x<W;x+=18){bg.fillStyle='#f2e5ff38';bg.fillRect(x,0,1.5,H);bg.fillStyle='#08142a28';bg.fillRect(x+2,0,1,H);}
    }else if(mode==='grid'||mode==='coordinates'){
`);
s=s.replace("const cx=wall<0?32+width/2:wall>0?W-32-width/2:clamp(state.x,32+width/2,W-32-width/2);","const [lo,hi]=bounds(width);\n    const cx=wall<0?lo:wall>0?hi:clamp(state.x,lo,hi);");
s=s.replace("fallback.hidden=false;const ctx=fallback.getContext('2d');ctx.drawImage(textureCanvas,0,0,W,H);","fallback.hidden=false;fallback.width=Math.round(viewWidth);fallback.height=H;const ctx=fallback.getContext('2d');ctx.translate(-viewLeft(),0);ctx.drawImage(textureCanvas,0,0,W,H);");
s=s.replace("const scale=Math.min(devicePixelRatio||1,2),width=Math.max(1,Math.round(canvas.clientWidth*scale)),height=Math.round(width*H/W);", "// Bound fragment work independently of high-DPI screens and window size.\n      const scale=Math.min(devicePixelRatio||1,1.5),width=Math.min(960,Math.max(1,Math.round(canvas.clientWidth*scale))),height=Math.round(width*H/viewWidth);");
s=s.replace('gl.uniform1i(uniforms.backdrop,0);','gl.uniform1f(uniforms.viewWidth,viewWidth);gl.uniform1i(uniforms.backdrop,0);');
s=s.replace('`${g.x/W*100}%`','`${(g.x-viewLeft())/viewWidth*100}%`');
s=s.replace('(g.x-g.w/2-32)/(W-64-g.w)','(g.x-viewLeft()-g.w/2-32)/(viewWidth-64-g.w)');
s=s.replace('(e.clientX-r.left)*W/r.width','viewLeft()+(e.clientX-r.left)*viewWidth/r.width');
s=s.replace('lo=32+g.w/2,hi=W-32-g.w/2','[lo,hi]=bounds(g.w)');
s=s.replace('clamp(state.x+state.v/10,32+g.w/2,W-32-g.w/2)','clamp(state.x+state.v/10,...bounds(g.w))');
s=s.replace('Home:32+w/2,End:W-32-w/2','Home:bounds(w)[0],End:bounds(w)[1]');
s=s.replace('clamp(targets[e.key],32+w/2,W-32-w/2)','clamp(targets[e.key],...bounds(w))');
s=s.replace("side==='left'?32+w/2:W-32-w/2","side==='left'?bounds(w)[0]:bounds(w)[1]");
s=s.replace("$('background').value='grid';$('ink').value='dark';", "$('background').value='lines';$('ink').value='light';$('reduce').checked=media.matches;");
s=s.replace('image.width=960;image.height=400','image.width=Math.round(viewWidth);image.height=400');
s=s.replace('0,0,960,400);','0,0,image.width,400);');
s=s.replace("expanded?'One continuing surface':'Drag me',g.x,g.y","expanded?'Expanded panel':'Drag lens',g.x-viewLeft(),g.y");
s=s.replace('new ResizeObserver(wake).observe(canvas);',`function resize(){
    viewWidth=canvas.clientWidth<520?520:W;
    canvas.style.aspectRatio=viewWidth+'/'+H;
    fallback.style.aspectRatio=viewWidth+'/'+H;
    state.target=clamp(state.target,...bounds(geometry().w));wake();
  }
  new ResizeObserver(resize).observe(canvas);resize();`);
s=s.replace('geometry:lastGeometry,state:', 'geometry:lastGeometry,renderSize:[canvas.width,canvas.height],viewWidth,state:');
s=s.replace('Math.floor(x/W*canvas.width)','Math.floor((x-viewLeft())/viewWidth*canvas.width)');
fs.writeFileSync(root+'lab.js',s);
