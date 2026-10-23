"""Even longitudinal modulation of an existing physical back height.

The base must certify |x| <= half[0] throughout its footprint and provide
nonnegative height, a global slope bound and an exact boundary classifier.
This wrapper supplies no intersection, normal, image warp or reflected-path
certificate. Its height and full gradient enter the existing primary tracer.
"""
import numpy as np


class LongitudinalHeight:
    def __init__(self, base, strength):
        self.base = base
        self.strength = float(strength)
        self.half = tuple(base.half)
        self.a = float(self.half[0])
        H, M = float(base.maximum_height), float(base.slope_bound)
        if (not np.isfinite([self.strength, self.a, H, M]).all()
                or abs(self.strength) >= 1 or self.a <= 0 or H < 0 or M < 0):
            raise ValueError('Finite bounded height and |strength| < 1 required')
        if not callable(getattr(base, 'boundary_mask', None)):
            raise ValueError('Base must provide its exact boundary classifier')
        e = abs(self.strength)
        self.maximum_height = (1 + e) * H
        self.slope_bound = (1 + e) * M + 2 * e * H / self.a

    def height_gradient(self, x, y):
        x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
        h, hx, hy, inside = self.base.height_gradient(x, y)
        if self.strength == 0:
            return h, hx, hy, inside
        factor = 1 + self.strength * (x / self.a) ** 2
        dx = 2 * self.strength * x / self.a ** 2
        return (factor * h, factor * hx + dx * h, factor * hy, inside)

    def boundary_mask(self, x, y):
        # The strictly positive multiplier preserves the base's zero-height
        # boundary and unresolved crease. Never create a numerical edge band.
        return self.base.boundary_mask(x, y)

    def section(self, values, axis='x'):
        values = np.asarray(values, float)
        zero = np.zeros_like(values)
        if axis == 'x':
            x, y = values, zero
        elif axis == 'y':
            x, y = zero, values
        else:
            raise ValueError('Section axis must be x or y')
        h, hx, hy, inside = self.height_gradient(x, y)
        return dict(front=np.stack([x, y, zero], -1),
                    back=np.where(inside[..., None], np.stack([x, y, -h], -1), np.nan),
                    inside=inside, gradient=np.stack([hx, hy], -1))
