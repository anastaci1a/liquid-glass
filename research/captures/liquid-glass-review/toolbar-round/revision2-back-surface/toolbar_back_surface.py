"""One declared biaxial physical back surface; empirical material stays separate.

back_surface absent delegates to accepted toolbar_candidate exactly. With the
profile present, h/L=t0+b_major*X_major²+b_minor*X_minor²+c*T² owns every ray.
Orthographic normal entry through flat front, glass n, background z=-G.
"""
import numpy as np
import cv2
import toolbar_candidate as baseline
from crowned_footprint import field as crown_field,longitudinal
from render import shade


def implicit(x,y,p):
    half=p['shape']['half'];soft=p.get('footprint_softness',0)
    if soft:return crown_field(x,y,half,soft)
    if half[0]!=half[1]:raise ValueError('Only crowned footprint or explicit circle supported')
    r=half[0];return (x*x+y*y)/(r*r),2*x/(r*r),2*y/(r*r)


def surface_field(x,y,p):
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));q=p['back_surface'];L=min(p['shape']['half']);T,tx,ty=implicit(x,y,p)
    horizontal=p['shape']['half'][0]>=p['shape']['half'][1];bx=q['b_major'] if horizontal else q['b_minor'];by=q['b_minor'] if horizontal else q['b_major']
    h=L*(q['thickness']+bx*(x/L)**2+by*(y/L)**2+q['quartic']*T*T)
    hx=2*bx*x/L+2*L*q['quartic']*T*tx;hy=2*by*y/L+2*L*q['quartic']*T*ty
    return T,h,hx,hy


def analytic_bounds(p):
    q=p['back_surface'];a=max(p['shape']['half']);L=min(p['shape']['half']);ratio=a/L
    qprime=1.
    if p.get('footprint_softness'):
        _,v=longitudinal(np.asarray(a),a,L,p['footprint_softness']);qprime=max(1.,abs(float(v)))
    height_variation=abs(q['b_major'])*ratio**2+abs(q['b_minor'])+abs(q['quartic'])
    slope=2*np.hypot(abs(q['b_major'])*ratio,abs(q['b_minor']))+4*abs(q['quartic'])*qprime
    critical=1/np.sqrt(q['ior']**2-1) if q['ior']>1 else 0.
    lo=L*(q['thickness']-height_variation);hi=L*(q['thickness']+height_variation);G=L*q['background']
    valid=bool(q['ior']>1 and lo>0 and G>hi and slope<critical)
    delta=np.arcsin(q['ior']*np.sin(np.arctan(slope)))-np.arctan(slope) if valid else np.nan
    return {'height_lower':lo,'height_upper':hi,'background':G,'minimum_gap':G-hi,'gradient_norm_upper':float(slope),'critical_gradient':float(critical),'global_subcritical_positive_clearance':valid,'no_reentry_sufficient_product':float(slope*np.tan(delta)) if valid else None,'displacement_norm_upper':float((G-lo)*np.tan(delta)) if valid else None}


def rays(x,y,p):
    T,h,hx,hy=surface_field(x,y,p);q=p['back_surface'];L=min(p['shape']['half']);G=L*q['background'];n=q['ior'];a=1/np.sqrt(1+hx*hx+hy*hy);K=1-n*n*(1-a*a)
    # Only valid transmitted branches become source rays. max(K,0) makes
    # arithmetic defined for outside-footprint diagnostics, never admits TIR.
    factor=np.sqrt(np.maximum(K,0))-n*a;vx=-factor*hx*a;vy=-factor*hy*a;vz=-n-factor*a
    inside=T<=1;valid=(h>0)&(G>h)&(K>0)&(vz<0)&np.isfinite(h)
    X=x+(G-h)*vx/(-vz);Y=y+(G-h)*vy/(-vz)
    return np.where(inside,X,x),np.where(inside,Y,y),np.where(inside,valid,True),{'inside':inside,'height':h,'discriminant':K,'gradient_norm':np.hypot(hx,hy)}


def mapping(x,y,p):
    if 'back_surface' not in p:return baseline.mapping(x,y,p)
    X,Y,valid,_=rays(x,y,p)
    if not np.all(valid):raise ValueError('Invalid physical surface ray: no TIR/gap clipping allowed')
    return X,Y


def render(source,case,p,samples=4,scale=1):
    if 'back_surface' not in p:return baseline.render(source,case,p,samples,scale)
    if not analytic_bounds(p)['global_subcritical_positive_clearance']:raise ValueError('Analytic surface safety bounds failed')
    L=min(case['half']);sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source
    x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale;result=np.zeros((H,W,3),np.float32);coverage=np.zeros((H,W),np.float32)
    for top in range(0,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples]
        x=(x0+(xx+.5)/(scale*samples)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(scale*samples)-.5-case['center'][1])/L;X,Y=mapping(x,y,p);sourcex=X*L+case['center'][0];sourcey=Y*L+case['center'][1]
        if np.min(sourcex)<0 or np.max(sourcex)>=source.shape[1]-1 or np.min(sourcey)<0 or np.max(sourcey)>=source.shape[0]-1:raise ValueError('Source domain exceeded')
        C=cv2.remap(blur,sourcex.astype(np.float32),sourcey.astype(np.float32),cv2.INTER_LINEAR)
        if p.get('blur_transition'):
            sd,*_=baseline.boundary(x,y,p);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10)
            clear=cv2.remap(source,sourcex.astype(np.float32),sourcey.astype(np.float32),cv2.INTER_LINEAR);C=clear+(C-clear)*w[...,None]
        C=shade(C,baseline.lighting(x,y,p),np.asarray(p['material']));sd,*_=baseline.boundary(x,y,p);inside=(sd<=0).astype(float);shape=(bot-top,samples,W,samples);weight=inside.reshape(shape).sum((1,3));result[top:bot]=(C*inside[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(weight,1)[...,None];coverage[top:bot]=weight/(samples*samples)
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale;numerator=cv2.GaussianBlur(result*coverage[...,None],(0,0),sigma);denominator=cv2.GaussianBlur(coverage,(0,0),sigma);result=numerator/np.maximum(denominator,1e-12)[...,None]
    return result,coverage
