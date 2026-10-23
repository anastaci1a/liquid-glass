"""One actual convex solid with quadratic front and frozen concave radial back."""
import numpy as np
class TwoGraphCircle:
 def __init__(self,back,front_sag):
  if front_sag<0 or not np.isfinite(front_sag):raise ValueError('Nonnegative finite actual front sag')
  self.back=back;self.maximum_height=back.maximum_height;self.slope_bound=max(back.slope_bound,2*front_sag);self.front_sag=float(front_sag);self.half_extents=np.array([1.,1.,(front_sag+back.maximum_height)/2]);self.center=np.array([0.,0.,(front_sag-back.maximum_height)/2])
 def front_height(self,x,y):
  r2=np.asarray(x)**2+np.asarray(y)**2;return self.front_sag*(1-r2),r2<1
 def boundary_mask(self,x,y):return np.hypot(x,y)==1
 def level_gradient(self,p):
  p=np.asarray(p,float);x,y,z=p[...,0],p[...,1],p[...,2];r2=x*x+y*y;h,hx,hy,_=self.back.height_gradient(x,y);f=self.front_sag*(1-r2)
  values=np.stack([z-f,-h-z,r2-1],-1);j=np.argmax(values,-1);ones=np.ones_like(x);zero=np.zeros_like(x)
  gradients=np.stack([np.stack([2*self.front_sag*x,2*self.front_sag*y,ones],-1),np.stack([-hx,-hy,-ones],-1),np.stack([2*x,2*y,zero],-1)],-2)
  return np.take_along_axis(values,j[...,None],-1)[...,0],np.take_along_axis(gradients,j[...,None,None],-2)[...,0,:]
 def section(self,x):
  x=np.asarray(x,float);h,_,_,inside=self.back.height_gradient(x,np.zeros_like(x));return self.front_sag*(1-x*x),-h,inside
