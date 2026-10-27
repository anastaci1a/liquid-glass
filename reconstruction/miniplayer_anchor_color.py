"""Held, hue-preserving final display responses from explicit color anchors."""
import numpy as np


def curve(values, specification):
    """Cubic Hermite curve with constant extension beyond its knot range."""
    x=np.asarray(specification['x'],float);y=np.asarray(specification['y'],float);m=np.asarray(specification['slopes'],float)
    v=np.clip(np.asarray(values,float),x[0],x[-1]);i=np.clip(np.searchsorted(x,v,side='right')-1,0,len(x)-2)
    h=x[i+1]-x[i];t=(v-x[i])/h
    return (2*t**3-3*t**2+1)*y[i]+(t**3-2*t**2+t)*h*m[i]+(-2*t**3+3*t**2)*y[i+1]+(t**3-t**2)*h*m[i+1]


def response(rgb, specification):
    """Encoded RGB in/out; final color, without subsequent optical scaling."""
    rgb=np.asarray(rgb,float)
    if rgb.shape[-1]!=3 or not np.isfinite(rgb).all() or np.any((rgb<0)|(rgb>1)):
        raise ValueError('Finite unit encoded RGB required')
    value=rgb.max(-1);minimum=rgb.min(-1)
    saturation=np.divide(value-minimum,value,out=np.zeros_like(value),where=value>0)
    neutral=curve(value,specification['neutral'])
    fraction=curve(value,specification['saturation_multiplier'])
    offset=curve(value,specification['value_logit_offset'])
    target_value=1/(1+np.exp(-(np.log(neutral/(1-neutral))+saturation*offset)))
    normalized=np.divide(rgb,value[...,None],out=np.ones_like(rgb),where=value[...,None]>0)
    result=target_value[...,None]*(1-fraction[...,None]*(1-normalized))
    if not np.isfinite(result).all() or np.any((result<0)|(result>1)):
        raise ArithmeticError('Unbounded calibrated response')
    return result


def body_response(rgb, calibration):
    return response(rgb,calibration['roles']['body'])


def outline_endpoint(rgb, calibration):
    return response(rgb,calibration['roles']['outline'])


def adjusted_outline_endpoint(rgb, calibration):
    """Existing endpoint plus an explicit, optional warm-hue correction."""
    result = outline_endpoint(rgb, calibration)
    adjustment = calibration.get('outline_hue_adjustment')
    if adjustment is None:
        return result
    rgb = np.asarray(rgb, float)
    maximum = rgb.max(-1)
    delta = maximum-rgb.min(-1)
    hue = np.zeros_like(maximum)
    for channel in [2, 1, 0]:
        take = (delta > 0) & (maximum == rgb[..., channel])
        a, b = ((0, 1) if channel == 2 else (2, 0) if channel == 1 else (1, 2))
        hue[take] = ((rgb[..., a][take]-rgb[..., b][take])/delta[take]+2*channel) % 6
    hue /= 6
    distance = (hue-adjustment['center_hue']+.5) % 1-.5
    width = adjustment['half_width']
    weight = np.where(abs(distance) < width, .5*(1+np.cos(np.pi*distance/width)), 0.)
    offset = curve(maximum, adjustment['offset_curve'])*weight
    active = (delta > 0) & (offset != 0)
    if not active.any():
        return result
    color = result[active]
    value = color.max(-1)
    saturation = (value-color.min(-1))/value
    h = ((hue[active]+offset[active]) % 1)*6
    sector = np.floor(h).astype(int) % 6
    fraction = h-np.floor(h)
    p = value*(1-saturation)
    q = value*(1-saturation*fraction)
    t = value*(1-saturation*(1-fraction))
    rotated = np.empty_like(color)
    for i, channels in enumerate([(value,t,p),(q,value,p),(p,value,t),(p,q,value),(t,p,value),(value,p,q)]):
        mask = sector == i
        rotated[mask] = np.stack([x[mask] for x in channels],axis=-1)
    result[active] = rotated
    return result


def outline_display_endpoint(rgb, calibration):
    """Optional HSV-value lift after the calibrated hue/saturation response."""
    result = adjusted_outline_endpoint(rgb, calibration)
    lift = float(calibration.get('outline_value_lift', 0.))
    if not 0 <= lift <= .05:
        raise ValueError('Outline value lift must lie between zero and .05')
    if lift == 0:
        return result
    value = result.max(-1, keepdims=True)
    raised = np.minimum(value + lift, 1.)
    ratio = np.divide(result, value, out=np.ones_like(result), where=value > 0)
    return ratio * raised
