"""Integrable thin-element comparator, not a recovered Apple optical solid.

F = p - grad(Phi), Phi = .5*(cx*x²+cy*y²) - g(x)*A(d),
g=1+k*(x/hx)², A'=spline(d/r), A(r)=0. The same implicit crown
coordinate d is used with its exact gradient, not a unit-normal substitute.
This is a paraxial optical-path approximation; large slopes require ray tracing.
"""
import sys
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from crowned_footprint import field

def components(study,x,y,p,k):
    x,y,half,r,(sd,_,_)=study.shape(x,y,p)
    T,gx,gy=field(x,y,half,p['crown_softness'])
    root=np.maximum(np.sqrt(T),1e-12);dx=-r*gx/(2*root);dy=-r*gy/(2*root)
    d=np.clip(-sd,0,r);B=BSpline.design_matrix((d/r).ravel(),KNOTS,3).toarray()[:,:7].reshape((*x.shape,7))
    I=[]
    for i in range(7):
        c=np.zeros(len(KNOTS)-4);c[i]=1;f=BSpline(KNOTS,c,3).antiderivative()
        I.append(r*(f(d/r)-f(1.)))
    I=np.stack(I,-1);g=1+k*(x/half[0])**2;dg=2*k*x/half[0]**2
    # -grad(Phi), before its quadratic core part.
    return x,y,I*dg[...,None]+B*(g*dx)[...,None],B*(g*dy)[...,None]

class PotentialStudy(Study):
    def geometry_field(self,x,y,p):
        _,_,d,J=super().geometry_field(x,y,p)
        q=p['potential_profile'];xx,yy,Fx,Fy=components(self,x,y,p,q['longitudinal_weight'])
        co=np.asarray(q['coefficients'])
        X=(1-q['core'][0])*xx+Fx@co+p.get('shape_dx',0)
        Y=(1-q['core'][1])*yy+Fy@co+p.get('shape_dy',0)
        return X,Y,d,J
