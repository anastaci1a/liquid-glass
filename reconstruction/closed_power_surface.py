"""One closed convex power solid over the ordinary rounded footprint.

The same implicit F defines both sheets, intersection gradients and sections.
Positive unequal front/back heights preserve a C1 level function across z=0.
No slope cap, image map or independent normal is supplied.
"""
import numpy as np
from rounded_rectangle_back import RoundedRectangleHarmonicBack


class ClosedPowerSurface:
    def __init__(self, half, radius, front_height, back_height, power=2.):
        if not np.isfinite([*half, radius, front_height, back_height, power]).all():
            raise ValueError('Finite physical parameters required')
        if min(front_height, back_height) <= 0 or power < 2:
            raise ValueError('Positive face heights and convex power >=2 required')
        self.coordinate = RoundedRectangleHarmonicBack(tuple(half), radius)
        self.half = tuple(map(float, half))
        self.radius = float(radius)
        self.front_depth = float(front_height)
        self.back_depth = float(back_height)
        self.power = float(power)

    @property
    def half_extents(self):
        return (*self.half, (self.front_depth+self.back_depth)/2)

    @property
    def center(self):
        return (0., 0., (self.front_depth-self.back_depth)/2)

    def level_gradient(self, points):
        p = np.asarray(points, float)
        if p.shape[-1:] != (3,) or not np.isfinite(p).all():
            raise ValueError('Finite three-dimensional points required')
        x, y, z = np.moveaxis(p, -1, 0)
        rho, qx, qy = self.coordinate.footprint(x, y)
        h = np.where(z >= 0, self.front_depth, self.back_depth)
        factor = self.power*rho**(self.power-2)/self.radius**2
        f = rho**self.power+(z/h)**2-1
        return f, np.stack([factor*qx, factor*qy, 2*z/h**2], -1)

    def boundary_mask(self, x, y):
        x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
        a, b = self.half
        lines = ((abs(x) == a) & (abs(y) <= b-self.radius)) | ((abs(y) == b) & (abs(x) <= a-self.radius))
        return (self.coordinate.footprint(x, y)[0] == 1) | lines

    def sheet_heights(self, x, y):
        rho = self.coordinate.footprint(x, y)[0]
        arg = np.where(rho <= 1, 1-rho**self.power, np.nan)
        root = np.sqrt(arg)
        return self.front_depth*root, -self.back_depth*root

    def front_height(self, x, y):
        rho = self.coordinate.footprint(x, y)[0]
        return self.sheet_heights(x, y)[0], (rho < 1) & ~self.boundary_mask(x, y)

    def section(self, values, axis='y'):
        v = np.asarray(values, float)
        if axis == 'x':
            x, y = v, np.zeros_like(v)
        elif axis == 'y':
            x, y = np.zeros_like(v), v
        else:
            raise ValueError('Axis x or y required')
        front, back = self.sheet_heights(x, y)
        return np.stack([x, y, front], -1), np.stack([x, y, back], -1)
