"""Element adapter only: actual concave back over the frozen rounded rectangle.

No image map, source lookup, independent normals or material. Coordinates use
the ORIGINAL case L; frozen half/radius deltas are lengths in that same unit.
"""
from dataclasses import dataclass
import numpy as np
from geometric_optics import harmonic_cap,bevel_profile

@dataclass(frozen=True)
class ExpandedHarmonicBack:
    half: tuple
    radius: float
    depth: float=.15
    crown_depth: float=.4
    power: float=3.
    isotropic_fixture: bool=False

    def __post_init__(self):
        if len(self.half)!=2 or not np.isfinite([*self.half,self.radius,self.depth,self.crown_depth,self.power]).all():raise ValueError('Finite parameters required')
        if min(self.half)<=0 or not 0<self.radius<=min(self.half) or min(self.depth,self.crown_depth)<=0 or self.power<3:raise ValueError('Invalid convex cap/rounded footprint')
        if self.isotropic_fixture and not self.half[0]==self.half[1]==self.radius:raise ValueError('Isotropic circle fixture requires equal axes and radius')

    @property
    def maximum_height(self):return self.depth*self.crown_depth/(self.depth+self.crown_depth)

    @property
    def slope_bound(self):
        quadratic=2*self.crown_depth/(self.radius if self.isotropic_fixture else self.half[0])
        return max(self.power*self.depth/self.radius,quadratic)

    def footprint(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
        if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Finite geometry points required')
        qx=np.maximum(abs(x)-(self.half[0]-self.radius),0)
        qy=np.maximum(abs(y)-(self.half[1]-self.radius),0)
        rho=np.hypot(qx,qy)/self.radius
        return rho,qx*np.sign(x),qy*np.sign(y)

    def boundary_mask(self,x,y):return self.footprint(x,y)[0]==1

    def height_gradient(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));rho,qx,qy=self.footprint(x,y);inside=rho<=1
        h1,hr,_=bevel_profile(np.where(inside,rho,1),0.,self.depth,self.power,0.)
        factor=np.divide(hr,rho,out=np.zeros_like(rho),where=(rho>0)&inside)/(self.radius*self.radius)
        g1x,g1y=factor*qx,factor*qy
        if self.isotropic_fixture:
            h2=self.crown_depth*np.maximum(1-rho*rho,0)
            g2x=-2*self.crown_depth*x/self.radius**2;g2y=-2*self.crown_depth*y/self.radius**2
        else:
            h2=np.where(inside,self.crown_depth*(1-(x/self.half[0])**2),0.)
            g2x=-2*self.crown_depth*x/self.half[0]**2;g2y=np.zeros_like(y)
        h,w1,w2=harmonic_cap(h1,h2)
        return h,w1*g1x+w2*g2x,w1*g1y+w2*g2y,inside

    def section(self,v,axis='x'):
        v=np.asarray(v,float);zero=np.zeros_like(v)
        if axis=='x':x,y=v,zero
        elif axis=='y':x,y=zero,v
        else:raise ValueError('Axis x/y required')
        h,hx,hy,inside=self.height_gradient(x,y)
        return dict(front=np.stack([x,y,zero],-1),back=np.where(inside[...,None],np.stack([x,y,-h],-1),np.nan),height_gradient=np.stack([hx,hy],-1),inside=inside,boundary_unresolved=self.boundary_mask(x,y))
