"""One prescribed raised-perimeter back; shared primary transport only."""
from dataclasses import dataclass
import numpy as np
from crowned_bevel import CrownedBevel
from geometric_optics import harmonic_cap
height_evaluations=0
@dataclass(frozen=True)
class RaisedBack:
 half:tuple
 softness:float=.08
 radial_fixture:bool=False
 length_scale:float=1.
 @property
 def base(self):return CrownedBevel(self.half,.4*self.length_scale,self.softness,self.radial_fixture)
 @property
 def maximum_height(self):return self.length_scale*.121*.4/(.121+.4)
 @property
 def slope_bound(self):return max(.88*self.length_scale*self.base.rho_gradient_bound,.8*self.length_scale/(min(self.half) if self.radial_fixture else self.half[0]))
 def boundary_mask(self,x,y):return self.base.boundary_mask(x,y)
 def height_gradient(self,x,y):
  global height_evaluations
  x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));height_evaluations+=x.size
  if height_evaluations>100000:raise RuntimeError('Height evaluation cap')
  if self.radial_fixture:
   b=min(self.half);rho=np.hypot(x,y)/b;T=rho*rho;tx=2*x/(b*b);ty=2*y/(b*b);inside=rho<=1
  else:T,tx,ty=self.base.level(x,y);inside=T<=1
  c=.4*self.length_scale;h1=np.where(inside,c*(1-T)*(.1+T),0.);f=c*(.9-2*T);gx1=f*tx;gy1=f*ty
  if self.radial_fixture:h2=c*np.maximum(1-T,0.);gx2=-c*tx;gy2=-c*ty
  else:
   a=self.half[0];h2=np.where(inside,c*(1-(x/a)**2),0.);gx2=-2*c*x/(a*a);gy2=np.zeros_like(y)
  h,w1,w2=harmonic_cap(h1,h2)
  return h,w1*gx1+w2*gx2,w1*gy1+w2*gy2,inside
 def section(self,v,axis='x'):
  zero=np.zeros_like(v);x,y=(v,zero) if axis=='x' else (zero,v);h,hx,hy,inside=self.height_gradient(x,y)
  return dict(front=np.stack([x,y,zero],-1),back=np.where(inside[...,None],np.stack([x,y,-h],-1),np.nan),gradient=np.stack([hx,hy],-1),inside=inside,boundary_unresolved=self.boundary_mask(x,y))
