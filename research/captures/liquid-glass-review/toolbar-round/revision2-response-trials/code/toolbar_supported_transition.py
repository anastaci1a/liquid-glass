"""Explicit bounded W/profile and inner-B-spline-support hypotheses."""
import numpy as np
import toolbar_candidate as base


def mapping(x,y,p):
    q=p['supported_transition'];optical={**p['parameters'],'coefficients':list(p['parameters']['coefficients'])}
    indices=[2,3,4] if q['mode']=='expanded' else [4,5,6]
    for i,v in zip(indices,q['normal_delta']):optical['coefficients'][i]+=v
    optical['tangent_band']=q.get('band',p['parameters']['tangent_band'])
    return base.mapping(x,y,{**p,'parameters':optical,'tangent_exponent':q.get('exponent',4.)})

import cv2
from render import shade

def render(source,case,p,samples=4,scale=1):
    """Same raster/material pipeline as frozen candidate; mapping differs only."""
    L=min(case['half']);sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source
    x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale;result=np.zeros((H,W,3),np.float32);coverage=np.zeros((H,W),np.float32)
    for top in range(0,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples]
        x=(x0+(xx+.5)/(scale*samples)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(scale*samples)-.5-case['center'][1])/L
        X,Y=mapping(x,y,p)
        def at(image):return cv2.remap(image,(X*L+case['center'][0]).astype(np.float32),(Y*L+case['center'][1]).astype(np.float32),cv2.INTER_LINEAR)
        C=at(blur)
        if p.get('blur_transition'):
            sd,*_=base.boundary(x,y,p);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=at(source);C=clear+(C-clear)*w[...,None]
        C=shade(C,base.lighting(x,y,p),np.asarray(p['material']));sd,*_=base.boundary(x,y,p);inside=(sd<=0).astype(float);shape=(bot-top,samples,W,samples);weight=inside.reshape(shape).sum((1,3))
        result[top:bot]=(C*inside[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(weight,1)[...,None];coverage[top:bot]=weight/(samples*samples)
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale
        result=cv2.GaussianBlur(result*coverage[...,None],(0,0),sigma)/np.maximum(cv2.GaussianBlur(coverage,(0,0),sigma),1e-12)[...,None]
    return result,coverage
