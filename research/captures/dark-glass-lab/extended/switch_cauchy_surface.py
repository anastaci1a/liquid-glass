"""Three-band Cauchy dispersion on one explicit switch back surface.
The same height/gradient/IOR law applies to both references. Ordinary Gaussian
blur and the inherited directional displaced-ray mixture remain separate.
This is NOT spectral radiometry or a recovered Apple refractive-index law.
"""
import copy
import numpy as np
from switch_euclidean_surface import EuclideanSurfaceStudy
from chromatic_transmission import enabled,weight

class CauchySurfaceStudy(EuclideanSurfaceStudy):
    @staticmethod
    def band_indices(p):
        s=float(p.get('cauchy_delta',0.));n=float(p['euclidean_surface']['n'])
        if not np.isfinite(s) or not 0<=s<=.03:raise ValueError('Cauchy delta outside declared bracket')
        wavelengths=np.array([.650,.550,.450])
        factors=(1/wavelengths**2-1/.550**2)/(1/.450**2-1/.550**2)
        return n+s*factors
    def field(self,x,y,p):
        ns=self.band_indices(p)
        if p.get('cauchy_delta',0.)==0:return super().field(x,y,p)
        X,Y,d,J=self.geometry_field(x,y,p);C=self.sample_field(X,Y,d,p)
        directional=enabled(p)
        if directional:w=weight(self,p,x);q=p['directional_transmission']
        for c,sign in [(0,1),(2,-1)]:
            pc=copy.deepcopy(p);pc['euclidean_surface']['n']=float(ns[c])
            X,Y,d,_=self.geometry_field(x,y,pc);value=self.sample_field(X,Y,d,pc)[...,c]
            if directional:
                qx=x+sign*q['length']*np.cos(q['angle']);qy=y+sign*q['length']*np.sin(q['angle'])
                X,Y,d,_=self.geometry_field(qx,qy,pc);*_,(sd,_,_)=self.shape(qx,qy,pc)
                value=value*(1-w)+self.sample_field(np.where(sd<=0,X,qx),np.where(sd<=0,Y,qy),d,pc)[...,c]*w
            C[...,c]=value
        return C,J
