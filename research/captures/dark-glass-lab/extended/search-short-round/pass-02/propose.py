"""One bounded joint material update; exact native and vector-foreground guards."""
import sys,json,ast,gc
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from paired_fit import Cached
from extended_shadow import shadow
from vector_foreground import coverage
from joint_material_jacobian import material_channels
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'search-short-round/pass-02';assert not (out/'joint-candidate.json').exists()
inputs=root/'music-search-vector-paired-replay';S=[Study(inputs/n) for n in ['a','b']];previous=root/'search-short-round/pass-01/joint-candidate.json'; prior=json.loads(previous.read_text()); old=dict(parameters=prior['parameters'],material=prior['candidate']['material']);p=old['parameters'];co=np.asarray(old['material']);base=prior['candidate']['scores'];scales=np.full(23,.015)
# Reuse exactly the first protocol's metrics without executing its completed sweep.
tree=ast.parse((root/'search-short-round/propose.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='metrics');exec(compile(ast.Module(body=[node],type_ignores=[]),'<retained metrics>','exec'))
forms=[]
for i,s in enumerate(S):
 cache=Cached(s,p);im=cache.render(co);assert np.max(np.abs(im-np.load(root/f'search-short-round/pass-01/joint-candidate-{i}.npy')))<2e-6
 residual=im.astype(float)-s.target_crop;layer=s.case['foreground_layers'][0];assert 'vector_asset' in layer and len(s.case['foreground_layers'])==1
 style=s.case['foreground_styles'][layer.get('style_key',layer['vector_asset'])];assert 'response' not in style
 alpha=coverage(s.folder,layer)*style.get('opacity',layer.get('opacity',1.));a,b,c,d=layer['box'];x0,y0,_,_=s.crop;roi=(slice(b-y0,d-y0),slice(a-x0,c-x0));fg=s.apply_foreground(im.copy())[roi]-s.target[b:d,a:c]
 f={k:[np.zeros((23,23)),np.zeros(23)] for k in ['glass','rim','foreground']}
 for channel,F in material_channels(cache,co):
  for name,mask in [('glass',s.valid),('rim',s.rim)]:
   D=F[mask]*scales;r=residual[...,channel][mask];factor=255**2/(3*mask.sum());f[name][0]+=D.T@D*factor;f[name][1]+=D.T@r*factor
  D=(F[roi]*(1-alpha[...,None])*scales).reshape(-1,23);r=fg[...,channel].ravel();factor=255**2/(3*len(r));f['foreground'][0]+=D.T@D*factor;f['foreground'][1]+=D.T@r*factor
 forms.append(f);del cache;gc.collect()
def value(i,z,key):
 H,g=(.7*forms[i]['glass'][0]+.3*forms[i]['rim'][0],.7*forms[i]['glass'][1]+.3*forms[i]['rim'][1]) if key=='loss' else forms[i][key]
 v=base[i]['loss'] if key=='loss' else base[i][key]['rmse']**2 if key=='glass' else base[i]['foreground']**2
 return v+2*g@z+z@H@z
def constraints(v):return np.array([q for i,b in enumerate(base) for q in [v[-1]-value(i,v[:-1],'loss')/b['loss'],1-value(i,v[:-1],'glass')/b['glass']['rmse']**2,1-value(i,v[:-1],'foreground')/b['foreground']**2]])
bounds=[]
for k,c in enumerate(co):
 lo,hi=(.05,1.5) if k<3 or k>=20 else (-.8,.8) if k<6 else(-4,4);bounds.append((max(-1.,(lo-c)/scales[k]),min(1.,(hi-c)/scales[k])))
fit=minimize(lambda v:v[-1],np.r_[np.zeros(23),1.],bounds=bounds+[(0,2)],method='SLSQP',constraints=[dict(type='ineq',fun=constraints)],options=dict(maxiter=100,ftol=1e-11));rows=[];best=None
for alpha in [1.,.5,.25,.125]:
 c=co+alpha*scales*fit.x[:-1];imgs=[s.render(p,c) for s in S];ms=[metrics(s,im) for s,im in zip(S,imgs)];ratios=[a['E']/b['E'] for a,b in zip(ms,base)];allowed=all(a['E']<=b['E'] and a['glass']['rmse']<=b['glass']['rmse'] and all(a[k]<=b[k] for k in ['shadow','foreground']) for a,b in zip(ms,base));row=dict(alpha=alpha,material=c.tolist(),scores=ms,ratios=ratios,allowed=allowed);rows.append(row);print('TRIAL',alpha,ratios,allowed,flush=True)
 if allowed and any(r<1-1e-7 for r in ratios):
  best=row
  for i,im in enumerate(imgs):np.save(out/f'joint-candidate-{i}.npy',im)
  break
record=dict(parameters=p,baseline=base,trials=rows,candidate=best,accepted=False,method=__doc__,solver_success=bool(fit.success),solver_message=str(fit.message),budget='ONE native constrained quadratic update, at most four backtracking trials; no convergence claim',limits='Shared existing affine material only, fixed source/glyph/map/blur/shadow. Simple scalar exposure neighborhood failed both-reference guard; this remains the same material family.')
(out/'joint-candidate.json').write_text(json.dumps(record,indent=2)+'\n')
