"""One positive shared power response before existing affine material; empirical."""
import hashlib,json
from pathlib import Path
import numpy as np
import cv2
import toolbar_candidate as baseline
from render import shade
from toolbar_scattering_renderer import geometry_signature

def response(c,gamma):
    if not .8<=gamma<=1.25:raise ValueError('Declared shared gamma bounds[.8,1.25]')
    return c if gamma==1 else np.maximum(c,0.)**gamma

def render(source,case,p,samples=4,scale=1,*,atlas=None,checkpoint=None):
    gamma=float(p.get('intensity_response',{}).get('gamma',1.))
    if gamma==1:return baseline.render(source,case,p,samples,scale)
    response(np.array([0.,1.]),gamma)
    if atlas is not None and (samples!=4 or scale!=1 or atlas['geometry_signature']!=geometry_signature(case,p)):raise ValueError('Frozen native atlas differs')
    L=min(case['half']);blur=cv2.GaussianBlur(source,(0,0),p['source_sigma']*L);x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale;start=0;root=Path(checkpoint) if checkpoint else None
    signature=hashlib.sha256(Path(__file__).read_bytes()+json.dumps({'case':case,'recipe':p,'samples':samples,'scale':scale,'source':hashlib.sha256(source.tobytes()).hexdigest()},sort_keys=True).encode()).hexdigest()
    if root:
        root.mkdir(parents=True,exist_ok=True);meta=root/'render-progress.json'
        if meta.exists():
            state=json.loads(meta.read_text());assert state['signature']==signature
            if state.get('complete'):return np.load(root/'material.npy'),np.load(root/'alpha.npy')
            start=state['next_top'];C=np.load(root/'raw-material.npy',mmap_mode='r+');alpha=np.load(root/'alpha.npy',mmap_mode='r+')
        else:
            C=np.lib.format.open_memmap(root/'raw-material.npy',mode='w+',dtype=np.float32,shape=(H,W,3));alpha=np.lib.format.open_memmap(root/'alpha.npy',mode='w+',dtype=np.float32,shape=(H,W));state={'signature':signature,'next_top':0,'complete':False};meta.write_text(json.dumps(state)+'\n')
    else:C=np.zeros((H,W,3),np.float32);alpha=np.zeros((H,W),np.float32)
    for top in range(start,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples];x=(x0+(xx+.5)/(samples*scale)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(samples*scale)-.5-case['center'][1])/L;sd,*_=baseline.boundary(x,y,p)
        if atlas is None:X,Y=baseline.mapping(x,y,p);sx=X*L+case['center'][0];sy=Y*L+case['center'][1]
        else:sx=atlas['sx'][top*4:bot*4];sy=atlas['sy'][top*4:bot*4]
        sx=sx.astype(np.float32);sy=sy.astype(np.float32);sample=cv2.remap(blur,sx,sy,cv2.INTER_LINEAR)
        if p.get('blur_transition'):
            u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=cv2.remap(source,sx,sy,cv2.INTER_LINEAR);sample=clear+(sample-clear)*w[...,None]
        shaded=shade(response(sample,gamma),baseline.lighting(x,y,p),np.asarray(p['material']));inside=sd<=0;sh=(bot-top,samples,W,samples);weight=inside.reshape(sh).sum((1,3));C[top:bot]=(shaded*inside[...,None]).reshape((*sh,3)).sum((1,3))/np.maximum(weight,1)[...,None];alpha[top:bot]=weight/(samples*samples)
        if root:C.flush();alpha.flush();state['next_top']=bot;meta.write_text(json.dumps(state)+'\n')
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale;num=cv2.GaussianBlur(np.asarray(C)*np.asarray(alpha)[...,None],(0,0),sigma);den=cv2.GaussianBlur(np.asarray(alpha),(0,0),sigma);final=num/np.maximum(den,1e-12)[...,None]
    else:final=np.asarray(C).copy()
    if root:np.save(root/'material.npy',final);state['complete']=True;meta.write_text(json.dumps(state)+'\n')
    return final,np.asarray(alpha)
