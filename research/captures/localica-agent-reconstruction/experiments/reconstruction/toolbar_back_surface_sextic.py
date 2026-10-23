"""One T³ scalar-height addition to the explicit biaxial back surface.

h=h_parent+lambda*L*T³, grad(h)=grad(h_parent)+3lambda*L*T²grad(T).
The complete surface owns Snell refraction; no displacement or RGB patch.
"""
import numpy as np
import cv2
import toolbar_back_surface as parent
from crowned_footprint import longitudinal
from render import shade
baseline=parent.baseline


def surface_field(x,y,p):
    T,h,hx,hy=parent.surface_field(x,y,p);v=p['back_surface'].get('sextic',0.)
    if v==0:return T,h,hx,hy
    _,tx,ty=parent.implicit(x,y,p);L=min(p['shape']['half']);f=3*v*L*T*T
    return T,h+v*L*T**3,hx+f*tx,hy+f*ty


def analytic_bounds(p):
    b=parent.analytic_bounds(p);q=p['back_surface'];v=abs(q.get('sextic',0.));a=max(p['shape']['half']);L=min(p['shape']['half']);qp=1.
    if p.get('footprint_softness'):
        _,t=longitudinal(np.asarray(a),a,L,p['footprint_softness']);qp=max(1.,abs(float(t)))
    lo=b['height_lower']-v*L;hi=b['height_upper']+v*L;M=b['gradient_norm_upper']+6*v*qp;G=b['background'];n=q['ior'];crit=b['critical_gradient'];valid=bool(n>1 and lo>0 and G>hi and M<crit)
    delta=np.arcsin(n*np.sin(np.arctan(M)))-np.arctan(M) if valid else np.nan
    return {'height_lower':lo,'height_upper':hi,'background':G,'minimum_gap':G-hi,'gradient_norm_upper':M,'critical_gradient':crit,'extra_height_bound':v*L,'extra_slope_bound':6*v*qp,'global_subcritical_positive_clearance':valid,'no_reentry_sufficient_product':float(M*np.tan(delta)) if valid else None,'displacement_norm_upper':float((G-lo)*np.tan(delta)) if valid else None}


def rays(x,y,p):
    if p['back_surface'].get('sextic',0.)==0:return parent.rays(x,y,p)
    T,h,hx,hy=surface_field(x,y,p);q=p['back_surface'];L=min(p['shape']['half']);G=L*q['background'];n=q['ior'];a=1/np.sqrt(1+hx*hx+hy*hy);K=1-n*n*(1-a*a);f=np.sqrt(np.maximum(K,0))-n*a;vx=-f*hx*a;vy=-f*hy*a;vz=-n-f*a
    inside=T<=1;valid=(h>0)&(G>h)&(K>0)&(vz<0)&np.isfinite(h);X=x+(G-h)*vx/(-vz);Y=y+(G-h)*vy/(-vz)
    return np.where(inside,X,x),np.where(inside,Y,y),np.where(inside,valid,True),{'inside':inside,'height':h,'discriminant':K,'gradient_norm':np.hypot(hx,hy)}


def mapping(x,y,p):
    if 'back_surface' not in p:return baseline.mapping(x,y,p)
    X,Y,valid,_=rays(x,y,p)
    if not np.all(valid):raise ValueError('Invalid complete surface ray')
    return X,Y


def render(source,case,p,samples=4,scale=1):
    if 'back_surface' not in p or p['back_surface'].get('sextic',0.)==0:return parent.render(source,case,p,samples,scale)
    if not analytic_bounds(p)['global_subcritical_positive_clearance']:raise ValueError('Complete analytic bounds failed')
    L=min(case['half']);sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale;result=np.zeros((H,W,3),np.float32);coverage=np.zeros((H,W),np.float32)
    for top in range(0,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples];x=(x0+(xx+.5)/(scale*samples)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(scale*samples)-.5-case['center'][1])/L;X,Y=mapping(x,y,p);sx=X*L+case['center'][0];sy=Y*L+case['center'][1]
        if sx.min()<0 or sx.max()>=source.shape[1]-1 or sy.min()<0 or sy.max()>=source.shape[0]-1:raise ValueError('Frozen source domain exceeded')
        C=cv2.remap(blur,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_LINEAR)
        if p.get('blur_transition'):
            sd,*_=baseline.boundary(x,y,p);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=cv2.remap(source,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_LINEAR);C=clear+(C-clear)*w[...,None]
        C=shade(C,baseline.lighting(x,y,p),np.asarray(p['material']));sd,*_=baseline.boundary(x,y,p);inside=(sd<=0).astype(float);shape=(bot-top,samples,W,samples);weight=inside.reshape(shape).sum((1,3));result[top:bot]=(C*inside[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(weight,1)[...,None];coverage[top:bot]=weight/(samples*samples)
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale;numerator=cv2.GaussianBlur(result*coverage[...,None],(0,0),sigma);denominator=cv2.GaussianBlur(coverage,(0,0),sigma);result=numerator/np.maximum(denominator,1e-12)[...,None]
    return result,coverage
