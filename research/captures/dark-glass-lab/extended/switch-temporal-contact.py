from pathlib import Path
import cv2,json
from PIL import Image,ImageDraw,ImageFont
root=Path('/evidence/extended');out=root/'active-switch/edge-diffusion-analysis';out.mkdir(exist_ok=True);video=cv2.VideoCapture(str(root/'sources/details.mp4'));frames=[];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
for sec in [9.25,9.4,9.55,10.35,10.5,10.65]:
 index=round(sec*60);video.set(cv2.CAP_PROP_POS_FRAMES,index);ok,frame=video.read();assert ok;image=Image.fromarray(frame[:,:,::-1]).crop((450,260,1450,820));frames.append((index,sec,image))
video.release();canvas=Image.new('RGB',(2020,3*604),'#14171e');draw=ImageDraw.Draw(canvas)
for col,group in enumerate([frames[:3],frames[3:]]):
 for row,(index,sec,image) in enumerate(group):
  x=col*1020;y=row*604;draw.text((x+8,y+8),f'Apple Details · {sec:.2f}s · frame {index}',font=font,fill='#f0f2f7');canvas.paste(image,(x,y+44))
canvas.save(out/'temporal-context.png');(out/'temporal-context.json').write_text(json.dumps(dict(frames=[dict(index=i,seconds=s) for i,s,_ in frames],crop=[450,260,1450,820],limits='Exploratory native OpenCV video decode, not a replacement for frozen reference extraction or a temporal fit.'),indent=2)+'\n')
