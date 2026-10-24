"""Explicit hypothetical scene radiance, independent of image coordinates.

The first-return helper requires a separate same-surface event-order certificate.
It does not trace later events or claim that the environment was observed.
"""
import numpy as np
from geometric_optics import fresnel_components, reflect_direction, refract


def decode_srgb(encoded):
    c = np.asarray(encoded, float)
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def encode_srgb(linear):
    c = np.asarray(linear, float)
    if np.any(c < 0):
        raise ValueError('Negative radiance')
    return np.where(c <= .0031308, 12.92*c, 1.055*c**(1/2.4)-.055)


def annular_environment(directions, inner_degrees=30., outer_degrees=80., shoulder_degrees=10.):
    """Unit white angular emitter about +z; no position/outline input."""
    d = np.asarray(directions, float)
    if d.shape[-1] != 3 or not np.isfinite(d).all() or np.any(abs(np.linalg.norm(d, axis=-1)-1) > 1e-10):
        raise ValueError('Finite unit environment directions required')
    if not 0 < shoulder_degrees < (outer_degrees-inner_degrees)/2 or not 0 <= inner_degrees < outer_degrees <= 180:
        raise ValueError('Invalid angular emitter')
    theta = np.rad2deg(np.arccos(np.clip(d[..., 2], -1, 1)))
    rise = np.clip((theta-inner_degrees)/shoulder_degrees, 0, 1)
    fall = np.clip((outer_degrees-theta)/shoulder_degrees, 0, 1)
    return (rise*rise*(3-2*rise))*(fall*fall*(3-2*fall))


def certified_first_return(outward_back_normal, index=1.5):
    """Separate s/p first-return power and direction, preserving TIR tail.

    Caller must certify that the actual initial back reflection next meets the
    flat front. This routine alone is not an ordered intersection certificate.
    Normal initial entry keeps these first two incidence planes aligned.
    """
    normal = np.asarray(outward_back_normal, float)
    if np.any(normal[..., 2] >= 0):
        raise ValueError('Actual downward back outward normal required')
    incident = np.zeros_like(normal); incident[..., 2] = -1
    reflected = reflect_direction(incident, normal)
    if np.any(reflected[..., 2] <= 0):
        raise ValueError('First front return not upward')
    front_normal = np.zeros_like(normal); front_normal[..., 2] = -1
    outgoing, blocked, discriminant = refract(reflected, front_normal, index, 1.)
    R0 = fresnel_components(1., 1., index)
    Rb = fresnel_components(-normal[..., 2], index, 1.)
    Rf = fresnel_components(reflected[..., 2], index, 1.)
    T0 = 1-R0
    primary = np.mean(T0*(1-Rb), axis=-1)
    return_power = np.mean(T0*Rb*(1-Rf), axis=-1)
    tail = np.mean(T0*Rb*Rf, axis=-1)
    closure = R0.mean()+primary+return_power+tail
    if np.max(abs(closure-1)) > 2e-14 or np.any(return_power[blocked] != 0):
        raise ValueError('Invalid first-return power partition')
    field = np.zeros_like(primary)
    field[~blocked] = annular_environment(outgoing[~blocked])
    initial_field = float(annular_environment(np.array([0., 0., 1.])))
    return dict(reflected_direction=reflected, environment_direction=outgoing,
                blocked=blocked, discriminant=discriminant,
                primary_power=primary, first_return_power=return_power,
                retained_tail=tail, initial_front_power=float(R0.mean()),
                unit_emitter_radiance=return_power*field+R0.mean()*initial_field,
                closure_max_error=float(np.max(abs(closure-1))))
