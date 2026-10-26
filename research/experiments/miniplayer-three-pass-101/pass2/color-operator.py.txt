"""Bounded display color contrasts, separate from optical transport."""
import numpy as np
from environment_radiance import decode_srgb, encode_srgb
from miniplayer_refinement_effects import soft_channel_rim


def interior_chroma(encoded, factor=1.):
    """Raise chroma at fixed linear luminance, stopping at the unit gamut."""
    if not 1 <= factor <= 2:
        raise ValueError('Invalid chroma factor')
    if factor == 1:
        return encoded.copy()
    linear = decode_srgb(np.asarray(encoded, float))
    y = linear @ np.array([.2126, .7152, .0722])
    delta = linear - y[..., None]
    upper = np.full_like(delta, np.inf)
    lower = np.full_like(delta, np.inf)
    np.divide(1-y[..., None], delta, out=upper, where=delta > 0)
    np.divide(-y[..., None], delta, out=lower, where=delta < 0)
    limit = np.minimum(upper, lower).min(-1)
    scale = np.minimum(factor, np.nextafter(limit, 0))
    result = y[..., None] + scale[..., None]*delta
    if not np.isfinite(result).all() or result.min() < -2e-15 or result.max() > 1+2e-15:
        raise ArithmeticError('Unbounded chroma result')
    return encode_srgb(result)


def bright_colored_rim(body, guide, alpha, exposure=1., saturation=1., chroma_weighted=False):
    """Brighten a guide-derived endpoint; preserve peak through chroma change.

    Exposure acts in linear light. Chroma expansion acts in encoded RGB
    around its largest channel, with a bounded common factor per color.
    This is a display hypothesis, not calibrated radiance.
    """
    if not 1 <= exposure <= 4 or not 1 <= saturation <= 3:
        raise ValueError('Invalid endpoint controls')
    active = alpha > 0
    if not active.any():
        return body.copy()
    endpoint = soft_channel_rim(body, guide, active.astype(float), curve_power=1.75)
    color = endpoint[active].astype(float)
    if exposure != 1:
        effective = exposure
        if chroma_weighted:
            raw = guide[active].astype(float)
            peak = raw.max(-1)
            strength = np.divide(peak-raw.min(-1), peak, out=np.zeros_like(peak), where=peak > 0)
            effective = (1+(exposure-1)*strength)[:, None]
        color = encode_srgb(1-(1-decode_srgb(color))**effective)
    if saturation != 1:
        peak = color.max(-1, keepdims=True)
        spread = peak-color
        maximum = spread.max(-1, keepdims=True)
        limit = np.divide(peak, maximum, out=np.full_like(peak, np.inf), where=maximum > 0)
        factor = np.minimum(saturation, np.nextafter(limit, 0))
        color = peak-factor*spread
    color[np.all(body[active] == 1, axis=-1)] = 1.
    if not np.isfinite(color).all() or color.min() < -2e-15 or color.max() > 1+2e-15:
        raise ArithmeticError('Unbounded rim endpoint')
    result = body.copy()
    result[active] = body[active]+alpha[active, None]*(color-body[active])
    return result
