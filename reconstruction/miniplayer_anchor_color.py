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
