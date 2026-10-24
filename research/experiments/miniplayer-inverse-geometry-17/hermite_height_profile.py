"""One actual C1 Hermite height profile; gradients differentiate this height."""
import numpy as np


class HermiteProfile:
    def __init__(self, radius, heights, derivatives):
        self.r=np.asarray(radius,float);self.h=np.asarray(heights,float);self.m=np.asarray(derivatives,float)
        if self.r.ndim!=1 or self.h.shape!=self.r.shape or self.m.shape!=self.r.shape or not np.isfinite([self.r,self.h,self.m]).all() or np.any(np.diff(self.r)<=0):
            raise ValueError('Finite ordered height/derivative nodes required')
    def evaluate(self, radius, derivative=False):
        x=np.asarray(radius,float)
        if np.any((x<self.r[0])|(x>self.r[-1])):raise ValueError('Outside actual profile domain')
        j=np.clip(np.searchsorted(self.r,x,side='right')-1,0,len(self.r)-2)
        dr=self.r[j+1]-self.r[j];t=(x-self.r[j])/dr
        if derivative:
            return ((6*t*t-6*t)*self.h[j]+(-6*t*t+6*t)*self.h[j+1])/dr+(3*t*t-4*t+1)*self.m[j]+(3*t*t-2*t)*self.m[j+1]
        return (2*t**3-3*t*t+1)*self.h[j]+(t**3-2*t*t+t)*dr*self.m[j]+(-2*t**3+3*t*t)*self.h[j+1]+(t**3-t*t)*dr*self.m[j+1]
