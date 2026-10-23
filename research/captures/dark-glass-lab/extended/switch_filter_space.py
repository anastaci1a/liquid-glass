"""Explicit filtering-space alternatives; no claim of Apple's private pipeline.

Decode/filter/encode only at the named source/output operators. Remaining
material, mixture, AA and reflection stay in encoded RGB, so this is not a
complete radiometric renderer. BT.709 is the source footage's declared transfer;
sRGB is a separate hypothesis motivated by the Core Image documentation.
"""
import numpy as np,cv2
from extended_fit import Study
from render import shade

def decode(v,kind):
    if kind=='srgb':return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
    if kind=='bt709':return np.where(v<.081,v/4.5,((v+.099)/1.099)**(1/.45))
    raise ValueError('Unknown transfer function')

def encode(v,kind):
    v=np.maximum(v,0.)
    if kind=='srgb':return np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055)
    if kind=='bt709':return np.where(v<.018,4.5*v,1.099*v**.45-.099)
    raise ValueError('Unknown transfer function')

class FilterSpaceStudy(Study):
    def sample_field(self,X,Y,d,p):
        kind=p.get('source_filter_space','encoded')
        if kind=='encoded':return super().sample_field(X,Y,d,p)
        # Same declared quarter-pixel implementation bins, no extra precision
        # advantage against the accepted renderer in this operator comparison.
        sigma=round(self.kernel_sigma(p)*4)/4;key=('linear-source',kind,sigma)
        if key not in self.cache:
            source=decode(self.source,kind).astype(np.float32)
            self.cache[key]=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source
        texture=self.cache[key];self.cache.move_to_end(key)
        while len(self.cache)>8:self.cache.popitem(last=False)
        x=(X*self.L+self.case['center'][0]+self.backdrop_shift[0]).astype(np.float32)
        y=(Y*self.L+self.case['center'][1]+self.backdrop_shift[1]).astype(np.float32)
        sample=cv2.remap(texture,x,y,cv2.INTER_LINEAR).reshape((*X.shape,3))
        if p.get('blur_transition',0)>1e-8:
            clear=cv2.remap(decode(self.source,kind).astype(np.float32),x,y,cv2.INTER_LINEAR).reshape((*X.shape,3))
            u=np.clip(d/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);sample=clear+(sample-clear)*w[...,None]
        return np.maximum(encode(sample,kind),0.)**p['gamma']
    def render(self,p,co,scale=1):
        kind=p.get('output_filter_space','encoded')
        if kind=='encoded':return super().render(p,co,scale)
        from material_context import effective
        from grazing_reflection import apply
        co=effective(self,p,co);x0,y0,x1,y1=self.crop
        result=np.empty(((y1-y0)*scale,(x1-x0)*scale,3),np.float32)
        for row,bottom,W,x,y in self.raster_tiles(scale):
            C,J=self.field(x,y,p);C=shade(C,J,co)
            result[row:bottom]=C.reshape(bottom-row,2,W,2,3).mean((1,3))
        sigma=self.kernel_sigma(p,'post_sigma')*scale
        if sigma>.001:result=encode(cv2.GaussianBlur(decode(result,kind).astype(np.float32),(0,0),sigma),kind).astype(np.float32)
        return apply(self,p,result,scale)
