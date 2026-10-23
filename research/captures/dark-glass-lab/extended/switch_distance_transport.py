"""Empirical normal transport in true boundary-distance coordinates.

Same silhouette, source, lighting, blur coordinate and material. Only the
normal displacement's coordinate/normal changes. This is not a physical solid.
"""
from collections import OrderedDict
import hashlib
import numpy as np
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from switch_euclidean_geometry import EuclideanCrown

class DistanceTransportStudy(Study):
    def __init__(self,folder):
        super().__init__(folder);self.transport_cache=OrderedDict();self.lighting_cache=OrderedDict();self.transport_geometry=None

    def transport_basis(self,x,y,p):
        xx,yy,half,r,(sd,_,_)=self.shape(x,y,p)
        key=(tuple(half),p['crown_softness'],p.get('cap_normal_gain',0),len(p.get('cap_edge_profile',[])),hashlib.blake2b(xx.tobytes()+yy.tobytes(),digest_size=16).digest())
        if key in self.transport_cache:
            self.transport_cache.move_to_end(key);return self.transport_cache[key]
        if self.transport_geometry is None or self.transport_geometry.half!=tuple(half) or self.transport_geometry.softness!=p['crown_softness']:
            self.transport_geometry=EuclideanCrown(half,p['crown_softness'])
        geometry=self.transport_geometry;inside=sd<=0;width=.75*r
        # A global Lipschitz bound for the implicit coordinate safely chooses
        # every point whose true inward distance could lie in the optical band.
        from crowned_footprint import longitudinal
        _,derivative=longitudinal(np.asarray(max(half)),max(half),min(half),p['crown_softness'])
        active=(~inside)|(-sd<width*max(1.,abs(float(derivative))))
        distance=np.full_like(xx,width);nx=np.zeros_like(xx);ny=np.zeros_like(xx)
        distance[active],nx[active],ny[active]=geometry.nearest(xx[active],yy[active])
        depth=np.where(inside,np.minimum(distance,width),0.)
        basis=BSpline.design_matrix(np.clip(depth/r,0,1).ravel(),KNOTS,3).toarray()[:,:7].reshape((*x.shape,7))
        weight=nx*nx if half[0]>=half[1] else ny*ny
        normal=basis*(1+p.get('cap_normal_gain',0)*weight[...,None])
        caps=basis[...,:len(p.get('cap_edge_profile',[]))]*weight[...,None]
        scalar=np.concatenate([normal,caps],axis=-1)
        result=(xx,yy,r,scalar,nx,ny,inside)
        self.transport_cache[key]=result
        while len(self.transport_cache)>8:self.transport_cache.popitem(last=False)
        return result

    def geometry_field(self,x,y,p):
        if not p.get('distance_transport',False):return super().geometry_field(x,y,p)
        if p.get('tangent',0)!=0 or p.get('coupling',0)!=0 or not p['spline']:
            raise ValueError('This comparator requires the accepted zero-tangent spline family')
        key=(hashlib.blake2b(x.tobytes()+y.tobytes(),digest_size=16).digest(),
             tuple((k,p.get(k)) for k in ['shape_dx','shape_dy','half_x_delta','half_y_delta','radius_delta','crown_softness','rim_width','thin_width']))
        if key not in self.lighting_cache:
            _,_,d,J=super().geometry_field(x,y,p);self.lighting_cache[key]=(d,J)
        self.lighting_cache.move_to_end(key)
        while len(self.lighting_cache)>4:self.lighting_cache.popitem(last=False)
        d,J=self.lighting_cache[key]
        xx,yy,r,basis,nx,ny,inside=self.transport_basis(x,y,p)
        coefficients=np.r_[[p[f'c{i}'] for i in range(7)],p.get('cap_edge_profile',[])]
        amplitude=basis@coefficients
        return ((1-p['core_x'])*xx-amplitude*nx+p.get('shape_dx',0),
                (1-p['core_y'])*yy-amplitude*ny+p.get('shape_dy',0),d,J)
