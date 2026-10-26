"""Primary-owned controls before native transport; no source sampling."""
from pathlib import Path
import json,datetime,sys,hashlib
import numpy as np
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from ellipse_core_coordinate import EllipseCoreCoordinate,EllipseCoreSplineBack
from spline_height_back import SplineFootprintBack
from hermite_height_back import HermiteFootprintBack
from raised_front_optics import VerticalScaleBack,trace_raised_front_orthographic
P=json.loads((OUT/'plan.json').read_text());F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());ledger=dict.fromkeys(P['geometry_caps'],0)
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['geometry_deadline']);assert ledger[k]+n<=P['geometry_caps'][k],k;ledger[k]+=int(n)
def hg(k,n):charge('height_point_queries',n)
try:
 g=F['geometry'];model=json.loads((ROOT/g['back_profile']).read_text());results=[]
 for member in ['expanded','compact']:
  half=(F['members'][member]['major_half'],g['minor_half']);R=g['corner_radius'];base=EllipseCoreSplineBack(half,R,g['breaks'],g['height_controls'],charge);back=HermiteFootprintBack(base,model);front=VerticalScaleBack(base,g['front_scale']);core=np.array(half)-R
  # Independent scalar root solver for distance, different from shared Newton.
  pts=np.array([[0,0],[core[0]/2,.2],[core[0],.2],[core[0]+.4,.3],[half[0]+.1,0],[0,half[1]+.1],[-core[0]-.5,-.5]])
  D,NX,NY=base.coordinate.distance_gradient(pts[:,0],pts[:,1]);reference=[]
  for x,y in pts:
   a,b=core
   if (x/a)**2+(y/b)**2<=1:reference.append(0.);continue
   f=lambda t:(a*x/(a*a+t))**2+(b*y/(b*b+t))**2-1
   t=brentq(f,0,np.hypot(a*x,b*y),xtol=1e-15,rtol=1e-14);reference.append(float(np.hypot(x-a*a*x/(a*a+t),y-b*b*y/(b*b+t))))
  distance_error=float(np.max(abs(D-reference)));assert distance_error<1e-10
  for surf in [base,back,front]:
   eps=1e-6;x=pts[:4,0];y=pts[:4,1];h,hx,hy,inside=surf.height_gradient(x,y)
   dx=(surf.height_gradient(x+eps,y)[0]-surf.height_gradient(x-eps,y)[0])/(2*eps);dy=(surf.height_gradient(x,y+eps)[0]-surf.height_gradient(x,y-eps)[0])/(2*eps)
   error=float(max(np.max(abs(dx-hx)),np.max(abs(dy-hy))));assert error<2e-6,(member,type(surf).__name__,error)
  poles=np.array([[half[0],0],[-half[0],0],[0,half[1]],[0,-half[1]]]);assert base.boundary_mask(*poles.T).all()
  eq=EllipseCoreCoordinate((half[1],half[1]),R);v=np.linspace(0,half[1]+1,81);d,_,_=eq.distance_gradient(v,v*0);assert np.max(abs(d-np.maximum(v-(half[1]-R),0)))<1e-12
  sc=EllipseCoreCoordinate(tuple(2*np.array(half)),2*R);sd,sx,sy=sc.distance_gradient(2*pts[:,0],2*pts[:,1]);assert np.max(abs(sd-2*D))<1e-12
  # Ordered physical controls at regular core/body/cap points, both indices.
  xx,yy=np.meshgrid(np.array([-core[0]-.4,-core[0],-1.,0.,1.,core[0],core[0]+.4]),np.array([-.5,0.,.5]));rec=[]
  for index in [1.,1.5]:
   charge('fixture_rays',xx.size);q=trace_raised_front_orthographic(back,xx,yy,1.,index,F['optics']['background_distance'],hg,front_surface=front)
   assert q['complete'].all();assert np.max(abs(q['X']+q['X'][:,::-1]))<1e-9 and np.max(abs(q['Y']+q['Y'][::-1]))<1e-9
   if index==1:assert np.max(abs(q['X']-xx))<1e-9 and np.max(abs(q['Y']-yy))<1e-9
   rec.append({'index':index,'rays':xx.size,'back_residual':float(np.nanmax(abs(q['back_residual']))),'outgoing_clearance':float(np.nanmin(q['outgoing_back_clearance']))})
  results.append({'member':member,'distance_vs_brent_error':distance_error,'front_slope':front.slope_bound,'back_slope':back.slope_bound,'physical_controls':rec})
 now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['geometry_checkpoint_deadline']);save('geometry-checkpoint.json',{'at':now.isoformat(),'status':'PASS','records':results,'ledger':ledger,'source_queries':0});print(json.dumps(results),flush=True)
except Exception as e:
 save('geometry-control-failure.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':repr(e),'ledger':ledger});raise
finally:save('geometry-control-ledger.json',ledger)
