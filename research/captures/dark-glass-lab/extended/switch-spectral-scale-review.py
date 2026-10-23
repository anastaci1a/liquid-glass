"""Bounded wavelength-dependent ray-displacement proposal; no painted rims.

X_c = x + k_c (X_g-x), Y_c = y + k_c (Y_g-y),
k_R=1-s, k_G=1, k_B=1+s. A weak-dispersion approximation,
not a physical recovered surface. Test both replacing and supplementing the
existing directional chromatic term, with every other parameter frozen.
"""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from chromatic_transmission import apply as directional
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'spectral-scale-review';out.mkdir(exist_ok=True)
old=json.loads((root/'rim-width-review/minimax.json').read_text())
class SpectralStudy(Study):
    def field(self,x,y,p):
        X,Y,d,light=self.geometry_field(x,y,p)
        sample=self.sample_field(X,Y,d,p)
        q=p.get('spectral_scale',{})
        for c,sign in [(0,-1),(2,1)]:
            k=1+sign*q.get('spread',0.)
            sample[...,c]=self.sample_field(x+k*(X-x),y+k*(Y-y),d,p)[...,c]
        if q.get('retain_directional',True):sample=directional(self,p,x,y,sample)
        return sample,light
S=[SpectralStudy(root/'paired'/n) for n in ['a','b']];co=np.asarray(old['material']);rows=[]
for keep in [True,False]:
    for spread in [0.,.015,.03,.06,.12,-.03]:
        p=copy.deepcopy(old['parameters']);p['spectral_scale']=dict(spread=spread,retain_directional=keep)
        sc=[]
        for s in S:
            im=s.render(p,co);m=s.scores(im,include_ssim=False);whole=clean_composite(s,p,im)
            ext=(s.sd>0)&(s.sd<.35);m['shadow']=dict(rmse=float(np.sqrt(np.mean(((whole-s.target_crop)[ext]*255)**2))))
            sc.append(m)
        ratios=[np.sqrt(a['loss']/b['loss']) for a,b in zip(sc,old['scores'])]
        ok=all(r<=.995 and a['glass']['rmse']<=b['glass']['rmse'] for r,a,b in zip(ratios,sc,old['scores']))
        row=dict(parameters=p,material=co.tolist(),scores=sc,ratios=ratios,numeric_pass=ok);rows.append(row)
        print('NATIVE',keep,spread,ratios,ok,flush=True)
        (out/'review.json').write_text(json.dumps(dict(trials=rows,accepted=False,formula=__doc__,limits='Shared empirical spectral displacement; no physical solid identified; unchanged sources, shapes, masks, lighting, blur and shadow. Exterior and independent replay still required for any candidate.'),indent=2)+'\n')
