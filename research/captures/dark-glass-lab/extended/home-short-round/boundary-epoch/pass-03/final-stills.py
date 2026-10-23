"""Reuse lossless zero-shift final movie frames; no duplicate HQ rendering."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from publish import pair
from preview_size import dimensions
r=Path('/evidence/extended/home-short-round');out=r/'boundary-epoch/pass-03/hq';out.mkdir(exist_ok=True)
for n in ['a','b']:
 s=Study(r/'input-boundary-replay-proposal'/n);width,height=dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],high_quality=True);frame=np.asarray(Image.open(r/f'boundary-epoch/pass-03/motion/{n}/final/frame-000.png').convert('RGB'));assert frame.shape[1]==width and frame.shape[0] in [height,height+1];frame=frame[:height];target=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(width,height),interpolation=cv2.INTER_LANCZOS4);pair(target,frame,('Apple source','Reconstruction'),font_size=24).save(out/(n+'-comparison.png'))
(out/'reuse.json').write_text(json.dumps(dict(method='Lossless frame000 from the already verified final1080-width export, at exact zero backdrop shift. Remove only replicated codec padding row; pair with unchanged reference crop resampled to same aspect. No duplicate high-resolution optical render.',width=1080),indent=2)+'\n')
