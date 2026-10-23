"""Saved-array structural diagnostic, common FIXED analysis bandwidth only.
No rendering/filter change; all original public scores remain untouched.
"""
from pathlib import Path
import json,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h2';regions=json.loads((O/'protocol.json').read_text())['reference_crops'];out={'new_rays':0,'new_native_images':0,'analysis_operator':'Common 49x49 sigma6 Gaussian derivative, applied identically to saved arrays/reference ONLY for structural measurement; not an optical operator or scored output. Whole footprint must be in original glass and finite; no glyph/rim/exterior contamination.','cases':{}}
for key in ['a','b']:
 case=json.loads((P/f'inputs/{key}/case.json').read_text());x0,y0,x1,y1=case['crop'];target=cv2.imread(str(P/f'inputs/{key}/target.png'))[:,:,::-1].astype(float)/255;T=target[y0:y1,x0:x1].mean(2);valid=np.load(P/f'historical-{key}-masks.npz')['glass'];safe=cv2.erode(valid.astype(np.uint8),np.ones((51,51),np.uint8))>0
 arrays={'Apple':T,'H1':np.load(P/'refraction/h1'/f'{key}-material.npy').mean(2),'H2':np.load(O/f'{key}-material.npy').mean(2),'historical':np.load(P/f'historical-{key}-material.npy').mean(2)};grad={}
 for name,C in arrays.items():
  f=cv2.GaussianBlur(np.nan_to_num(C),(49,49),6.);gy,gx=np.gradient(f);grad[name]=np.stack([gx,gy],-1)
 data={}
 for name,(a,b,c,d) in regions.items():
  m=np.zeros(valid.shape,bool);m[max(0,b-y0):min(y1-y0,d-y0),max(0,a-x0):min(x1-x0,c-x0)]=True;m&=safe
  if not m.any():continue
  ref=grad['Apple'][m];n=float((ref*ref).sum());data[name]={'frozen_safe_pixels':int(m.sum())}
  for candidate in ['H1','H2','historical']:
   g=grad[candidate][m];den=np.sqrt(n*(g*g).sum());data[name][candidate]={'signed_gradient_correlation':float((ref*g).sum()/den) if den>0 else None,'gradient_energy_ratio':float((g*g).sum()/n) if n>0 else None}
 out['cases'][key]=data
(O/'saved-structural-review.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
