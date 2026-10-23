"""Separate a selected-label size state from zero-blur refraction geometry.

A fixed shared semantic scale is an unproven UI-content hypothesis, not lens
magnification. Original RGB files/targets/accepted states stay unchanged.
"""
from pathlib import Path
import sys,json,copy,time,xml.etree.ElementTree as ET
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.optimize import least_squares
from extended_fit import Study
from vector_foreground import coverage
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'selected-state-sharp-probe';out.mkdir(exist_ok=True);old=json.loads((folder/'accepted.json').read_text());allrows=[]
class Selected(Study):
 def __init__(self,path,scale):
  super().__init__(path);track=self.case['background_estimate']['track_pose'];camera=track[2]/823.5;record=min(self.case['background_estimate']['font_calibration'],key=lambda r:abs((r['selected']['pose'][0]-957.5)*camera+track[0]-self.case['center'][0]));layer=copy.deepcopy(record['selected']['layer']);box=np.array(layer['vector_box']);box[[0,2]]=(box[[0,2]]-957.5)*camera+track[0];box[[1,3]]=(box[[1,3]]-547.5)*camera+track[1];center=np.tile((box[:2]+box[2:])/2,2);large=center+(box-center)*1.4;layer['box']=[int(large[0]-3),int(large[1]-3),int(large[2]+4),int(large[3]+4)];layer['vector_box']=box.tolist();normal=coverage(folder,layer);layer['vector_box']=(center+(box-center)*scale).tolist();selected=coverage(folder,layer);a,b,c,d=layer['box'];bg=self.source[500,400].copy();ink=np.array([1.,.35,.4]);self.source[b:d,a:c]+=(selected-normal)[...,None]*(ink-bg);self.source=np.clip(self.source,0,1);self.cache.clear()
for scale in [1.0625,1.125,1.1875]:
 A=Selected(folder,scale);B=Selected(folder/'second-observation',scale);source=np.clip((A.source[:,:,0]-A.source[:,:,1])/.65,0,1);target=np.clip((A.target[:,:,0]-A.target[:,:,1])/.65,0,1);a,b,c,d=A.crop;rng=np.random.default_rng(222);near=cv2.dilate((target>.05).astype(np.uint8),np.ones((21,21),np.uint8));general=np.flatnonzero(A.valid);special=np.flatnonzero(A.valid&(near[b:d,a:c]>0));rng.shuffle(general);rng.shuffle(special);idx=np.unique(np.r_[general[:2500],special[:3500]]);x=A.x.ravel()[idx];y=A.y.ravel()[idx]
 for seed in ['retained','flat-core']:
  p=copy.deepcopy(json.loads((folder/'clear-local-probe/measured-outline-1.json').read_text())['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.)
  if seed=='flat-core':p.update(c5=.02,c6=0.,core_x=0.,core_y=0.)
  keys=[*[f'c{i}' for i in range(7)],'core_x','core_y','cap_normal_gain','cap_tangent_fade','tangent','tangent_band','coupling','cap_join_width'];lo,hi=np.array([A.parameter_bounds(k) for k in keys]).T
  for level,sigma in enumerate([4.,1.,0.],1):
   S=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;T=cv2.GaussianBlur(target,(0,0),sigma) if sigma else target;expected=T[b:d,a:c].ravel()[idx];calls=0;t=time.time()
   def residual(v):
    global calls
    calls+=1;q={**p,**dict(zip(keys,map(float,v)))};X,Y,*_=A.geometry_field(x,y,q);pred=cv2.remap(S,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel();return (pred-expected).astype(float)
   def jac(v):
    h=.0007;J=np.empty((len(idx),len(v)))
    for i in range(len(v)):
     up=v.copy();dn=v.copy();up[i]=min(hi[i],v[i]+h);dn[i]=max(lo[i],v[i]-h);J[:,i]=(residual(up)-residual(dn))/(up[i]-dn[i])
    return J
   fit=least_squares(residual,np.clip([p[k] for k in keys],lo+1e-8,hi-1e-8),jac=jac,bounds=(lo,hi),x_scale='jac',max_nfev=120,ftol=1e-9,xtol=1e-8,gtol=1e-8);p.update(zip(keys,map(float,fit.x)));_,co=A.fit(p);scores=[s.scores(s.render(p,co)) for s in [A,B]];row=dict(content_scale=scale,seed=seed,level=level,registration_objective_sigma=sigma,renderer_sigma=0.,renderer_post_sigma=0.,parameters=p.copy(),material=co.tolist(),scores=scores,supported=[supported(s,coverage_report(s,p)) for s in [A,B]],beats_published_A=scores[0]['loss']<=old['scores']['loss'] and scores[0]['glass']['rmse']<=old['scores']['glass']['rmse'],evaluations=calls,seconds=time.time()-t);allrows.append(row);(out/f'{scale}-{seed}-{level}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(scale=scale,seed=seed,level=level,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],beats_published=row['beats_published_A'],calls=calls)),flush=True)
   if level==3:A.comparison(A.render(p,co),out/f'{scale}-{seed}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(rows=allrows,baseline=old,limits='Fixed shared selected-label size is an unproven semantic content-state hypothesis; no proprietary-pipeline claim. Rendering blurZERO; registration pyramids affect loss only. Source/target PNGs unchanged; native score nonregression still required. No accepted mutation.'),indent=2)+'\n')
