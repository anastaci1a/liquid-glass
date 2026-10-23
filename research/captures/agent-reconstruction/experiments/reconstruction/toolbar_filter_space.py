"""Fixed ordinary source/output transfer conventions, not Apple pipeline proof."""
import numpy as np
import cv2
import toolbar_candidate as baseline
from render import shade

def decode(v,kind):
    v=np.asarray(v)
    if kind=='encoded':return v
    if kind=='srgb':return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
    if kind=='bt709':return np.where(v<.081,v/4.5,((v+.099)/1.099)**(1/.45))
    raise ValueError(kind)

def encode(v,kind):
    v=np.maximum(v,0.)
    if kind=='encoded':return v
    if kind=='srgb':return np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055)
    if kind=='bt709':return np.where(v<.018,4.5*v,1.099*v**.45-.099)
    raise ValueError(kind)

def output_filter(raw,alpha,sigma,kind):
    if sigma==0:return encode(decode(raw,kind),kind) if kind!='encoded' else raw.copy()
    image=decode(raw,kind);den=cv2.GaussianBlur(alpha,(0,0),sigma);num=cv2.GaussianBlur(image*alpha[...,None],(0,0),sigma);filtered=num/np.maximum(den,1e-12)[...,None]
    return encode(filtered,kind).astype(np.float32) if kind!='encoded' else filtered

def raw_render(source,case,p,source_kind='encoded',samples=4,scale=1,atlas=None):
    L=min(case['half']);sigma=p['source_sigma']*L;texture=decode(source,source_kind);blur=cv2.GaussianBlur(texture,(0,0),sigma) if sigma else texture
    x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale;raw=np.zeros((H,W,3),np.float32);alpha=np.zeros((H,W),np.float32)
    if atlas is not None and (samples!=4 or scale!=1):raise ValueError('Native atlas requires original4x4')
    for top in range(0,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples];x=(x0+(xx+.5)/(samples*scale)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(samples*scale)-.5-case['center'][1])/L;sd,*_=baseline.boundary(x,y,p)
        if atlas is None:X,Y=baseline.mapping(x,y,p);sx=X*L+case['center'][0];sy=Y*L+case['center'][1]
        else:sx=atlas['sx'][top*4:bot*4];sy=atlas['sy'][top*4:bot*4]
        sx=sx.astype(np.float32);sy=sy.astype(np.float32);C=cv2.remap(blur,sx,sy,cv2.INTER_LINEAR)
        if p.get('blur_transition'):
            u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=cv2.remap(texture,sx,sy,cv2.INTER_LINEAR);C=clear+(C-clear)*w[...,None]
        if source_kind!='encoded':C=encode(C,source_kind)
        C=shade(C,baseline.lighting(x,y,p),np.asarray(p['material']));inside=sd<=0;sh=(bot-top,samples,W,samples);weight=inside.reshape(sh).sum((1,3));raw[top:bot]=(C*inside[...,None]).reshape((*sh,3)).sum((1,3))/np.maximum(weight,1)[...,None];alpha[top:bot]=weight/(samples*samples)
    return raw,alpha

def render(source,case,p,samples=4,scale=1,*,source_kind='encoded',output_kind='encoded',atlas=None):
    if source_kind==output_kind=='encoded':return baseline.render(source,case,p,samples,scale)
    raw,alpha=raw_render(source,case,p,source_kind,samples,scale,atlas)
    return output_filter(raw,alpha,p.get('post_sigma',0)*min(case['half'])*scale,output_kind),alpha
