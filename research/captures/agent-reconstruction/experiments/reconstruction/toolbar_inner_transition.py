"""Outer-rim-preserving normalized transition hypotheses; not Apple solids.

A shared C2 quintic envelope leaves d<=.04L unchanged and reaches unity at.08L.
It is geometry-based over the whole element, never a crop/letter mask. The coupled
family applies the envelope to its scalar potential before taking the gradient.
"""
import numpy as np
from crowned_footprint import field
import toolbar_candidate as base
from toolbar_transition import falloff


def envelope(d):
    z=np.clip((d-.04)/.04,0,1)
    S=z**3*(z*(6*z-15)+10)
    derivative=30*z*z*(1-z)**2/.04
    return S,derivative


def mapping(x,y,p):
    q=p['inner_transition'];m=q['exponent'];band=q['band'];family=q['family']
    X,Y=base.mapping(x,y,p);T,gx,gy=field(x,y,p['shape']['half'],p['footprint_softness']);r=np.sqrt(T);L=min(p['shape']['half']);d=L*(1-r);S,Sd=envelope(d)
    if family=='empirical':
        optical={**p['parameters'],'tangent_band':band,'tangent':p['parameters']['tangent']*q.get('gain',1.),'coefficients':list(p['parameters']['coefficients'])}
        for i,v in zip([2,3,4],q.get('normal_delta',[0,0,0])):optical['coefficients'][i]+=v
        U,V=base.mapping(x,y,{**p,'parameters':optical,'tangent_exponent':m})
        return X+S*(U-X),Y+S*(V-Y)
    if family!='coupled_difference':raise ValueError('Unknown inner transition')
    dx=np.divide(-.5*L*gx,r,out=np.zeros_like(gx),where=r>1e-14);dy=np.divide(-.5*L*gy,r,out=np.zeros_like(gy),where=r>1e-14)
    W,D=falloff(d,band,m);W0,D0=falloff(d,p['parameters']['tangent_band'],4.);k=p['parameters']['tangent'];K=k*(W-W0);Kd=k*(D-D0)
    # Envelope is inside the potential: extra derivative Sd is mandatory.
    X=X-x*K*S-.5*x*x*(Kd*S+K*Sd)*dx
    Y=Y-.5*x*x*(Kd*S+K*Sd)*dy
    # Independent global normal-profile freedom remains explicitly empirical.
    delta=q.get('normal_delta',[0,0,0])
    if any(delta):
        optical={**p['parameters'],'coefficients':list(p['parameters']['coefficients'])}
        for i,v in zip([2,3,4],delta):optical['coefficients'][i]+=v
        U,V=base.mapping(x,y,{**p,'parameters':optical});A,B=base.mapping(x,y,p)
        X+=S*(U-A);Y+=S*(V-B)
    return X,Y

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
