"""Zero-blur gradient map with a localized, decentered crown.

F=x-grad(Phi). Rim displacement is a positive convex mixture. Added phase is
-A*Gaussian(x-anchor)*W(d), with analytic gradient including the W' coupling.
Anchor alternatives are footprint center or nearest logical caption center.
No caption/source resizing occurs in this test; both are explicit hypotheses.
"""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from scipy.optimize import least_squares
from extended_fit import Study
from source_support import coverage_report,supported
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'localized-phase-probe';out.mkdir(exist_ok=True);old=json.loads((folder/'accepted.json').read_text());rows=[]
class Phase(Study):
 def __init__(self,path,anchor_mode):
  super().__init__(path);self.anchor=np.zeros(2)
  if anchor_mode=='control':
   tr=self.case['background_estimate']['track_pose'];cam=tr[2]/823.5;v=min(self.case['background_estimate']['font_calibration'],key=lambda r:abs((r['selected']['pose'][0]-957.5)*cam+tr[0]-self.case['center'][0]))['selected']['pose'];self.anchor=(np.array([(v[0]-957.5)*cam+tr[0],(v[1]-547.5)*cam+tr[1]])-self.case['center'])/self.L
 def geometry_field(self,x,y,p):
  q={**p,'spline':False,'amplitude':0.,'core_x':0.,'core_y':0.,'tangent':0.,'coupling':0.,'cap_join_width':0.,'cap_normal_gain':0.};X,Y,d,J=super().geometry_field(x,y,q);*_,(sd,nx,ny)=self.shape(x,y,q);a=sum(p[f'm{i}']*np.maximum(1-d/band,0)**3 for i,band in enumerate([.05,.1,.2,.4,.8,1.]));X-=a*nx;Y-=a*ny
  rx=x-self.anchor[0]-p['phase_dx'];ry=y-self.anchor[1]-p['phase_dy'];sx=p['phase_sx'];sy=p['phase_sy'];G=np.exp(-.5*((rx/sx)**2+(ry/sy)**2));u=np.clip(d/p['phase_band'],0,1);W=u**3*(u*(6*u-15)+10);Wd=30*u*u*(u-1)**2/p['phase_band'];K=p['phase_strength']*G
  return X-K*(W*rx/(sx*sx)+Wd*nx),Y-K*(W*ry/(sy*sy)+Wd*ny),d,J
for anchor in ['footprint','control']:
 A=Phase(folder,anchor);B=Phase(folder/'second-observation',anchor);source=np.clip((A.source[:,:,0]-A.source[:,:,1])/.65,0,1);target=np.clip((A.target[:,:,0]-A.target[:,:,1])/.65,0,1);a,b,c,d=A.crop;rng=np.random.default_rng(222);near=cv2.dilate((target>.05).astype(np.uint8),np.ones((21,21),np.uint8));general=np.flatnonzero(A.valid);special=np.flatnonzero(A.valid&(near[b:d,a:c]>0));rng.shuffle(general);rng.shuffle(special);idx=np.unique(np.r_[general[:2500],special[:3500]]);x=A.x.ravel()[idx];y=A.y.ravel()[idx]
 for width in [.8,1.4]:
  p=copy.deepcopy(old['parameters']);p.update(sigma=0.,post_sigma=0.,blur_transition=0.,gamma=1.,shape_dx=0.,shape_dy=0.,half_x_delta=0.,half_y_delta=0.,radius_delta=0.,cap_join_width=0.,phase_strength=.13*width**2,phase_sx=width,phase_sy=width,phase_band=.8,phase_dx=(-1.3 if anchor=='footprint' else 0.),phase_dy=0.);p.update({f'm{i}':(.55 if i==3 else .001) for i in range(6)})
  keys=[*[f'm{i}' for i in range(6)],'phase_strength','phase_sx','phase_sy','phase_band','phase_dx','phase_dy'];bounds=[(0.,2.)]*6+[(-1.,2.),(.3,3.),(.3,3.),(.15,.95),(-2.,2.),(-.5,.5)];lo,hi=np.array(bounds).T
  for level,sigma in enumerate([5.,2.,.5,0.],1):
   S=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;T=cv2.GaussianBlur(target,(0,0),sigma) if sigma else target;expected=T[b:d,a:c].ravel()[idx];calls=0;t=time.time()
   def residual(v):
    global calls
    calls+=1;q={**p,**dict(zip(keys,map(float,v)))};X,Y,*_=A.geometry_field(x,y,q);pred=cv2.remap(S,(X*A.L+A.case['center'][0]).astype(np.float32),(Y*A.L+A.case['center'][1]).astype(np.float32),cv2.INTER_LINEAR).ravel();return (pred-expected).astype(float)
   def jac(v):
    h=.0007;J=np.empty((len(idx),len(v)))
    for i in range(len(v)):
     up=v.copy();dn=v.copy();up[i]=min(hi[i],v[i]+h);dn[i]=max(lo[i],v[i]-h);J[:,i]=(residual(up)-residual(dn))/(up[i]-dn[i])
    return J
   fit=least_squares(residual,np.clip([p[k] for k in keys],lo+1e-8,hi-1e-8),jac=jac,bounds=(lo,hi),x_scale='jac',max_nfev=180,ftol=1e-9,xtol=1e-8,gtol=1e-8);p.update(zip(keys,map(float,fit.x)));_,co=A.fit(p);scores=[s.scores(s.render(p,co)) for s in [A,B]];row=dict(anchor_mode=anchor,width_seed=width,level=level,registration_objective_sigma=sigma,renderer_sigma=0.,renderer_post_sigma=0.,parameters=p.copy(),material=co.tolist(),scores=scores,supported=[supported(s,coverage_report(s,p)) for s in [A,B]],beats_published_A=scores[0]['loss']<=old['scores']['loss'] and scores[0]['glass']['rmse']<=old['scores']['glass']['rmse'],registration_loss=float(np.mean(fit.fun**2)),evaluations=calls,seconds=time.time()-t);rows.append(row);(out/f'{anchor}-{width}-{level}.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(anchor=anchor,width=width,level=level,loss=[q['loss'] for q in scores],glass=[q['glass']['rmse'] for q in scores],beats_published=row['beats_published_A'],calls=calls)),flush=True)
   if level==4:A.comparison(A.render(p,co),out/f'{anchor}-{width}.png',p,context_completed=True)
(out/'report.json').write_text(json.dumps(dict(rows=rows,baseline=old,limits='Analytic effective phase gradient, not a certified convex solid or Apple implementation. Shape and original source files unchanged, no caption scaling, zero renderer blur. Control anchoring is a disclosed interaction-focus hypothesis. No accepted-state mutation.'),indent=2)+'\n')
