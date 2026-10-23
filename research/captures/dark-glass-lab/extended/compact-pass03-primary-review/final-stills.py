import sys
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from publish import pair
root=Path('/evidence/extended/helper-toolbar-work/compact-mini-round')
for n in ['a','b']:
 s=Study(root/n)
 frame=np.array(Image.open(root/f'compact-final-1080/{n}/final/frame-000.png').convert('RGB'))
 assert frame.shape==(282,1080,3)
 target=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(1080,282),interpolation=cv2.INTER_LANCZOS4)
 pair(target,frame,('Apple source','Reconstruction'),font_size=24).save(Path('/evidence/extended/compact-pass03-primary-review/public')/(n+'-comparison.png'))
