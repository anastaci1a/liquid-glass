"""Saved-array residual decomposition; no spectral fitting or new rays."""
import json
import numpy as np
from native import OUT,setup,save
rows=[]
for k in ['a','b']:
 s,c,surf,known,ext,required=setup(k);M=np.load(OUT/f'{k}-raw.npz')['material'].astype(float)
 e=(M-s.target_crop)*255;neutral=e.mean(2);chroma=e-neutral[...,None]
 total=0.;colored=0.;cohorts={}
 for name,mask,weight in [('glass',s.valid,.7),('rim',s.rim,.3)]:
  mse=float(np.mean(e[mask]**2));ce=float(np.mean(chroma[mask]**2));ne=float(np.mean(neutral[mask]**2))
  assert abs(mse-ce-ne)<1e-9
  target_neutral=np.ptp(s.target_crop,axis=2)<=1/255
  cohorts[name]={'total_MSE':mse,'neutral_MSE':ne,'chroma_MSE':ce,'target_neutral_fraction':float(target_neutral[mask].mean())}
  total+=weight*mse;colored+=weight*ce
 rows.append({'reference':k,'cohorts':cohorts,'pure_chroma_ideal_E_reduction_percent':100*(1-np.sqrt((total-colored)/total))})
save('identification.json',{'status':'NO_IDENTIFIED_SPECTRAL_DIRECTION','references':rows,'new_rays':0,'source_queries':0,'fits':0,'meaning':'Arithmetic RGB neutral/chroma decomposition, not perceptual luminance. Ideal ceiling holds only for color-only correction with the neutral residual fixed. Real spectral transport may also change neutral structure.','limits':'Colored backdrop, unresolved geometry, frosting and camera encoding confound spectral interpretation; no claim that dispersion is absent.'})
print(json.dumps(rows),flush=True)
