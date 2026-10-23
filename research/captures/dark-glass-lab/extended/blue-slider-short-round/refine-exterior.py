"""One normalized common-parameter descent proposal; all exterior guards frozen."""
import os,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import linprog
os.umask(0o002);D=Path('/evidence/extended/blue-slider-short-round');R=D/'generated-exterior';P=D/'exterior-primary';O=D/'exterior-joint02';O.mkdir(exist_ok=False);j=json.loads((R/'proposal.json').read_text());c=j['parameters'];sd=np.load(P/'distance.npy');a=np.load(P/'coverage.npy');contact=np.load(P/'contact.npy');M=np.load(R/'native-material.npy');read=lambda n:np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/slider-'+n+'.png').convert('RGB'));B=read('source').astype(float)[440:690,540:985]/255;T=read('target').astype(np.float32)[440:690,540:985]/255;accent=np.array(c['accent_rgb']);L=56.5;yy,xx=np.mgrid[440:690,540:985];held=(xx//32+3*(yy//32))%4==0
masks={'near_exterior':(sd>0)&(sd<.35*L),'full_visible_exterior':sd>0};masks.update({k+'_'+n:v&h for k,v in list(masks.items()) for n,h in [('train',~held),('held',held)]})
def complete(v):
 q,ha,s,b=v;C0=B*(1-q*contact[...,None]);h=ha*np.exp(-.5*(np.maximum(sd,0)/(s*L))**2);C=(1-h[...,None])*C0+h[...,None]*(b*accent);return M*a[...,None]+C*(1-a[...,None])
def loss(C):return np.array([np.mean(((C-T)[m]*255)**2) for m in masks.values()])
v=np.array([c['contact_opacity'],c['halo_opacity'],c['halo_sigma_L'],c['halo_tint_scale']]);C=complete(v);assert np.array_equal(C,np.load(R/'candidate-complete.npy'));base=loss(C);steps=np.array([.01,.005,.04,.02]);J=np.stack([(loss(complete(v+np.eye(4)[i]*steps[i]*.001))-loss(complete(v-np.eye(4)[i]*steps[i]*.001)))/.002 for i in range(4)],axis=1)
scale=np.linalg.norm(J,axis=1);lp=linprog(J[1]/np.linalg.norm(J[1]),A_ub=J/scale[:,None],b_ub=np.zeros(6),bounds=[(-1,1),(-1,1),(-1,1),(-1,0)],method='highs');record=dict(start=v.tolist(),scales=steps.tolist(),jacobian=J.tolist(),lp_success=bool(lp.success),direction=lp.x.tolist() if lp.success else None,trials=[])
if lp.success:
 for t in [.5,.25,.125]:
  w=v+t*steps*lp.x;candidate=complete(w);mse=loss(candidate);ok=bool(np.all(mse<=base) and np.any(mse<base));r=dict(step=t,parameters=w.tolist(),metrics={k:dict(before=float(np.sqrt(b)),after=float(np.sqrt(n)),nonregression=bool(n<=b)) for k,b,n in zip(masks,base,mse)},qualifier=ok);record['trials'].append(r)
  if ok:np.save(O/'candidate-complete.npy',candidate);record['candidate']=r;break
(O/'result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
