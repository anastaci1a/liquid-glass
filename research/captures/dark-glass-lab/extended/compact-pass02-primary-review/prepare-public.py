import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from vector_revision import composite
from motion_support import complete
from source_support import masks
from publish import pair
from preview_size import dimensions
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/compact-mini-round');out=Path('/evidence/extended/compact-pass02-primary-review/public');out.mkdir(exist_ok=True);r=json.loads((root/'thin-material-pass1/candidate-native.json').read_text());r.update(large=True,case_sha256={},vector_sha256={},parameter_units='Native sigma/post_sigma in reference pixels; geometry and map normalized by L, the source short half-size. Preserve each case parameter_length_reference.',limits='Two observations from one Apple recording; source/artwork/icon assignments have their existing uncertainties. No proprietary Apple formula or parity claim.')
for i,n in enumerate(['a','b']):
 s=Study(root/n);r['case_sha256'][n]=hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest();r['vector_sha256'][n]={l['vector_asset']:hashlib.sha256((s.folder/l['vector_asset']).read_bytes()).hexdigest() for l in s.case['foreground_layers'] if 'vector_asset' in l}
 M=np.load(root/f'thin-material-pass1/trial2-ref{i}-material.npy');known,_=masks(s);rgb=composite(s,r['parameters'],M,1,complete(s,known));reference=np.load(root/f'thin-material-pass1/ref{i}-complete.npy');A=s.shape_coverage(r['parameters']);assert np.max(abs(rgb[A==1]-reference[A==1]))<2e-6
 W,H=dimensions(s.crop[2]-s.crop[0],s.crop[3]-s.crop[1],large=True);rgb=cv2.resize(np.uint8(np.rint(np.clip(rgb,0,1)*255)),(W,H),interpolation=cv2.INTER_LANCZOS4);target=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(W,H),interpolation=cv2.INTER_LANCZOS4);pair(target,rgb,('Apple source','Reconstruction'),font_size=24).save(out/(n+'-comparison.png'))
(out/'pass-01.json').write_text(json.dumps(r,indent=2)+'\n')
