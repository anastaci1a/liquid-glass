"""Presentation-only fixed crops from the already saved comparison PNGs."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,datetime
P=Path(__file__).resolve().parent
protocol=json.loads((P/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['deadline'].replace('Z','+00:00'))
crops=json.loads((P.parent/'agent-music-search-baseline-01/RGB-started.json').read_text())['fixed_original_frame_crops'];font=ImageFont.load_default(size=16)
for ref in ('a','b'):
 for amplitude in (4,):
  source=Image.open(P/f'{ref}-comparison.png');rows=[]
  for name,(a,b,c,d) in crops.items():
   w,h=2*(c-a),2*(d-b);row=Image.new('RGB',(3*w+4,h+32),'white');draw=ImageDraw.Draw(row)
   for i,label in enumerate(('Apple','Accepted baseline','Shared family transfer')):
    left=i*482+2*(a-1395);top=64+2*(b-560)
    row.paste(source.crop((left,top,left+w,top+h)),(i*(w+2),32));draw.text((i*(w+2)+3,6),name+': '+label,font=font,fill='black')
   rows.append(row)
  sheet=Image.new('RGB',(max(x.width for x in rows),sum(x.height for x in rows)+8*(len(rows)-1)),'white');y=0
  for row in rows:sheet.paste(row,(0,y));y+=row.height+8
  sheet.save(P/f'{ref}-crops.png')
(P/'presentation.json').write_text(json.dumps({'scope':'Four fixed sheets cropped from existing comparison PNGs; no Study, source RGB lookup, optical render, new candidate or metric.','rectangles':crops,'scale':2,'caption_pixels':32,'files':[f'{k}-crops.png' for k in ('a','b')]},indent=2)+'\n')
