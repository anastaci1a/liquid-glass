"""Curved-front, flat-back orthographic lens; exact two-interface ray geometry.
Top h/r=(1-T)*(t+bx*(x/r)^2+by*(y/r)^2), bottom z=0,
background z=-g*r. Boundary thickness vanishes. No target-defined surface.
"""
import numpy as np
from crowned_footprint import field,longitudinal
from extended_fit import Study

def bounds(half,softness,t,bx,by,g,n=1.5,edge_power=1):
    if edge_power not in (1,2,3):raise ValueError('Use declared integer edge order1,2,3')
    r=min(half);a=max(half);_,qd=longitudinal(np.asarray(a),a,r,softness)
    terms=[bx*(half[0]/r)**2,by*(half[1]/r)**2]
    lo=t+sum(min(v,0) for v in terms);hi=t+sum(max(v,0) for v in terms)
    if n<1 or lo<=0 or g<=0:raise ValueError('Invalid height, IOR or background gap')
    M=2*edge_power*max(1,abs(float(qd)))*hi+2*np.hypot(abs(bx)*half[0]/r,abs(by)*half[1]/r)
    theta=np.arctan(M);delta=theta-np.arcsin(np.sin(theta)/n)
    clearance=M*np.tan(delta);back_argument=n*np.sin(delta)
    if clearance>=1 or back_argument>=1:raise ValueError('No guaranteed top clearance or transmitted bottom branch')
    return dict(max_slope=M,minimum_height_factor=lo,maximum_height_factor=hi,internal_tilt_bound=float(delta),top_clearance_bound=float(clearance),bottom_snell_argument_bound=float(back_argument))

def mapping(x,y,half,softness,t,bx,by,g,n=1.5,edge_power=1):
    report=bounds(half,softness,t,bx,by,g,n,edge_power)
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));r=min(half)
    T,gx,gy=field(x,y,half,softness);inside=T<=1
    xx=np.where(inside,x,0);yy=np.where(inside,y,0);u=np.where(inside,T,1)
    P=t+bx*(xx/r)**2+by*(yy/r)**2;v=(1-u)**edge_power;vd=edge_power*(1-u)**(edge_power-1);h=r*v*P
    hx=np.where(inside,-r*gx*P*vd+v*2*bx*xx/r,0);hy=np.where(inside,-r*gy*P*vd+v*2*by*yy/r,0)
    cos=1/np.sqrt(1+hx*hx+hy*hy);eta=1/n;root=np.sqrt(1-eta*eta*(1-cos*cos));factor=(root-eta*cos)*cos
    vx,vy=factor*hx,factor*hy;vz=-eta-factor
    x1,y1=x+h*vx/(-vz),y+h*vy/(-vz)
    tb=field(x1,y1,half,softness)[0]
    if np.any(inside&(tb>1+1e-10)):raise ValueError('Bottom hit outside lens footprint')
    wx,wy=n*vx,n*vy;K=1-wx*wx-wy*wy
    if np.any(K<=0):raise ValueError('TIR at bottom; no transmitted continuation')
    wz=-np.sqrt(K);X=x1+g*r*wx/(-wz);Y=y1+g*r*wy/(-wz)
    return np.where(inside,X,x),np.where(inside,Y,y),dict(inside=inside,h=h,hx=hx,hy=hy,vx=vx,vy=vy,vz=vz,x1=x1,y1=y1,wx=wx,wy=wy,wz=wz,bounds=report)

class FrontSurfaceStudy(Study):
    def geometry_field(self,x,y,p):
        _,_,d,J=super().geometry_field(x,y,p)
        xx,yy,half,_,_=self.shape(x,y,p)
        X,Y,_=mapping(xx,yy,half,p['crown_softness'],**p['physical_front_surface'])
        return X+p.get('shape_dx',0),Y+p.get('shape_dy',0),d,J
