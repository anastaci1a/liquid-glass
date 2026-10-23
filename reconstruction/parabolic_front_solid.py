"""Certified rounded-footprint solid with an actual cylindrical front.

Coordinates, height, intersections, normals and sections describe one solid.
There is no source lookup, image warp, lighting or fitted normal field here.
"""
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack

class ParabolicFrontHeightSolid:
    def __init__(self,back,front_depth=0.,front_axis=0):
        if not isinstance(back,RoundedRectangleHarmonicBack) or not np.isfinite(front_depth) or front_depth<0 or front_axis not in (0,1):raise ValueError('Certified rounded back, nonnegative front depth and axis0/1 required')
        self.back=back;self.front_depth=float(front_depth);self.front_axis=front_axis
        self.half_extents=np.array([*back.half,(self.front_depth+back.maximum_height)/2])
        self.center=np.array([0.,0.,(self.front_depth-back.maximum_height)/2])
        self.level_point_evaluations=0;self.height_point_evaluations=0;self.maximum_level_points=None
    def _back(self,x,y):
        self.height_point_evaluations+=np.broadcast_arrays(x,y)[0].size
        return self.back.height_gradient(x,y)
    def _front(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));v=(x,y)[self.front_axis];a=self.back.half[self.front_axis]
        h=self.front_depth*(1-(v/a)**2);derivative=-2*self.front_depth*v/a**2;zero=np.zeros_like(x)
        return h,derivative if self.front_axis==0 else zero,derivative if self.front_axis==1 else zero
    def _fields(self,p):
        p=np.asarray(p,float)
        if p.shape[-1]!=3 or not np.isfinite(p).all():raise ValueError('Finite XYZ points required')
        count=p[...,0].size
        if self.maximum_level_points is not None and self.level_point_evaluations+count>self.maximum_level_points:raise RuntimeError('Declared level-point budget would be exceeded')
        self.level_point_evaluations+=count;x,y,z=np.moveaxis(p,-1,0);h,hx,hy,_=self._back(x,y);f,fx,fy=self._front(x,y);rho,qx,qy=self.back.footprint(x,y)
        values=np.stack([z-f,-z-h,rho*rho-1],-1);ones=np.ones_like(x);zero=np.zeros_like(x)
        gradients=np.stack([np.stack([-fx,-fy,ones],-1),np.stack([-hx,-hy,-ones],-1),np.stack([2*qx/self.back.radius**2,2*qy/self.back.radius**2,zero],-1)],-2)
        return values,gradients
    def level_gradient(self,p):
        v,g=self._fields(p);j=np.argmax(v,axis=-1)
        return np.take_along_axis(v,j[...,None],-1)[...,0],np.take_along_axis(g,j[...,None,None],-2)[...,0,:]
    def front_height(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));return self._front(x,y)[0],self.back.footprint(x,y)[0]<1
    def boundary_mask(self,x,y):
        rho=self.back.footprint(x,y)[0];h=self._back(x,y)[0];f=self._front(x,y)[0]
        return (rho==1)|((rho<1)&(f+h==0))
    def nonsmooth_mask(self,p,uncertainty):
        v,_=self._fields(p);ordered=np.sort(v,axis=-1);bound=max(1+self.back.slope_bound,1+2*self.front_depth/self.back.half[self.front_axis],4/self.back.radius)
        return ordered[...,-1]-ordered[...,-2]<=2*np.asarray(uncertainty)*bound
    def section(self,v,axis='x'):
        v=np.asarray(v,float);zero=np.zeros_like(v)
        if axis=='x':x,y=v,zero
        elif axis=='y':x,y=zero,v
        else:raise ValueError('Section axis x/y required')
        h,_,_,inside=self._back(x,y);f,_,_=self._front(x,y)
        return dict(front=np.where(inside[...,None],np.stack([x,y,f],-1),np.nan),back=np.where(inside[...,None],np.stack([x,y,-h],-1),np.nan),inside=inside)
