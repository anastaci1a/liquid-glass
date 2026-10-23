"""One bounded geometry checkpoint. Imports pinned shared transport unchanged."""
import sys,json,time,hashlib
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent; R=P.parents[2];sys.path.insert(0,str(R/'reconstruction'))
from harmonic_crowned_back import HarmonicCrownedBack
from geometric_optics import HarmonicCircularBack,trace_flat_front_orthographic
class PosedSurface:
 def __init__(self,base,dx,dy):self.base=base;self.dx=dx;self.dy=dy;self.maximum_height=base.maximum_height;self.slope_bound=base.slope_bound
 def height_gradient(self,x,y):return self.base.height_gradient(x-self.dx,y-self.dy)
 def boundary_mask(self,x,y):return self.base.boundary_mask(x-self.dx,y-self.dy)
 def section(self,v,axis='x'):return self.base.section(v,axis)
count=0
def trace(s,x,y,n=1.5,D=2):
 global count
 count+=np.broadcast_arrays(x,y)[0].size
 assert count<=10000
 return trace_flat_front_orthographic(s,x,y,n,D)
def main():
 schedule=json.loads((P/'execution-schedule.json').read_text());end=__import__('datetime').datetime.fromisoformat(schedule['subpass']['geometry_checkpoint_deadline'].replace('Z','+00:00')).timestamp();assert time.time()<end
 proposal=json.loads((P/'proposal.json').read_text());out=P/'baseline';assert not (out/'checkpoint.json').exists();rows=[];arrays={}
 for pin in proposal['code']:assert hashlib.sha256((R/pin['file']).read_bytes()).hexdigest()==pin['sha256'],pin['file']
 for case in proposal['cases']:
  a,b=case['corrected_half_over_L'];s=HarmonicCrownedBack((a,b),.15,.4,.08);yy,xx=np.meshgrid(np.linspace(-.991*b,.991*b,41),np.linspace(-.993*a,.993*a,41),indexing='ij');q=trace(s,xx,yy);assert q['complete'].all();mirror=trace(s,-xx,yy);assert np.allclose(mirror['X'],-q['X'],atol=1e-13,rtol=0);assert np.allclose(mirror['Y'],q['Y'],atol=1e-13,rtol=0)
  h,hx,hy,inside=s.height_gradient(xx,yy);e=1e-6;f=(s.height_gradient(xx+e,yy)[0]-s.height_gradient(xx-e,yy)[0])/(2*e);g=(s.height_gradient(xx,yy+e)[0]-s.height_gradient(xx,yy-e)[0])/(2*e);safe=inside&(h>1e-5);err=max(abs(f[safe]-hx[safe]).max(),abs(g[safe]-hy[safe]).max());assert err<1e-7;assert s.slope_bound<1/np.sqrt(1.5**2-1);assert np.hypot(hx[inside],hy[inside]).max()<=s.slope_bound
  dx=(case['corrected_center'][0]-case['center'][0])/case['L'];dy=(case['corrected_center'][1]-case['center'][1])/case['L'];posed=PosedSurface(s,dx,dy);x=xx.ravel()[:10];y=yy.ravel()[:10];qq=trace(posed,x+dx,y+dy);assert np.allclose(qq['X'],q['X'].ravel()[:10]+dx,atol=1e-13)
  # Scaling every length, including depth and background, preserves the normalized path.
  scaled=HarmonicCrownedBack((2*a,2*b),.3,.8,.08);qs=trace(scaled,2*x,2*y,D=4);assert np.allclose(qs['X']/2,q['X'].ravel()[:10],atol=1e-13)
  tangent=trace(s,np.array([a,-a]),np.zeros(2));assert not tangent['complete'].any();assert np.isnan(tangent['X']).all()
  arrays[case['key']+'_X']=q['X'];arrays[case['key']+'_Y']=q['Y'];arrays[case['key']+'_inside']=inside
  rows.append(dict(case=case['key'],half=[a,b],slope_bound=s.slope_bound,maximum_height=s.maximum_height,finite_difference_error=float(err),minimum_discriminant=float(q['discriminant'].min()),complete=True,exact_poles_unresolved=True,source_queries=0))
 y,x=np.mgrid[-.91:.92:17j,-.93:.94:17j];a=trace(HarmonicCrownedBack((1.,1.),.15,.4,.08,True),x,y);b=trace(HarmonicCircularBack(.15,.4),x,y);error=max(float(np.max(abs(a[k]-b[k]))) for k in ['X','Y']);assert error<1e-13
 assert time.time()<end
 np.savez_compressed(out/'geometry-checkpoint.npz',**arrays)
 result=dict(status='PASS_GEOMETRY_CHECKPOINT',rows=rows,circle_fixture_max_difference=error,charged_fixture_comparator_rays=count,remaining_fixture_budget=10000-count,finished_utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),fits=0,native_rays=0,images=0)
 (out/'checkpoint.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
