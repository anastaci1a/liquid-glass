"""Reuse fixed RGB rays while testing existing directional mixture weights.
No new optics: same accepted ray coordinates, source kernels and material order.
"""
import copy
import numpy as np
from paired_fit import Cached
from material_context import affine
from chromatic_transmission import rays,weight

class DirectionalCache(Cached):
    def __init__(self,study,p):
        self.study=study;self.p=copy.deepcopy(p)
        self.material_transform,self.material_offset=affine(study,p)
        a,b,c,d=study.crop;self.H=d-b;self.W=c-a
        yy,xx=np.mgrid[b:d:.5,a:c:.5]
        self.x=(xx-.25-study.case['center'][0])/study.L
        y=(yy-.25-study.case['center'][1])/study.L
        bare=copy.deepcopy(p);bare['directional_transmission']['strength']=0.
        self.base,self.J=study.field(self.x,y,bare);shifted=self.base.copy()
        for c,X,Y,d in rays(study,p,self.x,y):shifted[...,c]=study.sample_field(X,Y,d,p)[...,c]
        self.shifted=shifted
        self.weights(p['directional_transmission'])
    def weights(self,q):
        self.p['directional_transmission']=copy.deepcopy(q)
        w=weight(self.study,self.p,self.x)[...,None]
        # Keep the exact original operation order, rather than a+B*(b-a).
        self.C=self.base*(1-w)+self.shifted*w
        return self
