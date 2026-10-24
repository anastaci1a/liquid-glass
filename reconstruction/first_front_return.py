"""Ordered first upward return between boundary-zero Lipschitz height graphs.

The two directional clearance inequalities, not solid convexity, certify this
single event. This is not a general intersector or a reflected-scene renderer.
"""
import numpy as np
from raised_front_optics import escape_clearance


def trace_first_front_return(front, back, start, direction, charge=None):
    """Trace an upward ray from the actual back to its unique front event.

    Both graphs must share their certified convex projected footprint and vanish
    on its boundary. Every input is a regular physical back event. Rejected
    prerequisites raise before tracing; no shifted origin or replacement path
    is supplied. Brackets use the original ray parameter throughout.
    """
    p, v = np.asarray(start, float), np.asarray(direction, float)
    if p.shape != v.shape or p.ndim != 2 or p.shape[1] != 3 or not len(p):
        raise ValueError('Matched nonempty Nx3 points and directions required')
    if not np.isfinite(p).all() or not np.isfinite(v).all():
        raise ValueError('Finite back events required')
    if np.max(abs(np.linalg.norm(v, axis=-1)-1)) > 1e-10:
        raise ValueError('Unit optical directions required')
    if getattr(front, 'coordinate', None) is None or front.coordinate is not getattr(back, 'coordinate', None):
        raise ValueError('Same certified projected footprint required')
    mf = escape_clearance(v, front.slope_bound, upward=True)
    mb = escape_clearance(v, back.slope_bound, upward=True)
    if np.any(mf <= 0) or np.any(mb <= 0):
        raise ValueError('First-return order lacks positive directional clearance')

    def evaluate(surface, points, label):
        if charge is not None:
            charge(label, len(points))
        return surface.height_gradient(points[:, 0], points[:, 1])

    hb, _, _, ib = evaluate(back, p, 'initial_back_height')
    hf, _, _, inf = evaluate(front, p, 'initial_front_height')
    if not ib.all() or not inf.all() or np.any(hb <= 0) or np.any(hf < 0):
        raise ValueError('Strict interior back launch required')
    initial_residual = p[:, 2]+hb
    if np.max(abs(initial_residual)) > 2e-11 or np.any(p[:, 2]-hf >= 0):
        raise ValueError('Launch is not the actual separated back event')
    low = np.zeros(len(p))
    high = (front.maximum_height-p[:, 2])/v[:, 2]*(1+16*np.finfo(float).eps)

    def level(t):
        q = p+t[:, None]*v
        return q[:, 2]-evaluate(front, q, 'front_root_height')[0]

    if np.any(high <= 0) or np.any(level(high) < 0):
        raise ValueError('Missing front-event upper bracket')
    for iteration in range(40):
        middle = (low+high)/2
        negative = level(middle) < 0
        low = np.where(negative, middle, low)
        high = np.where(negative, high, middle)
        if np.max(high-low) <= 1e-11:
            break
    if np.max(high-low) > 1e-11:
        raise ValueError('Front-event bracket did not converge')
    point = p+((low+high)/2)[:, None]*v
    hf, fx, fy, inside = evaluate(front, point, 'final_front_height')
    hb, _, _, back_inside = evaluate(back, point, 'final_back_height')
    residual = point[:, 2]-hf
    if not inside.all() or not back_inside.all() or np.any(hf+hb <= 0):
        raise ValueError('Front root is not a regular shared-footprint event')
    if np.max(abs(residual)) > 2e-11:
        raise ValueError('Front-event level residual exceeds tolerance')
    normal = np.stack([-fx, -fy, np.ones(len(p))], axis=-1)
    normal /= np.linalg.norm(normal, axis=-1)[:, None]
    if np.any(np.sum(normal*v, axis=-1) <= 0):
        raise ValueError('Front event lacks strict outward incidence')
    return dict(point=point, outward_normal=normal, bracket_low=low,
                bracket_high=high, residual=residual,
                initial_back_residual=initial_residual,
                front_clearance=mf, back_clearance=mb,
                regular_event=np.ones(len(p), bool), iterations=np.array(iteration+1))
