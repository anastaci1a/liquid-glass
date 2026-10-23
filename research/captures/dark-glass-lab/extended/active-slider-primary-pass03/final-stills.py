import os,sys,json,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from extended_fit import Study
from publish import pair
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');D=ROOT/'active-slider-final-1080';OUT=Path('/evidence/extended/active-slider-primary-pass03');summary=json.loads((D/'export-summary.json').read_text());os.umask(0o002)
for row in summary['exports']:
 n=row['reference'];s=Study(ROOT/n);folder=D/n/'final';frame=np.array(Image.open(folder/'frame-000.png').convert('RGB'));h=round((s.crop[3]-s.crop[1])*1080/(s.crop[2]-s.crop[0]));assert frame.shape[1]==1080 and frame.shape[0] in [h,h+1];frame=frame[:h]
 target=cv2.resize(np.rint(s.target_crop*255).astype(np.uint8),(1080,h),interpolation=cv2.INTER_LANCZOS4);pair(target,frame,('Apple source','Reconstruction')).save(OUT/f'{n}-final-comparison.png')
 for key,file in [('mp4','motion.mp4'),('gif','motion-6s.gif')]:
  b=(folder/file).read_bytes();assert hashlib.sha256(b).hexdigest()==row[key]['sha256'];assert key!='gif' or len(b)<10_000_000
print('Green final stills and preferred media hashes verified',flush=True)
