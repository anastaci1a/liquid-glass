"""Switch deformation comparator using measured footprint and track scale.

For a self-similar height profile of fixed volume, H/r is proportional to
1/(area*r). In track-radius units this is track_ratio³ / normalized_area.
Scaling displacement by that ratio is a weak-optics approximation, not exact
Snell transport. Both references share one anchor and one coupling value.
"""
import sys
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from extended_fit import Study
from crowned_footprint import longitudinal

def depth_coordinate(study,p):
    half=study.half+[p.get('half_x_delta',0),p.get('half_y_delta',0)]
    a,b=max(half),min(half);x=np.linspace(0,a,4097)
    q,_=longitudinal(x,a,b,p['crown_softness'])
    area=4*np.trapezoid(b*np.sqrt(np.maximum(1-(q/b)**2,0)),x)
    track=study.case['background_estimate']['track_half_over_L'][1]
    return float(track**3/(area*b)),float(area)

class DeformationStudy(Study):
    def geometry_field(self,x,y,p):
        X,Y,d,J=super().geometry_field(x,y,p)
        if 'deformation_response' not in p:return X,Y,d,J
        q=p['deformation_response'];depth,_=depth_coordinate(self,p)
        support=J[...,-1] if q.get('support')=='paraxial-core' else 1.
        factor=1+support*q['coupling']*(depth/q['reference_depth_coordinate']-1)
        return x+factor*(X-x),y+factor*(Y-y),d,J
