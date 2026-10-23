"""A single potential core-strain addition to the frozen empirical image map.

Psi=.5*amplitude*(e dot position)^2*S(d/width). The actual gradient of the
crowned r-b coordinate is used; it is not replaced with its unit normal.
Quintic S makes the potential C2 and the added vector field C1 at the joins.
Only this addition is integrable; inherited total refraction remains empirical.
"""
import numpy as np
import cv2
import toolbar_candidate as baseline
from crowned_footprint import field as crown_field,longitudinal
from render import shade


def core_axis(p):
    return np.array([1.,0.]) if p['shape']['half'][0]>=p['shape']['half'][1] else np.array([0.,1.])


def smoothstep(u):
    v=np.clip(np.asarray(u,float),0,1)
    return v**3*(10-15*v+6*v*v),30*v*v*(1-v)**2


def depth_gradient(x,y,p):
    sd,nx,ny=baseline.boundary(x,y,p);depth=-sd
    if not p.get('footprint_softness'):return depth,-nx,-ny
    T,gx,gy=crown_field(x,y,p['shape']['half'],p['footprint_softness'])
    # At T=0 the coordinate has no unique gradient, but S'=0 throughout this
    # deep core, so assigning zero there cannot affect the potential gradient.
    factor=np.divide(-min(p['shape']['half']),2*np.sqrt(np.maximum(T,0)),out=np.zeros_like(T,dtype=float),where=T>1e-28)
    return depth,factor*gx,factor*gy


def potential(x,y,p):
    q=p.get('core_strain',{});amplitude=float(q.get('amplitude',0.));x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
    if amplitude==0:return np.zeros_like(x)
    width=float(q['width'])
    if width<=0:raise ValueError('Fixed positive core support width required')
    depth=-baseline.boundary(x,y,p)[0];S,_=smoothstep(depth/width);e=core_axis(p);z=e[0]*x+e[1]*y
    return .5*amplitude*z*z*S


def addition(x,y,p):
    q=p.get('core_strain',{});amplitude=float(q.get('amplitude',0.));x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
    if amplitude==0:return np.zeros_like(x),np.zeros_like(y)
    width=float(q['width'])
    if width<=0:raise ValueError('Fixed positive core support width required')
    depth,dx,dy=depth_gradient(x,y,p);S,Sp=smoothstep(depth/width);e=core_axis(p);z=e[0]*x+e[1]*y;normal=.5*z*z*Sp/width
    return -amplitude*(e[0]*z*S+normal*dx),-amplitude*(e[1]*z*S+normal*dy)


def displacement_bound(p,maximum_fraction=.12):
    half=p['shape']['half'];a=max(half);L=min(half);width=float(p['core_strain']['width'])
    if not(0<width<L):raise ValueError('Require fixed core transition width between zero and minor half')
    max_depth_gradient=1.
    if p.get('footprint_softness'):
        _,qd=longitudinal(np.asarray(a),a,L,p['footprint_softness']);max_depth_gradient=max(1.,abs(float(qd)))
    # Convex longitudinal q has monotone q': |grad(d)|<=max(1,q'(a)).
    # |e dot position|<=a inside the footprint, S<=1 and max S'=15/8.
    unit_bound=a+.5*a*a/width*(15/8)*max_depth_gradient
    conservative=unit_bound*(1+1e-4)
    return {'lambda_max':maximum_fraction*L/conservative,'maximum_added_displacement_fraction':maximum_fraction,'unit_displacement_bound':unit_bound,'conservative_unit_bound':conservative,'max_depth_gradient_bound':max_depth_gradient,'fixed_width':width,'major_half':a,'minor_half':L,'S_prime_max':15/8,'origin':'analytic triangle bound from fixed geometry, independent of target pixels'}


def mapping(x,y,p):
    if p.get('curvature_normal',{}).get('amplitude',0.):
        import toolbar_curvature_profile
        X,Y=toolbar_curvature_profile.mapping(x,y,p)
    else:X,Y=baseline.mapping(x,y,p)
    if p.get('core_strain',{}).get('amplitude',0.)==0:return X,Y
    dx,dy=addition(x,y,p)
    return X+dx,Y+dy


def render(source,case,p,samples=4,scale=1):
    if p.get('core_strain',{}).get('amplitude',0.)==0:
        if p.get('curvature_normal',{}).get('amplitude',0.):
            import toolbar_curvature_profile
            return toolbar_curvature_profile.render(source,case,p,samples,scale)
        return baseline.render(source,case,p,samples,scale)
    L=min(case['half']);sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source
    x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale
    result=np.zeros((H,W,3),np.float32);coverage=np.zeros((H,W),np.float32)
    for top in range(0,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples]
        x=(x0+(xx+.5)/(scale*samples)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(scale*samples)-.5-case['center'][1])/L
        X,Y=mapping(x,y,p)
        def at(image):return cv2.remap(image,(X*L+case['center'][0]).astype(np.float32),(Y*L+case['center'][1]).astype(np.float32),cv2.INTER_LINEAR)
        C=at(blur)
        if p.get('blur_transition'):
            sd,*_=baseline.boundary(x,y,p);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=at(source);C=clear+(C-clear)*w[...,None]
        C=shade(C,baseline.lighting(x,y,p),np.asarray(p['material']));sd,*_=baseline.boundary(x,y,p);inside=(sd<=0).astype(float)
        shape=(bot-top,samples,W,samples);weight=inside.reshape(shape).sum((1,3));result[top:bot]=(C*inside[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(weight,1)[...,None];coverage[top:bot]=weight/(samples*samples)
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale;numerator=cv2.GaussianBlur(result*coverage[...,None],(0,0),sigma);denominator=cv2.GaussianBlur(coverage,(0,0),sigma);result=numerator/np.maximum(denominator,1e-12)[...,None]
    return result,coverage
