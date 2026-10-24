"""Ordered primary paths between front z=scale*h and back z=-h.

One boundary-zero height supplies both surfaces and all normals. Global slope
bounds certify primary event order; this is not a multi-reflection intersector.
"""
import numpy as np
from geometric_optics import refract, reflect_direction, fresnel_components


def escape_clearance(direction, slope_bound, upward=False):
    """Sufficient no-reentry margin for a globally Lipschitz height graph."""
    v = np.asarray(direction, float)
    if v.shape[-1] != 3 or not np.isfinite(v).all() or not np.isfinite(slope_bound) or slope_bound < 0:
        raise ValueError('Finite directions and nonnegative slope bound required')
    vertical = v[..., 2] if upward else -v[..., 2]
    return vertical-slope_bound*np.linalg.norm(v[..., :2], axis=-1)


class VerticalScaleBack:
    """Physical height scaling; derivative and bounds scale identically."""
    def __init__(self, base, scale):
        if not np.isfinite(scale) or scale <= 0:
            raise ValueError('Positive finite physical height scale required')
        self.base, self.scale = base, float(scale)
        self.maximum_height = base.maximum_height*scale
        self.slope_bound = base.slope_bound*scale
    def height_gradient(self, x, y):
        h, hx, hy, inside = self.base.height_gradient(x, y)
        return self.scale*h, self.scale*hx, self.scale*hy, inside
    def boundary_mask(self, x, y):
        return self.base.boundary_mask(x, y)


def trace_raised_front_orthographic(back, x, y, scale, index, background_distance, charge=None, front_surface=None):
    if not 0 < scale <= 1 or index < 1 or background_distance <= back.maximum_height:
        raise ValueError('Invalid physical front/index/background parameters')
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    def count(label, n):
        if charge is not None: charge(label, n)
    def hg(X, Y):
        count('height', np.asarray(X).size)
        return back.height_gradient(X, Y)
    if front_surface is None:
        h, hx, hy, inside = hg(x, y)
        front_slope = scale*back.slope_bound
        front_boundary = np.zeros_like(inside)
    else:
        key = front_surface
        while isinstance(key, VerticalScaleBack): key = key.base
        if not hasattr(key, 'coordinate') or key.coordinate is not getattr(back, 'coordinate', None):
            raise ValueError('Independent height graphs require the same certified footprint object')
        count('front_height', x.size)
        h, hx, hy, inside = front_surface.height_gradient(x, y)
        if not np.array_equal(inside, hg(x, y)[3]):
            raise ValueError('Inconsistent front/back membership')
        front_slope = scale*front_surface.slope_bound
        count('front_boundary', x.size)
        front_boundary = front_surface.boundary_mask(x, y)
    count('boundary', x.size)
    boundary = back.boundary_mask(x, y) | front_boundary
    regular = inside & ~boundary
    flat = regular.ravel(); X, Y = x.ravel()[flat], y.ravel()[flat]
    H = h.ravel()[flat]; gx, gy = hx.ravel()[flat], hy.ravel()[flat]
    entry = np.stack([X, Y, scale*H], -1)
    nf = np.stack([-scale*gx, -scale*gy, np.ones_like(H)], -1)
    nf /= np.linalg.norm(nf, axis=-1)[:, None]
    camera = np.zeros_like(entry); camera[:, 2] = -1
    interior, blocked_entry, _ = refract(camera, nf, 1., index)
    if blocked_entry.any(): raise ValueError('Unavailable front entry')
    speed = np.linalg.norm(interior[:, :2], axis=-1)
    margin_b = -interior[:, 2]-back.slope_bound*speed
    margin_f = -interior[:, 2]-front_slope*speed
    if np.any(margin_b <= 0) or np.any(margin_f <= 0):
        raise ValueError('Event order lacks positive clearance certificate')
    low = np.zeros_like(H)
    high = (entry[:, 2]+back.maximum_height)/(-interior[:, 2])*(1+16*np.finfo(float).eps)
    def level(t):
        points = entry+t[:, None]*interior
        return points[:, 2]+hg(points[:, 0], points[:, 1])[0]
    if np.any(level(high) > 0): raise ValueError('Missing upper bracket')
    for iteration in range(40):
        middle = (low+high)/2; positive = level(middle) > 0
        low = np.where(positive, middle, low)
        high = np.where(positive, high, middle)
        if np.max(high-low) <= 1e-11: break
    distance = (low+high)/2
    point = entry+distance[:, None]*interior
    hb, bx, by, occupied = hg(point[:, 0], point[:, 1])
    residual = point[:, 2]+hb
    if not occupied.all() or np.max(abs(residual)) > 2e-11:
        raise ValueError('Invalid back root')
    nb = np.stack([-bx, -by, -np.ones_like(bx)], -1)
    nb /= np.linalg.norm(nb, axis=-1)[:, None]
    outgoing, blocked_exit, discriminant = refract(interior, -nb, index, 1.)
    valid = ~blocked_exit & (outgoing[:, 2] < 0)
    outgoing_margin = np.full_like(H, np.nan)
    outgoing_margin[valid] = escape_clearance(outgoing[valid], back.slope_bound)
    if np.any(outgoing_margin[valid] <= 0):
        raise ValueError('Outgoing no-reentry unresolved: ordered later intersector required')
    t = np.full_like(H, np.nan)
    t[valid] = (-background_distance-point[valid, 2])/outgoing[valid, 2]
    valid &= t >= 0
    source = point[:, :2]+t[:, None]*outgoing[:, :2]
    plane = np.abs(np.sum(np.cross(nf, nb)*interior, axis=-1))
    if np.max(plane) > 1e-10: raise ValueError('Unresolved polarization-basis rotation')
    Rf = fresnel_components(nf[:, 2], 1., index)
    Rb = fresnel_components(np.sum(interior*nb, axis=-1), index, 1.)
    primary = np.mean((1-Rf)*(1-Rb), axis=-1)
    tail = np.mean((1-Rf)*Rb, axis=-1)
    reflected = reflect_direction(camera, nf)
    reflection_margin = escape_clearance(reflected, front_slope, upward=True)
    if np.any(reflection_margin <= 0):
        raise ValueError('Direct front reflection escape unresolved')
    if np.max(abs(Rf.mean(axis=-1)+primary+tail-1)) > 2e-14:
        raise ValueError('Power closure')
    shape = x.shape
    def expand(v):
        a = np.full((x.size,)+v.shape[1:], np.nan, dtype=v.dtype)
        a[flat] = v
        return a.reshape(shape+v.shape[1:])
    SX, SY = x.copy(), y.copy()
    SX.ravel()[flat] = source[:, 0]; SY.ravel()[flat] = source[:, 1]
    SX[boundary] = np.nan; SY[boundary] = np.nan
    complete = ~inside
    complete.ravel()[flat] = valid; complete[boundary] = False
    return dict(X=SX, Y=SY, inside=inside, projected_inside=inside|boundary, regular_entry=regular,
        boundary_unresolved=boundary, complete=complete,
        front=expand(entry), front_normal=expand(nf), back=expand(point),
        outward_normal=expand(nb), interior_direction=expand(interior),
        exit_direction=expand(outgoing), front_reflection_direction=expand(reflected),
        front_reflection_power=expand(Rf.mean(axis=-1)), primary_power=expand(primary),
        retained_back_power=expand(tail), back_bracket_low=expand(low),
        back_bracket_high=expand(high), back_residual=expand(residual),
        discriminant=expand(discriminant), primary_back_clearance=expand(margin_b),
        primary_front_clearance=expand(margin_f), polarization_plane_residual=expand(plane),
        outgoing_back_clearance=expand(outgoing_margin), reflection_front_clearance=expand(reflection_margin),
        iterations=np.array(iteration+1))
