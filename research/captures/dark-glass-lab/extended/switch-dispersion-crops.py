from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'edge-diffusion-analysis';out.mkdir(exist_ok=True);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20);panels=[]
for name in ['a','b']:
 case=json.loads((root/name/'case.json').read_text());image=Image.open(root/name/'target.png');cx,cy=case['center'];hx,hy=case['half'];left=int(cx-hx);right=int(cx-hx/2);top=int(cy-hy);bottom=int(cy+hy)
 # One unaltered native-source excerpt contains the full left-quarter column;
 # adjacent column preserves the transition toward the lens center.
 for label,a,b in [('Left quarter',left,right),('Adjacent quarter',right,int(cx))]:
  crop=image.crop((a,top,b,bottom));scale=3;crop=crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.NEAREST);panels.append((name.upper()+' · '+label,crop,[a,top,b,bottom]))
W=sum(p[1].width for p in panels)+12*(len(panels)-1);H=max(p[1].height for p in panels)+68;canvas=Image.new('RGB',(W,H),'#14171e');draw=ImageDraw.Draw(canvas);x=0;records=[]
for label,image,box in panels:
 draw.text((x+6,8),label,font=font,fill='#f0f2f7');draw.text((x+6,34),'Native pixels ×3',font=font,fill='#a8aebb');canvas.paste(image,(x,68));records.append(dict(label=label,native_box=box));x+=image.width+12
canvas.save(out/'apple-left-quarter-context.png');(out/'crops.json').write_text(json.dumps(dict(crops=records,limits='Native source enlarged nearest-neighbor for pixel inspection; no additional detail. Region boundaries are comparison windows, not a rendering mask.'),indent=2)+'\n')
