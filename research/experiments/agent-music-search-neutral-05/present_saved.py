"""Saved native presentation only; no response/compositor or optical evaluation."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;B=P.parent/'agent-music-search-baseline-01';W=P.parents[2]/'.evidence-working/music-search-baseline-01';r=json.loads((P/'result.json').read_text());crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];font=ImageFont.load_default(size=16);small=ImageFont.load_default(size=13);records=[]
def image(v):
 finite=np.isfinite(v).all(2);yy,xx=np.indices(finite.shape);v=np.where(finite[...,None],v,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));return Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)))
for k in ['a','b']:
 arrays=[np.asarray(Image.open(W/k/'target.png').convert('RGB'),np.float32)[560:795,1395:1635]/255,np.load(B/f'{k}-candidate.npz')['complete']];labels=['Apple reference','Unit H1 baseline']
 for trial in r['trials']:arrays.append(np.load(P/f"{trial['name']}-{k}-candidate.npz")['complete']);labels.append(trial['name']+' neutral proposal')
 n=len(arrays);can=Image.new('RGB',(n*480+(n-1)*2,534),'white');d=ImageDraw.Draw(can)
 for i,(lab,v) in enumerate(zip(labels,arrays)):can.paste(image(v).resize((480,470),Image.Resampling.LANCZOS),(i*482,64));d.text((i*482+8,20),lab,font=font,fill='black')
 fn=f'{k}-comparison.png';can.save(P/fn);records.append(dict(file=fn,width_per_side=480,caption_height=64))
 cell=280;hh=64+sum((box[3]-box[1])*2+26 for box in crops.values());can=Image.new('RGB',(n*cell+(n-1)*2,hh),'white');d=ImageDraw.Draw(can)
 for i,lab in enumerate(labels):d.text((i*(cell+2)+5,18),lab,font=small,fill='black')
 top=64
 for name,(a,b,c,e) in crops.items():
  d.text((5,top+3),name+' '+str([a,b,c,e]),font=small,fill='black');top+=26
  for i,v in enumerate(arrays):can.paste(image(v[b-560:e-560,a-1395:c-1395]).resize(((c-a)*2,(e-b)*2),Image.Resampling.NEAREST),(i*(cell+2),top))
  top+=(e-b)*2
 fn=f'{k}-fixed-crops.png';can.save(P/fn);records.append(dict(file=fn,scale=2,frozen_rectangles=crops))
for x in records:x['sha256']=hashlib.sha256((P/x['file']).read_bytes()).hexdigest()
(P/'presentation.json').write_text(json.dumps(dict(records=records,new_candidate_composites=0,new_optical_evaluations=0,source='Retained actual native arrays only; unavailable unscored exterior remains checkerboard'),indent=2)+'\n')
