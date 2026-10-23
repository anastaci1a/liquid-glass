"""Reuse fixed source lookups while varying the existing input power curve."""
import numpy as np
from extended_fit import Study
from paired_fit import Cached
from chromatic_transmission import enabled,weight

class GammaStudy(Study):
    def sample_field(self,X,Y,d,p):
        if not getattr(self,'capture_gamma',False):return super().sample_field(X,Y,d,p)
        q=dict(p);q['gamma']=1.
        sample=super().sample_field(X,Y,d,q)
        index=len(self.gamma_buffers)
        self.gamma_buffers.append(sample if index==0 else sample[...,0 if index==1 else 2].copy())
        return sample**p['gamma']

class GammaCache(Cached):
    def __init__(self,study,p):
        study.gamma_buffers=[];study.capture_gamma=True
        try:super().__init__(study,p)
        finally:study.capture_gamma=False
        self.samples=study.gamma_buffers;del study.gamma_buffers
        if enabled(p):
            assert len(self.samples)==3
            a,b,c,d=study.crop;_,xx=np.mgrid[b:d:.5,a:c:.5]
            self.weight=weight(study,p,(xx-.25-study.case['center'][0])/study.L)
        else:
            assert len(self.samples)==1;self.weight=None
        original=self.C.copy();self.gamma(p['gamma'])
        self.capture_error=float(np.max(abs(self.C-original)))
        assert self.capture_error<1e-12,self.capture_error

    def gamma(self,value):
        if not np.isfinite(value) or value<=0:raise ValueError('Require positive finite gamma')
        sample=self.samples[0]**value
        if self.weight is not None:
            dispersed=sample.copy();dispersed[...,0]=self.samples[1]**value;dispersed[...,2]=self.samples[2]**value
            self.C=sample*(1-self.weight[...,None])+dispersed*self.weight[...,None]
        else:self.C=sample
        self.p={**self.p,'gamma':float(value)}
        return self
