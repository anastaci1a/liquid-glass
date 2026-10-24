"""Ordered primary paths between front z=scale*h and back z=-h.

One boundary-zero height supplies both surfaces and all normals. Global slope
bounds certify primary event order; this is not a multi-reflection intersector.
"""
import numpy as np
from geometric_optics import refract, reflect_direction, fresnel_components


def trace_raised_front_orthographic(back, x, y, scale, index, background_distance, charge=None):
    if not 0 < scale <= 1 or index < 1 or background_distance <= back.maximum_height:
        raise ValueError('Invalid physical front/index/background parameters')
    x, y = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float))
    def count(label, n):
        if charge is not None: charge(label, n)
    def hg(X, Y):
        count('height', np.asarray(X).size)
        return back.height_gradient(X, Y)
    h, hx, hy, inside = hg(x, y)
    count('boundary', x.size)
    boundary = back.boundary_mask(x, y)
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
    margin_f = -interior[:, 2]-scale*back.slope_bound*speed
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
    return dict(X=SX, Y=SY, inside=inside, regular_entry=regular,
        boundary_unresolved=boundary, complete=complete,
        front=expand(entry), front_normal=expand(nf), back=expand(point),
        outward_normal=expand(nb), interior_direction=expand(interior),
        exit_direction=expand(outgoing), front_reflection_direction=expand(reflected),
        front_reflection_power=expand(Rf.mean(axis=-1)), primary_power=expand(primary),
        retained_back_power=expand(tail), back_bracket_low=expand(low),
        back_bracket_high=expand(high), back_residual=expand(residual),
        discriminant=expand(discriminant), primary_back_clearance=expand(margin_b),
        primary_front_clearance=expand(margin_f), polarization_plane_residual=expand(plane),
        iterations=np.array(iteration+1))
