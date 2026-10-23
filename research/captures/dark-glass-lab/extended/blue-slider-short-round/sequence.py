from pathlib import Path
import cv2,json,os
from PIL import Image,ImageDraw
os.umask(0o002);cv2.setNumThreads(1)
root=Path('/evidence/extended/blue-slider-short-round/sequence');cap=cv2.VideoCapture('/evidence/apple-matches/284-hd.mp4');assert cap.isOpened()
sheet=Image.new('RGB',(1500,1040),'#171920');draw=ImageDraw.Draw(sheet);rows=[]
for i in range(24):
 t=1090.5+i*.15;cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok
 pts=cap.get(cv2.CAP_PROP_POS_MSEC)/1000;index=int(cap.get(cv2.CAP_PROP_POS_FRAMES))-1
 frame=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB));frame.save(root/f'frame-{i:02}.png')
 crop=frame.crop((450,450,1450,650));crop.thumbnail((500,100));x=(i%3)*500;y=(i//3)*130;sheet.paste(crop,(x,y+25));draw.text((x+8,y+5),f'{t:.2f}s PTS {pts:.6f}',fill='white');rows.append(dict(requested=t,pts=pts,frame=index,file=f'frame-{i:02}.png'))
sheet.save(root/'contact.png');(root/'frames.json').write_text(json.dumps(dict(video='Existing Apple UIKit WWDC2025/284 HD capture',rows=rows,limits='Observation-only matching-state/source feasibility, no optical fits or source adoption.'),indent=2)+'\n');print('Saved24sampled observations',flush=True)
