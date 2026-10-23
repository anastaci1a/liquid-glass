"""Private three-band dispersion comparator; not recovered Apple optics.

The input is RGB, not a measured spectrum. Gaussian channel sensitivities and
Cauchy-like inverse-square displacement are explicit approximations. All color
bands traverse the same normalized geometric map. No target pixels participate.
"""
import numpy as np
from extended_fit import Study as Base
from chromatic_transmission import weight

class SpectralBandStudy(Base):
    def field(self,x,y,p):
        q=p.get('spectral_band_response')
        if q is None:return super().field(x,y,p)
        X,Y,d,J=self.geometry_field(x,y,p)
        base=self.sample_field(X,Y,d,p)
        t=p['directional_transmission'];w=weight(self,p,x)
        angle=t['angle'];length=t['length'];width=q['bandwidth_nm']
        assert width>=0 and 0<=q['dispersion_law']<=1
        # Gaussian quadrature: mean zero and variance one, positive weights.
        offsets=np.array([-np.sqrt(3.),0,np.sqrt(3.)])*width
        weights=np.array([1/6,2/3,1/6])
        cauchy_den=1/460**2-1/550**2
        rgb=np.empty_like(base)
        for c,center in enumerate([610.,550.,460.]):
            band=np.zeros_like(x)
            for offset,ww in zip(offsets,weights):
                wavelength=center+offset
                assert wavelength>350
                # Positive red, negative blue matches inherited orientation.
                cauchy=-(1/wavelength**2-1/550**2)/cauchy_den
                linear=(wavelength-550)/(60 if wavelength>=550 else 90)
                shift=(1-q['dispersion_law'])*linear+q['dispersion_law']*cauchy
                px=x+length*shift*np.cos(angle);py=y+length*shift*np.sin(angle)
                xx,yy,dd,_=self.geometry_field(px,py,p)
                *_,(sd,_,_)=self.shape(px,py,p)
                sample=self.sample_field(np.where(sd<=0,xx,px),np.where(sd<=0,yy,py),dd,p)
                band+=ww*sample[...,c]
            rgb[...,c]=band
        return base*(1-w[...,None])+rgb*w[...,None],J
