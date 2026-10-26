"""Color-bearing display rim with a finite peak plateau; no optical calls."""
import numpy as np
from ellipse_core_coordinate import EllipseCoreCoordinate
from ellipse_edge_effects import pixel_rule_batch
from outline_response import cap_strength
from edge_color_filter import edge_filter
from environment_radiance import decode_srgb,encode_srgb

def profile(depth, sigma, power, plateau=0.):
    if sigma <= 0 or power <= 1 or plateau < 0:
        raise ValueError('Positive width, smooth exponent, nonnegative plateau required')
    return np.exp(-(np.maximum(np.asarray(depth)-plateau,0)/sigma)**power)

def integrate_profiles(crop,half,radius,center,angular,profiles,order,charge,tail=1e-12):
    x0,y0,x1,y1=crop; yy,xx=np.mgrid[y0:y1,x0:x1]
    coord=EllipseCoreCoordinate(tuple(half),radius)
    charge('distance_points',xx.size)
    sd,_,_=coord.boundary_distance(xx-center[0],yy-center[1])
    depth=max(p['plateau']+p['sigma']*(-np.log(tail))**(1/p['power']) for p in profiles)
    active=(sd<=np.sqrt(.5))&(sd>=-depth-np.sqrt(.5));iy,ix=np.nonzero(active)
    out=np.zeros((len(profiles),)+sd.shape)
    for start in range(0,len(iy),96):
        y,x=iy[start:start+96],ix[start:start+96]
        pixels=np.stack([xx[y,x]-center[0],yy[y,x]-center[1]],1)
        pts,w,owner=pixel_rule_batch(pixels,half,radius,order,charge)
        if not len(w):continue
        charge('distance_points',len(w));d,_,_=coord.boundary_distance(pts[:,0],pts[:,1]);assert d.max()<2e-8
        angular_strength=cap_strength(pts[:,0],pts[:,1],half,radius,(0,0),angular)
        for j,p in enumerate(profiles):
            charge('profile_points',len(w))
            values=profile(np.maximum(-d,0),**p)*angular_strength
            out[j,y,x]=np.bincount(owner,weights=w*values,minlength=len(pixels))
    assert np.isfinite(out).all() and out.min()>=0 and out.max()<1+1e-12
    return out

def apply_color_rim(backing,guide,alpha,exposure=1.4,lift=.4378927114042099):
    """Blend toward a color-bearing endpoint; retain exact zero support."""
    out=backing.copy();a=np.asarray(alpha);active=a>0
    if not active.any():return out
    if np.any(a[active]>1+1e-12):raise ValueError('Unit strength required')
    # Restrict evaluation to supported edge colors; unavailable exterior stays raw.
    v=guide[active]
    endpoint=edge_filter(v,np.ones(v.shape[:-1]),exposure=exposure,lift=lift,desaturation=0.)
    out[active]=backing[active]+a[active,None]*(endpoint-backing[active])
    return out

def apply_luminance_floor_rim(backing,guide,alpha,brightening):
    """Keep source color subject to a minimum linear-luminance highlight.

    Minimal mixing toward neutral white reaches the declared brightness floor.
    This is a display response, not a physical radiance identification.
    """
    if not 0<=brightening<=1:raise ValueError('Unit brightening required')
    out=backing.copy();a=np.asarray(alpha);active=a>0
    if not active.any():return out
    if np.any(a[active]>1+1e-12):raise ValueError('Unit alpha required')
    body=backing[active].astype(float);color=guide[active]
    endpoint=edge_filter(color,np.ones(color.shape[:-1]),exposure=1.4,lift=.4378927114042099,desaturation=0.)
    B=decode_srgb(body);E=decode_srgb(endpoint)
    weights=np.array([.2126,.7152,.0722]);yb=B@weights;ye=E@weights
    required=yb+brightening*(1-yb)
    neutral=np.divide(np.maximum(required-ye,0),1-ye,out=np.zeros_like(ye),where=ye<1)
    if np.any(neutral>1+1e-12):raise ArithmeticError('Unreachable luminance floor')
    target=encode_srgb(E+neutral[:,None]*(1-E));target[np.all(body==1,axis=-1)]=1.
    out[active]=body+a[active,None]*(target-body)
    return out
