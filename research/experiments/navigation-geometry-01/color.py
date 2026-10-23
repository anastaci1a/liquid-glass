"""One common affine response; cached geometry and fixed solid compositing."""
import datetime,json,time
import numpy as np
from native import OUT,setup,save,metrics,preview
from vector_foreground import coverage
deadline=datetime.datetime.fromisoformat(json.loads((OUT/'protocol.json').read_text())['stages'][2]['deadline']).timestamp()
if (OUT/'color-result.json').exists():raise RuntimeError('Completed color study cannot repeat')
def gate():
 if time.time()>deadline:raise RuntimeError('Color deadline reached')
states=[];A=np.zeros((2,2));rhs=np.zeros(2)
for k in ['a','b']:
 gate();s,c,surf,known,ext,required=setup(k);raw=np.load(OUT/f'{k}-raw.npz');M=raw['material'];C=raw['complete'];alpha=raw['coverage']
 # Fixed solid foreground is affine in its backing. Its transmission product
 # is exact geometry, not a fitted per-pixel material coefficient.
 trans=np.ones(alpha.shape);x0,y0,_,_=s.crop
 assert not s.transmission_layers
 for layer in s.case['foreground_layers']:
  assert layer['mode']=='solid'
  style=s.case.get('foreground_styles',{}).get(layer.get('style_key',layer['vector_asset']),{})
  assert 'response' not in style
  a,b,c0,d=layer['box'];a0=coverage(s.folder,layer)*style.get('opacity',layer.get('opacity',1.))
  trans[b-y0:d-y0,a-x0:c0-x0]*=1-a0
 train=s.valid&~s.held;v=M[train].astype(float).reshape(-1);t=s.target_crop[train].astype(float).reshape(-1)
 A+=np.array([[v@v,v.sum()],[v.sum(),len(v)]])/len(v);rhs+=np.array([v@t,t.sum()])/len(v)
 zero=(C.astype(float)+((1-1)*M.astype(float)+0)*alpha[...,None]*trans[...,None]).astype(C.dtype)
 np.testing.assert_array_equal(zero,C)
 states.append((k,s,raw,ext,trans))
# Exact minimization of the convex two-variable quadratic over its triangle.
candidates=[]
free=np.linalg.solve(A,rhs)
if free[0]>=0 and free[1]>=0 and free.sum()<=1:candidates.append(free)
for origin,direction in [(np.array([0.,0.]),np.array([1.,0.])),(np.array([0.,0.]),np.array([0.,1.])),(np.array([0.,1.]),np.array([1.,-1.]))]:
 t=np.clip(direction@(rhs-A@origin)/(direction@A@direction),0,1);candidates.append(origin+t*direction)
best=min(candidates,key=lambda z:float(z@A@z-2*z@rhs));save('color-proposal.json',{'gain':float(best[0]),'bias':float(best[1]),'training':'Original train pixels only; equal reference weight, shared RGB response.', 'normal_matrix':A.tolist(),'rhs':rhs.tolist(),'zero_composite_exact':True,'operator':'C_new = C_saved + alpha * product(1-alpha_foreground) * ((g-1)*M_saved+b); fixed solid compositor, float32 final output. No image-coordinate change.','precision':'This cached incremental material operator preserves zero exactly; it is not a new full-ray render. Saved quantization remains explicit.'})
baseline=json.loads((OUT/'raw-result.json').read_text())['references'];trials=[];selected=None
for step in [1.,.5,.25,.125]:
 gate();g=1+step*(best[0]-1);b=step*best[1];rows=[]
 for (k,s,raw,ext,trans),old in zip(states,baseline):
  M=raw['material'].astype(float);graded=g*M+b;assert graded.min()>=0 and graded.max()<=1+1e-14
  C=(raw['complete'].astype(float)+((g-1)*M+b)*raw['coverage'][...,None]*trans[...,None]).astype(np.float32)
  z=metrics(s,graded.astype(np.float32),C,ext);prev=old['scores'];guards={n:z[n]['rmse']<=prev[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};guards.update(E=z['E']<=prev['E'],ssim=z['ssim']>=prev['ssim']);guards.update({n:z['foreground_mse'][n]<=v for n,v in prev['foreground_mse'].items()})
  np.savez_compressed(OUT/f'{k}-color-{step:g}.npz',material=graded.astype(np.float32),complete=C)
  rows.append({'reference':k,'scores':z,'guards':guards,'range':[float(graded.min()),float(graded.max())]})
 trial={'factor':step,'gain':float(g),'bias':float(b),'references':rows};trials.append(trial);save('color-ledger.json',trials)
 if all(all(r['guards'].values()) for r in rows):selected=trial;break
save('color-result.json',{'status':'CACHED_COMPONENT_QUALIFIER_PENDING_REVIEW' if selected else 'NO_PAIRED_QUALIFIER','selected':selected,'trials':len(trials),'new_rays':0,'source_queries':0,'clipping':0,'limitations':'Empirical encoded neutral response on the raw physical diagnostic, not historical replacement or calibrated radiance.'})
if selected:
 for k,s,raw,ext,trans in states:preview(s,np.load(OUT/f'{k}-color-{selected["factor"]:g}.npz')['complete'],k+'-color','Common neutral color response')
print(json.dumps({'selected':selected,'trials':len(trials)}),flush=True)
