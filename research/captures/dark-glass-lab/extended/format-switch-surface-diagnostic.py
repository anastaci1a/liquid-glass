"""Reformat saved diagnostic pixels; no rendering, scoring or image resampling."""
import sys
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from PIL import Image,ImageDraw,ImageFont
from joint_visible_statistics import CROPS
root=Path('/evidence/extended/active-switch/physical-euclidean-surface')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
rows=[];column=260;gap=16
for name in ['a','b']:
 panel=Image.open(root/f'native-diagnostic-{name}.png').convert('RGB');W=panel.width//3;H=panel.height-36
 for label,box in CROPS.items():
  if label=='center':continue
  x0,y0,x1,y1=[round(v*n) for v,n in zip(box,[W,H,W,H])]
  assert x1-x0<=column
  row=Image.new('RGB',(3*column+4*gap,y1-y0+68),'#15171d');draw=ImageDraw.Draw(row)
  draw.text((gap,5),name.upper()+' · '+label,fill='#aeb7c4',font=font)
  for i,title in enumerate(['Apple','Published revision 5','Unaccepted surface']):
   tile=panel.crop((i*W+x0,y0+36,i*W+x1,y1+36));left=gap+i*(column+gap)
   draw.text((left,30),title,fill='white',font=font);row.paste(tile,(left+(column-tile.width)//2,58))
  rows.append(row)
sheet=Image.new('RGB',(rows[0].width,sum(r.height for r in rows)),'#15171d');top=0
for row in rows:sheet.paste(row,(0,top));top+=row.height
sheet.save(root/'native-diagnostic-crops-readable.png')
print('Reused all original diagnostic pixels; readable fixed-width labels.',flush=True)
