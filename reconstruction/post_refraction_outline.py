"""Independent display outline over a frozen completed reconstruction.

This operator never traces rays, modifies optical normals, or samples a source.
Distances and widths use native pixels. The analytic inward fade has no cutoff.
"""
import numpy as np
from pixel_quadrature import rounded_rectangle_pixel_rule


def signed_distance(x, y, half, radius, center=(0., 0.)):
    """Exact Euclidean signed distance; negative inside the rounded rectangle."""
    qx = np.abs(np.asarray(x, float)-center[0])-(half[0]-radius)
    qy = np.abs(np.asarray(y, float)-center[1])-(half[1]-radius)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)-radius


def inward_opacity(distance, sigma):
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError('Positive finite width required')
    d = np.asarray(distance, float)
    return np.where(d <= 0, np.exp(-np.square(d/sigma)), 0.)


def pixel_opacity(crop, half, radius, center, sigma, *, order=16,
                  tail_bound=1e-15, charge=lambda key, n: None,
                  reserve=lambda key, n: None):
    """Full-pixel integral with a declared bound on omitted deep-interior tails."""
    if not 0 < tail_bound < 1:
        raise ValueError('Tail bound must lie between zero and one')
    x0, y0, x1, y1 = map(int, crop)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    d = signed_distance(xx, yy, half, radius, center)
    diagonal = np.sqrt(.5)
    # The signed distance is 1-Lipschitz. Every omitted interior pixel has
    # opacity at most tail_bound at all points, including its nearest corner.
    tail_depth = sigma*np.sqrt(-np.log(tail_bound))
    active = (d <= diagonal) & (d >= -tail_depth-diagonal)
    alpha = np.zeros_like(d)
    for iy, ix in zip(*np.nonzero(active)):
        charge('quadrature_calls', 1)
        # Reserve the maximum partition size before generating nodes.
        # This bound covers at most 15 x intervals and 4 y intervals.
        # Actual generated nodes are charged immediately by the caller.
        reserve('quadrature_nodes', 60*order*order)
        rule = rounded_rectangle_pixel_rule((xx[iy, ix], yy[iy, ix]), half,
                    radius, center=center, order=order)
        points, weights = rule['points'], rule['weights']
        charge('quadrature_nodes', len(weights))
        if len(weights):
            assert np.isfinite(weights).all() and (weights > 0).all()
            sd = signed_distance(points[:, 0], points[:, 1], half, radius, center)
            assert np.max(sd) < 1e-9
            alpha[iy, ix] = weights @ inward_opacity(sd, sigma)
    assert np.isfinite(alpha).all() and (alpha >= 0).all() and (alpha <= 1).all()
    return alpha, dict(active_pixels=int(active.sum()),
                       omitted_inside_pixels=int((d < -tail_depth-diagonal).sum()),
                       maximum_omitted_pixel_alpha=tail_bound,
                       analytic_profile_has_inner_cutoff=False)


def composite_outline(complete, alpha, *, strength=1., color=(1., 1., 1.)):
    if not np.isfinite(strength) or not 0 <= strength <= 1:
        raise ValueError('Opacity strength must be in the unit interval')
    image, alpha = np.asarray(complete), np.asarray(alpha, float)
    color = np.asarray(color, float)
    if alpha.shape != image.shape[:2] or color.shape != (3,):
        raise ValueError('Image, alpha, and color dimensions must agree')
    if not np.isfinite(alpha).all() or np.any((alpha < 0) | (alpha > 1)):
        raise ValueError('Finite unit alpha required')
    if not np.isfinite(color).all() or np.any((color < 0) | (color > 1)):
        raise ValueError('Finite unit encoded color required')
    out = image.copy()
    affected = (alpha > 0) & (strength > 0)
    if not np.isfinite(image[affected]).all():
        raise ValueError('Outline backing is unavailable')
    a = alpha[affected, None]*strength
    out[affected] = image[affected]*(1-a)+color*a
    return out
