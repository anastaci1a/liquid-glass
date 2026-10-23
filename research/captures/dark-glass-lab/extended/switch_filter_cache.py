"""Native cache and chain-rule material derivatives for the filter-space test."""
import cv2,numpy as np
from paired_fit import Cached
from render import shade
from grazing_reflection import apply,layers
from switch_filter_space import decode,encode
from revision_replay import clean_composite
from joint_visible_statistics import visible_masks

def decode_derivative(v,kind):
    if kind=='srgb':return np.where(v<=.04045,1/12.92,2.4/1.055*((v+.055)/1.055)**1.4)
    if kind=='bt709':return np.where(v<.081,1/4.5,(1/.45)/1.099*((v+.099)/1.099)**(1/.45-1))
    raise ValueError(kind)

def encode_derivative(v,kind):
    if kind=='srgb':return np.where(v<=.0031308,12.92,1.055/2.4*np.maximum(v,.0031308)**(1/2.4-1))
    if kind=='bt709':return np.where(v<.018,4.5,1.099*.45*np.maximum(v,.018)**(-.55))
    raise ValueError(kind)

class FilterSpaceCache(Cached):
    def render(self,co):
        kind=self.p.get('output_filter_space','encoded')
        if kind=='encoded':return super().render(co)
        co=self.material_transform@co+self.material_offset
        im=shade(self.C,self.J,co).reshape(self.H,2,self.W,2,3).mean((1,3)).astype(np.float32)
        sigma=self.study.kernel_sigma(self.p,'post_sigma')
        if sigma>.001:im=encode(cv2.GaussianBlur(decode(im,kind).astype(np.float32),(0,0),sigma),kind).astype(np.float32)
        return apply(self.study,self.p,im)

    def material_channels(self,co):
        if self.p.get('output_filter_space','encoded')=='encoded':
            from joint_material_jacobian import material_channels
            yield from material_channels(self,co)
            return
        s=self.study;H,W=self.H,self.W;C,J=self.C,self.J;T=self.material_transform
        effective=T@co+self.material_offset;core=J[...,-1]
        gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:]
        raw=C*gain+effective[3:6]+(J[...,:-1]@effective[6:-3])[...,None]
        mean=np.clip(raw,0,1).reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
        sigma=s.kernel_sigma(self.p,'post_sigma');kind=self.p['output_filter_space']
        before=decode(mean,kind).astype(np.float32)
        after=cv2.GaussianBlur(before,(0,0),sigma) if sigma>.001 else before
        for channel in range(3):
            active=(raw[...,channel]>0)&(raw[...,channel]<1)
            def average(v):return v.reshape(H,2,W,2,*v.shape[2:]).mean((1,3))
            F=np.zeros((H,W,23),np.float64)
            F[...,channel]=average(active*C[...,channel]*(1-core))
            F[...,channel+3]=average(active)
            F[...,6:20]=average(active[...,None]*J[...,:-1])
            F[...,channel+20]=average(active*C[...,channel]*core)
            F=F@T
            if sigma>.001:
                F*=decode_derivative(mean[...,channel],kind)[...,None]
                F=cv2.GaussianBlur(F,(0,0),sigma)
                F*=encode_derivative(after[...,channel],kind)[...,None]
            if 'grazing_reflection' in self.p:F*=1-layers(s,self.p)[0][...,None]
            yield channel,F

def material_statistics(cache,co,scales,pred):
    s=cache.study;residual=pred.astype(np.float64)-s.target_crop
    visible=clean_composite(s,cache.p,pred).astype(np.float64)-s.target_crop;alpha=s.shape_coverage(cache.p)
    masks={'glass':s.valid,'rim':s.rim,'shadow':visible_masks(s)['shadow']}
    forms={k:[np.zeros((23,23)),np.zeros(23)] for k in masks}
    for channel,F in cache.material_channels(co):
        for name,mask in masks.items():
            D=F[mask]*scales
            if name=='shadow':D*=alpha[mask,None]
            r=(visible if name=='shadow' else residual)[...,channel][mask];factor=255**2/(3*mask.sum())
            forms[name][0]+=D.T@D*factor;forms[name][1]+=D.T@r*factor
    return forms
