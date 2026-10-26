"""Verified display operations for a certified smooth contour; no optics."""
import copy
import numpy as np
import cv2
from environment_radiance import decode_srgb,encode_srgb
from outline_response import cap_strength

def extent_at(values,coordinate,axis=0):
    v=np.abs(np.asarray(values,float));A,B=coordinate.half
    lo=np.zeros_like(v);hi=np.full_like(v,np.pi/2)
    for _ in range(48):
        t=(lo+hi)/2;h,hp,_=coordinate.support(t);h=h+coordinate.radius
        x=h*np.cos(t)-hp*np.sin(t);y=h*np.sin(t)+hp*np.cos(t)
        if axis:
            lo=np.where(y<v,t,lo);hi=np.where(y<v,hi,t)
        else:
            lo=np.where(x>v,t,lo);hi=np.where(x>v,hi,t)
    t=(lo+hi)/2;h,hp,_=coordinate.support(t);h=h+coordinate.radius
    result=h*np.cos(t)-hp*np.sin(t) if axis else h*np.sin(t)+hp*np.cos(t)
    return np.where(v<(B if axis else A),result,0.)

def pixel_rule_batch(pixels,coordinate,order,charge=lambda k,n:None):
    half,radius=coordinate.half,coordinate.radius
    """Cut every pixel at center/axis and each horizontal-edge intersection.

    Returns point coordinates, positive full-pixel weights and pixel owners.
    No normalization to occupied area is performed.
    """
    p=np.asarray(pixels,float);A,B=half;a,b=np.asarray(half)-radius
    horizontal=np.stack([p[:,1]-.5,p[:,1],p[:,1]+.5],1)
    charge('boundary_inversions',horizontal.size)
    cuts=extent_at(horizontal,coordinate,axis=1)
    seg=[];owners=[]
    for i,(x,y) in enumerate(p):
        left=max(x-.5,-A);right=min(x+.5,A)
        if right<=left:continue
        candidates=[left,right,x,0.,-a,a]
        for v in cuts[i]:candidates.extend([-v,v])
        c=np.unique(np.clip(candidates,left,right))
        for l,r in zip(c[:-1],c[1:]):
            if r>l:seg.append((l,r));owners.append(i)
    if not seg:return np.empty((0,2)),np.empty(0),np.empty(0,int)
    seg=np.array(seg);owners=np.array(owners);u,w=np.polynomial.legendre.leggauss(order)
    # x=A*sin(t) regularizes the vertical tangent at both horizontal extrema.
    t0=np.arcsin(np.clip(seg[:,0]/A,-1,1));t1=np.arcsin(np.clip(seg[:,1]/A,-1,1));t=(t0[:,None]+t1[:,None])*.5+(t1-t0)[:,None]*u*.5
    X=A*np.sin(t);WX=(t1-t0)[:,None]*w*.5*A*np.cos(t);oi=np.repeat(owners,order);X=X.ravel();WX=WX.ravel()
    charge('boundary_inversions',X.size);Y=extent_at(X,coordinate)
    lower=np.maximum(p[oi,1]-.5,-Y);upper=np.minimum(p[oi,1]+.5,Y)
    # Include pixel center and both global axes before vertical integration.
    mid=np.clip(p[oi,1],lower,upper);zero=np.clip(np.zeros_like(mid),lower,upper)
    yc=np.sort(np.stack([lower,mid,zero,upper],1),axis=1)
    points=[];weights=[];ids=[]
    for j in range(3):
        yl,yh=yc[:,j],yc[:,j+1];ok=(upper>lower)&(yh>yl)
        yy=(yl[ok,None]+yh[ok,None])*.5+(yh-yl)[ok,None]*u*.5
        ww=WX[ok,None]*(yh-yl)[ok,None]*w*.5
        points.append(np.stack([np.broadcast_to(X[ok,None],yy.shape),yy],-1).reshape(-1,2));weights.append(ww.ravel());ids.append(np.repeat(oi[ok],order))
    points=np.concatenate(points);weights=np.concatenate(weights);ids=np.concatenate(ids);charge('quadrature_nodes',len(weights))
    assert np.isfinite(weights).all() and (weights>0).all()
    return points,weights,ids


def integrate_rims(crop,coordinate,center,angular,profiles,order,charge,tail=1e-10):
    x0,y0,x1,y1=crop;yy,xx=np.mgrid[y0:y1,x0:x1]
    charge('distance_points',xx.size)
    sd,_,_=coordinate.boundary_distance(xx-center[0],yy-center[1])
    maximum=max(p['plateau']+p['fade']*(-np.log(tail))**.5 for p in profiles)
    iy,ix=np.nonzero((sd<=np.sqrt(.5))&(sd>=-maximum-np.sqrt(.5)))
    out=np.zeros((len(profiles),)+sd.shape)
    for start in range(0,len(iy),64):
        i,j=iy[start:start+64],ix[start:start+64]
        xy=np.stack([xx[i,j]-center[0],yy[i,j]-center[1]],1)
        pts,w,owner=pixel_rule_batch(xy,coordinate,order,charge)
        if not len(w):continue
        charge('distance_points',len(w));d,_,_=coordinate.boundary_distance(pts[:,0],pts[:,1])
        assert d.max()<2e-8
        ang=cap_strength(pts[:,0],pts[:,1],coordinate.half,coordinate.original_radius,(0,0),angular)
        for k,p in enumerate(profiles):
            charge('profile_points',len(w));v=np.exp(-(np.maximum(-d-p['plateau'],0)/p['fade'])**2)*ang
            out[k,i,j]=np.bincount(owner,weights=w*v,minlength=len(xy))
    assert np.isfinite(out).all() and out.min()>=0 and out.max()<=1+1e-12
    return out

def saturated_rim(body,guide,alpha,chroma=1.5,exposure=3.,floor=.12):
    """Raise a colored endpoint, then increase chroma at constant luminance.

    The largest allowable chroma scale keeps every linear channel in gamut.
    No clipping is used to hide an out-of-range response.
    """
    if chroma<1 or exposure<=0 or not 0<=floor<=1:raise ValueError('Invalid response')
    out=body.copy();ok=alpha>0
    if not ok.any():return out
    B=decode_srgb(body[ok].astype(float));G=decode_srgb(guide[ok].astype(float))
    if not np.isfinite(B).all() or not np.isfinite(G).all():raise ValueError('Unsupported color guide')
    weights=np.array([.2126,.7152,.0722]);peak=G.max(-1,keepdims=True)
    ratio=np.divide(G,peak,out=np.ones_like(G),where=peak>0)
    endpoint=ratio*(exposure*(peak+.4378927114042099)/(exposure*(peak+.4378927114042099)+1-peak))
    y=endpoint@weights;required=B@weights+floor*(1-B@weights)
    neutral=np.divide(np.maximum(required-y,0),1-y,out=np.zeros_like(y),where=y<1)
    endpoint+=neutral[:,None]*(1-endpoint);y=endpoint@weights;delta=endpoint-y[:,None]
    lim=np.full_like(delta,np.inf)
    np.divide(1-y[:,None],delta,out=lim,where=delta>0)
    lower=np.full_like(delta,np.inf);np.divide(-y[:,None],delta,out=lower,where=delta<0)
    k=np.minimum(chroma,np.nextafter(np.minimum(lim,lower).min(-1),0.))
    endpoint=y[:,None]+k[:,None]*delta
    assert endpoint.min()>-2e-15 and endpoint.max()<1+2e-15
    endpoint=encode_srgb(endpoint);endpoint[np.all(body[ok]==1,axis=-1)]=1.
    out[ok]=body[ok]+alpha[ok,None]*(endpoint-body[ok])
    return out

def shadow_field(crop,coordinate,center,sigma_x,sigma_y,offset,charge):
    """Finite anisotropic Gaussian of the actual shifted silhouette at AA2."""
    if min(sigma_x,sigma_y)<=0:raise ValueError('Positive Gaussian widths required')
    x0,y0,x1,y1=crop;rx=int(np.ceil(6*sigma_x));ry=int(np.ceil(6*sigma_y))
    yy,xx=np.mgrid[-ry:2*(y1-y0)+ry,-rx:2*(x1-x0)+rx]
    charge('shadow_points',xx.size)
    d,_,_=coordinate.boundary_distance(x0+xx*.5-.25-center[0],y0+yy*.5-.25-center[1]-offset)
    mask=(d<0).astype(np.float64)
    kx=cv2.getGaussianKernel(2*rx+1,2*sigma_x);ky=cv2.getGaussianKernel(2*ry+1,2*sigma_y)
    charge('shadow_filters',1)
    result=cv2.sepFilter2D(mask,-1,kx,ky,borderType=cv2.BORDER_CONSTANT)
    return result[ry:ry+2*(y1-y0),rx:rx+2*(x1-x0)]

def artwork_study(study,scale=.94,up=3,radius=20):
    """Original ordered compositor with only the content rectangle replaced."""
    if not 0<scale<=1 or up<0 or radius<0:raise ValueError('Invalid artwork transform')
    if scale==1 and up==0 and radius==17:return study
    from extended_fit import geometry
    result=copy.copy(study);result.foreground_layers=[];result.artwork_layers=dict(study.artwork_layers)
    for box,alpha,color in study.foreground_layers:
        if tuple(box) not in study.artwork_layers:
            result.foreground_layers.append((box,alpha,color));continue
        a,b,c,d=box;w=int(round((c-a)*scale));h=int(round((d-b)*scale))
        left=int(round((a+c-w)/2));top=int(round((b+d-h)/2-up));new=[left,top,left+w,top+h]
        if not(study.crop[0]<=left and study.crop[1]<=top and new[2]<=study.crop[2] and new[3]<=study.crop[3]):raise ValueError('Artwork outside crop')
        source,_=study.artwork_layers[tuple(box)];pixels=cv2.resize(source,(w,h),interpolation=cv2.INTER_AREA)
        yy,xx=np.mgrid[:h,:w];sd,*_=geometry(xx-(w-1)/2,yy-(h-1)/2,[w/2,h/2],radius)
        cov=np.clip(.5-sd,0,1)
        result.foreground_layers.append((new,cov,pixels));result.artwork_layers[tuple(new)]=(source,radius)
    return result


def peak_preserving_rim(body,guide,alpha,chroma=1.25,exposure=3.,peak_lift=.12):
    """Preserve peak color without requiring unchanged body luminance.

    A smooth neutral lift dominates near black and vanishes toward unit peak.
    Chroma is adjusted before applying the shared raised peak. This is a
    bounded encoded-display hypothesis, not calibrated scene radiance.
    """
    if not 1<=chroma<=2 or exposure<=0 or not 0<=peak_lift<=1:
        raise ValueError('Invalid peak response')
    out=body.copy();active=alpha>0
    if not active.any():return out
    if np.any(alpha[active]>1+1e-12) or np.any(alpha<0):raise ValueError('Unit alpha required')
    B=decode_srgb(body[active].astype(float));G=decode_srgb(guide[active].astype(float))
    if not np.isfinite(B).all() or not np.isfinite(G).all():raise ValueError('Supported finite guide required')
    m=G.max(-1,keepdims=True);neutral=.4378927114042099*(1-m)**3
    ratio=(G+neutral)/(m+neutral)
    intrinsic=exposure*(m+.4378927114042099)/(exposure*(m+.4378927114042099)+1-m)
    body_peak=B.max(-1,keepdims=True);peak=np.maximum(intrinsic,body_peak+peak_lift*(1-body_peak))
    E=peak*ratio**chroma
    if np.any(E<0) or np.any(E>1):raise ArithmeticError('Unbounded peak response')
    endpoint=encode_srgb(E);endpoint[np.all(body[active]==1,axis=-1)]=1.
    out[active]=body[active]+alpha[active,None]*(endpoint-body[active])
    return out


def low_luminance_body(raw,gain,bias,amount=0.):
    """Bounded display lift; incident filtering has already occurred."""
    if not 0<=amount<=.2:raise ValueError('Invalid low-luminance lift')
    base=raw*gain+bias
    if np.any(base<0) or np.any(base>1):raise ValueError('Invalid base response')
    Y=decode_srgb(raw)@np.array([.2126,.7152,.0722])
    return base+amount*(1-Y[:,None])**3*(1-base)


def soft_channel_rim(body,guide,alpha,curve_power=2.):
    """Per-channel highlight with a neutral floor strongest near black."""
    if not 1.75<=curve_power<=2.25:raise ValueError('Invalid highlight power')
    out=body.copy();active=alpha>0
    if not active.any():return out
    if np.any(alpha<0) or np.any(alpha>1+1e-12):raise ValueError('Invalid alpha')
    B=decode_srgb(body[active].astype(float));G=decode_srgb(guide[active].astype(float))
    if not np.isfinite(B).all() or not np.isfinite(G).all():raise ValueError('Finite colors required')
    Y=G@np.array([.2126,.7152,.0722]);floor=.12+.38*(1-Y)**2
    E=1-(1-floor[:,None])*(1-G)**curve_power
    maximum=B.max(-1,keepdims=True);required=maximum+.12*(1-maximum)
    E*=np.maximum(1,required/E.max(-1,keepdims=True))
    if np.any(E<0) or np.any(E>1+1e-14):raise ArithmeticError('Unbounded response')
    endpoint=encode_srgb(E);endpoint[np.all(body[active]==1,axis=-1)]=1.
    out[active]=body[active]+alpha[active,None]*(endpoint-body[active])
    return out
