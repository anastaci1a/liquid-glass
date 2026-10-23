"""Exact single-transmission geometry for an explicitly specified flat-front solid.

See physical-back-surface/model.md. Current material is still empirical.
"""
import numpy as np
from crowned_footprint import field,longitudinal
from extended_fit import Study

def bounds(half,softness,b,c,g,n,t0=.2):
    a,r=max(half),min(half);_,qd=longitudinal(np.asarray(a),a,r,softness)
    M=2*max(abs(b),abs(b+2*c))*max(1,abs(float(qd)))
    points=[0.,1.]
    if c and 0<-b/(2*c)<1:points.append(-b/(2*c))
    heights=[t0+b*u+c*u*u for u in points]
    if n<1 or min(heights)<=0 or t0+g<=max(heights):raise ValueError('Invalid IOR, thickness or background plane')
    critical=float('inf') if n==1 else 1/np.sqrt(n*n-1)
    if M>=critical:raise ValueError('Global slope does not guarantee a subcritical transmitted branch')
    delta=np.arcsin(n*np.sin(np.arctan(M)))-np.arctan(M)
    return dict(max_slope=M,critical_slope=critical,minimum_thickness_over_r=min(heights),maximum_thickness_over_r=max(heights),maximum_exit_tilt=float(delta),reentry_bound=float(M*np.tan(delta)))

def mapping(x,y,half,softness,b,c,g,n=1.5,t0=.2):
    report=bounds(half,softness,b,c,g,n,t0)
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));r=min(half)
    T,gx,gy=field(x,y,half,softness);inside=T<=1
    u=np.clip(T,0,1);h=r*(t0+b*u+c*u*u);hx=r*(b+2*c*u)*gx;hy=r*(b+2*c*u)*gy
    cos=1/np.sqrt(1+hx*hx+hy*hy);K=1-n*n*(1-cos*cos)
    if np.any(inside&(K<=0)):raise ValueError('TIR in actual active ray')
    root=np.sqrt(np.where(inside,K,1.));factor=(n*cos-root)*cos
    vx,vy=factor*hx,factor*hy;vz=-n+factor
    if np.any(inside&(vz>=0)):raise ValueError('Transmitted ray does not reach backdrop')
    travel=(r*(t0+g)-h)/np.where(inside,-vz,1.)
    X=np.where(inside,x+travel*vx,x);Y=np.where(inside,y+travel*vy,y)
    return X,Y,dict(inside=inside,h=h,hx=hx,hy=hy,vx=vx,vy=vy,vz=vz,K=K,bounds=report)

class BackSurfaceStudy(Study):
    def geometry_field(self,x,y,p):
        _,_,d,J=super().geometry_field(x,y,p)
        q=p['physical_back_surface'];xx,yy,half,_,_=self.shape(x,y,p)
        X,Y,_=mapping(xx,yy,half,p['crown_softness'],**q)
        return X+p.get('shape_dx',0),Y+p.get('shape_dy',0),d,J
