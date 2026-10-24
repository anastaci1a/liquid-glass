"""Presentation only: saved completed images and actual cached geometry."""
from pathlib import Path
import json, numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
font=ImageFont.load_default(size=16)
def picture(v):
 good=np.isfinite(v).all(-1);y,x=np.indices(good.shape)
 v=np.where(good[...,None],v,np.where(((x//6+y//6)%2)[...,None],.72,.9))
 return Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)))
for phase in ['miniplayer-outline-light-07','miniplayer-curved-front-08','miniplayer-split-surface-09']:
 D=ROOT/'research/experiments'/phase;P=json.loads((D/'protocol.json').read_text())
 for member in ['expanded','compact']:
  work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  base=ROOT/('research/experiments/expanded-contrast-guard-02' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06')
  for k in ['a','b']:
   case=json.loads((work/k/'case.json').read_text());x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0
   T=np.asarray(Image.open(work/k/'target.png').convert('RGB'),np.float32)[y0:y1,x0:x1]/255
   baseline=np.load(base/(f'{k}-candidate.npz' if member=='expanded' else f'compact-{k}-candidate.npz'))['complete']
   for amp in [1,4]:
    prefix=f'{member}-{k}-light{amp}';C=np.load(D/(prefix+'.npz'))['complete'];width=min(1080,W);height=round(H*width/W)
    canvas=Image.new('RGB',(2*width+2,height+64),'white');draw=ImageDraw.Draw(canvas)
    label=('Conditional back return' if phase.endswith('07') else 'Conditional direct-front reflection')+f'; light {amp}'
    for i,(v,title) in enumerate([(T,'Apple reference'),(C,label)]):
     canvas.paste(picture(v).resize((width,height),Image.Resampling.LANCZOS),(i*(width+2),64));draw.text((i*(width+2)+8,20),title,font=font,fill='black')
    canvas.save(D/(prefix+'-comparison.png'))
    rows=[]
    for name,(a,b,c,d) in P['fixed_crops'][member].items():
     w,h=2*(c-a),2*(d-b);row=Image.new('RGB',(3*w+4,h+48),'white');draw=ImageDraw.Draw(row)
     draw.text((2,1),name+' — reference / selected / conditional',font=font,fill='black')
     for i,v in enumerate([T,baseline,C]):
      row.paste(picture(v[b-y0:d-y0,a-x0:c-x0]).resize((w,h),Image.Resampling.NEAREST),(i*(w+2),48))
     rows.append(row)
    sheet=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+8*(len(rows)-1)),'white');top=0
    for row in rows:sheet.paste(row,(0,top));top+=row.height+8
    sheet.save(D/(prefix+'-crops.png'))

for member in ['expanded','compact']:
 q=np.load(ROOT/f'research/experiments/miniplayer-split-surface-09/{member}-paths.npz')
 front=q['front'];back=q['back'];col=front.shape[1]//2
 r=int(np.nanargmin(abs(front[:,col,1])));valid=np.isfinite(front[r,:,0]);ids=np.flatnonzero(valid)
 # At most 1,600 selected surface samples per member and 20 actual paths.
 ids=ids[np.linspace(0,len(ids)-1,min(1600,len(ids))).astype(int)]
 f=front[r,ids];b=back[r,ids];xmin,xmax=float(f[:,0].min()),float(f[:,0].max())
 def point(v):return f'{30+940*(v[0]-xmin)/(xmax-xmin):.3f},{155-650*v[2]:.3f}'
 parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="260" viewBox="0 0 1000 260">','<rect width="1000" height="260" fill="white"/>',f'<text x="20" y="24" font-size="17">{member}: projected actual native front/back paths; vertical display exaggerated</text>','<text x="20" y="48" font-size="14">Same cached surfaces and normals as the rendered refraction; units L. No new height or ray evaluation.</text>']
 for curve,color in [(f,'#1165a5'),(b,'#175e31')]:parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="'+ ' '.join(point(v) for v in curve)+'"/>')
 for i in np.linspace(0,len(f)-1,20).astype(int):parts.append(f'<polyline fill="none" stroke="#b75a18" stroke-width="1" points="{point(f[i]+[0,0,.025])} {point(f[i])} {point(b[i])}"/>')
 parts+=['<text x="20" y="232" font-size="14">Blue: actual raised front. Green: actual back. Orange: cached incoming and internal segments.</text>','</svg>']
 (OUT/f'{member}-actual-section.svg').write_text('\n'.join(parts)+'\n')
(OUT/'presentation.json').write_text(json.dumps({'arrays_changed':False,'new_composites':0,'new_rays':0,'new_heights':0,'format':'Explicit direct-front/back-return labels; fixed crops at2x; actual cached section projections, not decorative geometry.'},indent=2)+'\n')
