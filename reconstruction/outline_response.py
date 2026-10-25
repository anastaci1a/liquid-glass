"""Shared display outline: geometric coverage, angular fade, encoded responses.

No optical surface, source sampling or ray transport is evaluated here.
"""
import numpy as np
from post_refraction_outline import signed_distance
from pixel_quadrature import rounded_rectangle_pixel_rule


def smooth(t):
    t = np.clip(t, 0., 1.)
    return t*t*(3-2*t)


def cap_strength(x, y, half, radius, center, config):
    x = np.asarray(x, float)-center[0]
    y = np.asarray(y, float)-center[1]
    core = half[0]-radius
    side = np.where(x >= 0, 1., -1.)
    angle = np.rad2deg(np.arctan2(-y, x-side*core))
    angle = (angle-np.where(side < 0, 180., 0.)+180.) % 360.-180.
    start, low, hold, end = [config[k] for k in ['start', 'minimum', 'hold', 'recover']]
    if not -90 <= start < low <= hold < end < 90:
        raise ValueError('Ordered cap angles strictly before the joins required')
    down = 1-smooth((angle-start)/(low-start))
    up = smooth((angle-hold)/(end-hold))
    weight = np.where(angle <= low, down, up)
    return np.where(np.abs(x) > core, weight, 1.)


def point_alpha(x, y, half, radius, center, config):
    sigma, power = config['sigma'], config['power']
    if sigma <= 0 or power <= 1 or not np.isfinite(sigma+power):
        raise ValueError('Positive width and smooth inward exponent required')
    d = signed_distance(x, y, half, radius, center)
    inward = np.maximum(-d, 0.)
    return np.where(d <= 0, np.exp(-(inward/sigma)**power), 0.) * cap_strength(x,y,half,radius,center,config)


def integrate(crop, half, radius, center, configs, order, charge, reserve, tail=1e-12):
    x0,y0,x1,y1 = map(int,crop)
    yy,xx = np.mgrid[y0:y1,x0:x1]
    distance = signed_distance(xx,yy,half,radius,center)
    depth = max(c['sigma']*(-np.log(tail))**(1/c['power']) for c in configs)
    active = (distance <= np.sqrt(.5)) & (distance >= -depth-np.sqrt(.5))
    fields = np.zeros((len(configs),)+distance.shape)
    for iy,ix in zip(*np.nonzero(active)):
        charge('quadrature_calls',1);reserve('quadrature_nodes',60*order*order)
        rule=rounded_rectangle_pixel_rule((xx[iy,ix],yy[iy,ix]),half,radius,center=center,order=order)
        points,w=rule['points'],rule['weights'];charge('quadrature_nodes',len(w))
        if not len(w):continue
        assert np.isfinite(w).all() and (w>0).all()
        for j,c in enumerate(configs):
            charge('profile_evaluations',len(w))
            a=point_alpha(points[:,0],points[:,1],half,radius,center,c)
            assert np.isfinite(a).all() and (a>=0).all() and (a<=1).all()
            fields[j,iy,ix]=w@a
    assert np.isfinite(fields).all() and (fields>=0).all() and (fields<=1).all()
    return fields,dict(order=order,active_pixels=int(active.sum()),omitted_pixel_opacity_bound=tail)


def response_delta(image, kind):
    """Unit endpoint minus encoded backing; common bounded operator for all cases."""
    C=np.asarray(image,float);delta=np.zeros_like(C);good=np.isfinite(C).all(axis=-1)
    v=C[good]
    if np.any((v<0)|(v>1)):raise ValueError('Unit encoded backing required')
    if kind=='white':d=1-v
    elif kind=='encoded_lift':
        m=np.max(v,axis=-1,keepdims=True)
        d=v*np.divide(1-m,m,out=np.zeros_like(m),where=m>0)
    elif kind=='linear_lift':
        linear=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
        m=np.max(linear,axis=-1,keepdims=True)
        endpoint=np.divide(linear,m,out=np.zeros_like(linear),where=m>0)
        encoded=np.where(endpoint<=.0031308,12.92*endpoint,1.055*endpoint**(1/2.4)-.055)
        d=encoded-v
    else:raise ValueError(kind)
    delta[good]=d
    return delta


def composite(image, alpha, delta, strength):
    if not 0 <= strength <= 1:raise ValueError('Unit strength required')
    out=image.copy();affected=(alpha>0)&(strength>0)
    if not np.isfinite(image[affected]).all():raise ValueError('Unavailable outline backing')
    raw=image[affected].astype(float)+strength*alpha[affected,None]*delta[affected]
    if np.any((raw<0)|(raw>1)):raise ValueError('Unclipped unit response required')
    out[affected]=raw
    return out
