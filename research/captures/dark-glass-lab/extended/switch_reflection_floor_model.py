"""Private prototype: one shared isotropic fraction in angular reflection.

Only layers() is extended. Public render/cache/Jacobian order is unchanged.
R(d)*[A(n)+rho*(1-A(n))],0<=rho<=1, is a convex angular mixture.
It uses the existing source-derived environment, with no target RGB sampling.
Negative infinitesimal rho may be used ONLY for central-difference proposals;
all candidate parameters and invariant renders must remain in[0,1].
"""
import copy,numpy as np
import grazing_reflection as module
original=module.layers

def layers(study,p,scale=1,row=0,bottom=None):
    weight,environment=original(study,p,scale,row,bottom)
    rho=p.get('reflection_isotropic',0.)
    if rho==0:return weight,environment
    assert np.isfinite(rho)
    q=copy.deepcopy(p);q['grazing_reflection']['angular_power']=0.
    iso,_=original(study,q,scale,row,bottom)
    return weight+rho*(iso-weight),environment

def install():module.layers=layers
