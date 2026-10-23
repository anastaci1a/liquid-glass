import sys,json
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
from extended_fit import Study
from switch_euclidean_surface import EuclideanSurfaceStudy
from revision_replay import clean_composite
from joint_visible_statistics import CROPS
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());trial=json.loads((out/'native-settlement.json').read_text());font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17);rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);t=EuclideanSurfaceStudy(root/'paired'/name);images=[s.target_crop]
 for obj,q in [(s,old),(t,trial)]:images.append(clean_composite(obj,q['parameters'],obj.render(q['parameters'],np.array(q['material']))))
 rgb=[np.uint8(np.clip(im*255,0,255)) for im in images];H,W=rgb[0].shape[:2];panel=Image.new('RGB',(3*W,H+36),'#15171d');draw=ImageDraw.Draw(panel)
 for i,(im,title) in enumerate(zip(rgb,['Apple','Published revision5','Unaccepted physical surface'])):panel.paste(Image.fromarray(im),(i*W,36));draw.text((i*W+10,8),title,fill='white',font=font)
 panel.save(out/f'native-diagnostic-{name}.png')
 for label,box in CROPS.items():
  if label=='center':continue
  a,b,c,d=[round(v*n) for v,n in zip(box,[W,H,W,H])];tiles=[im[b:d,a:c] for im in rgb];height=max(z.shape[0] for z in tiles);width=tiles[0].shape[1];row=Image.new('RGB',(3*width,height+30),'#15171d');draw=ImageDraw.Draw(row)
  for i,(im,title) in enumerate(zip(tiles,['Apple','Published5','Trial'])):row.paste(Image.fromarray(im),(i*width,30));draw.text((i*width+4,5),name.upper()+' '+label+' '+title,fill='white',font=font)
  rows.append(row)
 del s,t,images,rgb
sheet=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)),'#15171d');top=0
for row in rows:sheet.paste(row,(0,top));top+=row.height
sheet.save(out/'native-diagnostic-crops.png');print('Saved two native diagnostic panels and fixed crop sheet; unaccepted, no new score/pass.',flush=True)
