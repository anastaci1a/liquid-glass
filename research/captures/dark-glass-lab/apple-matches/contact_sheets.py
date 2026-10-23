from pathlib import Path
import cv2,numpy as np
root=Path('/evidence/apple-matches')
for vid,ts in [('219',list(range(100,351,10))+list(range(360,461,10))+list(range(640,801,10))),('284',list(range(1080,1126,3)))]:
 cap=cv2.VideoCapture(str(root/f'{vid}-hd.mp4'));print(vid,cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT),cap.get(cv2.CAP_PROP_FPS))
 tiles=[]
 for t in ts:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read()
  if not ok:print('fail',t);continue
  cv2.imwrite(str(root/f'{vid}-{t}.png'),im)
  a=cv2.resize(im,(384,216));cv2.putText(a,f'{vid}: {t}s',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),3);cv2.putText(a,f'{vid}: {t}s',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1);tiles.append(a)
 for offset in range(0,len(tiles),16):
  batch=tiles[offset:offset+16];batch+=[np.zeros((216,384,3),np.uint8)]*((-len(batch))%4)
  sheet=np.vstack([np.hstack(batch[i:i+4]) for i in range(0,len(batch),4)])
  cv2.imwrite(str(root/f'{vid}-sheet-{offset}.jpg'),sheet)
