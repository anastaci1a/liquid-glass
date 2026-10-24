"""Presentation-only relabeling. Preserve every existing comparison/crop pixel."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
out=Path(__file__).resolve().parent
p=json.loads((out/'protocol.json').read_text())
font=ImageFont.load_default(size=15)
for member in ['expanded','compact']:
 for key in ['a','b']:
  for amp in [1,4]:
   prefix=f'{member}-{key}-light{amp}'
   path=out/f'{prefix}-comparison.png'; im=Image.open(path).convert('RGB');w=(im.width-2)//2
   ImageDraw.Draw(im).rectangle((0,0,im.width,63),fill='white');d=ImageDraw.Draw(im)
   d.text((8,20),'Apple reference',fill='black',font=font)
   d.text((w+10,20),f'Inverse back; direct-front reflection; conditional light {amp}',fill='black',font=font)
   im.save(path)
   path=out/f'{prefix}-crops.png';old=Image.open(path).convert('RGB');rows=[];y=0
   for name,(a,b,c,e) in p['fixed_crops'][member].items():
    cw,ch=2*(c-a),2*(e-b);row=Image.new('RGB',(3*cw+4,ch+52),'white');draw=ImageDraw.Draw(row)
    draw.text((3,1),name.replace('_',' '),fill='black',font=font)
    for i,label in enumerate(['Reference','Selected','Conditional']):
     row.paste(old.crop((i*(cw+2),y+32,i*(cw+2)+cw,y+32+ch)),(i*(cw+2),52))
     draw.text((i*(cw+2)+3,26),label,fill='black',font=font)
    rows.append(row);y+=ch+40
   sheet=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+8*(len(rows)-1)),'white');y=0
   for row in rows:sheet.paste(row,(0,y));y+=row.height+8
   sheet.save(path)
(out/'presentation.json').write_text(json.dumps({'status':'HEADERS_ONLY','scientific_pixels_unchanged':True,'crop_scale':2,'note':'Correct the inherited first-return label to direct-front reflection; one crop name per row avoids narrow-column overlap.'},indent=2)+'\n')
