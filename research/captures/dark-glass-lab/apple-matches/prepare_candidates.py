from pathlib import Path
import cv2,numpy as np
root=Path('/evidence/apple-matches')
for vid,ts in [('219',[178,180,182,184,186,188,190,192,194,196,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,724]),('284',[1090,1090.5,1091,1091.5,1092,1092.5,1093,1093.5,1094])]:
 cap=cv2.VideoCapture(str(root/f'{vid}-hd.mp4'));tiles=[]
 for t in ts:
  cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,im=cap.read()
  if not ok:continue
  cv2.imwrite(str(root/f'{vid}-{t}.png'),im)
  a=cv2.resize(im,(384,216));cv2.putText(a,f'{vid}: {t}s',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,0),3);cv2.putText(a,f'{vid}: {t}s',(8,20),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1);tiles.append(a)
 for offset in range(0,len(tiles),16):
  batch=tiles[offset:offset+16];batch+=[np.zeros((216,384,3),np.uint8)]*((-len(batch))%4)
  cv2.imwrite(str(root/f'{vid}-fine-{offset}.jpg'),np.vstack([np.hstack(batch[i:i+4]) for i in range(0,len(batch),4)]))
