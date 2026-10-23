"""Flat-front solid with a back height parameterized by true inward distance.
Height is a biaxial quadratic plus integral of a compact scalar rim profile.
All normals are height derivatives, not independent image-map coefficients.
"""
from collections import OrderedDict
import hashlib
import numpy as np
from scipy.interpolate import BSpline
from extended_fit import Study,KNOTS
from crowned_footprint import longitudinal
from switch_euclidean_geometry import EuclideanCrown

class EuclideanSurfaceStudy(Study):
    def __init__(self,folder):
        super().__init__(folder);self.distance_cache=OrderedDict();self.euclidean_geometry=None
    def distance(self,x,y,half,softness,width):
        key=(tuple(half),softness,width,hashlib.blake2b(x.tobytes()+y.tobytes(),digest_size=16).digest())
        if key in self.distance_cache:
            self.distance_cache.move_to_end(key);return self.distance_cache[key]
        if self.euclidean_geometry is None or self.euclidean_geometry.half!=tuple(half) or self.euclidean_geometry.softness!=softness:self.euclidean_geometry=EuclideanCrown(half,softness)
        geo=self.euclidean_geometry;sd,*_=geo.boundary(x,y);inside=sd<=0;_,qd=longitudinal(np.asarray(max(half)),max(half),min(half),softness);m=max(1,abs(float(qd)))
        active=inside&(-sd<width*m);d=np.full_like(x,width);nx=np.zeros_like(x);ny=np.zeros_like(x)
        if active.any():d[active],nx[active],ny[active]=geo.nearest(x[active],y[active])
        self.distance_cache[key]=(inside,d,nx,ny)
        while len(self.distance_cache)>96:self.distance_cache.popitem(last=False)
        return self.distance_cache[key]
    def surface(self,x,y,p):
        xx,yy,half,r,_=self.shape(x,y,p);q=p['euclidean_surface'];width=q['width']*r
        inside,d,nx,ny=self.distance(xx,yy,half,p['crown_softness'],width)
        u=np.clip(d/width,0,1);co=np.r_[q['profile'],np.zeros(len(KNOTS)-4-len(q['profile']))];spline=BSpline(KNOTS,co,3);integral=spline.antiderivative();a=spline(u)
        h=r*(q['t0']+q['bx']*(xx/r)**2+q['by']*(yy/r)**2)+width*(integral(u)-integral(0))
        hx=2*q['bx']*xx/r-a*nx;hy=2*q['by']*yy/r-a*ny
        coupling=q.get('longitudinal',0.)
        if coupling:
            horizontal=half[0]>=half[1];major=xx if horizontal else yy;A=max(half)
            tail=width*(integral(u)-integral(1.));weight=coupling*(major/A)**2
            h+=weight*tail;hx-=weight*a*nx;hy-=weight*a*ny
            if horizontal:hx+=2*coupling*major/A**2*tail
            else:hy+=2*coupling*major/A**2*tail
        return xx,yy,half,r,inside,h,hx,hy
    def geometry_field(self,x,y,p):
        _,_,d,J=super().geometry_field(x,y,p);xx,yy,half,r,inside,h,hx,hy=self.surface(x,y,p);q=p['euclidean_surface'];n=q['n'];G=q['gap']*r
        # Convex spline partition and unit true-distance gradient bound slopes.
        M=2*np.hypot(abs(q['bx'])*half[0]/r,abs(q['by'])*half[1]/r)+max(abs(v) for v in q['profile'])*(1+abs(q.get('longitudinal',0))*(1+2*q['width']*r/max(half)))
        if M>=1/np.sqrt(n*n-1):raise ValueError('Cannot guarantee subcritical global slope')
        if np.any(inside&((h<=0)|(h>=G))):raise ValueError('Invalid thickness/background')
        cos=1/np.sqrt(1+hx*hx+hy*hy);K=1-n*n*(1-cos*cos)
        if np.any(inside&(K<=0)):raise ValueError('TIR active ray')
        factor=(n*cos-np.sqrt(np.where(inside,K,1.)))*cos;vz=-n+factor
        travel=(G-h)/np.where(inside,-vz,1.)
        X=np.where(inside,xx+travel*factor*hx,xx)+p.get('shape_dx',0);Y=np.where(inside,yy+travel*factor*hy,yy)+p.get('shape_dy',0)
        return X,Y,d,J
