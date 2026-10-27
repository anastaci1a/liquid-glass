"""Shared horizontal outline width and brightness profiles, in full-width units."""
import numpy as np
from miniplayer_refinement_effects import pixel_rule_batch
from outline_response import cap_strength


def ease(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)


def profiles(fraction, config):
    x = np.asarray(fraction)
    left, shoulder, right = (config[k] for k in ('left_fraction', 'shoulder_fraction', 'right_fraction'))
    assert 0 < left < config['brightness_start'] < shoulder < right < 1
    width = config['left_scale'] + (config['middle_scale']-config['left_scale'])*ease((x-left)/(shoulder-left))
    width += (config['right_scale']-config['middle_scale'])*np.clip((x-shoulder)/(right-shoulder), 0, 1)
    reduction = config['brightness_increase_reduction']*(1-ease((x-left)/(config['brightness_start']-left)))
    return config['base_scale']*width, reduction


def integrate(crop, coordinate, center, angular, config, order, charge, pixel_mask=None, tail=1e-10):
    x0,y0,x1,y1=crop; yy,xx=np.mgrid[y0:y1,x0:x1]
    charge('distance_points',xx.size)
    sd,_,_=coordinate.boundary_distance(xx-center[0],yy-center[1])
    maximum=config['base_scale']*config['right_scale']*(config['plateau_native']+config['fade_native']*np.sqrt(-np.log(tail)))
    mask=(sd<=np.sqrt(.5))&(sd>=-maximum-np.sqrt(.5))
    if pixel_mask is not None:mask &= pixel_mask
    iy,ix=np.nonzero(mask);out=np.zeros((2,)+sd.shape)
    for start in range(0,len(iy),64):
        i,j=iy[start:start+64],ix[start:start+64]
        xy=np.stack([xx[i,j]-center[0],yy[i,j]-center[1]],1)
        pts,w,owner=pixel_rule_batch(xy,coordinate,order,charge)
        if not len(w):continue
        charge('distance_points',len(w));d,_,_=coordinate.boundary_distance(pts[:,0],pts[:,1]);assert d.max()<2e-8
        scale,reduction=profiles((pts[:,0]+coordinate.half[0])/(2*coordinate.half[0]),config)
        angular_strength=cap_strength(pts[:,0],pts[:,1],coordinate.half,coordinate.original_radius,(0,0),angular)
        charge('profile_points',2*len(w))
        v=np.exp(-(np.maximum(-d-config['plateau_native']*scale,0)/(config['fade_native']*scale))**2)*angular_strength
        out[0,i,j]=np.bincount(owner,weights=w*v,minlength=len(xy))
        out[1,i,j]=np.bincount(owner,weights=w*v*reduction,minlength=len(xy))
    assert np.isfinite(out).all() and out.min()>=0 and out[0].max()<=1+1e-12
    assert np.all(out[1]<=config['brightness_increase_reduction']*out[0]+1e-14)
    return out
