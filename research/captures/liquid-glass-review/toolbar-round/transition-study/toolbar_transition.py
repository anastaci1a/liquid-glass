"""Bounded transition/profile families; inverse-map hypotheses, not Apple solids."""
import numpy as np
from crowned_footprint import field
import toolbar_candidate as base


def falloff(d,band,m):
    u=np.clip(d/band,0,1);W=(1-u)**m*(1+m*u)
    derivative=-m*(m+1)*u*(1-u)**(m-1)/band
    return W,derivative


def mapping(x,y,p):
    q=p.get('transition',{'family':'empirical','exponent':4.,'band':p['parameters']['tangent_band'],'normal_delta':[0,0,0]})
    m=q['exponent'];band=q['band'];family=q['family']
    if family=='empirical':
        optical={**p['parameters'],'tangent_band':band,'coefficients':list(p['parameters']['coefficients'])}
        for i,v in zip([2,3,4],q.get('normal_delta',[0,0,0])):optical['coefficients'][i]+=v
        return base.mapping(x,y,{**p,'parameters':optical,'tangent_exponent':m})
    if family!='coupled_difference':raise ValueError('Unknown transition family')
    X,Y=base.mapping(x,y,p)
    # Added potential .5*x^2*(Knew(d)-Kold(d)), including exact gradient.
    T,gx,gy=field(x,y,p['shape']['half'],p['footprint_softness']);r=np.sqrt(T);L=min(p['shape']['half']);d=L*(1-r)
    dx=np.divide(-.5*L*gx,r,out=np.zeros_like(gx),where=r>1e-14);dy=np.divide(-.5*L*gy,r,out=np.zeros_like(gy),where=r>1e-14)
    W,D=falloff(d,band,m);W0,D0=falloff(d,p['parameters']['tangent_band'],4.)
    k=p['parameters']['tangent'];K=k*(W-W0);Kd=k*(D-D0)
    return X-x*K-.5*x*x*Kd*dx,Y-.5*x*x*Kd*dy

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
