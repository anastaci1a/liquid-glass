from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
P=Path('/evidence/extended/agent-pipeline-01');O=P/'icon-shape-material'
for key in ['a','b']:
 case=json.loads((P/f'inputs/{key}/case.json').read_text());x0,y0,_,_=case['crop'];a,b,c,d=next(l['box'] for l in case['foreground_layers'] if l.get('vector_asset')=='artist.svg');T=np.asarray(Image.open(P/f'inputs/{key}/target.png')).astype(float)/255;old=np.load(P/'color-grading'/f'{key}-step0.5-complete.npy');new=np.load(O/f'{key}-black-opacity-complete.npy');panels=[T[b:d,a:c],old[b-y0:d-y0,a-x0:c-x0],new[b-y0:d-y0,a-x0:c-x0]];w=(c-a)*2;h=(d-b)*2;sheet=Image.new('RGB',(w*3,h+52),'white');draw=ImageDraw.Draw(sheet)
 for i,(im,label) in enumerate(zip(panels,['Apple','Original style retained','REJECTED shared black opacity'])):
  pic=Image.fromarray(np.uint8(np.rint(np.clip(im,0,1)*255))).resize((w,h),Image.Resampling.NEAREST);sheet.paste(pic,(i*w,52));draw.text((i*w+5,10),label,fill='black')
 sheet.save(O/f'{key}-artist-crop.png')
