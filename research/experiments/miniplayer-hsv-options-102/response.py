"""One requested HSV endpoint comparison; independent of selected optics."""
import numpy as np
from miniplayer_refinement_effects import low_luminance_body

VALUE = 253 / 255


def body_grade(raw, bias, dark_lift):
    return low_luminance_body(raw, VALUE-bias, bias, dark_lift)


def endpoint(guide, fraction):
    if not .6 <= fraction <= 1:
        raise ValueError('Declared saturation range only')
    maximum = np.max(guide, axis=-1, keepdims=True)
    normalized = np.divide(guide, maximum, out=np.ones_like(guide, dtype=float), where=maximum > 0)
    return VALUE * (1-fraction+fraction*normalized)


def overlay(body, guide, alpha, fraction):
    result = body.copy()
    active = alpha > 0
    result[active] = body[active] + alpha[active, None] * (endpoint(guide[active], fraction)-body[active])
    return result
