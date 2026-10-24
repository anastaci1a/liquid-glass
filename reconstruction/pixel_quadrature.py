"""Positive camera-pixel area quadrature for an unsmoothed rounded rectangle.

This partitions the actual projected footprint, never a target/error mask.
Weights refer to full pixel area. Finite-order weights do not certify optical
convergence; mapped source knots and illumination transitions need refinement.
"""
import numpy as np


def rounded_rectangle_pixel_rule(pixel_center, half, radius, *, center=(0., 0.),
                                 pixel_width=1., order=16):
    """Return native XY nodes and positive full-pixel-normalized area weights.

    Only ordinary Euclidean rounded rectangles are supported. The calling
    adapter must independently establish exact footprint equivalence.
    """
    px, py = map(float, pixel_center)
    cx, cy = map(float, center)
    a, b = map(float, half)
    r, w = float(radius), float(pixel_width)
    if not np.isfinite([px, py, cx, cy, a, b, r, w]).all():
        raise ValueError('Finite geometry required')
    if min(a, b, r, w) <= 0 or r > min(a, b):
        raise ValueError('Positive extents and valid corner radius required')
    if isinstance(order, bool) or int(order) != order or not 2 <= order <= 64:
        raise ValueError('Integer Gauss order from 2 through 64 required')
    core_x, core_y = a-r, b-r
    xl, xr, yl, yr = px-w/2, px+w/2, py-w/2, py+w/2
    ycuts = sorted(set([yl, py, yr] + [v for v in (cy-core_y, cy+core_y)
                                                  if yl < v < yr]))
    xcuts = [xl, px, xr]
    xcuts += [v for v in (cx-a, cx-core_x, cx+core_x, cx+a) if xl < v < xr]
    # Include crossings with EVERY internal y-partition edge, not just the pixel box.
    for ye in ycuts:
        qy = max(abs(ye-cy)-core_y, 0.)
        if qy <= r:
            span = core_x + np.sqrt(max(0., r*r-qy*qy))
            xcuts += [v for v in (cx-span, cx+span) if xl < v < xr]
    xcuts = sorted(set(xcuts))
    g, gw = np.polynomial.legendre.leggauss(int(order))
    points, weights = [], []
    for left, right in zip(xcuts[:-1], xcuts[1:]):
        mid = (left+right)/2
        if abs(mid-cx) >= a:
            continue
        if abs(mid-cx) <= core_x:
            xx = (left+right)/2 + (right-left)/2*g
            wx = (right-left)/2*gw
        else:
            # Arc parameter removes the square-root singularity at the cap tip.
            sign = 1. if mid > cx else -1.
            q = (np.abs(np.array([left, right])-cx)-core_x)/r
            if np.any(q < -1e-12) or np.any(q > 1+1e-12):
                raise ArithmeticError('Unpartitioned cap interval')
            theta = np.arccos(np.clip(q, 0., 1.))
            lo, hi = sorted(theta)
            tt = (lo+hi)/2+(hi-lo)/2*g
            xx = cx+sign*(core_x+r*np.cos(tt))
            wx = (hi-lo)/2*gw*r*np.sin(tt)
        for x, xweight in zip(xx, wx):
            qx = max(abs(x-cx)-core_x, 0.)
            ymax = core_y+np.sqrt(max(0., r*r-qx*qx))
            low, high = max(yl, cy-ymax), min(yr, cy+ymax)
            if high <= low:
                continue
            edges = [low]+[v for v in ycuts if low < v < high]+[high]
            for bottom, top in zip(edges[:-1], edges[1:]):
                yy = (bottom+top)/2+(top-bottom)/2*g
                ww = xweight*(top-bottom)/2*gw/(w*w)
                points.append(np.column_stack([np.full_like(yy, x), yy]))
                weights.append(ww)
    if not points:
        return {'points': np.empty((0, 2)), 'weights': np.empty(0)}
    return {'points': np.concatenate(points), 'weights': np.concatenate(weights)}
