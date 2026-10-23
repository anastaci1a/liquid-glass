"""Private local-normal Snell dispersion test, not a recovered lens solid.

Given the inherited green map F and a declared effective propagation gap g,
D=F(p)-p, delta=atan(|D|/g), alpha=atan2(sin(delta),n0-cos(delta)).
For channel index nc, delta_c=asin(nc*sin(alpha))-alpha;
F_c=p+g*tan(delta_c)*D/|D|. n0=1.5, R=n0-dn, B=n0+dn.
The inverse relation follows sin(alpha+delta)=n0*sin(alpha).
Only the subcritical branch is permitted. TIR proposals fail, never clip rays.
Normals inferred independently this way need not integrate to a surface; g is
an assumed constant effective gap, not measured Apple thickness. RGB channel
indices are samples, not a full spectral integral. No Fresnel/energy claim.
"""
import numpy as np
from extended_fit import Study as Base
from chromatic_transmission import apply as directional
class InvalidSnell(ValueError):pass

def ray_scale(radius,g,n0,nc,active):
 delta=np.arctan2(radius,g)
 if np.any(active&(np.cos(delta)<1/n0-1e-12)):raise InvalidSnell('Baseline exceeds subcritical inverse branch')
 alpha=np.arctan2(np.sin(delta),n0-np.cos(delta))
 argument=nc*np.sin(alpha)
 if np.any(active&(abs(argument)>=1)):raise InvalidSnell('Total internal reflection; no transmitted branch modeled')
 # Outside footprint the archived continuation is unchanged; do not assign a
 # physical surface there. Its ordinary output-blur convention is preserved.
 beta=np.arcsin(np.where(active,argument,0.))
 distance=g*np.tan(beta-alpha)
 return np.where(active,np.divide(distance,radius,out=np.ones_like(radius),where=radius>1e-12),1.)

class SnellStudy(Base):
 def field(self,x,y,p):
  q=p['snell_dispersion'];X,Y,d,J=self.geometry_field(x,y,p)
  *_,(sd,_,_)=self.shape(x,y,p);active=sd<=0
  sample=self.sample_field(X,Y,d,p);radius=np.hypot(X-x,Y-y)
  for c,sign in [(0,-1),(2,1)]:
   k=ray_scale(radius,q['gap'],q['n0'],q['n0']+sign*q['delta_n'],active)
   sample[...,c]=self.sample_field(x+k*(X-x),y+k*(Y-y),d,p)[...,c]
  if q['retain_directional']:sample=directional(self,p,x,y,sample)
  return sample,J
