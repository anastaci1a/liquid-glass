import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from switch_spectral_band_model import SpectralBandStudy
root=Path('/evidence/extended/active-switch');out=root/'spectral-band-review';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text());S=[SpectralBandStudy(root/'paired'/n) for n in ['a','b']];co=np.array(old['material']);rows=[]
# Baseline recovery and uniform-field conservation are unit-level sanity checks.
for s in S:
 p=copy.deepcopy(old['parameters']);p['spectral_band_response']=dict(bandwidth_nm=0,dispersion_law=0)
 x=np.linspace(-1,1,100);y=x*.4
 A,J=s.field(x,y,p);B,K=Study.field(s,x,y,old['parameters']);assert np.max(abs(A-B))<1e-6
 source=s.source;s.source=np.ones_like(source)*.4;s.cache.clear()
 U,_=s.field(x,y,p);assert np.max(abs(U-U[0]))<1e-6
 s.source=source;s.cache.clear()
for law,width in [(0,10),(0,25),(0,40),(1,0),(1,15),(1,30)]:
 p=copy.deepcopy(old['parameters']);p['spectral_band_response']=dict(bandwidth_nm=width,dispersion_law=law)
 sc=[s.scores(s.render(p,co),include_ssim=False) for s in S];ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,old['scores'])]
 ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,sc,old['scores']))
 row=dict(parameters=p,scores=sc,ratios=ratios,numeric_pass=ok);rows.append(row);print('TRIAL',law,width,ratios,ok,flush=True)
 (out/'review.json').write_text(json.dumps(dict(trials=rows,accepted=False,checks=['zero bandwidth/linear law recovers legacy field','uniform input remains uniform'],limits='RGB channel-integrated approximation, not a measured spectrum or full Snell lens; ordinary sigma/post_sigma unchanged'),indent=2)+'\n')
