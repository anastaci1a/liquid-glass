"""Existing geometric bevel law over a shared convex-distance footprint."""
from dataclasses import dataclass
import numpy as np
from geometric_optics import bevel_profile
from rounded_rectangle_back import RoundedRectangleHarmonicBack


@dataclass(frozen=True)
class BevelFootprintBack:
    coordinate: RoundedRectangleHarmonicBack
    depth: float
    power: float = 3.

    def __post_init__(self):
        if type(self.coordinate) is not RoundedRectangleHarmonicBack or self.coordinate.cap_join_width != 0:
            raise ValueError('Exact unsmoothed convex-distance footprint required')
        if not np.isfinite([self.depth, self.power]).all() or self.depth <= 0 or self.power < 3:
            raise ValueError('Positive finite height and power at least three required')

    @property
    def half(self):
        return self.coordinate.half

    @property
    def radius(self):
        return self.coordinate.radius

    @property
    def maximum_height(self):
        return self.depth

    @property
    def slope_bound(self):
        return self.depth*self.power/self.radius

    def radial_profile(self, radius):
        """Actual height and first/second derivatives in physical radial units."""
        h, first, second = bevel_profile(np.asarray(radius, float)/self.radius, 0., self.depth, self.power, 0.)
        return h, first/self.radius, second/self.radius**2

    def height_gradient(self, x, y):
        rho, qx, qy = self.coordinate.footprint(x, y)
        inside = rho <= 1
        h, first, _ = bevel_profile(np.where(inside, rho, 1.), 0., self.depth, self.power, 0.)
        factor = np.divide(first, rho, out=np.zeros_like(rho), where=(rho > 0) & inside)/self.radius**2
        return np.where(inside, h, 0.), factor*qx, factor*qy, inside

    def boundary_mask(self, x, y):
        rho = self.coordinate.footprint(x, y)[0]
        h, _, _, inside = self.height_gradient(x, y)
        return (rho == 1) | (inside & (h == 0))

    def section(self, coordinates, axis='x'):
        v = np.asarray(coordinates, float)
        zero = np.zeros_like(v)
        if axis == 'x':
            x, y = v, zero
        elif axis == 'y':
            x, y = zero, v
        else:
            raise ValueError('Section axis x/y required')
        h, hx, hy, inside = self.height_gradient(x, y)
        return dict(front=np.stack([x, y, zero], -1),
                    back=np.where(inside[..., None], np.stack([x, y, -h], -1), np.nan),
                    inside=inside, gradient=np.stack([hx, hy], -1))
