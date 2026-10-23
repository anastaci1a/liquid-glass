"""Actual nonconcave back over the existing frozen rounded footprint.

Uses the shared annular scalar height and harmonic crown. Only primary normal
front transmission is certified. Do not pass this nonconvex solid to the convex
multiple-reflection boundary tracer.
"""
import numpy as np
from annular_profile import annular_level_profile
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from geometric_optics import harmonic_cap

class RaisedPerimeterRoundedBack:
    def __init__(self,half,radius,depth=.4,core_ratio=.1,crown_depth=.4,isotropic_fixture=False,cap_join_width=0.):
        self.coordinate=RoundedRectangleHarmonicBack(tuple(half),radius,isotropic_fixture=isotropic_fixture,cap_join_width=cap_join_width)
        annular_level_profile(0.,depth,core_ratio)
        if not np.isfinite(crown_depth) or crown_depth<=0:raise ValueError('Positive crown height required')
        self.half=tuple(half);self.radius=float(radius);self.depth=float(depth);self.core_ratio=float(core_ratio);self.crown_depth=float(crown_depth);self.isotropic_fixture=isotropic_fixture
    @property
    def maximum_height(self):
        first=self.depth*(1+self.core_ratio)**2/4
        return first*self.crown_depth/(first+self.crown_depth)
    @property
    def slope_bound(self):
        return max(2*self.depth*(1+self.core_ratio)/self.radius,2*self.crown_depth/(self.radius if self.isotropic_fixture else self.half[0]))
    def height_gradient(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));rho,qx,qy=self.coordinate.footprint(x,y);inside=rho<=1;t=np.where(inside,rho*rho,1.)
        h1,hT,_=annular_level_profile(t,self.depth,self.core_ratio);gx1=2*hT*qx/self.radius**2;gy1=2*hT*qy/self.radius**2
        if self.isotropic_fixture:
            h2=self.crown_depth*(1-t);gx2=-2*self.crown_depth*x/self.radius**2;gy2=-2*self.crown_depth*y/self.radius**2
        else:
            h2=np.where(inside,self.crown_depth*(1-(x/self.half[0])**2),0.);gx2=-2*self.crown_depth*x/self.half[0]**2;gy2=np.zeros_like(y)
        h,w1,w2=harmonic_cap(h1,h2)
        return h,w1*gx1+w2*gx2,w1*gy1+w2*gy2,inside
    def boundary_mask(self,x,y):
        rho=self.coordinate.footprint(x,y)[0];h,_,_,inside=self.height_gradient(x,y)
        return (rho==1)|(inside&(h==0))
    def section(self,v,axis='x'):
        v=np.asarray(v,float);zero=np.zeros_like(v)
        if axis=='x':x,y=v,zero
        elif axis=='y':x,y=zero,v
        else:raise ValueError('Section x/y required')
        h,hx,hy,inside=self.height_gradient(x,y)
        return dict(front=np.stack([x,y,zero],-1),back=np.where(inside[...,None],np.stack([x,y,-h],-1),np.nan),inside=inside,gradient=np.stack([hx,hy],-1),boundary_unresolved=self.boundary_mask(x,y))
