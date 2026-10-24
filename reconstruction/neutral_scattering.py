"""Neutral linear-light scattering under a normalized white-illumination prior.

This is a material hypothesis, not recovered scene radiance or angular transport.
It does not change coordinates, normals, filters or interface powers.
"""
import numpy as np
from environment_radiance import decode_srgb


def white_scattering_response(incident_linear, transmission, white_level=1.):
    """Bounded neutral mixture; identical parameters apply to every RGB channel."""
    light = np.asarray(incident_linear, dtype=float)
    if light.shape[-1:] != (3,) or not np.isfinite(light).all():
        raise ValueError('Finite RGB incident light required')
    if np.any(light < 0) or np.any(light > 1):
        raise ValueError('Normalized incident light must lie in [0,1]')
    if not np.isscalar(transmission) or not np.isfinite(transmission) or not 0 <= transmission <= 1:
        raise ValueError('One shared transmission in [0,1] required')
    if not np.isscalar(white_level) or not np.isfinite(white_level) or not 0 <= white_level <= 1:
        raise ValueError('One shared normalized white level required')
    return white_level * (transmission * light + (1-transmission))


def match_encoded_material_anchors(gain, bias):
    """Derive mixture from old white and middle-gray anchors, without target data."""
    if not np.isfinite([gain, bias]).all() or gain < 0 or bias < 0 or not 0 < gain+bias <= 1:
        raise ValueError('Positive bounded encoded material anchors required')
    white = float(decode_srgb(gain+bias))
    middle = float(decode_srgb(.5*gain+bias))
    transmission = (1-middle/white)/(1-float(decode_srgb(.5)))
    if not 0 <= transmission <= 1:
        raise ValueError('The supplied anchors do not define a passive mixture')
    return dict(transmission=transmission, white_level=white,
                middle_linear=middle, anchor_encoded=.5)
