"""Private compact core-potential addition, not an integrable TOTAL lens map.

Psi=.5*(kx*x^2+ky*y^2)*S(d/w), addition=-grad(Psi).
S is quintic smoothstep; d is the crowned boundary coordinate, with its actual
analytic gradient. The C2 potential adds a C1 map; the inherited map remains
empirical. One shared pair of coefficients, fixed w=.30*minor-half, no target
coordinates. At depth>=w this is uniform central anisotropic scaling; at the
outer boundary it adds zero value/first derivative, leaving rim rays unchanged.
This is distinct from replacing/projecting the entire prior map onto a potential.
"""
import numpy as np
from crowned_footprint import field,longitudinal
from extended_fit import Study

def potential_terms(x,y,half,softness,coefficients,width):
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));k=np.asarray(coefficients,float)
    assert k.shape==(2,) and np.isfinite(k).all() and 0<width<min(half)
    T,gx,gy=field(x,y,half,softness);root=np.sqrt(np.maximum(T,0));d=min(half)*(1-root)
    factor=np.divide(-min(half),2*root,out=np.zeros_like(root),where=root>1e-14)
    dx,dy=factor*gx,factor*gy
    u=np.clip(d/width,0,1);S=u**3*(10+u*(-15+6*u));Sp=30*u*u*(1-u)**2
    q=.5*(k[0]*x*x+k[1]*y*y);H=q*S
    return H,-(k[0]*x*S+q*Sp/width*dx),-(k[1]*y*S+q*Sp/width*dy)

def coefficient_bound(half,softness,width,maximum=.12):
    a,b=max(half),min(half);_,qd=longitudinal(np.asarray(a),a,b,softness)
    gradient_bound=max(1.,abs(float(qd)));rho=np.hypot(a,b)
    factor=rho+.5*rho*rho*(15/8)/width*gradient_bound
    return maximum*b/factor

class CorePotentialStudy(Study):
    def geometry_field(self,x,y,p):
        X,Y,d,J=super().geometry_field(x,y,p);co=p.get('core_potential',[0.,0.])
        if not np.any(co):return X,Y,d,J
        xx,yy,half,r,_=self.shape(x,y,p)
        _,dx,dy=potential_terms(xx,yy,half,p['crown_softness'],co,.30*r)
        return X+dx,Y+dy,d,J
