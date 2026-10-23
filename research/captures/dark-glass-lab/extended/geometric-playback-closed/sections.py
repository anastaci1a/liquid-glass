import json
from pathlib import Path
import numpy as np
D=Path('/evidence/extended/geometric-playback-closed');svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="300" viewBox="0 0 1040 300"><rect width="1040" height="300" fill="white"/>']
svg.append('<text x="20" y="23" font-family="sans-serif" font-size="16">Actual closed surfaces and saved primary rays — equal x/z scale; no image render</text>')
for panel,k in enumerate([0,1/3]):
 data=np.load(D/f'radial-k{k:.6f}.npz');ox=265+panel*510;oy=105;scale=210
 def xy(p):return f'{ox+scale*p[0]:.3f},{oy-scale*p[1]:.3f}'
 def line(points,color,width=1):
  svg.append(f'<polyline points="'+ ' '.join(xy(p) for p in points)+f'" fill="none" stroke="{color}" stroke-width="{width}"/>')
 x=np.linspace(-1,1,1001);u=np.sqrt((1-x*x)/(1+k*x*x));zfront=.15*(u-1);zback=.15*(-u-1)
 line(zip(x,zfront),'#1261a0',2);line(zip(x,zback),'#1261a0',2)
 for r in [0,.4,.7,.9,.97,.99]:
  j=int(np.argmin(abs(data['r']-r)));p=data['entry'][j,[0,2]];q=data['exit'][j,[0,2]]
  for sign in [-1,1] if r else [1]:
   pp=p*np.array([sign,1]);qq=q*np.array([sign,1]);line([pp+[0,.09],pp],'#555');line([pp,qq],'#555')
   if data['complete'][j]:
    e=data['exit_direction'][j,[0,2]]*np.array([sign,1]);line([qq,qq+.40*e],'#c32b2b')
   else:
    px,py=xy(qq).split(',');svg.append(f'<circle cx="{px}" cy="{py}" r="3" fill="#a500a5"/>')
 svg.append(f'<text x="{panel*510+30}" y="62" font-family="sans-serif" font-size="14">κ={k:.6f}; depth η=.15; n=1.5; D=2</text>')
 svg.append(f'<text x="{panel*510+30}" y="255" font-family="sans-serif" font-size="12">Blue: same F=0; gray: entry/internal; red: transmitted segment.</text>')
 svg.append(f'<text x="{panel*510+30}" y="276" font-family="sans-serif" font-size="12">Purple: unavailable transmission; no replacement ray or sampled pixel.</text>')
svg.append('</svg>');(D/'actual-sections-rays.svg').write_text(''.join(svg))
(D/'section-provenance.json').write_text(json.dumps(dict(source='Saved radial-k*.npz entry/exit/direction; F=0 solved analytically for section vertices',new_rays=0,new_images=0,same_x_z_scale=True,exit_segments_length_L=.4,full_background_distance_L=2,limits='Exit segments shortened for readability; no invented reflected branch.'),indent=2)+'\n')
