"""Nonnegative actual spline height over the existing rounded footprint.

Control values are surface heights, never image displacements. Nonnegative
B-spline bases certify height positivity; derivative control values bound the
actual slope globally. Only the flat-front primary certificate applies.
"""
import numpy as np
from scipy.interpolate import BSpline
from rounded_rectangle_back import RoundedRectangleHarmonicBack
class SplineFootprintBack:
    def __init__(self,half,radius,breaks,height_controls,cap_join_width=0.):
        self.coordinate=RoundedRectangleHarmonicBack(tuple(half),radius,cap_join_width=cap_join_width);self.half=tuple(half);self.radius=float(radius)
        b=np.array(breaks,float,copy=True);c=np.array(height_controls,float,copy=True)
        if b.ndim!=1 or len(b)<2 or not np.isfinite(b).all() or b[0]!=0 or b[-1]!=1 or np.any(np.diff(b)<=0):raise ValueError('Ordered finite normalized breaks from zero to one required')
        t=np.r_[np.repeat(b[0],3),b,np.repeat(b[-1],3)]
        if c.shape!=(len(t)-4,) or not np.isfinite(c).all() or np.any(c[:-1]<=0) or c[-1]!=0 or c[0]!=c[1]:raise ValueError('Positive interior height controls, zero edge and exact zero center slope required')
        derivative=3*np.diff(c)/(t[4:4+len(c)-1]-t[1:1+len(c)-1])
        self.maximum_height=float(c.max());self.slope_bound=float(np.max(abs(derivative))/self.radius)
        self.profile=BSpline(t,c,3,extrapolate=False);self.radial_derivative=self.profile.derivative();self.breaks=b;self.height_controls=c
        self.breaks.flags.writeable=False;self.height_controls.flags.writeable=False
    def height_gradient(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));rho,qx,qy=self.coordinate.footprint(x,y);inside=rho<=1;r=np.where(inside,rho,1.);h=self.profile(r);hr=self.radial_derivative(r);factor=np.divide(hr,rho,out=np.zeros_like(rho),where=(rho>0)&inside)/self.radius**2
        return np.where(inside,h,0.),factor*qx,factor*qy,inside
    def boundary_mask(self,x,y):
        rho=self.coordinate.footprint(x,y)[0];h,_,_,inside=self.height_gradient(x,y)
        return (rho==1)|(inside&(h==0))
    def section(self,v,axis='x'):
        v=np.asarray(v,float);zero=np.zeros_like(v)
        if axis=='x':x,y=v,zero
        elif axis=='y':x,y=zero,v
        else:raise ValueError('Section x/y required')
        h,hx,hy,inside=self.height_gradient(x,y)
        return dict(front=np.stack([x,y,zero],-1),back=np.where(inside[...,None],np.stack([x,y,-h],-1),np.nan),inside=inside,gradient=np.stack([hx,hy],-1))
