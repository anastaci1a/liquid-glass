"""One bounded shared existing-material proposal with original paired guards."""
import os,sys,json,math
from pathlib import Path
import numpy as np,cv2
from scipy.optimize import minimize
ROOT=Path('/evidence/extended/expanded-mini-short-round');sys.path.insert(0,str(ROOT));from preflight import Study,guards
from paired_fit import Cached
from vector_foreground import coverage
from vector_revision import composite
from motion_support import complete
from source_support import masks
from publish import pair
os.umask(0o002)
OUT=ROOT/'material-step';OUT.mkdir(exist_ok=True)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
assert json.loads((ROOT/'preflight-result.json').read_text())['fit_authorized_by_source']
assert not (OUT/'started.json').exists(),'Inspect saved study before restarting'
save('started.json',dict(budget='ONE analytic23existingmaterial linearization and one SLSQP direction, max4actual native backtracks',source='original emitted whole+ALL scored3sigma support reused: map/kernel/input unchanged',normalized_coefficient_bound=.005,clipping='recomputed by original native render for every trial'))
base=json.loads((ROOT/'baseline-native-recipe.json').read_text());p=base['parameters'];co=np.array(base['material']);ss=[Study(ROOT/n) for n in ['a','b']];forms=[]
for i,s in enumerate(ss):
 cache=Cached(s,p);pred=np.load(ROOT/f'ref{i}-baseline-material.npy');assert np.array_equal(cache.render(co),pred),'Cached proposal baseline must match native exactly'
 C,J=cache.C,cache.J;core=J[...,-1];z=C*((1-core[...,None])*co[:3]+core[...,None]*co[-3:])+co[3:6]+(J[...,:-1]@co[6:-3])[...,None]
 H,W=cache.H,cache.W;factor=np.ones((H,W));x0,y0,_,_=s.crop;boxes={}
 for box,alpha,_ in s.foreground_layers:
  vec=s.vector_layers.get(tuple(box))
  if vec:
   sty=s.case.get('foreground_styles',{}).get(vec.get('style_key',vec['vector_asset']),{});assert 'response' not in sty
   alpha=coverage(s.folder,vec)*sty.get('opacity',vec.get('opacity',1.))
  a,b,c,d=box;factor[b-y0:d-y0,a-x0:c-x0]*=1-alpha
 for l in s.case['foreground_layers']:
  a,b,c,d=l['box'];boxes[l.get('style_key',l.get('vector_asset',l.get('artwork_asset')))]=np.s_[b-y0:d-y0,a-x0:c-x0]
 err=pred.astype(float)-s.target_crop;fgerr=s.apply_foreground(pred.copy()).astype(float)-s.target_crop
 forms.append({k:[np.zeros((23,23)),np.zeros(23)] for k in ['glass','rim',*boxes]})
 def accum(k,D,e):
  X=D.reshape(-1,23);e=e.ravel();w=255**2/(3*len(e));forms[-1][k][0]+=X.T@X*w;forms[-1][k][1]+=X.T@e*w
 for c in range(3):
  active=(z[...,c]>0)&(z[...,c]<1);avg=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3));F=np.zeros((H,W,23))
  F[...,c]=avg(active*C[...,c]*(1-core));F[...,c+3]=avg(active);F[...,6:20]=avg(active[...,None]*J[...,:-1]);F[...,c+20]=avg(active*C[...,c]*core)
  sigma=s.kernel_sigma(p,'post_sigma')
  if sigma>.001:F=cv2.GaussianBlur(F,(0,0),sigma)
  F*=.005
  for k,mask in [('glass',s.valid),('rim',s.rim)]:accum(k,F[mask],err[...,c][mask])
  F*=factor[...,None]
  for k,sl in boxes.items():accum(k,F[sl],fgerr[...,c][sl])
 forms[-1]['loss']=[.7*forms[-1]['glass'][k]+.3*forms[-1]['rim'][k] for k in range(2)]
 del cache,C,J,z;print('J',i,flush=True)
save('forms.json',[{k:dict(H=v[0].tolist(),g=v[1].tolist()) for k,v in scene.items()} for scene in forms])
keys=['loss','glass',*base['scores'][0]['foreground_mse']]
def norm(i,k):
 b=base['scores'][i];return max(1.,b['loss'] if k=='loss' else b['glass']['rmse']**2 if k=='glass' else b['foreground_mse'][k])
def value(i,k,v):
 H,g=forms[i][k];return (2*g@v+v@H@v)/norm(i,k)
def jac(i,k,v):
 H,g=forms[i][k];return 2*(g+H@v)/norm(i,k)
fun=lambda v:sum(value(i,'loss',v) for i in range(2))/2
funjac=lambda v:sum(jac(i,'loss',v) for i in range(2))/2
cons=lambda v:np.array([-value(i,k,v) for i in range(2) for k in keys])
consjac=lambda v:np.array([-jac(i,k,v) for i in range(2) for k in keys])
opt=minimize(fun,np.zeros(23),jac=funjac,method='SLSQP',bounds=[(-1,1)]*23,constraints=[dict(type='ineq',fun=cons,jac=consjac)],options=dict(maxiter=100,ftol=1e-12))
save('proposal.json',dict(delta_material=(.005*opt.x).tolist(),predicted_change=float(opt.fun),success=bool(opt.success),message=opt.message,constraints=cons(opt.x).tolist()))
rows=[]
for t in ([1.,.5,.25,.125] if opt.fun < -1e-12 else []):
 new=co+t*.005*opt.x;imgs=[s.render(p,new) for s in ss];scores=[guards(s,p,a)[0] for s,a in zip(ss,imgs)]
 good=all(sc['E']<=b['E'] and sc['glass']['rmse']<=b['glass']['rmse'] and sc['exterior']['rmse']<=b['exterior']['rmse'] and all(v<=b['foreground_mse'][k] for k,v in sc['foreground_mse'].items()) for sc,b in zip(scores,base['scores']))
 gain=any(sc['E']<b['E'] for sc,b in zip(scores,base['scores']))
 row=dict(factor=t,scores=scores,all_guards=good,progress=gain);rows.append(row)
 for i,a in enumerate(imgs):np.save(OUT/f'trial{len(rows)-1}-ref{i}-material.npy',a)
 save('trials.json',rows);print('TRIAL',t,[s['E'] for s in scores],good,flush=True)
 if good and gain:
  candidate={**base,'material':new.tolist(),'scores':scores,'source_proof':'Map/kernel/shape/source/emittedgrid unchanged; original native whole+ALLscored support proof transfers.'};save('candidate-native.json',candidate)
  for i,(s,a) in enumerate(zip(ss,imgs)):
   known,_=masks(s);full=composite(s,p,a,1,complete(s,known));np.save(OUT/f'ref{i}-complete.npy',full);pair(np.rint(s.target_crop*255).astype(np.uint8),np.rint(np.clip(full,0,1)*255).astype(np.uint8),('Apple source','Reconstruction')).save(OUT/f'ref{i}-comparison.png')
  break
save('result.json',dict(trials=rows,accepted=False,count=0,limits='Only original shared23material parameters; no target overlays, source change, glyph fitting or mask/AA changes. Independent native/source/visual acceptance pending.'))
