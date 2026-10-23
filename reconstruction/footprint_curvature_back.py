"""One concave perimeter height, integrated from nonnegative curvature.

The existing rounded coordinate supplies shape only. Height, its gradient and
all traced normals come from the same existing RadialCurvatureBack polynomial.
"""
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from geometric_optics import RadialCurvatureBack

class FootprintCurvatureBack:
    def __init__(self,half,radius,knots,curvature,cap_join_width=0.):
        self.coordinate=RoundedRectangleHarmonicBack(tuple(half),radius,cap_join_width=cap_join_width)
        self.profile=RadialCurvatureBack(knots,curvature);self.half=tuple(half);self.radius=float(radius)
    @property
    def maximum_height(self):return self.profile.maximum_height
    @property
    def slope_bound(self):return self.profile.slope_bound/self.radius
    def height_gradient(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));rho,qx,qy=self.coordinate.footprint(x,y);inside=rho<=1
        h,hr=self.profile.radial_profile(np.where(inside,rho,1));factor=np.divide(hr,rho,out=np.zeros_like(rho),where=(rho>0)&inside)/self.radius**2
        return np.where(inside,h,0),factor*qx,factor*qy,inside
    def boundary_mask(self,x,y):
        rho=self.coordinate.footprint(x,y)[0];h,_,_,inside=self.height_gradient(x,y);return (rho==1)|(inside&(h==0))
    def section(self,v,axis='x'):
        v=np.asarray(v,float);zero=np.zeros_like(v)
        if axis=='x':x,y=v,zero
        elif axis=='y':x,y=zero,v
        else:raise ValueError('Section x/y required')
        h,hx,hy,inside=self.height_gradient(x,y)
        return dict(front=np.stack([x,y,zero],-1),back=np.where(inside[...,None],np.stack([x,y,-h],-1),np.nan),inside=inside,gradient=np.stack([hx,hy],-1))
