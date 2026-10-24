"""Actual positive Hermite back over the shared rounded footprint.

The curve is a physical height, never a source displacement. The factored basis
is algebraically the frozen inverse-design Hermite polynomial. Exact rational
Bernstein bounds describe that intended curve, not all floating-point errors.
"""
from fractions import Fraction
import numpy as np


class HermiteFootprintBack:
    def __init__(self, footprint_base, model):
        self.coordinate=footprint_base.coordinate;self.half=footprint_base.half;self.radius=footprint_base.radius
        self.r=np.asarray(model['radius_nodes'],float);self.h=np.asarray(model['heights'],float);self.m=np.asarray(model['derivatives'],float)
        if self.r.ndim!=1 or self.h.shape!=self.r.shape or self.m.shape!=self.r.shape or not np.isfinite([self.r,self.h,self.m]).all() or np.any(np.diff(self.r)<=0):
            raise ValueError('Finite ordered actual Hermite data required')
        if self.r[0]!=0 or self.r[-1]!=self.radius or self.m[0]!=0 or self.h[-1]!=0 or np.any(self.h[:-1]<=0):
            raise ValueError('Positive interior, exact zero edge and regular center required')
        fr=lambda x:Fraction.from_float(float(x));H=Fraction(0);M=Fraction(0)
        for i in range(len(self.r)-1):
            d=fr(self.r[i+1])-fr(self.r[i]);a,b=fr(self.h[i]),fr(self.h[i+1]);u,v=fr(self.m[i]),fr(self.m[i+1])
            controls=[a,a+d*u/3,b-d*v/3,b]
            if min(controls)<0:raise ValueError('Uncertified positive polynomial')
            H=max(H,*controls);M=max(M,*[abs(3*(controls[j+1]-controls[j])/d) for j in range(3)])
        def upper(value):
            x=float(value)
            return float(np.nextafter(x,np.inf)) if fr(x)<value else x
        self.maximum_height=upper(H);self.slope_bound=upper(M);self.bound_segments=len(self.r)-1
    def profile(self, r, derivative=False):
        x=np.asarray(r,float)
        if np.any((x<0)|(x>self.radius)):raise ValueError('Outside height-profile domain')
        j=np.clip(np.searchsorted(self.r,x,side='right')-1,0,len(self.r)-2);d=self.r[j+1]-self.r[j];t=(x-self.r[j])/d
        if derivative:
            return (-6*t*(1-t)*self.h[j]+6*t*(1-t)*self.h[j+1])/d+(1-t)*(1-3*t)*self.m[j]+t*(3*t-2)*self.m[j+1]
        return (1+2*t)*(1-t)**2*self.h[j]+t*(1-t)**2*d*self.m[j]+t*t*(3-2*t)*self.h[j+1]-t*t*(1-t)*d*self.m[j+1]
    def height_gradient(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));rho,qx,qy=self.coordinate.footprint(x,y);inside=rho<=1
        r=np.where(inside,rho*self.radius,self.radius);h=self.profile(r);hr=self.profile(r,True)
        factor=np.divide(hr,r,out=np.zeros_like(r),where=(r>0)&inside)
        return np.where(inside,h,0.),factor*qx,factor*qy,inside
    def boundary_mask(self,x,y):
        rho=self.coordinate.footprint(x,y)[0];h,_,_,inside=self.height_gradient(x,y)
        return (rho==1)|(inside&(h==0))
