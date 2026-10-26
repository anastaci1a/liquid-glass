"""Finite display-filter strength over an edge field, not a white endpoint."""
import numpy as np
from environment_radiance import decode_srgb,encode_srgb

def edge_filter(image,alpha,exposure=1.25,lift=.035,desaturation=.1):
    if not (exposure>=1 and lift>=0 and 0<=desaturation<=1):
        raise ValueError('Brightening exposure, nonnegative lift and unit desaturation required')
    out=image.copy();active=np.asarray(alpha)>0
    if not active.any():return out
    if np.any(np.asarray(alpha)[active]>1+1e-12):raise ValueError('Unit strength field required')
    v=image[active].astype(float)
    if not np.isfinite(v).all() or np.any((v<0)|(v>1)):raise ValueError('Finite unit backing required')
    a=np.asarray(alpha)[active,None];linear=decode_srgb(v);p=linear.max(-1,keepdims=True)
    e=1+(exposure-1)*a;b=lift*a;s=desaturation*a
    q=(p+b)/(p+b+(1-p)/e)
    # Black has a neutral direction and lifts to gray. It is never divided by zero.
    direction=np.divide(linear,p,out=np.ones_like(linear),where=p>0)
    value=q*((1-s)*direction+s)
    encoded=encode_srgb(value)
    if not np.isfinite(encoded).all() or np.any((encoded<0)|(encoded>1+1e-14)):
        raise ArithmeticError('Filter left the display range')
    encoded[np.all(v==1,axis=-1)]=1.
    out[active]=encoded
    return out
