from pathlib import Path
import cv2
from PIL import Image,ImageDraw
out=Path('/evidence/extended/active-segmented-selector/crown-review');cap=cv2.VideoCapture('/evidence/extended/sources/details.mp4');sheet=Image.new('RGB',(1440,1800),'#171922');D=ImageDraw.Draw(sheet)
for i,t in enumerate([14.,14.6,14.8,15.,15.3,15.7,16.,16.4,17.]):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read();assert ok
 frame=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB));frame.save(out/f'reference-{t}.png')
 crop=frame.crop((180,370,1740,730));crop.thumbnail((700,330));x=(i%2)*720;y=(i//2)*360
 sheet.paste(crop,(x,y+25));D.text((x+10,y+6),str(t)+'s',fill='white')
sheet.save(out/'sequence.png')
