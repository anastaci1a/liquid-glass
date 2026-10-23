"""Avoid discarded lighting-basis evaluation on directional secondary rays.
Private cost-only comparator. Same geometry, sample ordering and RGB blending.
"""
import numpy as np
from switch_euclidean_surface import EuclideanSurfaceStudy
from chromatic_transmission import enabled,weight
class FastEuclideanSurfaceStudy(EuclideanSurfaceStudy):
    def secondary_ray(self,x,y,p):
        *_,(sd,_,_)=self.shape(x,y,p);d=np.maximum(-sd,0)
        xx,yy,half,r,inside,h,hx,hy=self.surface(x,y,p);q=p['euclidean_surface'];n=q['n'];G=q['gap']*r
        M=2*np.hypot(abs(q['bx'])*half[0]/r,abs(q['by'])*half[1]/r)+max(abs(v) for v in q['profile'])*(1+abs(q.get('longitudinal',0))*(1+2*q['width']*r/max(half)))
        if M>=1/np.sqrt(n*n-1):raise ValueError('Cannot guarantee subcritical global slope')
        if np.any(inside&((h<=0)|(h>=G))):raise ValueError('Invalid thickness/background')
        cos=1/np.sqrt(1+hx*hx+hy*hy);K=1-n*n*(1-cos*cos)
        if np.any(inside&(K<=0)):raise ValueError('TIR active ray')
        factor=(n*cos-np.sqrt(np.where(inside,K,1.)))*cos;vz=-n+factor;travel=(G-h)/np.where(inside,-vz,1.)
        X=np.where(inside,xx+travel*factor*hx,xx)+p.get('shape_dx',0);Y=np.where(inside,yy+travel*factor*hy,yy)+p.get('shape_dy',0)
        return X,Y,d,sd
    def field(self,x,y,p):
        X,Y,d,J=self.geometry_field(x,y,p);C=self.sample_field(X,Y,d,p)
        if not enabled(p):return C,J
        w=weight(self,p,x);q=p['directional_transmission'];dispersed=C.copy()
        for c,sign in [(0,1),(2,-1)]:
            qx=x+sign*q['length']*np.cos(q['angle']);qy=y+sign*q['length']*np.sin(q['angle'])
            X,Y,d,sd=self.secondary_ray(qx,qy,p)
            dispersed[...,c]=self.sample_field(np.where(sd<=0,X,qx),np.where(sd<=0,Y,qy),d,p)[...,c]
        return C*(1-w[...,None])+dispersed*w[...,None],J
