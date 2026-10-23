"""Independent Snell/geometry invariants before any target-image fitting."""
import sys,json
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np
from crowned_footprint import field
from switch_back_surface import mapping,bounds
out=Path('/evidence/extended/active-switch/physical-back-surface'); rows=[]
for half in [np.array([1.55,1.]),np.array([1.,1.55])]:
 y,x=np.mgrid[-1.7:1.7:137j,-1.7:1.7:139j];soft=.08;b=.15;c=-.17;g=4.;n=1.5;e=1e-5
 X,Y,d=mapping(x,y,half,soft,b,c,g,n);inside=d['inside'];safe=field(x,y,half,soft)[0]<.98
 def H(x,y):return .2+b*field(x,y,half,soft)[0]+c*field(x,y,half,soft)[0]**2
 gx=(H(x+e,y)-H(x-e,y))/(2*e);gy=(H(x,y+e)-H(x,y-e))/(2*e)
 grad=float(np.max(np.hypot(gx-d['hx'],gy-d['hy'])[safe]));assert grad<1e-7
 norm=float(np.max(abs(d['vx']**2+d['vy']**2+d['vz']**2-1)[inside]));assert norm<1e-12
 # Independent angle construction in the local plane: outgoing tilt is
 # arcsin(n sin(theta))-theta, toward the increasing-thickness direction.
 slope=np.hypot(d['hx'],d['hy']);theta=np.arctan(slope[inside]);delta=np.arcsin(n*np.sin(theta))-theta
 err=float(np.max(abs(np.arctan2(np.hypot(d['vx'],d['vy'])[inside],-d['vz'][inside])-delta)));assert err<1e-12
 # Snell tangential component continuity, with independent cross-products.
 N=np.stack([-d['hx'],-d['hy'],-np.ones_like(x)],-1);N/=np.linalg.norm(N,axis=-1)[...,None]
 V=np.stack([d['vx'],d['vy'],d['vz']],-1);D=np.zeros_like(V);D[...,2]=-1
 snell=float(np.max(np.linalg.norm(np.cross(V,N)-n*np.cross(D,N),axis=-1)[inside]));assert snell<1e-12
 A,B,_=mapping(-x,y,half,soft,b,c,g,n);mirror=float(max(np.max(abs(A+X)),np.max(abs(B-Y))));assert mirror<1e-12
 A,B,_=mapping(-y,x,half[::-1],soft,b,c,g,n);rotation=float(max(np.max(abs(A+Y)),np.max(abs(B-X))));assert rotation<1e-12
 scales=[]
 for f in [.1,4,100]:
  A,B,_=mapping(x*f,y*f,half*f,soft,b,c,g,n);v=float(np.max(np.hypot(A/f-X,B/f-Y)));assert v<1e-11;scales.append(v)
 for bb,cc,nn in [(0.,0.,n),(b,c,1.)]:
  A,B,_=mapping(x,y,half,soft,bb,cc,g,nn);assert np.max(np.hypot(A-x,B-y))<1e-12
 assert np.array_equal(X[~inside],x[~inside]) and np.array_equal(Y[~inside],y[~inside])
 assert np.max(slope[inside])<=d['bounds']['max_slope']+1e-12 and d['bounds']['reentry_bound']<1
 # Trace outside rays through the thickness range, testing they stay below
 # back surface wherever their xy projection remains inside the footprint.
 smallest=1e9
 for tau in np.linspace(.001,2.,64):
  xx=x+d['vx']*tau;yy=y+d['vy']*tau;zz=-d['h']+d['vz']*tau
  T=field(xx,yy,half,soft)[0];active=inside&(T<=1);gap=-H(xx,yy)-zz
  smallest=min(smallest,float(np.min(gap[active])))
 assert smallest>0
 # A fold can occur without TIR: calculate signed Jacobian away from boundary.
 def F(x,y):return mapping(x,y,half,soft,b,c,g,n)[:2]
 xp,yp=F(x+e,y);xm,ym=F(x-e,y);xu,yu=F(x,y+e);xd,yd=F(x,y-e)
 det=((xp-xm)*(yu-yd)-(xu-xd)*(yp-ym))/(4*e*e)
 rows.append(dict(half=half.tolist(),gradient_error=grad,unit_vector_error=norm,angle_error=err,snell_error=snell,mirror_error=mirror,rotation_error=rotation,scale_errors=scales,minimum_sampled_back_clearance=smallest,map_jacobian_range=[float(np.min(det[safe])),float(np.max(det[safe]))],bounds=d['bounds']))
rejected=[]
for label,args in [('negative thickness',(-.4,0,4,1.5)),('background inside solid',(.1,0,.05,1.5)),('supercritical slope',(1.,0.,4,1.5)),('invalid IOR',(.1,0,4,.9))]:
 try:bounds(np.array([1.5,1.]),.08,*args)
 except ValueError:rejected.append(label)
 else:raise AssertionError(label)
assert len(rejected)==4
(out/'invariants.json').write_text(json.dumps(dict(passed=True,observations=rows,rejected=rejected,scope='Flat-front orthographic geometry only; current image material remains empirical. Sampled tests supplement sufficient analytic bounds.'),indent=2)+'\n');print(json.dumps(rows),flush=True)
