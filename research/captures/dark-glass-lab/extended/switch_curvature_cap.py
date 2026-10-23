"""Shape-curvature perturbation of existing cap-only image transport.
No physical-solid or proprietary-renderer identification is asserted.
"""
import numpy as np
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from switch_crown_geometry import CrownGeometry

def cap_mode(study,x,y,p):
    x,y,half,radius,(sd,nx,ny)=study.shape(x,y,p)
    delta_x=np.zeros_like(x);delta_y=np.zeros_like(y)
    if study.case.get('radial',False):return delta_x,delta_y
    if not p.get('crown_softness') or not p.get('cap_edge_profile'):raise ValueError('Requires crowned footprint and cap profile')
    depth=np.maximum(-sd,0)/radius
    active=(depth<.09)
    # Match incumbent conditional-map continuation d=max(-sd,0).
    # Its cap spline is finite outside coverage; avoid adding a new sd=0
    # map jump before the fixed output-filter/compositing order.
    if active.any():
        geom=CrownGeometry(half,p['crown_softness'])
        qx,qy=geom.closest_boundary(x[active],y[active])
        curvature=geom.curvature(qx,qy)*min(half)
        orientation=(nx[active] if half[0]>=half[1] else ny[active])**2
        basis=BSpline.design_matrix(depth[active],KNOTS,3).toarray()[:,:3]
        amplitude=(curvature-orientation)*(basis@np.asarray(p['cap_edge_profile']))
        delta_x[active]=-amplitude*nx[active];delta_y[active]=-amplitude*ny[active]
    return delta_x,delta_y

class CurvatureCapStudy(Study):
    def geometry_field(self,x,y,p):
        X,Y,d,J=super().geometry_field(x,y,p)
        strength=float(p.get('curvature_cap_mix',0.))
        if strength==0:return X,Y,d,J
        dx,dy=cap_mode(self,x,y,p)
        return X+strength*dx,Y+strength*dy,d,J
