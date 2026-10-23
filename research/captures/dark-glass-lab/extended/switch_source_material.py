"""Shared source-colored rim basis; empirical environment response, not dispersion.

L_c = L * ((1-w)+w*C_c), 0<=w<=1. Keeps the same 23 material
coefficients and geometric support; introduces one shared color-coupling weight.
No target-color or per-reference coefficients enter this response.
"""
import sys
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from paired_fit import Cached
from grazing_reflection import layers

class SourceMaterialStudy(Study):
    def field(self,x,y,p):
        C,J=super().field(x,y,p);w=p['source_rim_mix']
        K=np.broadcast_to(J[...,None,:],(*C.shape,15)).copy()
        K[...,:-1]*=((1-w)+w*C)[...,None]
        return C,K

def statistics(cache,co):
    s=cache.study;H,W=cache.H,cache.W;C,J=cache.C,cache.J
    transform=cache.material_transform;effective=transform@co+cache.material_offset
    core=J[...,0,-1];gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:]
    z=C*gain+effective[3:6]+(J[...,:-1]@effective[6:-3])
    residual=cache.render(co).astype(np.float64)-s.target_crop
    forms={name:[np.zeros((23,23)),np.zeros(23)] for name in ['glass','rim']}
    for channel in range(3):
        active=(z[...,channel]>0)&(z[...,channel]<1)
        average=lambda v:v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
        F=np.zeros((H,W,23),np.float64)
        F[...,channel]=average(active*C[...,channel]*(1-core))
        F[...,channel+3]=average(active)
        F[...,6:20]=average(active[...,None]*J[...,channel,:-1])
        F[...,channel+20]=average(active*C[...,channel]*core)
        F=F@transform;sigma=s.kernel_sigma(cache.p,'post_sigma')
        if sigma>.001:F=cv2.GaussianBlur(F,(0,0),sigma)
        if 'grazing_reflection' in cache.p:F*=1-layers(s,cache.p)[0][...,None]
        for name,mask in [('glass',s.valid),('rim',s.rim)]:
            X=F[mask];e=residual[...,channel][mask];factor=255**2/(3*mask.sum())
            forms[name][0]+=(X.T@X)*factor;forms[name][1]+=(X.T@e)*factor
    return forms
