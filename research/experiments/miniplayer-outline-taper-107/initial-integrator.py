"""Hue-preserving outline with a proportional horizontal width transition."""
import numpy as np
from miniplayer_refinement_effects import pixel_rule_batch
from outline_response import cap_strength


def transition(x, half_length, left, right):
    if not 0 <= left < right <= 1 or half_length <= 0:
        raise ValueError('Ordered normalized transition required')
    return np.clip(((np.asarray(x) + half_length)/(2*half_length)-left)/(right-left), 0, 1)


def integrate_taper(crop, coordinate, center, angular, config, order, charge, tail=1e-10):
    """Integrate alpha and its brightness-reduction moment over actual pixels.

    Color is the retained pixel guide. Width and reduction are evaluated at
    quadrature nodes, with full-pixel weights and no occupied-area normalization.
    """
    x0,y0,x1,y1=crop
    yy,xx=np.mgrid[y0:y1,x0:x1]
    charge('distance_points',xx.size)
    sd,_,_=coordinate.boundary_distance(xx-center[0],yy-center[1])
    base=config['base_scale'];plateau=config['plateau_native'];fade=config['fade_native']
    maximum=base*max(config['left_scale'],config['right_scale'])*(plateau+fade*np.sqrt(-np.log(tail)))
    iy,ix=np.nonzero((sd<=np.sqrt(.5))&(sd>=-maximum-np.sqrt(.5)))
    out=np.zeros((2,)+sd.shape)
    for start in range(0,len(iy),64):
        i,j=iy[start:start+64],ix[start:start+64]
        xy=np.stack([xx[i,j]-center[0],yy[i,j]-center[1]],1)
        pts,w,owner=pixel_rule_batch(xy,coordinate,order,charge)
        if not len(w):continue
        charge('distance_points',len(w));d,_,_=coordinate.boundary_distance(pts[:,0],pts[:,1])
        assert d.max()<2e-8
        t=transition(pts[:,0],coordinate.half[0],config['left_fraction'],config['right_fraction'])
        scale=base*(config['left_scale']+(config['right_scale']-config['left_scale'])*t)
        ang=cap_strength(pts[:,0],pts[:,1],coordinate.half,coordinate.original_radius,(0,0),angular)
        charge('profile_points',2*len(w))
        v=np.exp(-(np.maximum(-d-plateau*scale,0)/(fade*scale))**2)*ang
        out[0,i,j]=np.bincount(owner,weights=w*v,minlength=len(xy))
        out[1,i,j]=np.bincount(owner,weights=w*v*config['brightness_increase_reduction']*(1-t),minlength=len(xy))
    assert np.isfinite(out).all() and out.min()>=0 and out[0].max()<=1+1e-12
    assert np.all(out[1]<=config['brightness_increase_reduction']*out[0]+1e-14)
    return out


def compose(body, guide, endpoint, alpha, reduction):
    """Reduce only the positive value increase, retaining endpoint hue/S."""
    active=alpha>0
    peak=endpoint.max(-1)
    lift=np.maximum(peak-guide[active].max(-1),0)
    unit=np.divide(endpoint,peak[:,None],out=np.zeros_like(endpoint),where=peak[:,None]>0)
    result=body.copy()
    result[active]=body[active]+alpha[active,None]*(endpoint-body[active])-reduction[active,None]*lift[:,None]*unit
    return result
