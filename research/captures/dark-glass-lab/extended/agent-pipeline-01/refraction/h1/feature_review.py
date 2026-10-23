"""Fixed saved-array B text profiles; no fit, registration or new image."""
from pathlib import Path
import json,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h1';c=json.loads((P/'inputs/b/case.json').read_text());x0,y0,x1,y1=c['crop'];a,b,d,e=[875,326,1258,505]
target=cv2.imread(str(P/'inputs/b/target.png'))[:,:,::-1].astype(np.float32)/255
# No source lookup: native integer crop is the fixed original source control itself.
source=cv2.imread(str(P/'inputs/b/source.png'))[:,:,::-1].astype(np.float32)/255
arrays={'Apple':target[y0:y1,x0:x1], 'fixed_unrefracted_source':source[y0:y1,x0:x1], 'historical_material':np.load(P/'historical-b-material.npy'),'H1_raw_material':np.load(O/'b-material.npy')}
profiles={};ys=np.arange(b,e)
for name,im in arrays.items():
 crop=im[b-y0:e-y0,a-x0:d-x0];luma=crop@np.array([.2126,.7152,.0722]);energy=abs(np.gradient(luma,axis=0)).mean(1);total=energy.sum();cdf=np.cumsum(energy)/total
 profiles[name]={'vertical_gradient_energy':energy.tolist(),'normalized_energy_centroid_y':float(ys@energy/total),'energy_y_quantiles':[int(ys[np.searchsorted(cdf,p)]) for p in [.1,.25,.5,.75,.9]]}
result={'fixed_original_crop':[a,b,d,e],'no_new_rays_or_images':True,'profiles':profiles,'limits':'Contrast-normalized profile is descriptive. Apple frost changes bandwidth and overlapping lines; centroid differences alone do not identify refraction or register targets. Historical model includes blur/grade; no new filtering applied.'}
(O/'feature-review.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:{x:y for x,y in v.items() if x!='vertical_gradient_energy'} for k,v in profiles.items()}))
