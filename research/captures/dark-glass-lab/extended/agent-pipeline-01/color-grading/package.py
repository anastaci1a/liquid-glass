from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw
P=Path('/evidence/extended/agent-pipeline-01');O=P/'color-grading';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
regions=json.loads((P/'refraction/h1/protocol.json').read_text())['reference_crops']
def rgba(p):
 ok=np.isfinite(p).all(2);return Image.fromarray(np.dstack([np.uint8(np.rint(np.clip(np.nan_to_num(p),0,1)*255)),ok.astype(np.uint8)*255]),'RGBA')
for key in ['a','b']:
 s=Study(P/f'inputs/{key}');x0,y0,_,_=s.crop;historical=np.load(P/f'historical-{key}-presentation.npy');panels=[s.target_crop,historical,np.load(P/'blurriness'/f'{key}-sigma6p75-complete.npy'),np.load(O/f'{key}-step0.5-complete.npy'),np.load(O/f'{key}-step1-complete.npy')];labels=['Apple','Historical accepted pass03 (saved native PNG; presentation only)','Physical H1 + sigma6.75, unit color','Common neutral halfstep: ALL guards pass vs prior physical stage','Full LS: REJECTED B artwork/artist guard, retained']
 H,W=s.valid.shape;sheet=Image.new('RGBA',(W,(H+42)*len(panels)),(255,255,255,255));draw=ImageDraw.Draw(sheet)
 for i,(p,label) in enumerate(zip(panels,labels)):sheet.paste(rgba(p),(0,i*(H+42)+42));draw.text((8,i*(H+42)+10),label,fill='black')
 sheet.save(O/f'{key}-comparison.png')
 for name,(a,b,c,d) in regions.items():
  w=c-a;h=d-b;fw=max(w,200);sheet=Image.new('RGBA',(fw*len(panels),h+50),(255,255,255,255));draw=ImageDraw.Draw(sheet)
  for i,(p,label) in enumerate(zip(panels,['Apple','Historical saved PNG','Prior physical stage','Halfstep, strict local pass','Full LS rejected'])):sheet.paste(rgba(p[b-y0:d-y0,a-x0:c-x0]),(fw*i,50));draw.text((fw*i+5,10),label,fill='black')
  sheet.save(O/f'{key}-crop-{name}.png')
