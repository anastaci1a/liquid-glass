"""Explicit pose-area response of the existing empirical transport map.

Uses measured geometry only, no target RGB or per-observation optical fit.
Constant-volume weak-slope scaling motivates a bounded phenomenological law;
it does not make the inherited folded map a physical optical solid.
"""
import numpy as np
from extended_fit import Study
from switch_euclidean_geometry import CrownGeometry

def relative_area(study,p):
    _,_,half,_,_=study.shape(np.array([0.]),np.array([0.]),p)
    geometry=CrownGeometry(half,p['crown_softness'])
    theta=(np.arange(8192)+.5)*2*np.pi/8192
    bx,by=geometry.radial_boundary(theta)
    area=np.pi*np.mean(bx*bx+by*by)*study.L**2
    # Independently measured exposed track cap, already in the frozen case.
    track_radius=study.case['background_estimate']['exposed_track_fit']['circle'][2]
    return float(area/(np.pi*track_radius**2))

class AreaResponseStudy(Study):
    def geometry_field(self,x,y,p):
        X,Y,d,J=super().geometry_field(x,y,p)
        k=float(p.get('area_exponent',0.))
        if k==0:return X,Y,d,J
        if not 0<=k<=2:raise ValueError('Area exponent outside declared comparator range')
        reference=float(p['area_reference'])
        if not np.isfinite(reference) or reference<=0:raise ValueError('Invalid canonical relative area')
        key=tuple((n,p.get(n)) for n in ['half_x_delta','half_y_delta','radius_delta','crown_softness'])
        if getattr(self,'area_key',None)!=key:
            self.area_key=key;self.area_value=relative_area(self,p)
        scale=(self.area_value/reference)**(-k)
        return x+scale*(X-x),y+scale*(Y-y),d,J
