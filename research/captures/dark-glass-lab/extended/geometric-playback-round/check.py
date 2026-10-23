import os,json,time,hashlib
from pathlib import Path
import numpy as np
from geometric_optics import CircularBevel,refract,trace_flat_front_orthographic
os.umask(2);D=Path('/evidence/extended/geometric-playback-round');started=time.time();results={}
S=CircularBevel();x=np.linspace(-.98,.98,500);y=np.full_like(x,.11);h,hx,hy,inside=S.height_gradient(x,y);eps=1e-6
fdx=(S.height_gradient(x+eps,y)[0]-S.height_gradient(x-eps,y)[0])/(2*eps);fdy=(S.height_gradient(x,y+eps)[0]-S.height_gradient(x,y-eps)[0])/(2*eps);graderr=float(max(abs(fdx-hx).max(),abs(fdy-hy).max()));assert graderr<1e-9
q=trace_flat_front_orthographic(S,x,y,1.5,2);out=q['exit_direction'];normal=q['outward_normal'];ci=-normal[:,2];ct=(out*normal).sum(-1);snell=float(np.max(abs(1.5*np.linalg.norm(normal[:,:2],axis=-1)-np.linalg.norm(np.cross(out,normal),axis=-1))));assert snell<1e-12
reverse,tir,_=refract(-out,normal,1,1.5);rev=float(np.max(abs(reverse-np.array([0,0,1]))));assert not tir.any() and rev<1e-12
identity=trace_flat_front_orthographic(S,x,y,1,2);assert np.max(abs(identity['X']-x))<1e-12 and np.max(abs(identity['Y']-y))<1e-12
mx=trace_flat_front_orthographic(S,-x,y,1.5,2);rot=trace_flat_front_orthographic(S,-y,x,1.5,2);assert np.max(abs(mx['X']+q['X']))<1e-12 and np.max(abs(rot['X']+q['Y']))<1e-12 and np.max(abs(rot['Y']-q['X']))<1e-12
# Actual same-surface outgoing path lies below the entire back; concavity is
# the analytic global certificate; this is an additional finite-ray control.
clearance=[]
for t in np.linspace(1e-6,2,101):
 points=q['back']+t*out;hh,_,_,inside=S.height_gradient(points[:,0],points[:,1]);g=points[:,2]+hh;clearance.append(float(np.max(g[inside])) if inside.any() else -1)
assert max(clearance)<0
for n in [1.2,1.5,2.]:
 incident=np.array([[0.,0.,-1.]]);N=np.array([[.8,0.,.6]]);d,tir,k=refract(incident,N,n,1);assert bool(tir[0])==(n*.8>1)
try:trace_flat_front_orthographic(CircularBevel(depth=.3),x,y,1.5,2)
except ValueError:results['invalid_branch_rejected']=True
else:raise AssertionError('Uncertified branch accepted')
results.update(height_gradient_fd_max=graderr,snell_max=snell,reciprocity_max=rev,identity_index_pass=True,mirror_rotation_pass=True,no_reentry_finite_control_max=max(clearance),global_no_reentry_proof='h concave on convex disk; outgoing g=z+h has negative initial derivative and is concave; outside disk ray is below cylinder bottom',front='exact normal-incidence air/solid interface',units='all lengths normalized by radius; scale similarity exact by construction',optical_blur=0,new_image_renders=0,wall_seconds=time.time()-started)
(D/'invariants.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results))
