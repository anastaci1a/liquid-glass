"""Flat front + convex underside: true Snell transmission, no image-space spline.

Orthographic observer in air, front z=0, underside z=-h(x,y), background
z=-(H+gap). Rays enter perpendicular to the front; exit bends at the underside.
Unsupported TIR is rejected, not replaced with a fabricated refracted lookup.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from crowned_footprint import field
from PIL import Image
folder=Path('/evidence/extended/active-segmented-selector');out=folder/'physical-crown-probe';out.mkdir(exist_ok=True)

class Physical(Study):
 def geometry_field(self,x,y,p):
  q={**p,'spline':False,'amplitude':0.,'core_x':0.,'core_y':0.,'tangent':0.,'coupling':0.}
  _,_,d,J=super().geometry_field(x,y,q)
  T,Tx,Ty=field(x,y,self.half,p['crown_softness']);inside=T<=1;S=np.maximum(1-T,0)
  H=p['height'];n=p['ior'];g=p['gap'];c=p['long_crown'];a=self.half[0]
  C=1-c*(x/a)**2;Cx=-2*c*x/(a*a)
  h=H*S*C;hx=H*(-Tx*C+S*Cx);hy=-H*Ty*C
  norm=np.sqrt(1+hx*hx+hy*hy);cos=1/norm;k=1-n*n*(1-cos*cos)
  if np.any((k<=1e-8)&inside):raise ValueError('TIR outside transmitted-only candidate support')
  root=np.sqrt(np.maximum(k,1e-8));f=n*cos-root
  rx=f*hx/norm;ry=f*hy/norm;rz=-n+f/norm
  distance=H+g-h
  X=x+distance*rx/(-rz);Y=y+distance*ry/(-rz)
  return np.where(inside,X,x),np.where(inside,Y,y),d,J

A=Physical(folder);B=Physical(folder/'second-observation');idx=A.indices;rim=A.rim.ravel()[idx];A.weights=np.sqrt(.7+.3*(A.valid.sum()/A.rim.sum())*rim)
p=copy.deepcopy(json.loads((folder/'crown-review/optics-01.json').read_text())['parameters']);p.update(height=.15,ior=1.3,gap=2.,long_crown=.5)
keys=['height','ior','gap','long_crown'];bounds=[(.02,.28),(1.02,1.8),(.02,10.),(0.,.95)]
rows=[]
for seed in [(0.08,1.2,5.,.2),(.15,1.4,2.,.5),(.25,1.6,.5,.8)]:
 q={**p,**dict(zip(keys,seed))};calls=0;best=[float('inf'),None,q];start=time.time()
 def objective(v):
  global calls
  calls+=1;trial={**q,**dict(zip(keys,map(float,v)))}
  try:loss,co=A.fit(trial)
  except ValueError:return 1e3
  if loss<best[0]:best[:]=[loss,co,trial]
  return loss
 minimize(objective,seed,method='Powell',bounds=bounds,options=dict(maxfev=1000,xtol=.00015,ftol=1e-9))
 _,co,q=best
 if co is None:continue
 try:
  pred=[s.render(q,co) for s in [A,B]];scores=[s.scores(im) for s,im in zip([A,B],pred)]
 except ValueError:
  print('Rejected native TIR',seed,flush=True);continue
 row=dict(seed=seed,parameters=q,material=co.tolist(),scores=scores,evaluations=calls,seconds=time.time()-start,accepted=False);rows.append(row)
 (out/f'trial-{len(rows)}.json').write_text(json.dumps(row,indent=2)+'\n')
 for label,s,im in zip(['A','B'],[A,B],pred):
  x0,y0,x1,y1=s.crop;cov=s.shape_coverage(q);base=s.exterior_source[y0:y1,x0:x1];result=im*cov[...,None]+base*(1-cov[...,None]);Image.fromarray(np.uint8(np.rint(np.clip(result,0,1)*255))).save(out/f'trial-{len(rows)}-{label}.png')
 print(json.dumps(dict(seed=seed,loss=[s['loss'] for s in scores],glass=[s['glass']['rmse'] for s in scores],parameters={k:q[k] for k in keys},seconds=time.time()-start)),flush=True)
(out/'review.json').write_text(json.dumps(dict(trials=rows,ordinary_blur=0,dispersion=0,qualified_passes=0,limits='Exact single transmitted Snell branch through explicit height graph, orthographic flat-front camera. TIR rejected, no internal-reflection solution. Lighting remains the historical fitted image-space basis, not physical environment reconstruction. No source or public recipe mutation.'),indent=2)+'\n')
