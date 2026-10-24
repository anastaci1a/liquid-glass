"""Synthetic adapter invariants only, without a target-selected profile."""
from pathlib import Path
import datetime,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from bevel_footprint_back import BevelFootprintBack
from geometric_optics import CircularBevel
from raised_front_optics import monotone_front_reflection_escape
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});rows=[]
for half in [(1.,1.),(3.,1.)]:
 for depth,power in [(.1,3.),(.05,8.)]:
  charge('synthetic_configurations',1);coordinate=RoundedRectangleHarmonicBack(half,1.,cap_join_width=0);surface=BevelFootprintBack(coordinate,depth,power);v=np.linspace(-.9,.9,8);x,y=np.meshgrid(v*half[0],v);N=x.size
  charge('matched_gradient_points',N);charge('finite_difference_height_points',5*N);h,hx,hy,inside=surface.height_gradient(x,y);e=1e-6;dx=(surface.height_gradient(x+e,y)[0]-surface.height_gradient(x-e,y)[0])/(2*e);dy=(surface.height_gradient(x,y+e)[0]-surface.height_gradient(x,y-e)[0])/(2*e);strict=coordinate.footprint(x,y)[0]<1-1e-4;err=float(max(np.max(abs(dx[strict]-hx[strict])),np.max(abs(dy[strict]-hy[strict]))));assert err<1e-8 and np.all(h>=0) and h.max()<=depth
  assert surface.coordinate is coordinate and surface.boundary_mask(half[0],0.)
  if half==(1.,1.):
   charge('circle_delegate_points',N);old=CircularBevel(core=0.,depth=depth,power=power,edge=0.);before=old.height_gradient(x,y);assert np.array_equal(inside,before[3]);assert max(float(np.max(abs(a[inside]-b[inside]))) for a,b in zip((h,hx,hy),before[:3]))<1e-14
  # Actual reflected directions under the declared camera, calculated directly
  # from the same height normal; no optical primitive or traced ray is executed.
  g=np.stack([hx.ravel()[:16],hy.ravel()[:16]],-1);den=1+np.sum(g*g,-1);direction=np.c_[-2*g/den[:,None],(1-np.sum(g*g,-1))/den];charge('certificate_direction_points',16);assert monotone_front_reflection_escape(surface,direction,g).all()
  rows.append(dict(half=half,synthetic_depth=depth,synthetic_power=power,gradient_max_error=err,positive_height=True,circle_limit_checked=half==(1.,1.)))
  if len(rows)==1:save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,ledger=ledger))
save('result.json',dict(status='SYNTHETIC_ADAPTER_CONTROLS_PASS',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,ledger=ledger,target_profile_selected=False));print(json.dumps({'status':'PASS','ledger':ledger}),flush=True)
