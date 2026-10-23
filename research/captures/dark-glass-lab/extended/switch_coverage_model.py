"""Private covered-color convolution proposal; retain sharp geometric coverage."""
import sys,copy
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from paired_fit import Cached
from render import shade
from grazing_reflection import apply,layers

def filter_color(value,alpha,sigma):
    if sigma<=.001:return value
    return cv2.GaussianBlur(value*alpha[...,None],(0,0),sigma)/np.maximum(cv2.GaussianBlur(alpha,(0,0),sigma)[...,None],1e-10)

class CoverageStudy(Study):
    def render(self,p,co,scale=1):
        q=copy.deepcopy(p);q['post_sigma']=0.;q.pop('grazing_reflection',None)
        raw=super().render(q,co,scale)
        return apply(self,p,filter_color(raw,self.shape_coverage(p,scale),self.kernel_sigma(p,'post_sigma')*scale),scale)

class CoverageCache(Cached):
    def __init__(self,study,p):
        super().__init__(study,p);self.alpha=study.shape_coverage(p)
    def render(self,co):
        co=self.material_transform@np.asarray(co)+self.material_offset
        color=shade(self.C,self.J,co).reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32)
        return apply(self.study,self.p,filter_color(color,self.alpha,self.study.kernel_sigma(self.p,'post_sigma')))

def statistics(cache,co):
    s=cache.study;H,W=cache.H,cache.W;C,J=cache.C,cache.J
    transform=cache.material_transform;effective=transform@co+cache.material_offset
    core=J[...,-1];gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:]
    z=C*gain+effective[3:6]+(J[...,:-1]@effective[6:-3])[...,None]
    residual=cache.render(co).astype(np.float64)-s.target_crop
    forms={name:[np.zeros((23,23)),np.zeros(23)] for name in ['glass','rim']}
    for channel in range(3):
        active=(z[...,channel]>0)&(z[...,channel]<1)
        average=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
        F=np.zeros((H,W,23),np.float64)
        F[...,channel]=average(active*C[...,channel]*(1-core))
        F[...,channel+3]=average(active)
        F[...,6:20]=average(active[...,None]*J[...,:-1])
        F[...,channel+20]=average(active*C[...,channel]*core)
        F=filter_color(F@transform,cache.alpha,s.kernel_sigma(cache.p,'post_sigma'))
        if 'grazing_reflection' in cache.p:F*=1-layers(s,cache.p)[0][...,None]
        for name,mask in [('glass',s.valid),('rim',s.rim)]:
            X=F[mask];e=residual[...,channel][mask];factor=255**2/(3*mask.sum())
            forms[name][0]+=(X.T@X)*factor;forms[name][1]+=(X.T@e)*factor
    return forms
