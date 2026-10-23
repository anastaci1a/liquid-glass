import sys,json
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np
from crowned_footprint import field
from switch_front_surface import mapping,bounds
out=Path('/evidence/extended/active-switch/physical-front-surface');out.mkdir(exist_ok=True);rows=[]
for half in [np.array([1.55,1.]),np.array([1.,1.55])]:
 y,x=np.mgrid[-1.7:1.7:137j,-1.7:1.7:139j];soft=.08;t=.03;bx=.05;by=.1;g=5;n=1.5;e=1e-5
 X,Y,d=mapping(x,y,half,soft,t,bx,by,g,n);inside=d['inside'];safe=field(x,y,half,soft)[0]<.98
 def H(x,y):return (1-field(x,y,half,soft)[0])*(t+bx*x*x+by*y*y)
 gx=(H(x+e,y)-H(x-e,y))/(2*e);gy=(H(x,y+e)-H(x,y-e))/(2*e)
 grad=float(np.max(np.hypot(gx-d['hx'],gy-d['hy'])[safe]));assert grad<1e-7
 V=np.stack([d['vx'],d['vy'],d['vz']],-1);W=np.stack([d['wx'],d['wy'],d['wz']],-1)
 unit=float(max(np.max(abs(np.linalg.norm(V,axis=-1)-1)),np.max(abs(np.linalg.norm(W,axis=-1)-1))));assert unit<1e-12
 N=np.stack([-d['hx'],-d['hy'],np.ones_like(x)],-1);N/=np.linalg.norm(N,axis=-1)[...,None];D=np.zeros_like(V);D[...,2]=-1
 first=float(np.max(np.linalg.norm(np.cross(D,N)-n*np.cross(V,N),axis=-1)[inside]));second=float(np.max(np.linalg.norm(W[...,:2]-n*V[...,:2],axis=-1)[inside]));assert max(first,second)<1e-12
 A,B,_=mapping(-x,y,half,soft,t,bx,by,g,n);mirror=float(max(np.max(abs(A+X)),np.max(abs(B-Y))));assert mirror<1e-12
 A,B,_=mapping(-y,x,half[::-1],soft,t,by,bx,g,n);rot=float(max(np.max(abs(A+Y)),np.max(abs(B-X))));assert rot<1e-12
 scales=[]
 for scale in [.1,4,100]:
  A,B,_=mapping(x*scale,y*scale,half*scale,soft,t,bx,by,g,n);v=float(np.max(np.hypot(A/scale-X,B/scale-Y)));assert v<1e-11;scales.append(v)
 A,B,_=mapping(x,y,half,soft,t,bx,by,g,1.);assert np.max(np.hypot(A-x,B-y))<1e-12
 assert np.max(np.hypot(d['hx'],d['hy'])[inside])<=d['bounds']['max_slope']+1e-12
 # At every sampled internal segment location the ray stays below top and
 # above bottom. Shape convexity + valid bottom intersection handles sides.
 clearances=[]
 for f in np.linspace(.01,.99,30):
  xx=x+f*(d['x1']-x);yy=y+f*(d['y1']-y);zz=(1-f)*d['h'];gap=H(xx,yy)-zz;clearances.append(float(np.min(gap[safe])))
 assert min(clearances)>0
 rows.append(dict(half=half.tolist(),gradient_error=grad,unit_error=unit,front_snell_error=first,back_snell_error=second,mirror_error=mirror,rotation_error=rot,scale_errors=scales,minimum_sampled_internal_top_clearance=min(clearances),bounds=d['bounds']))
(out/'invariants.json').write_text(json.dumps(dict(passed=True,observations=rows,scope='Unequal-axis crowned footprint; exact rays, inherited empirical material not a Fresnel/environment model.'),indent=2)+'\n');print(json.dumps(rows),flush=True)
