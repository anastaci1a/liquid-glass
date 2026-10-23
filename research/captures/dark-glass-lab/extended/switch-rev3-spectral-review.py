"""Recheck a bounded chromatic map after material/normal-cap baseline changed.

F_c(p)=p+k_c(F_green(p)-p); k_R=1-s,k_G=1,k_B=1+s.
An empirical weak-dispersion map, NOT a recovered physical surface. Positive s
has the usual stronger blue deviation; negative s is a diagnostic comparator.
Existing directional transmission, ordinary blur, lighting, sources and masks
remain fixed. No target-colored corrections. This entire family is one study.
"""
import sys,json,copy,time,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from switch_native_cache import NativeCachedStudy
from switch_spectral_model import SpectralStudy
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'rev3-spectral-review';out.mkdir(exist_ok=True)
base=json.loads((root/'joint-native-review/candidate.json').read_text());verification=json.loads((root/'joint-native-review/hq/verification.json').read_text())
old=[verification['candidate']['observations'][n] for n in ['A','B']]
class CachedSpectral(NativeCachedStudy):
 def geometry_field(self,x,y,p):
  clean={k:v for k,v in p.items() if k!='spectral_scale'}
  return super().geometry_field(x,y,clean)
 field=SpectralStudy.field
studies=[CachedSpectral(root/'paired'/n,base['parameters']) for n in ['a','b']];co=np.array(base['material']);rows=[]
for spread in [0.,.015,.03,.06,.12,-.015,-.03,-.06]:
 p=copy.deepcopy(base['parameters']);p['spectral_scale']={'spread':spread,'retain_directional':True};scores=[];t=time.time()
 for i,s in enumerate(studies):
  im=s.render(p,co);m=s.scores(im,include_ssim=False);whole=clean_composite(s,p,im);ext=(s.sd>0)&(s.sd<.35)
  m['shadow']={'rmse':float(np.sqrt(np.mean(((whole-s.target_crop)[ext]*255)**2)))};scores.append(m)
  if spread==0:
   assert abs(m['loss']-old[i]['loss'])<1e-8,(m['loss'],old[i]['loss'])
 ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(scores,old)]
 guards=[a['glass']['rmse']<=b['glass']['rmse']+1e-8 and a['shadow']['rmse']<=b['shadow']['rmse']+1e-8 for a,b in zip(scores,old)]
 row=dict(spread=spread,scores=scores,ratios=ratios,guards=guards,numeric_pass=all(r<=.995 and g for r,g in zip(ratios,guards)),seconds=time.time()-t);rows.append(row)
 print('NATIVE',spread,ratios,guards,row['numeric_pass'],row['seconds'],flush=True)
 (out/'screen.json').write_text(json.dumps(dict(protocol=__doc__,baseline=base,baseline_scores=old,trials=rows,accepted=False,limits='Screen only. New chromatic ray domains require separate complete source proof and independent replay before any acceptance.'),indent=2)+'\n')
