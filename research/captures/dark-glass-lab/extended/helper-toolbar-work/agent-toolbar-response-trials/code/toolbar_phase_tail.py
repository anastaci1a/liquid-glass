"""Smooth potential perturbation of the empirical toolbar inverse map.

The ADDED displacement is -grad(Psi), Psi=.5*k*x*x*H(d/b), H=64u^3(1-u)^3
on 0<u<1, zero elsewhere. Its Jacobian is symmetric; the TOTAL inherited tensor
map need not be integrable. This is an analytic image-map hypothesis, not a
recovered optical solid, Apple technique or text-anchored correction.
"""
import numpy as np
import cv2
from crowned_footprint import field
from render import shade
import toolbar_candidate as base


def perturbation(x,y,p):
    q=p.get('phase_tail',{'strength':0.,'band':1.});k=q['strength'];band=q['band']
    if not (0<band<=1):raise ValueError('Phase band must lie in (0,1]')
    if k==0:return np.zeros_like(x),np.zeros_like(y)
    # d=min(half)*(1-sqrt(T)); its exact gradient is NOT assumed -unit normal.
    T,gx,gy=field(x,y,p['shape']['half'],p['footprint_softness']);r=np.sqrt(T);L=min(p['shape']['half']);d=L*(1-r)
    dx=np.divide(-.5*L*gx,r,out=np.zeros_like(gx),where=r>1e-14)
    dy=np.divide(-.5*L*gy,r,out=np.zeros_like(gy),where=r>1e-14)
    u=np.clip(d/band,0,1);H=64*u**3*(1-u)**3;Hd=192*u**2*(1-u)**2*(1-2*u)/band
    return -k*x*H-.5*k*x*x*Hd*dx,-.5*k*x*x*Hd*dy


def mapping(x,y,p):
    X,Y=base.mapping(x,y,p);A,B=perturbation(x,y,p)
    return X+A,Y+B


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
