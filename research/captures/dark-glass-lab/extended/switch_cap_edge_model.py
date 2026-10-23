"""Depth-dependent cap normal profile on the existing crowned footprint.

a_new(d,theta)=a_old(d,theta)+cos(theta)^2 sum_i b_i B_i(d/r).
The first two/three existing cubic spline bases vanish smoothly before the
interior. This separates cap/body curvature by depth; the archived scalar
cap gain forces the same relative change at all depths. All references share
one coefficient vector; no target position/color/feature masks enter the map.
This remains an empirical normal map, not a proven integrable optical solid.
"""
import hashlib,numpy as np
from scipy.interpolate import BSpline
from extended_fit import Study as Base,KNOTS
from switch_native_cache import NativeCachedStudy
class CapEdgeStudy(Base):
 def geometry_field(self,x,y,p):
  X,Y,d,J=super().geometry_field(x,y,p)
  b=p.get('cap_edge_profile',[])
  if not len(b):return X,Y,d,J
  xx,yy,half,r,(sd,nx,ny)=self.shape(x,y,p)
  B=BSpline.design_matrix(np.clip(d/r,0,1).ravel(),KNOTS,3).toarray()[:,:len(b)].reshape((*x.shape,len(b)))
  weight=nx*nx if half[0]>=half[1] else ny*ny
  extra=weight*(B@np.asarray(b))
  return X-extra*nx,Y-extra*ny,d,J
class CachedCapEdge(NativeCachedStudy):
 def geometry_field(self,x,y,p):
  clean={k:v for k,v in p.items() if k!='cap_edge_profile'}
  X,Y,d,J=super().geometry_field(x,y,clean)
  b=p.get('cap_edge_profile',[])
  if not len(b):return X,Y,d,J
  if x.size<=131072:
   key=(x.shape,hashlib.sha256(x.tobytes()+y.tobytes()).digest())
   _,_,_,nx,ny,B,weight,*_=self.templates[key];extra=weight*(B[...,:len(b)]@np.asarray(b))
  else:
   xx,yy,half,r,(sd,nx,ny)=self.shape(x,y,p);B=BSpline.design_matrix(np.clip(d/r,0,1).ravel(),KNOTS,3).toarray()[:,:len(b)].reshape((*x.shape,len(b)))
   weight=nx*nx if half[0]>=half[1] else ny*ny;extra=weight*(B@np.asarray(b))
  return X-extra*nx,Y-extra*ny,d,J
