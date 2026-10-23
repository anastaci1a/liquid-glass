"""Private exact geometry-template cache for fixed-shape native calibration."""
import hashlib,json
import numpy as np
from scipy.interpolate import BSpline
from extended_fit import Study as Base,KNOTS

FREE={'core_x','core_y',*[f'c{i}' for i in range(7)],'cap_normal_gain'}
class NativeCachedStudy(Base):
 def __init__(self,folder,parameters):
  super().__init__(folder);self.fixed=json.dumps({k:v for k,v in parameters.items() if k not in FREE},sort_keys=True);self.templates={};self.template_bytes=0
 def geometry_field(self,x,y,p):
  assert self.fixed==json.dumps({k:v for k,v in p.items() if k not in FREE},sort_keys=True),'Cache fixed geometry/material parameters changed'
  assert p['spline'] and not self.case.get('radial',False)
  if x.size>131072:return Base.geometry_field(self,x,y,p)
  key=(x.shape,hashlib.sha256(x.tobytes()+y.tobytes()).digest())
  if key not in self.templates:
   xx,yy,half,radius,(sd,nx,ny)=self.shape(x,y,p);d=np.maximum(-sd,0)
   basis=BSpline.design_matrix(np.clip(d/radius,0,1).ravel(),KNOTS,3).toarray()[:,:7].reshape((*x.shape,7))
   cap=nx*nx if half[0]>=half[1] else ny*ny
   u=np.clip(d/p['tangent_band'],0,1);v=1-u;exponent=p.get('tangent_exponent',4)
   W=v**exponent*(1+exponent*u);Wd=-exponent*(exponent+1)*u*v**(exponent-1)/p['tangent_band']
   W*=1-p.get('cap_tangent_fade',0)*cap
   tangent_pos=-ny*xx+nx*yy
   _,_,_,light=Base.geometry_field(self,x,y,p)
   template=(xx,yy,d,nx,ny,basis,cap,W,Wd,tangent_pos,light)
   self.template_bytes+=sum(q.nbytes for q in template)
   assert self.template_bytes<1_900_000_000,'Unexpected cache growth; do not exceed container memory'
   self.templates[key]=template
  xx,yy,d,nx,ny,basis,cap,W,Wd,tangent_pos,light=self.templates[key]
  a=basis@np.array([p[f'c{i}'] for i in range(7)])
  a*=1+p.get('cap_normal_gain',0)*cap
  X=(1-p['core_x'])*xx-a*nx+p['tangent']*W*tangent_pos*ny
  Y=(1-p['core_y'])*yy-a*ny-p['tangent']*W*tangent_pos*nx
  coupling=.5*p['coupling']*p['tangent']*Wd*xx*xx
  X-=coupling*nx;Y-=coupling*ny
  X+=p.get('shape_dx',0);Y+=p.get('shape_dy',0)
  return X,Y,d,light
