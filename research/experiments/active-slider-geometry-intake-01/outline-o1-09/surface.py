"""Private closed-solid protocol for unchanged H1. Shared transport is not copied."""
import numpy as np
from harmonic_crowned_back import HarmonicCrownedBack
from crowned_footprint import longitudinal
class Budget:
 def __init__(self):self.graph=0;self.fixture_points=0;self.fixture=True;self.events=0;self.calls={}
 def charge(self,n,kind,weight=20,fixture=True):
  n=int(n)
  if self.graph+weight*n>3000000:raise RuntimeError('Graph cap would be exceeded')
  if self.fixture and fixture and self.fixture_points+n>2048:raise RuntimeError('Fixture cap would be exceeded')
  self.graph+=weight*n;self.calls[kind]=self.calls.get(kind,0)+n
  if self.fixture and fixture:self.fixture_points+=n
 def event(self,n):
  if self.events+n>4096:raise RuntimeError('Interface cap would be exceeded')
  self.events+=n
 def record(self):return dict(combined_graph_evaluations=self.graph,fixture_level_points=self.fixture_points,interface_encounters=self.events,calls=self.calls,graph_limit=3000000,fixture_limit=2048,interface_limit=4096)
class ClosedH1:
 def __init__(self,half,dx,dy,budget,scale=1.):
  self.budget=budget;self.scale=scale;self.half=np.asarray(half,float)*scale;self.dx=dx*scale;self.dy=dy*scale;self.back=HarmonicCrownedBack(tuple(self.half),.15*scale,.4*scale,.08)
  budget.charge(1,'initial_bounds',20,False);self.H=self.back.maximum_height;self.M=self.back.slope_bound;self.half_extents=np.array([*self.half,self.H/2]);self.center=np.array([self.dx,self.dy,-self.H/2])
 def geometry(self,x,y,kind='geometry'):
  x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));self.budget.charge(x.size,kind);xx=x-self.dx;yy=y-self.dy;h,hx,hy,inside=self.back.height_gradient(xx,yy);T,tx,ty=self.back.base.level(xx,yy);return h,hx,hy,T,tx,ty,inside
 def constraints(self,p,kind):
  p=np.asarray(p,float);h,hx,hy,T,tx,ty,inside=self.geometry(p[...,0],p[...,1],kind);z=p[...,2];values=np.stack([z,-z-h,T-1],-1);one=np.ones_like(z);zero=np.zeros_like(z);grad=np.stack([np.stack([zero,zero,one],-1),np.stack([-hx,-hy,-one],-1),np.stack([tx,ty,zero],-1)],-2);return values,grad,h,inside
 def level_gradient(self,p):
  values,grad,h,inside=self.constraints(p,'level_gradient');j=np.argmax(values,-1);F=np.take_along_axis(values,j[...,None],-1)[...,0];G=np.take_along_axis(grad,j[...,None,None],-2)[...,0,:];crease=(F==0)&((values==0).sum(-1)>1);return F,np.where(crease[...,None],np.nan,G)
 def front_height(self,x,y):
  h,_,_,T,_,_,_=self.geometry(x,y,'front_height');return np.zeros_like(h),(T<1)&(h>0)
 def boundary_mask(self,x,y):
  h,_,_,T,_,_,inside=self.geometry(x,y,'boundary_mask');return (T==1)|(inside&(h==0))
 def nonsmooth_mask(self,p,uncertainty):
  p=np.asarray(p,float);u=np.broadcast_to(np.asarray(uncertainty,float),p.shape[:-1]);assert np.isfinite(u).all() and (u>=0).all();values,_,h,inside=self.constraints(p,'nonsmooth_mask')
  # The bracket is a spatial uncertainty, not a fitted boundary band.
  a,b=self.half;self.budget.charge(u.size,'longitudinal_bracket_bound',1,False);q,qd=longitudinal(a+u,a,b,.08);LT=2*np.hypot(q*qd,b+u)/(b*b);bounds=np.stack([np.ones_like(u),np.full_like(u,np.sqrt(1+self.M*self.M)),LT],-1)*u[...,None];near=np.abs(values)<=bounds
  return (near.sum(-1)>=2)|((h==0)&inside&(np.abs(p[...,2])<=u))
