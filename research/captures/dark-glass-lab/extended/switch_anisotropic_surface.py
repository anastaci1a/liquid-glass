"""Declared biaxial quadratic back surface with one crowned quartic rim term.
No displacement painting: a single height and its derivative determine rays.
"""
import numpy as np
from crowned_footprint import field,longitudinal
from extended_fit import Study

def bounds(half,softness,bx,by,c,g,n=1.5,t0=.5):
    r=min(half);a=max(half);_,qd=longitudinal(np.asarray(a),a,r,softness)
    M=2*np.hypot(abs(bx)*half[0]/r,abs(by)*half[1]/r)+4*abs(c)*max(1,abs(float(qd)))
    terms=[bx*(half[0]/r)**2,by*(half[1]/r)**2,c]
    low=t0+sum(min(v,0) for v in terms);high=t0+sum(max(v,0) for v in terms)
    if n<1 or low<=0 or t0+g<=high:raise ValueError('Invalid IOR, thickness or background plane')
    critical=float('inf') if n==1 else 1/np.sqrt(n*n-1)
    if M>=critical:raise ValueError('Cannot guarantee subcritical slope')
    delta=np.arcsin(n*np.sin(np.arctan(M)))-np.arctan(M)
    return dict(max_slope=M,critical_slope=critical,minimum_thickness_over_r=low,maximum_thickness_over_r=high,reentry_bound=float(M*np.tan(delta)))

def mapping(x,y,half,softness,bx,by,c,g,n=1.5,t0=.5):
    report=bounds(half,softness,bx,by,c,g,n,t0)
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));r=min(half)
    T,gx,gy=field(x,y,half,softness);inside=T<=1
    # Inactive points are harmless placeholders, never clamped active rays.
    u=np.where(inside,T,0);xx=np.where(inside,x,0);yy=np.where(inside,y,0)
    h=r*(t0+bx*(xx/r)**2+by*(yy/r)**2+c*u*u)
    hx=2*bx*xx/r+2*c*r*u*gx;hy=2*by*yy/r+2*c*r*u*gy
    cos=1/np.sqrt(1+hx*hx+hy*hy);K=1-n*n*(1-cos*cos)
    if np.any(K<=0):raise ValueError('TIR')
    factor=(n*cos-np.sqrt(K))*cos;vx,vy=factor*hx,factor*hy;vz=-n+factor
    if np.any(vz>=0):raise ValueError('Wrong transmitted direction')
    travel=(r*(t0+g)-h)/(-vz)
    return np.where(inside,x+travel*vx,x),np.where(inside,y+travel*vy,y),dict(inside=inside,h=h,hx=hx,hy=hy,vx=vx,vy=vy,vz=vz,K=K,bounds=report)

class AnisotropicSurfaceStudy(Study):
    def geometry_field(self,x,y,p):
        _,_,d,J=super().geometry_field(x,y,p)
        xx,yy,half,_,_=self.shape(x,y,p)
        X,Y,_=mapping(xx,yy,half,p['crown_softness'],**p['physical_anisotropic_surface'])
        return X+p.get('shape_dx',0),Y+p.get('shape_dy',0),d,J
