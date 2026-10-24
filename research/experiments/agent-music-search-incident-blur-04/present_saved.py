"""Presentation only from already completed arrays; no study or renderer imports."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;B=P.parent/'agent-music-search-baseline-01';W=P.parents[2]/'.evidence-working/music-search-baseline-01';font=ImageFont.load_default(size=17);small=ImageFont.load_default(size=14);crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];records=[]
def img(v):
 finite=np.isfinite(v).all(2);yy,xx=np.indices(finite.shape);view=np.where(finite[...,None],v,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));return Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255)))
for k in ['a','b']:
 target=np.asarray(Image.open(W/k/'target.png').convert('RGB'),np.float32)[560:795,1395:1635]/255
 arrays=[target,np.load(B/f'{k}-candidate.npz')['complete'],np.load(P/f'narrow-{k}-candidate.npz')['complete'],np.load(P/f'wide-{k}-candidate.npz')['complete']];labels=['Apple reference','Seed 6.75 px','Narrow 5.0625 px','Wide 8.4375 px']
 width=480;hh=470;can=Image.new('RGB',(4*width+6,hh+64),'white');d=ImageDraw.Draw(can)
 for i,(label,v) in enumerate(zip(labels,arrays)):can.paste(img(v).resize((width,hh),Image.Resampling.LANCZOS),(i*(width+2),64));d.text((i*(width+2)+8,20),label,font=font,fill='black')
 name=f'{k}-comparison.png';can.save(P/name);records.append(dict(file=name,width_per_side=480,source_crop_width=240,caption_height=64,source='Saved native arrays only'))
 cell=280;total_h=64+sum((r[3]-r[1])*2+26 for r in crops.values());can=Image.new('RGB',(4*cell+6,total_h),'white');d=ImageDraw.Draw(can)
 for i,label in enumerate(labels):d.text((i*(cell+2)+5,18),label,font=small,fill='black')
 top=64
 for name,(a,b,c,e) in crops.items():
  d.text((5,top+3),name+' '+str([a,b,c,e]),font=small,fill='black');top+=26
  for i,v in enumerate(arrays):can.paste(img(v[b-560:e-560,a-1395:c-1395]).resize(((c-a)*2,(e-b)*2),Image.Resampling.NEAREST),(i*(cell+2),top))
  top+=(e-b)*2
 name=f'{k}-fixed-crops.png';can.save(P/name);records.append(dict(file=name,scale=2,unchanged_rectangles=crops,source='Saved native arrays only; nearest-neighbor diagnostic enlargement'))
for r in records:r['sha256']=hashlib.sha256((P/r['file']).read_bytes()).hexdigest()
(P/'presentation.json').write_text(json.dumps(dict(records=records,new_optical_evaluations=0,new_candidate_composites=0,unavailable_presentation='Checkerboard only outside required support; never copied target'),indent=2)+'\n')
