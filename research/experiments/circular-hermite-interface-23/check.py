from pathlib import Path
import sys,json,datetime,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from geometric_optics import HarmonicCircularBack
from hermite_height_back import CircularHarmonicFootprintBack,HermiteFootprintBack
P=json.loads((OUT/'protocol.json').read_text());end=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));points=0
assert not (OUT/'result.json').exists()
def count(n):
 global points
 assert datetime.datetime.now(datetime.timezone.utc)<end and points+n<=5000
 points+=n
records=[]
for R in [.9,.9972124917582454,1.1]:
 front=CircularHarmonicFootprintBack(R);old=HarmonicCircularBack();xx,yy=np.meshgrid(np.linspace(-1.05,1.05,7)*R,np.linspace(-1.05,1.05,7)*R);x=np.r_[xx.ravel(),R,-R,0.,0.,0.];y=np.r_[yy.ravel(),0.,0.,R,-R,0.]
 count(5*x.size);actual=front.height_gradient(x,y);h,hx,hy,inside=old.height_gradient(x/R,y/R)
 assert all(np.array_equal(a,b,equal_nan=True) for a,b in zip(actual,(h,hx/R,hy/R,inside)))
 assert np.array_equal(front.boundary_mask(x,y),old.boundary_mask(x/R,y/R))
 assert np.array_equal(front.coordinate.footprint(x,y)[0]<=1,inside)
 records.append({'radius':R,'original_height_gradient_membership_boundary_exact':True,'points':x.size})
path=ROOT/'research/experiments/agent-search-inverse-back-27/back-profile.json';digest=hashlib.sha256(path.read_bytes()).hexdigest();model=json.loads(path.read_text());front=CircularHarmonicFootprintBack(.9972124917582454);back=HermiteFootprintBack(front,model)
errors=[]
for x,y in [(.2,.1),(.5,.2),(.8,.1)]:
 eps=1e-6;count(5);h,hx,hy,inside=back.height_gradient(x,y);dx=(back.height_gradient(x+eps,y)[0]-back.height_gradient(x-eps,y)[0])/(2*eps);dy=(back.height_gradient(x,y+eps)[0]-back.height_gradient(x,y-eps)[0])/(2*eps);error=float(max(abs(dx-hx),abs(dy-hy)));assert error<1e-7;errors.append(error)
count(2*x.size if hasattr(x,'size') else 2);assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
(OUT/'result.json').write_text(json.dumps({'status':'PASS_CIRCULAR_INTERFACE_NO_RAYS','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'height_footprint_points':points,'Hermite_gradient_FD_max':max(errors),'profile_sha256':digest,'profile_read_only_unchanged':True,'height_bound':back.maximum_height,'slope_bound':back.slope_bound,'rays_RGB_images_fits':0},indent=2)+'\n')
