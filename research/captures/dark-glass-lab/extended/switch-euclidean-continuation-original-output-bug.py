"""Joint geometry/material photometric proposals for the true-distance solid.
5000 fixed train coordinates +16 fixed Gaussian quadrature offsets propose
only. Full native original E/glass/exterior and source/visual checks decide.
No model-source or native scoring changes. One family, no pass per iteration.
"""
import sys,json,copy,time,gc
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from scipy.optimize import minimize
from extended_fit import Study
from switch_euclidean_surface import EuclideanSurfaceStudy
from render import shade
from material_context import affine
from grazing_reflection import layers
from joint_visible_statistics import measures
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());initial=json.loads((out/'photometric-settlement.json').read_text());p0=old['parameters'];S=[Study(root/'paired'/n) for n in ['a','b']];P=[EuclideanSurfaceStudy(s.folder) for s in S];probes=[]
for s in S:
 idx=s.indices;x=s.x.ravel()[idx];y=s.y.ravel()[idx];h=np.sqrt(2)*s.kernel_sigma(p0,'post_sigma')/s.L;dx,dy=np.meshgrid([-h,0,0,h],[-h,0,0,h]);w,env=layers(s,p0);T,offset=affine(s,p0)
 probes.append(dict(x=x[:,None]+dx.ravel(),y=y[:,None]+dy.ravel(),target=s.target_crop.reshape(-1,3)[idx],rim=s.rim.ravel()[idx],T=T,offset=offset,w=w.ravel()[idx,None],env=env.reshape(-1,3)[idx]))
def sample(s,p,co,q,with_jac=False):
 C,J=s.field(q['x'],q['y'],p);effective=q['T']@co+q['offset'];rgb=shade(C,J,effective).mean(1);rgb=rgb*(1-q['w'])+q['env']*q['w']
 if not with_jac:return rgb
 core=J[...,-1];z=C*((1-core[...,None])*effective[:3]+core[...,None]*effective[-3:])+effective[3:6]+(J[...,:-1]@effective[6:-3])[...,None];D=np.zeros((len(C),3,23))
 for channel in range(3):
  active=(z[...,channel]>0)&(z[...,channel]<1);F=np.zeros((len(C),23))
  F[:,channel]=(active*C[...,channel]*(1-core)).mean(1);F[:,channel+3]=active.mean(1);F[:,6:20]=(active[...,None]*J[...,:-1]).mean(1);F[:,channel+20]=(active*C[...,channel]*core).mean(1)
  D[:,channel,:]=(F@q['T'])*(1-q['w'])
 return rgb,D
q0=initial['parameters']['euclidean_surface'];point=np.r_[[q0['bx'],q0['by']],q0['profile'],initial['material']];scales=np.r_[np.full(9,.005),np.full(23,.08)];history=copy.deepcopy(initial['history']);offset_iteration=len(history)
def unpack(v):
 p=copy.deepcopy(initial['parameters']);q=p['euclidean_surface'];q['bx']=float(v[0]);q['by']=float(v[1]);q['profile']=v[2:9].tolist();return p,v[9:]
def metric(im,q):
 e=(im-q['target'])*255;glass=float(np.mean(e**2));rim=float(np.mean(e[q['rim']]**2));return dict(loss=.7*glass+.3*rim,glass=glass,rim=rim)
base=[metric(sample(s,p0,np.array(old['material']),q),q) for s,q in zip(S,probes)]
def evaluate(v,jac=False):
 p,co=unpack(v);return [sample(s,p,co,q,jac) for s,q in zip(P,probes)]
ims=evaluate(point);met=[metric(im,q) for im,q in zip(ims,probes)]
def merit(ms):return max(a['loss']/b['loss'] for a,b in zip(ms,base))
def bound(k):
 if k<2:return (-.08,.08)
 if k<9:return (-.5,.5)
 j=k-9;return (.05,1.5) if j<3 or j>=20 else (-.8,.8) if j<6 else (-4,4)
trust=1.5
for iteration in range(10):
 started=time.time();forms=[];p,co=unpack(point)
 for s,q in zip(P,probes):
  im,Dm=sample(s,p,co,q,True);Do=[]
  for k in range(9):
   eps=.0002;v=point.copy();v[k]+=eps;pa,ca=unpack(v);v[k]-=2*eps;pb,cb=unpack(v);Do.append((sample(s,pa,ca,q)-sample(s,pb,cb,q))/(2*eps))
  D=np.concatenate([np.stack(Do,axis=-1),Dm],axis=-1)*scales;res=im-q['target'];row={}
  for name,mask in [('glass',np.ones(len(im),bool)),('rim',q['rim'])]:
   a=D[mask].reshape(-1,32);r=res[mask].ravel();factor=255**2/len(r);row[name]=(a.T@a*factor,a.T@r*factor)
  row['loss']=(.7*row['glass'][0]+.3*row['rim'][0],.7*row['glass'][1]+.3*row['rim'][1]);forms.append(row)
 def value(i,v,kind):
  H,g=forms[i][kind];d=v[:-1];return met[i][kind]+2*g@d+d@H@d
 def constraints(v):return np.array([z for i,b in enumerate(base) for z in [v[-1]-value(i,v,'loss')/b['loss'],max(1.,met[i]['glass']/b['glass'])-value(i,v,'glass')/b['glass']]])
 ranges=[(max(-trust,(bound(k)[0]-v)/scales[k]),min(trust,(bound(k)[1]-v)/scales[k])) for k,v in enumerate(point)]+[(0,50)]
 fit=minimize(lambda v:v[-1],np.r_[np.zeros(32),merit(met)],method='SLSQP',bounds=ranges,constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=200,ftol=1e-10))
 best=point.copy();bm=met;bi=ims;trials=[]
 for a in [1,.5,.25,.125]:
  v=point+a*scales*fit.x[:-1];images=evaluate(v);m=[metric(im,q) for im,q in zip(images,probes)];allowed=all(x['glass']<=max(b['glass'],pr['glass'])+1e-6 for x,b,pr in zip(m,base,met));trials.append(dict(alpha=a,scores=m,allowed=allowed))
  if allowed and merit(m)<merit(bm):best,bm,bi=v,m,images
 gain=merit(met)-merit(bm);point,met,ims=best,bm,bi;history.append(dict(iteration=offset_iteration+iteration+1,seconds=time.time()-started,gain=gain,merit=merit(met),solver_success=bool(fit.success),trials=trials))
 p,co=unpack(point);(out/'continuation-progress.json').write_text(json.dumps(dict(parameters=p,material=co.tolist(),proposal_scores=met,history=history,accepted=False),indent=2)+'\n');print('STEP',offset_iteration+iteration+1,merit(met),gain,round(time.time()-started,2),flush=True)
 if gain<1e-5:trust*=.4
 else:trust=min(1.5,trust*1.2)
 if trust<.1:break
p,co=unpack(point);native=[]
for s,b in zip(P,S):
 im=s.render(p,co);m={**s.scores(im),**measures(s,p,im)};baseline_image=b.render(p0,np.array(old['material']));bm={**b.scores(baseline_image),**measures(b,p0,baseline_image)};native.append(dict(E=float(np.sqrt(m['loss'])),ratio=float(np.sqrt(m['loss']/bm['loss'])),scores=m,baseline=bm,nonregression=all(m[k]['rmse']<=bm[k]['rmse'] for k in ['glass','shadow'])))
(out/'photometric-settlement.json').write_text(json.dumps(dict(parameters=p,material=co.tolist(),native=native,history=history,proposal_baseline=base,method=__doc__,accepted=False,numeric_pass=all(v['ratio']<=.995 and v['nonregression'] for v in native)),indent=2)+'\n');print('NATIVE',[(v['E'],v['ratio']) for v in native],flush=True)
