"""One explicit raised-perimeter height law, independent of footprint shape."""
import numpy as np

def annular_level_profile(level,depth,core_ratio):
    """Return height, dheight/dlevel and its second derivative on [0,1].

    level is the squared normalized footprint coordinate from actual geometry.
    Maximum height is depth*(1+core_ratio)^2/4. The radial slope magnitude
    is bounded by 2*depth*(1+core_ratio); multiply by the footprint rho bound.
    This is not an image-coordinate displacement or independently set normal.
    """
    if not np.isfinite([depth,core_ratio]).all() or depth<=0 or not 0<core_ratio<1:
        raise ValueError('Positive depth and core ratio strictly between zero and one required')
    t=np.asarray(level,float)
    if not np.isfinite(t).all() or np.any((t<0)|(t>1)):
        raise ValueError('Finite physical squared footprint coordinates in [0,1] required')
    return (depth*(1-t)*(core_ratio+t),
            depth*(1-core_ratio-2*t),
            np.full_like(t,-2*depth))
