"""Fixed primary-only controls for globally Lipschitz, nonconcave back heights."""
from pathlib import Path
import datetime,json
import numpy as np
from geometric_optics import trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'result.json').exists()
class PolynomialDisk:
 def __init__(self,kind,scale):
  self.kind=kind;self.scale=scale
  if kind=='redistributed':self.maximum_height=.12*scale;self.slope_bound=max(.08,.4*np.sqrt(.4/.96)-.32*np.sqrt(.4/.96)**3)*scale
  else:self.maximum_height=.1*((1+.1)**2/4)*scale;self.slope_bound=.22*scale
 def boundary_mask(self,x,y):return np.hypot(x,y)==1
 def height_gradient(self,x,y):
  u=x*x+y*y
  if self.kind=='redistributed':h=.04*(1-u)+.08*(1-u)**2;factor=-.08-.32*(1-u)
  else:h=.1*(1-u)*(.1+u);factor=.2*(.9-2*u)
  return self.scale*h,self.scale*factor*x,self.scale*factor*y,np.hypot(x,y)<=1
rows=[];rays=0;levels=0;arrays={}
for i,(kind,scale,index) in enumerate([('redistributed',1.,1.5),('redistributed',4.5,1.5),('annular',1.,1.5),('annular',1.,1.)]):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 s=PolynomialDisk(kind,scale);j=np.arange(129);r=np.sqrt(np.linspace(.001,.99,129));theta=j*np.pi*(3-np.sqrt(5));x=r*np.cos(theta);y=r*np.sin(theta);x[0]=y[0]=0;h,hx,hy,inside=s.height_gradient(x,y);levels+=len(x);q=trace_flat_front_orthographic(s,x,y,index,2.);rays+=len(x);assert q['complete'].all();assert np.hypot(hx,hy).max()<=s.slope_bound+1e-14
 # Independent Snell-angle formula is a comparator, not a rendering normal tweak.
 m=np.hypot(hx,hy);theta=np.arctan(m);phi=np.arcsin(index*np.sin(theta))-theta;factor=np.divide(np.sin(phi),m,out=np.zeros_like(m),where=m>0);d=np.stack([factor*hx,factor*hy,-np.cos(phi)],-1);rays+=len(x);np.testing.assert_allclose(d,q['exit_direction'],atol=8e-16,rtol=0)
 gamma=np.sqrt(1-(index*index-1)*s.slope_bound**2);t=np.linspace(0,1,65)[None,:]*q['path_length'][:,None];xx=x[:,None]+t*d[:,0,None];yy=y[:,None]+t*d[:,1,None];z=-h[:,None]+t*d[:,2,None];hh,_,_,within=s.height_gradient(xx,yy);levels+=xx.size;clearance=-z-hh;bound=t*gamma;valid=within&(t>0);gap=(clearance-bound)[valid];assert gap.min()>-1e-12
 # Finite differences check normals of the SAME polynomial, including rising annulus.
 e=1e-6;xp=s.height_gradient(x+e,y)[0];xm=s.height_gradient(x-e,y)[0];yp=s.height_gradient(x,y+e)[0];ym=s.height_gradient(x,y-e)[0];levels+=4*len(x);gradient_error=max(abs((xp-xm)/(2*e)-hx).max(),abs((yp-ym)/(2*e)-hy).max());assert gradient_error<1e-9
 if index==1:np.testing.assert_allclose(q['X'],x,atol=1e-15,rtol=0);np.testing.assert_allclose(q['Y'],y,atol=1e-15,rtol=0)
 arrays[f'{i}_start']=np.stack([x,y,-h],-1);arrays[f'{i}_direction']=d;arrays[f'{i}_source']=np.stack([q['X'],q['Y']],-1);arrays[f'{i}_clearance_margin']=np.where(within,clearance-bound,np.nan)
 rows.append(dict(kind=kind,scale=scale,index=index,maximum_height=s.maximum_height,global_slope_bound=s.slope_bound,certified_clearance_rate=gamma,checked_rays=len(x),gradient_max_error=float(gradient_error),sampled_clearance_excess_min=float(gap.min()),nonconcave_height=True))
 assert rays<=p['budgets']['fixture_comparator_rays'] and levels<=p['budgets']['height_level_evaluations']
np.savez_compressed(OUT/'controls.npz',**arrays);(OUT/'result.json').write_text(json.dumps(dict(status='PRIMARY_ONLY_CERTIFICATE_CONTROLS_PASS',records=rows,charged_fixture_comparator_rays=rays,height_level_evaluations=levels,RGB_queries=0,images=0,fits=0,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),limits=['Analytic proof supplies the global claim; sampled controls alone do not.','Does not certify multiply reflected paths or a curved front.','No Apple surface, visual improvement or source validity identified.']),indent=2)+'\n');print(json.dumps(rows),flush=True)
