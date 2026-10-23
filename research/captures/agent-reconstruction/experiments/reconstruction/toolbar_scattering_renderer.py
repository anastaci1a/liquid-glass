"""One achromatic geometry-conditioned scattering operator; frozen native AA.

Shared Gaussian offsets precede the current affine/clipped material. This is an
empirical covariance proxy, not derived microfacet roughness or Apple geometry.
"""
from functools import lru_cache
import hashlib,json
from pathlib import Path
import numpy as np
import cv2
from numpy.polynomial.hermite import hermgauss
import toolbar_candidate as baseline
from toolbar_scattering_covariance import scattering_factor
from render import shade

_CODE_HASHES={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ['toolbar_scattering_renderer.py','toolbar_scattering_covariance.py','toolbar_candidate.py','crowned_footprint.py','toolbar_curvature_profile.py','render.py']}


@lru_cache(maxsize=8)
def quadrature(order):
    if order not in [3,5,7,9]:raise ValueError('Predeclared square Gaussian orders3/5/7/9 only')
    nodes,w=hermgauss(order);nodes=nodes*np.sqrt(2);w=w/np.sqrt(np.pi);xx,yy=np.meshgrid(nodes,nodes,indexing='xy');weights=np.outer(w,w).ravel();weights/=weights.sum()
    return np.stack([xx.ravel(),yy.ravel()],axis=-1),weights


def prepare_source(source,case,p):
    source=np.array(source,dtype=np.float64,copy=True);sigma=p['source_sigma']*min(case['half']);blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source;source.setflags(write=False);blur.setflags(write=False)
    return {'source':source,'blurred':blur,'source_array_sha256':hashlib.sha256(source.tobytes()).hexdigest(),'sigma_native':sigma}


def geometry_signature(case,p):
    return json.dumps({'case':case,'shape':p['shape'],'parameters':p['parameters'],'footprint_softness':p.get('footprint_softness',0),'tangent_exponent':p.get('tangent_exponent',4)},sort_keys=True)


def load_native_atlas(path,case,p,reference_recipe):
    if geometry_signature(case,p)!=geometry_signature(reference_recipe['case'],reference_recipe):raise ValueError('Atlas geometry differs')
    root=Path(path);state=json.loads((root/'progress.json').read_text());assert state['next_top']==case['crop'][3]-case['crop'][1]
    if state['code_sha256']!=_CODE_HASHES['toolbar_scattering_covariance.py']:raise ValueError('Atlas Jacobian code differs')
    return {'sx':np.load(root/'sx.npy',mmap_mode='r'),'sy':np.load(root/'sy.npy',mmap_mode='r'),'A':np.load(root/'A.npy',mmap_mode='r'),'inside':np.load(root/'inside.npy',mmap_mode='r'),'geometry_signature':geometry_signature(case,p)}


def render(source,case,p,samples=4,scale=1,*,order=5,atlas=None,prepared=None,checkpoint=None):
    rho=float(p.get('scattering_covariance',{}).get('rho',0.))
    if rho==0:return baseline.render(source,case,p,samples=samples,scale=scale)
    if not 0<rho<=.02:raise ValueError('Declared initial scattering rho bound[0,.02] exceeded')
    nodes,weights=quadrature(order);prepared=prepared or prepare_source(source,case,p);source=prepared['source'];blur=prepared['blurred'];L=min(case['half']);assert prepared['sigma_native']==p['source_sigma']*L
    if atlas is not None:
        if samples!=4 or scale!=1 or atlas['geometry_signature']!=geometry_signature(case,p):raise ValueError('Native atlas is only original4x4 geometry')
    x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale;start=0;root=Path(checkpoint) if checkpoint is not None else None
    signature=hashlib.sha256(json.dumps({'case':case,'recipe':p,'samples':samples,'scale':scale,'order':order,'source_array_sha256':prepared['source_array_sha256'],'code_hashes':_CODE_HASHES},sort_keys=True).encode()).hexdigest()
    if root:
        root.mkdir(parents=True,exist_ok=True);meta=root/'render-progress.json'
        if meta.exists():
            state=json.loads(meta.read_text());assert state['signature']==signature
            if state.get('complete') and (root/'material.npy').exists():return np.load(root/'material.npy'),np.load(root/'alpha.npy')
            start=state['next_top'];result=np.load(root/'raw-material.npy',mmap_mode='r+');coverage=np.load(root/'alpha.npy',mmap_mode='r+')
        else:
            result=np.lib.format.open_memmap(root/'raw-material.npy',mode='w+',dtype=np.float32,shape=(H,W,3));coverage=np.lib.format.open_memmap(root/'alpha.npy',mode='w+',dtype=np.float32,shape=(H,W));state={'signature':signature,'next_top':0,'complete':False};meta.write_text(json.dumps(state)+'\n')
    else:result=np.zeros((H,W,3),np.float32);coverage=np.zeros((H,W),np.float32)
    for top in range(start,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples];x=(x0+(xx+.5)/(scale*samples)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(scale*samples)-.5-case['center'][1])/L;sd,*_=baseline.boundary(x,y,p);inside=sd<=0
        if atlas is None:
            factor,_,_=scattering_factor(x,y,p);X,Y=baseline.mapping(x,y,p);sx=X*L+case['center'][0];sy=Y*L+case['center'][1]
        else:
            sl=slice(top*4,bot*4);factor=np.asarray(atlas['A'][sl]);sx=np.asarray(atlas['sx'][sl]);sy=np.asarray(atlas['sy'][sl]);assert np.array_equal(inside,np.asarray(atlas['inside'][sl],bool))
        if not inside.any():
            result[top:bot]=0.;coverage[top:bot]=0.
        else:
            if p.get('blur_transition'):
                u=np.clip(-sd/p['blur_transition'],0,1);mix=u**3*(u*(6*u-15)+10)
            else:mix=np.ones_like(sd)
            need_clear=bool(np.any(inside&(mix<1)));average=np.zeros((*sx.shape,3),np.float64)
            for node,weight in zip(nodes,weights):
                dx=rho*L*(factor[...,0,0]*node[0]+factor[...,0,1]*node[1]);dy=rho*L*(factor[...,1,0]*node[0]+factor[...,1,1]*node[1]);qx=sx+dx;qy=sy+dy
                if qx.min()<0 or qx.max()>=source.shape[1]-1 or qy.min()<0 or qy.max()>=source.shape[0]-1:raise ValueError('Emitted scattering node exceeds frozen source')
                qx=qx.astype(np.float32);qy=qy.astype(np.float32);sample=cv2.remap(blur,qx,qy,cv2.INTER_LINEAR)
                if need_clear:
                    clear=cv2.remap(source,qx,qy,cv2.INTER_LINEAR);sample=clear+(sample-clear)*mix[...,None]
                average+=weight*sample
            C=shade(average,baseline.lighting(x,y,p),np.asarray(p['material']));sh=(bot-top,samples,W,samples);weight=inside.reshape(sh).sum((1,3));result[top:bot]=(C*inside[...,None]).reshape((*sh,3)).sum((1,3))/np.maximum(weight,1)[...,None];coverage[top:bot]=weight/(samples*samples)
        if root:
            result.flush();coverage.flush();state['next_top']=bot;meta.write_text(json.dumps(state)+'\n')
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale;numerator=cv2.GaussianBlur(np.asarray(result)*np.asarray(coverage)[...,None],(0,0),sigma);denominator=cv2.GaussianBlur(np.asarray(coverage),(0,0),sigma);final=numerator/np.maximum(denominator,1e-12)[...,None]
    else:final=np.asarray(result).copy()
    if root:
        np.save(root/'material.npy',final);state['complete']=True;meta.write_text(json.dumps(state)+'\n')
    return final,np.asarray(coverage)
