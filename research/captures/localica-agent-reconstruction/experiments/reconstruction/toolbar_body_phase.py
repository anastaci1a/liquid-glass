"""Geometry-defined image-coordinate potential; NOT a recovered optical solid.

Psi=.5*lambda*z**2*S7(clip(1-sqrt(T),0,1)). Only its added map is
conservative. The inherited map, source and material are untouched. No renderer.
Pills use their major axis. Explicit true-circle controls require an axis and
are anisotropic; no automatic orientation-invariant circle limit is asserted.
"""
import numpy as np
from crowned_footprint import field, longitudinal


def _axis(half, circle, axis):
    half = tuple(float(v) for v in half)
    if len(half) != 2 or not all(np.isfinite(v) and v > 0 for v in half):
        raise ValueError('Two positive finite half extents required')
    if circle:
        if half[0] != half[1] or axis is None:
            raise ValueError('Explicit circle requires equal extents and a declared unit axis')
        e = np.asarray(axis, float)
        if e.shape != (2,) or not np.all(np.isfinite(e)) or abs(e@e-1) > 1e-12:
            raise ValueError('Declared circle axis must be a finite unit vector')
    else:
        if half[0] == half[1] or axis is not None:
            raise ValueError('Pill major axis must be unique; no pill axis override')
        e = np.array([1., 0.]) if half[0] > half[1] else np.array([0., 1.])
    return half, e


def geometry(x, y, half, softness, *, circle=False, axis=None):
    half, e = _axis(half, circle, axis)
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    if circle:
        R = half[0]
        T, gx, gy = (x*x+y*y)/(R*R), 2*x/(R*R), 2*y/(R*R)
    else:
        T, gx, gy = field(x, y, half, softness)
    return x, y, T, gx, gy, e


def s7(u):
    u = np.clip(np.asarray(u, float), 0, 1)
    v = np.minimum(u, 1-u)
    tail = v**4*(35+v*(-84+v*(70-20*v)))
    return np.where(u <= .5, tail, 1-tail)


def potential(x, y, half, softness, amplitude=1., *, circle=False, axis=None):
    if not np.isfinite(amplitude):
        raise ValueError('Finite dimensionless amplitude required')
    x, y, T, gx, gy, e = geometry(x, y, half, softness, circle=circle, axis=axis)
    if amplitude == 0:
        return np.zeros_like(T)
    u = np.clip(1-np.sqrt(T), 0, 1)
    z = e[0]*x+e[1]*y
    return .5*amplitude*z*z*s7(u)


def addition(x, y, half, softness, amplitude=1., *, circle=False, axis=None):
    if not np.isfinite(amplitude):
        raise ValueError('Finite dimensionless amplitude required')
    x, y, T, gx, gy, e = geometry(x, y, half, softness, circle=circle, axis=axis)
    if amplitude == 0:
        return np.zeros_like(T), np.zeros_like(T)
    u = np.clip(1-np.sqrt(T), 0, 1)
    z = e[0]*x+e[1]*y
    response = s7(u)
    coupling = 35*z*z*u**3*T
    # Exact cancellation S7'(u)/(4sqrt(T))=35u^3*T on 0<T<1.
    # No division bysqrt(T); atT0 the declared value is exactly affine -lambda*z*e.
    return (amplitude*(-z*response*e[0]+coupling*gx),
            amplitude*(-z*response*e[1]+coupling*gy))


def displacement_bound(half, softness, amplitude=1., *, circle=False, axis=None):
    if not np.isfinite(amplitude):
        raise ValueError('Finite dimensionless amplitude required')
    half, e = _axis(half, circle, axis)
    a, L = max(half), min(half)
    G = 1. if circle else max(1., abs(float(longitudinal(np.asarray(a), a, L, softness)[1])))
    unit = a+(35/32)*a*a*G/L
    return {'major_half': a, 'minor_half': L, 'max_depth_gradient_factor': G,
            'unit_displacement_bound': unit, 'amplitude': float(amplitude),
            'absolute_displacement_bound': abs(float(amplitude))*unit,
            'formula': '|deltaF|<=|lambda|[a+35*a^2*G/(32L)]',
            'proof': '|gradT|<=2sqrt(T)G/L by monotone convexq; max s^3(1-s)^3=1/64, s=sqrt(T).',
            'limits': 'Analytic real-arithmetic inequality on the footprint; displayed constants use floating evaluation, not interval arithmetic. No ray/source domain or native acceptance claim.'}
