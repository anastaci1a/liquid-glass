"""Convex distance coordinate for an ellipse dilated by a disk.

The closest ellipse point supplies the distance and its actual gradient.
No image deformation, fitted normals, or source sampling is involved.
"""
from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class EllipseCoreCoordinate:
    half: tuple
    radius: float
    counter: object = field(default=None, compare=False, repr=False)

    def __post_init__(self):
        h = tuple(float(v) for v in self.half)
        if len(h) != 2 or not np.isfinite([*h, self.radius]).all():
            raise ValueError('Finite two-dimensional extents required')
        if self.radius <= 0 or min(h) <= self.radius:
            raise ValueError('Strictly positive inner ellipse axes required')
        object.__setattr__(self, 'half', h)
        object.__setattr__(self, 'radius', float(self.radius))

    def distance_gradient(self, x, y):
        x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
        if not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError('Finite coordinates required')
        if self.counter is not None:
            self.counter('coordinate_queries', x.size)
        a, b = np.asarray(self.half)-self.radius
        u, v = np.abs(x), np.abs(y)
        outside = (u/a)**2+(v/b)**2 > 1
        d, nx, ny = (np.zeros_like(x) for _ in range(3))
        U, V = u[outside], v[outside]
        if not U.size:
            return d, nx, ny
        aa, bb = a*a, b*b
        # Each single-component root is a lower bound for the sum root.
        lam = np.maximum(np.maximum(a*(U-a), b*(V-b)), 0.)
        for _ in range(32):
            if self.counter is not None:
                self.counter('projection_iteration_points', U.size)
            A, B = aa+lam, bb+lam
            fx, fy = (a*U/A)**2, (b*V/B)**2
            f = fx+fy-1
            if np.max(np.abs(f)) <= 4e-14:
                break
            deriv = -2*(fx/A+fy/B)
            lam = np.maximum(lam-f/deriv, 0.)
        if np.max(np.abs((a*U/(aa+lam))**2+(b*V/(bb+lam))**2-1)) > 2e-12:
            raise ArithmeticError('Unresolved closest-ellipse projection')
        ex, ey = aa*U/(aa+lam), bb*V/(bb+lam)
        dx, dy = U-ex, V-ey
        dd = np.hypot(dx, dy)
        if np.any(dd <= 0):
            raise ArithmeticError('Outside ellipse has no positive distance')
        d[outside] = dd
        nx[outside] = dx/dd*np.sign(x[outside])
        ny[outside] = dy/dd*np.sign(y[outside])
        return d, nx, ny

    def footprint(self, x, y):
        x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
        d, nx, ny = self.distance_gradient(x, y)
        rho = d/self.radius
        # Exact named extrema are boundary events, not transmitted launches.
        poles = ((np.abs(x) == self.half[0]) & (y == 0)) | ((x == 0) & (np.abs(y) == self.half[1]))
        rho = np.where(poles, 1., rho)
        return rho, d*nx, d*ny

    def boundary_distance(self, x, y):
        """Exact signed distance outside the core; truncated at -radius inside.

        The truncated core is sufficient for short exterior/inner-edge effects.
        It must not be advertised as exact deep-interior signed distance.
        """
        d, nx, ny = self.distance_gradient(x, y)
        return d-self.radius, nx, ny


from spline_height_back import SplineFootprintBack


class EllipseCoreSplineBack(SplineFootprintBack):
    """Same actual radial spline on a new, explicitly certified coordinate."""
    def __init__(self, half, radius, breaks, height_controls, counter=None):
        super().__init__(half, radius, breaks, height_controls)
        self.coordinate = EllipseCoreCoordinate(tuple(half), radius, counter)
        # Distance to a closed convex core is 1-Lipschitz, so the inherited
        # radial derivative/radius bound applies without a normal adjustment.
