"""Private, low-order chromatic reflection basis. No spatially painted colors."""
from pathlib import Path
import json,time
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached,permitted
from material_context import matrix
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-22.json').read_text())['current'];out=root.parent/'chromatic-rim-probe';out.mkdir(exist_ok=True);start=time.time()
N=41
class Cache(Cached):
 def render(self,v):
  co=self.material_transform@v[:23];core=self.J[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:];q=self.J[...,:9]@v[23:].reshape(9,2);colored=np.stack([q[...,0],-q.sum(-1),q[...,1]],-1)
  z=self.C*gain+co[3:6]+(self.J[...,:-1]@co[6:-3])[...,None]+colored
  result=np.clip(z,0,1).reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32);sigma=self.study.kernel_sigma(self.p,'post_sigma')
  return cv2.GaussianBlur(result,(0,0),sigma) if sigma>.001 else result
 def statistics(self,v):
  s=self.study;C,J=self.C,self.J;co=self.material_transform@v[:23];core=J[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:];q=J[...,:9]@v[23:].reshape(9,2);z=C*gain+co[3:6]+(J[...,:-1]@co[6:-3])[...,None]+np.stack([q[...,0],-q.sum(-1),q[...,1]],-1);residual=self.render(v).astype(float)-s.target_crop
  forms={n:[np.zeros((N,N)),np.zeros(N)] for n in ['glass','rim']};average=lambda a:a.reshape(self.H,2,self.W,2,*a.shape[2:]).mean((1,3))
  for channel in range(3):
   active=(z[...,channel]>0)&(z[...,channel]<1);F=np.zeros((self.H,self.W,N));F[...,channel]=average(active*C[...,channel]*(1-core));F[...,channel+3]=average(active);F[...,6:20]=average(active[...,None]*J[...,:-1]);F[...,channel+20]=average(active*C[...,channel]*core);F[...,:23]=F[...,:23]@self.material_transform
   D=average(active[...,None]*J[...,:9])
   if channel==0:F[...,23::2]=D
   elif channel==1:F[...,23::2]=-D;F[...,24::2]=-D
   else:F[...,24::2]=D
   sigma=s.kernel_sigma(self.p,'post_sigma')
   if sigma>.001:F=cv2.GaussianBlur(F,(0,0),sigma)
   for name,mask in [('glass',s.valid),('rim',s.rim)]:
    X=F[mask];e=residual[...,channel][mask];factor=255**2/(3*mask.sum());forms[name][0]+=(X.T@X)*factor;forms[name][1]+=(X.T@e)*factor
  return forms
studies=[Study(root/n) for n in ['a','b']];caches=[Cache(s,old['parameters']) for s in studies];point=np.r_[old['material'],np.zeros(18)];metric=old['scores'];best=None;history=[]
for s,c in zip(studies,caches):assert np.max(abs(s.render(old['parameters'],point[:23])-c.render(point)))<2e-6
# The chromatic lobe extends the same normalized thin/broad reflection basis;
# color contrasts have zero channel mean. Fit never samples target as texture.
for iteration in range(14):
 forms=[c.statistics(point) for c in caches];scale=np.mean([m['loss'] for m in metric]);radius=.8 if iteration==0 else .3
 def val(i,v,kind='loss'):
  d=v-point;gH,gg=forms[i]['glass'];rH,rg=forms[i]['rim'];H,g=(.7*gH+.3*rH,.7*gg+.3*rg) if kind=='loss' else (gH,gg);return (metric[i]['loss'] if kind=='loss' else metric[i]['glass']['rmse']**2)+2*g@d+d@H@d
 def obj(v):return np.mean([val(i,v) for i in range(2)])/scale+1e-6*sum(v[23:]**2)
 def cone(v):
  color=v[23:].reshape(9,2);E=np.stack([color[:,0],-color.sum(-1),color[:,1]],-1);thin=E[:3]+v[6:9,None];return thin[0]-np.hypot(thin[1],thin[2])
 def bound(k):return (.05,1.5) if k<3 or 20<=k<23 else (-.8,.8) if k<6 else (-4,4)
 bounds=[(max(bound(k)[0],point[k]-radius),min(bound(k)[1],point[k]+radius)) for k in range(N)]
 # Enforce nonnegative thin reflection only once the feasible cone is reached.
 # This diagnostic first lets new chromatic freedom settle, then tests removal.
 constraints=[] if iteration<5 else [dict(type='ineq',fun=cone)]
 fit=minimize(obj,point,method='SLSQP',bounds=bounds,constraints=constraints,options=dict(maxiter=100,ftol=1e-10));v=fit.x;actual=[s.scores(c.render(v),include_ssim=False) for s,c in zip(studies,caches)];allowed=permitted(actual,old['scores']);row=dict(iteration=iteration,losses=[m['loss'] for m in actual],glass=[m['glass']['rmse'] for m in actual],cone=cone(v).tolist(),allowed=allowed,solver_success=bool(fit.success));history.append(row);print(json.dumps(row),flush=True)
 if allowed and (best is None or sum(m['loss'] for m in actual)<sum(m['loss'] for m in best['scores'])):best=dict(coefficients=v.tolist(),scores=actual,iteration=iteration)
 point,metric=v,actual;(out/'running.json').write_text(json.dumps(dict(history=history,best=best,seconds=time.time()-start),indent=2)+'\n')
 # Save actual native proof panels at each iteration, including failures.
 for n,s,c in zip(['a','b'],studies,caches):s.comparison(c.render(v),out/f'{n}-{iteration:02}.png',old['parameters'])
report=dict(model='23 original shared material coefficients +18 zero-mean chromatic reflection coefficients on first9 normalized geometric lighting lobes. Thin radiance nonnegative in later trials. Empirical lighting, not a recovered spectral environment.',baseline=old['scores'],baseline_pass=22,history=history,best=best,seconds=time.time()-start,status='Private hypothesis; final full native/source/HQ visual verification required before adoption.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
