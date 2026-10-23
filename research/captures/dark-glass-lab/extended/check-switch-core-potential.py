"""Finite differences and geometric invariants before native fitting."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import numpy as np,cv2
from switch_core_potential import potential_terms,coefficient_bound,CorePotentialStudy
from extended_fit import Study
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-core-potential';out.mkdir(exist_ok=True)
p=json.loads((root/'rev4-ambient-review/candidate.json').read_text())['parameters'];rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);_,_,half,r,_=s.shape(np.array([0.]),np.array([0.]),p);w=.30*r;bound=coefficient_bound(half,p['crown_softness'],w);co=np.array([.7,-.3])*bound
 y,x=np.mgrid[-1.2:1.2:65j,-1.8:1.8:79j];e=1e-5*r
 def terms(x,y,half=half,co=co,width=w):return potential_terms(x,y,half,p['crown_softness'],co,width)
 H,dx,dy=terms(x,y);fdx=-(terms(x+e,y)[0]-terms(x-e,y)[0])/(2*e);fdy=-(terms(x,y+e)[0]-terms(x,y-e)[0])/(2*e)
 grad=float(np.max(np.hypot(dx-fdx,dy-fdy)));curl=float(np.max(abs((terms(x+e,y)[2]-terms(x-e,y)[2]-terms(x,y+e)[1]+terms(x,y-e)[1])/(2*e))))
 assert grad<1e-8 and curl<1e-7,(grad,curl)
 _,mx,my=terms(-x,y);mirror=float(max(np.max(abs(mx+dx)),np.max(abs(my-dy))));assert mirror<1e-14
 _,rx,ry=terms(-y,x,half[::-1],co[::-1],w);rotation=float(max(np.max(abs(rx+dy)),np.max(abs(ry-dx))));assert rotation<1e-14
 scaling=[]
 for scale in [.2,4,100]:
  _,sx,sy=terms(x*scale,y*scale,half*scale,co,w*scale);scaling.append(float(np.max(np.hypot(sx/scale-dx,sy/scale-dy))));assert scaling[-1]<1e-13
 _,bx,by=terms(x,y,half,np.array([bound,bound]),w);*_,(sd,_,_)=s.shape(x+p.get('shape_dx',0),y+p.get('shape_dy',0),p)
 maximum=float(np.max(np.hypot(bx,by)[sd<=0])/r);assert maximum<=.12
 rows.append(dict(observation=name.upper(),coefficient_bound=bound,gradient_error=grad,curl=curl,mirror_error=mirror,rotation_error=rotation,scale_errors=scaling,maximum_grid_displacement_over_minor=maximum))
q=copy.deepcopy(p);q['core_potential']=[0.,0.];co=np.array(json.loads((root/'rev4-ambient-review/candidate.json').read_text())['material']);s=Study(root/'paired/a');t=CorePotentialStudy(root/'paired/a');zero=float(np.max(abs(s.render(p,co)-t.render(q,co))));assert zero==0
(out/'invariants.json').write_text(json.dumps(dict(equation='Psi=.5*(kx*x²+ky*y²)*S(d/(.3r)); added map=-gradPsi; actual grad d',observations=rows,zero_native_render_error=zero,coefficient_bound=min(v['coefficient_bound'] for v in rows),limits='Only added field integrable. No recovered physical solid; fixed pose/source masks. Analytic triangle displacement bound; native source proof required for any accepted candidate.'),indent=2)+'\n');print(json.dumps(rows),flush=True)
