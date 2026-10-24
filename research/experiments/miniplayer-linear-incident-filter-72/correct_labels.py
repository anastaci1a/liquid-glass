"""Caption-only correction; preserve every scientific pixel and the as-run sheets."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).parent;ROOT=OUT.parents[2];old=OUT/'as-run-labels';old.mkdir(exist_ok=True);font=ImageFont.load_default(size=16);records=[]
for member in ['expanded','compact']:
 crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops'][member]
 for k in ['a','b']:
  for kind in ['comparison','crops']:
   p=OUT/f'{member}-{k}-{kind}.png';
   if not (old/p.name).exists():shutil.copy2(p,old/p.name)
   im=Image.open(old/p.name).convert('RGB');before=np.array(im);draw=ImageDraw.Draw(im);mask=np.ones(before.shape[:2],bool)
   if kind=='comparison':
    w=(im.width-4)//3;x=2*(w+2);draw.rectangle((x,0,im.width-1,63),fill='white');draw.text((x+8,20),'Linear-light incident blur; same width',font=font,fill='black');mask[:64,x:]=False
   else:
    y=0
    for name,(a,b,c,d) in crops.items():
     w=2*(c-a);x=2*(w+2);caption=Image.new('RGB',(im.width-x,32),'white');ImageDraw.Draw(caption).text((3,6),f'{name}: Linear incident blur',font=font,fill='black');im.paste(caption,(x,y));mask[y:y+32,x:]=False;y+=2*(d-b)+32+8
   after=np.array(im);assert np.array_equal(before[mask],after[mask]);im.save(p);records.append(dict(file=p.name,as_run_sha256=hashlib.sha256((old/p.name).read_bytes()).hexdigest(),corrected_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),all_pixels_outside_changed_captions_exact=True))
(OUT/'caption-correction.json').write_text(json.dumps(dict(reason='Reused panel function retained earlier scattering captions. Scientific arrays, metrics and noncaption image pixels are unchanged; original mislabeled sheets preserved.',records=records),indent=2)+'\n')
