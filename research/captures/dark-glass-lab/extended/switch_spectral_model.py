import sys
sys.path.insert(0,"/workspace/docs/liquid-glass/experiments/reconstruction")
from extended_fit import Study
from chromatic_transmission import apply as directional
class SpectralStudy(Study):
    def field(self,x,y,p):
        X,Y,d,light=self.geometry_field(x,y,p)
        sample=self.sample_field(X,Y,d,p)
        q=p.get('spectral_scale',{})
        for c,sign in [(0,-1),(2,1)]:
            k=1+sign*q.get('spread',0.)
            sample[...,c]=self.sample_field(x+k*(X-x),y+k*(Y-y),d,p)[...,c]
        if q.get('retain_directional',True):sample=directional(self,p,x,y,sample)
        return sample,light
