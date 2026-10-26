"""Smooth convex support shoulder correction with a true distance coordinate.

The outer support subtracts delta*sin(2 theta)^2 from an ellipse-plus-disk.
A smaller rolling disk leaves a strictly convex core, so actual distance
supplies the shared height coordinate and its gradient.
"""
from dataclasses import dataclass, field
import numpy as np
from spline_height_back import SplineFootprintBack

@dataclass(frozen=True)
class ShoulderCoreCoordinate:
    half: tuple
    original_radius: float
    shoulder: float
    counter: object = field(default=None, compare=False, repr=False)

    def __post_init__(self):
        h=tuple(float(v) for v in self.half)
        if len(h)!=2 or not np.isfinite([*h,self.original_radius,self.shoulder]).all():
            raise ValueError('Finite extents required')
        if min(h)<=self.original_radius or not 0<self.shoulder<self.original_radius/8:
            raise ValueError('Positive ellipse axes and rolling radius required')
        object.__setattr__(self,'half',h)
        object.__setattr__(self,'radius',float(self.original_radius-8*self.shoulder))

    def support(self,t):
        a,b=np.asarray(self.half)-self.original_radius
        c,s=np.cos(t),np.sin(t);v=a*a*c*c+b*b*s*s
        e=np.sqrt(v);u=(b*b-a*a)*s*c
        ep=u/e;epp=(b*b-a*a)*(c*c-s*s)/e-u*u/(e**3)
        d=self.shoulder
        return (e+8*d-d*np.sin(2*t)**2,
                ep-2*d*np.sin(4*t),epp-8*d*np.cos(4*t))

    def distance_gradient(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
        if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Finite positions required')
        if self.counter is not None:self.counter('coordinate_queries',x.size)
        u,v=np.abs(x),np.abs(y);lo=np.zeros_like(u);hi=np.full_like(u,np.pi/2)
        t=np.arctan2(v,u);active=np.ones_like(u,dtype=bool)
        for _ in range(64):
            if self.counter is not None:self.counter('projection_iteration_points',int(active.sum()))
            c,s=np.cos(t),np.sin(t);h,hp,hpp=self.support(t)
            f=-u*s+v*c-hp;dist=u*c+v*s-h
            done=(np.abs(f)<2e-13)|(hi-lo<2e-14)
            active &= ~done
            if not active.any():break
            lo=np.where(active&(f>0),t,lo);hi=np.where(active&(f<=0),t,hi)
            denom=u*c+v*s+hpp
            step=t+np.divide(f,denom,out=np.zeros_like(f),where=denom>0)
            proposal=np.where((denom>0)&(step>lo)&(step<hi),step,(lo+hi)/2)
            t=np.where(active,proposal,t)
        c,s=np.cos(t),np.sin(t);h,hp,_=self.support(t)
        dist=u*c+v*s-h;f=-u*s+v*c-hp
        exterior=dist>0
        if np.any(exterior&(np.abs(f)>2e-11)):
            raise ArithmeticError('Unresolved convex-core projection')
        return np.maximum(dist,0),np.where(exterior,c*np.sign(x),0),np.where(exterior,s*np.sign(y),0)

    def footprint(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
        d,nx,ny=self.distance_gradient(x,y);rho=d/self.radius
        poles=((np.abs(x)==self.half[0])&(y==0))|((x==0)&(np.abs(y)==self.half[1]))
        return np.where(poles,1.,rho),d*nx,d*ny

    def boundary_distance(self,x,y):
        d,nx,ny=self.distance_gradient(x,y)
        return d-self.radius,nx,ny

class ShoulderCoreSplineBack(SplineFootprintBack):
    def __init__(self,half,original_radius,shoulder,breaks,height_controls,counter=None):
        coordinate=ShoulderCoreCoordinate(tuple(half),original_radius,shoulder,counter)
        super().__init__(half,coordinate.radius,breaks,height_controls)
        self.coordinate=coordinate
