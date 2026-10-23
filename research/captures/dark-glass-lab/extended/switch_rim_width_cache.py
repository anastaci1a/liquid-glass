"""Cost-only reuse of accepted transmission for lighting-width experiments.
Only existing thin/rim basis widths change. No source, mapping, blur or alpha
change; output still follows Cached.render's original operation order.
"""
import copy
import numpy as np
from paired_fit import Cached

class RimWidthCache(Cached):
    def __init__(self,study,p):
        super().__init__(study,copy.deepcopy(p))
        a,b,c,d=study.crop;yy,xx=np.mgrid[b:d:.5,a:c:.5]
        *_,(sd,self.nx,self.ny)=study.shape((xx-.25-study.case['center'][0])/study.L,(yy-.25-study.case['center'][1])/study.L,p)
        self.depth=np.maximum(-sd,0.)
    def widths(self,rim,thin):
        if not np.isfinite([rim,thin]).all() or min(rim,thin)<=0:raise ValueError('Invalid lighting width')
        self.p.update(rim_width=float(rim),thin_width=float(thin))
        for start,width in [(0,thin),(3,rim),(6,4*rim)]:
            value=np.exp(-(self.depth/width)**2)
            self.J[...,start]=value;self.J[...,start+1]=value*self.nx;self.J[...,start+2]=value*self.ny
        return self
