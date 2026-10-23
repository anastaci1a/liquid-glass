"""Sampled quadrature proposals; every retained result uses full native gates."""
from pathlib import Path
exec(Path('/evidence/extended/switch-spectral-reflection-probe.py').read_text().split('root=Path(')[0])
from paired_fit import permitted
from material_context import matrix
from grazing_reflection import layers
root=Path('/evidence/extended/active-switch/paired');old=json.loads((root/'pass-23.json').read_text())['current'];out=root.parent/'spectral-proposal';out.mkdir(exist_ok=True);start=time.time();studies=[SpectralStudy(root/n) for n in ['a','b']];co=np.array(old['material'])
class Proposal:
 def __init__(self,s):
  self.s=s;p=old['parameters'];x=s.x.ravel()[s.indices];y=s.y.ravel()[s.indices];h=np.sqrt(2)*s.kernel_sigma(p,'post_sigma')/s.L;dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);self.x=x[:,None]+dx.ravel();self.y=y[:,None]+dy.ravel();self.X,self.Y,d,J=s.geometry_field(self.x,self.y,p);*_,R,(sd,self.nx,self.ny)=s.shape(self.x,self.y,p);self.B=BSpline.design_matrix(np.clip(d/R,0,1).ravel(),KNOTS,3).toarray()[:,:7].reshape((*self.x.shape,7));c=matrix(s,p)@co;core=J[...,-1];self.gain=(1-core[...,None])*c[:3]+core[...,None]*c[-3:];self.light=c[3:6]+(J[...,:-1]@c[6:-3])[...,None];weight,E=layers(s,p);self.F=weight.ravel()[s.indices,None];self.E=E.reshape(-1,3)[s.indices];self.rim=s.rim.ravel()[s.indices]
 def render(self,v,sigma):
  s=self.s;p={**old['parameters'],'sigma':sigma};a=self.B@v[:7];dx=a*self.nx+v[7]*self.x;dy=a*self.ny+v[8]*self.y;texture=s.blur(s.kernel_sigma(p));channels=[]
  for channel,sign in enumerate([1,0,-1]):
   X=((self.X+sign*dx)*s.L+s.case['center'][0]).astype(np.float32);Y=((self.Y+sign*dy)*s.L+s.case['center'][1]).astype(np.float32);channels.append(cv2.remap(texture[:,:,channel],X,Y,cv2.INTER_LINEAR))
  C=np.maximum(np.stack(channels,-1),0)**p['gamma'];T=np.clip(C*self.gain+self.light,0,1).mean(1);return T*(1-self.F)+self.E*self.F
 def loss(self,v,sigma):
  error=(self.render(v,sigma)-self.s.expected)*255;return .7*np.mean(error**2)+.3*np.mean(error[self.rim]**2)
proposals=[Proposal(s) for s in studies];baseline=[p.loss(np.zeros(9),old['parameters']['sigma']) for p in proposals];prior=json.loads((root.parent/'spectral-reflection-probe/running.json').read_text())['best']['parameters'];seed=np.array(prior);trials=[];best=None;calls=0;scale=np.mean(baseline)
for sigma in [0.,1.,2.,3.,old['parameters']['sigma']]:
 memo={}
 def evaluate(v):
  global calls
  key=np.asarray(v).tobytes()
  if key not in memo:memo.clear();memo[key]=[p.loss(v,sigma) for p in proposals];calls+=1
  return np.array(memo[key])
 fit=minimize(lambda v:evaluate(v).mean()/scale,seed,method='SLSQP',bounds=[(-.5,.5)]*7+[(-.1,.1)]*2,constraints=[dict(type='ineq',fun=lambda v:(np.array(baseline)-evaluate(v))/scale)],options=dict(maxiter=40,ftol=1e-9,eps=.001));checks=[]
 for t in [1.,.5,.25,.125]:
  p={**old['parameters'],'sigma':old['parameters']['sigma']+t*(sigma-old['parameters']['sigma']),'spectral_profile':(fit.x*t).tolist()};metrics=[s.scores(s.render(p,co),include_ssim=False) for s in studies];allowed=permitted(metrics,old['scores']);checks.append(dict(t=t,losses=[m['loss'] for m in metrics],allowed=allowed))
  if allowed and (best is None or sum(m['loss'] for m in metrics)<sum(m['loss'] for m in best['scores'])):
   best=dict(parameters=p,scores=metrics)
   for n,s in zip(['a','b'],studies):s.comparison(s.render(p,co),out/f'{n}.png',p)
 trials.append(dict(sigma=sigma,proposal_coefficients=fit.x.tolist(),proposal_losses=evaluate(fit.x).tolist(),solver_success=bool(fit.success),native_checks=checks));(out/'running.json').write_text(json.dumps(dict(trials=trials,best=best,proposals=calls,seconds=time.time()-start),indent=2)+'\n');print(json.dumps(dict(sigma=sigma,native=checks,best=best,proposals=calls)),flush=True)
(root.parent/'spectral-proposal/report.json').write_text(json.dumps(dict(baseline_pass=23,proposal_protocol='5000 frozen train positions,16 Gaussian quadrature offsets; approximate proposal objective only. No reference-score/protocol change. All selected results replay full native renderer.',baseline_proposal=baseline,trials=trials,best=best,evaluations=calls,seconds=time.time()-start,status='Private unadopted proposal search; spectral source coverage and HQ visual checks still required.'),indent=2)+'\n')
