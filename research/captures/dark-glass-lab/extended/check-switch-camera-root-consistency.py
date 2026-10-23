"""Selected local height-root consistency, not a global lens-exclusion proof."""
import sys,json,ast
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np
from extended_fit import Study
from perspective_back_surface import projected_height_gradient
# Reuse pure diagnostic functions without executing the completed screen driver.
source=Path('/evidence/extended/audit-switch-finite-camera.py').read_text();tree=ast.parse(source)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ['gradient','condition']:
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<saved camera diagnostic>','exec'),globals())
root=Path('/evidence/extended/active-switch');out=root/'rev6-finite-camera';rows=[]

def fields(q,step,mapping):
 result=[mapping(q)]
 for axis in np.eye(2):result.extend([mapping(q+axis*step),mapping(q-axis*step)])
 return result

def criterion(q,H,step,mapping,C,G,n):return condition(q,H,fields(q,step,mapping),step,C,G,n)

def consistency(q,H,mapping,C,G,n,outer,inner):
 B,valid=gradient(q,H,mapping(q),C,G,n);parts=[]
 for axis in np.eye(2):
  plus,vp=criterion(q+axis*outer,H,inner,mapping,C,G,n);minus,vm=criterion(q-axis*outer,H,inner,mapping,C,G,n);valid&=vp&vm;parts.append((plus-minus)/(2*outer))
 plus,vp=criterion(q,H+outer,inner,mapping,C,G,n);minus,vm=criterion(q,H-outer,inner,mapping,C,G,n);valid&=vp&vm;ch=(plus-minus)/(2*outer)
 residual=np.stack(parts,-1)+ch[...,None]*B
 return residual,valid,B,ch

# New second-compatibility control on independently forward-traced quadratic.
test=Path('/workspace/docs/liquid-glass/experiments/reconstruction/verify-perspective-back-surface.py').read_text();tree=ast.parse(test)
forward_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='forward');exec(compile(ast.Module(body=[forward_node],type_ignores=[]),'<known physical forward>','exec'),globals())
x,y=np.meshgrid(np.linspace(-.3,.3,11),np.linspace(-.2,.2,9));q=np.stack([x,y],-1).reshape(-1,2);C,G,n=3.,2.,1.5;K=np.array([[.08,.02],[.02,.04]])
def known(q):return forward(q,C,G,n,K,.4)[0]
H=forward(q,C,G,n,K,.4)[1];R,valid,_,_=consistency(q,H,known,C,G,n,.001,.0001);assert valid.all();control=float(np.linalg.norm(R,axis=-1).max());assert control<2e-7,control;print('KNOWN_CONTROL',control,flush=True)
model=json.loads((root/'rev5-joint-existing/candidate.json').read_text());p=model['parameters']
for name in ['a','b']:
 s=Study(root/'paired'/name);half=s.half+np.array([p['half_x_delta'],p['half_y_delta']]);x,y=np.meshgrid(np.linspace(-half[0]+.01,half[0]-.01,71),np.linspace(-half[1]+.01,half[1]-.01,51));origin=np.array([p['shape_dx'],p['shape_dy']]);pos=np.stack([x,y],-1);sd=s.shape(x+origin[0],y+origin[1],p)[-1][0];points=pos[sd<-.01]
 def mapping(q):
  X,Y,_,_=s.geometry_field(q[...,0]+origin[0],q[...,1]+origin[1],p);return np.stack([X-origin[0],Y-origin[1]],-1)
 C,G,n=10.,4.,1.5;inner=.0001;f=fields(points,inner,mapping);samples=[]
 for fraction in np.linspace(.05,.95,19):
  H=np.full(len(points),G*fraction);value,valid=condition(points,H,f,inner,C,G,n);samples.append((H,value,valid))
 chosen=np.zeros(len(points),bool);lo=np.zeros(len(points));hi=np.zeros(len(points));clo=np.zeros(len(points))
 for a,b in zip(samples,samples[1:]):
  selected=~chosen&a[2]&b[2]&(a[1]*b[1]<0);lo[selected]=a[0][selected];hi[selected]=b[0][selected];clo[selected]=a[1][selected];chosen|=selected
 q=points[chosen];lo=lo[chosen];hi=hi[chosen];clo=clo[chosen];f=fields(q,inner,mapping);ok=np.ones(len(q),bool)
 for _ in range(42):
  mid=(lo+hi)/2;value,valid=condition(q,mid,f,inner,C,G,n);ok&=valid
  left=(clo*value<=0)&valid;right=(~left)&valid;hi=np.where(left,mid,hi);lo=np.where(right,mid,lo);clo=np.where(right,value,clo)
 H=(lo+hi)/2;value,valid=condition(q,H,f,inner,C,G,n);ok&=valid&(abs(value)<1e-6)
 r1,v1,B,ch=consistency(q,H,mapping,C,G,n,.002,.0001);r2,v2,_,_=consistency(q,H,mapping,C,G,n,.001,.00005);length=np.linalg.norm(r2,axis=-1);noise=np.linalg.norm(r1-r2,axis=-1);finite=ok&v1&v2&np.isfinite(length)&np.isfinite(noise);nonzero=finite&(length>np.maximum(1e-5,100*noise))
 row=dict(observation=name.upper(),camera_over_L=C,gap_over_L=G,index=n,inside_nodes=len(points),lowest_sampled_bracket_selected=int(chosen.sum()),refined_compatible_local_roots=int(ok.sum()),second_condition_evaluable=int(finite.sum()),stable_nonzero_second_condition=int(nonzero.sum()),unresolved_or_small_second_condition=int((finite&~nonzero).sum()),residual_norm_quantiles=np.quantile(length[finite],[0,.1,.5,.9,1]).tolist(),limits='Only lowest sampled sign bracket per point at one declared camera/index/gap; other roots/parameters unexamined. Finite-step disagreement is not a rigorous error bound. No root or global physical impossibility claim.')
 rows.append(row);np.savez_compressed(out/f'{name}-selected-root-consistency.npz',points=q,height=H,first_residual=value,refined_valid=ok,second_residual=r2,step_difference=r1-r2,valid=finite,stable_nonzero=nonzero);print(json.dumps(row),flush=True)
with (out/'selected-root-consistency.json').open('x') as f:json.dump(dict(method=__doc__,known_quadratic_second_residual_max=control,observations=rows),f,indent=2);f.write('\n')
