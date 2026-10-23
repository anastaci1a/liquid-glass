import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from revision_replay import clean_composite
from publish import pair
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'joint-native-review';r=json.loads((out/'interim-visual.json').read_text())
for n in ['a','b']:
 s=Study(root/'paired'/n);p=r['parameters'];pred=s.render(p,np.array(r['material']));C=clean_composite(s,p,pred);a=Image.fromarray(np.uint8(np.rint(s.target_crop*255)));b=Image.fromarray(np.uint8(np.rint(np.clip(C,0,1)*255)));pair(np.asarray(a),np.asarray(b),['Apple','Interim native candidate']).save(out/f'interim-{n}.png')
