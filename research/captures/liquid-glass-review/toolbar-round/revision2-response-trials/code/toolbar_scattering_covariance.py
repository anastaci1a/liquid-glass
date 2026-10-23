"""Bounded empirical geometry-conditioned scattering factor, not physical roughness.

Differentiate the accepted crowned B-spline/tangent map on the lens side. The
positional Jacobian is NOT a microfacet-normal response. No rendering/AA change.
"""
from functools import lru_cache
import numpy as np
from scipy.interpolate import BSpline
import toolbar_candidate as baseline
from crowned_footprint import field as crown_field
from toolbar_curvature_profile import geometry


@lru_cache(maxsize=8)
def _normal_spline(coefficients):
    n=len(baseline.KNOTS)-4;co=np.zeros(n);co[:len(coefficients)]=coefficients;s=BSpline(baseline.KNOTS,co,3,extrapolate=False)
    return s,s.derivative()


def transport_jacobian(x,y,p):
    """J_ij=dF_i/dx_j, flags. Lens-side limit at boundary; identity outside.

    Accepted soft crown or explicit circle only. Near-zero inherited normal
    branch uses the affine core Jacobian; flags retain this numerical region.
    """
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));half=p['shape']['half'];L=min(half);soft=p.get('footprint_softness',0.)
    g=geometry(tuple(half),soft);f,gx,gy,hxx,hxy,hyy=g.field_hessian(x,y)
    if soft:T,gx,gy=crown_field(x,y,half,soft)
    else:T=(x*x+y*y)/(L*L)
    grad=np.stack([gx,gy],axis=-1);H=np.stack([np.stack([hxx,hxy],axis=-1),np.stack([hxy,hyy],axis=-1)],axis=-2);norm=np.linalg.norm(grad,axis=-1);regular=norm*L>1e-14
    normal=np.divide(grad,norm[...,None],out=np.zeros_like(grad),where=regular[...,None]);normal_H=np.einsum('...i,...ij->...j',normal,H);Dn=np.divide(H-normal[..., :,None]*normal_H[...,None,:],norm[...,None,None],out=np.zeros_like(H),where=regular[...,None,None]);R=np.sqrt(np.maximum(T,0));depth=L*(1-R);gd=np.divide(-L*grad,2*R[...,None],out=np.zeros_like(grad),where=R[...,None]>1e-30)
    q=p['parameters'];radius=p['shape']['radius'];rawt=depth/radius;t=np.clip(rawt,0,1);s,sp=_normal_spline(tuple(q['coefficients']));a=L*s(t);ga=(L/radius*sp(t)*((rawt>=0)&(rawt<1)))[...,None]*gd
    u=np.clip(depth/(radius*q['tangent_band']),0,1);exponent=p.get('tangent_exponent',4.);W=(1-u)**exponent*(1+exponent*u);Wu=-exponent*(exponent+1)*u*(1-u)**(exponent-1);gW=(Wu/(radius*q['tangent_band'])*((u>0)&(u<1)))[...,None]*gd
    nx,ny=normal[...,0],normal[...,1];tau=-ny*x+nx*y;gtau=np.stack([-ny, nx],axis=-1)-x[...,None]*Dn[...,1,:]+y[...,None]*Dn[...,0,:];tangent=np.stack([ny,-nx],axis=-1);Dt=np.stack([Dn[...,1,:],-Dn[...,0,:]],axis=-2)
    J=np.zeros_like(H);J[...,0,0]=1-q['core_x'];J[...,1,1]=1-q['core_y'];J-=normal[..., :,None]*ga[...,None,:]+a[...,None,None]*Dn;J+=q['tangent']*(tangent[..., :,None]*(tau[...,None]*gW+W[...,None]*gtau)[...,None,:]+(W*tau)[...,None,None]*Dt)
    # Core-affine branch matches the accepted zero-normal branch. First seven
    # spline coefficients leave the last three basis functions zero, so normal
    # refraction vanishes smoothly at the center rather than adding an ad-hoc ray.
    core=np.zeros_like(J);core[...,0,0]=1-q['core_x'];core[...,1,1]=1-q['core_y'];J=np.where(regular[...,None,None],J,core);inside=T<=1;J=np.where(inside[...,None,None],J,np.eye(2))
    return J,{'inside':inside,'undefined_normal_branch':inside&~regular,'depth':depth}


def scattering_factor(x,y,p):
    J,flags=transport_jacobian(x,y,p);H=J-np.eye(2);A=H/np.sqrt(1+np.sum(H*H,axis=(-2,-1)))[...,None,None]
    return A,J,flags


def covariance(x,y,p,rho):
    if rho<0:raise ValueError('Nonnegative shared scattering scale required')
    A,J,flags=scattering_factor(x,y,p);M=np.einsum('...ik,...jk->...ij',A,A);L=min(p['shape']['half']);return (rho*L)**2*M,flags
