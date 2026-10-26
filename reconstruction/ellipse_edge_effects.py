"""Positive pixel integration and color-aware overlay for an ellipse parallel body.

This is a display layer. It does not alter any optical path or surface normal.
"""
import numpy as np
from ellipse_core_coordinate import EllipseCoreCoordinate
from outline_response import cap_strength
from environment_radiance import decode_srgb,encode_srgb

def extent_at(coordinate,half,radius,axis=0):
    """Positive opposite-axis boundary extent; zero beyond the named extremum."""
    h=np.asarray(half,float);a,b=h-radius
    if axis: a,b=b,a;h=h[::-1]
    x=np.abs(np.asarray(coordinate,float));lo=np.zeros_like(x);hi=np.full_like(x,np.pi/2)
    for _ in range(48):
        t=(lo+hi)*.5;c,s=np.cos(t),np.sin(t);q=np.hypot(a*c,b*s);u=a*a*c/q+radius*c
        lo=np.where(u>x,t,lo);hi=np.where(u>x,hi,t)
    t=(lo+hi)*.5;c,s=np.cos(t),np.sin(t);q=np.hypot(a*c,b*s)
    y=b*b*s/q+radius*s
    return np.where(x<h[0],y,0.)

def pixel_rule_batch(pixels,half,radius,order,charge=lambda k,n:None):
    """Cut every pixel at center/axis and each horizontal-edge intersection.

    Returns point coordinates, positive full-pixel weights and pixel owners.
    No normalization to occupied area is performed.
    """
    p=np.asarray(pixels,float);A,B=half;a,b=np.asarray(half)-radius
    horizontal=np.stack([p[:,1]-.5,p[:,1],p[:,1]+.5],1)
    charge('boundary_inversions',horizontal.size)
    cuts=extent_at(horizontal,half,radius,axis=1)
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
    charge('boundary_inversions',X.size);Y=extent_at(X,half,radius)
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

def integrate_alpha(crop,half,radius,center,config,order,charge,tail=1e-12):
    x0,y0,x1,y1=crop;yy,xx=np.mgrid[y0:y1,x0:x1];coord=EllipseCoreCoordinate(tuple(half),radius)
    charge('distance_points',xx.size);sd,_,_=coord.boundary_distance(xx-center[0],yy-center[1]);depth=config['sigma']*(-np.log(tail))**(1/config['power'])
    active=(sd<=np.sqrt(.5))&(sd>=-depth-np.sqrt(.5));iy,ix=np.nonzero(active);out=np.zeros_like(sd)
    for start in range(0,len(iy),96):
        iyb,ixb=iy[start:start+96],ix[start:start+96];pixels=np.stack([xx[iyb,ixb]-center[0],yy[iyb,ixb]-center[1]],1)
        pts,w,owner=pixel_rule_batch(pixels,half,radius,order,charge)
        if not len(w):continue
        charge('distance_points',len(w));d,_,_=coord.boundary_distance(pts[:,0],pts[:,1]);assert d.max()<2e-8
        alpha=np.exp(-(np.maximum(-d,0)/config['sigma'])**config['power'])*cap_strength(pts[:,0],pts[:,1],half,radius,(0,0),config)
        sums=np.bincount(owner,weights=w*alpha,minlength=len(pixels));out[iyb,ixb]=sums
    assert np.isfinite(out).all() and out.min()>=0 and out.max()<1+1e-12
    return out,dict(order=order,active_pixels=len(iy),omitted_opacity_bound=tail)

def color_lift(image,alpha,exposure,desaturation):
    if exposure<0 or not 0<=desaturation<=1:raise ValueError('Nonnegative lift and unit desaturation required')
    out=image.copy()
    if exposure==0:return out
    affected=alpha>0;v=image[affected].astype(float)
    if not np.isfinite(v).all() or np.any((v<0)|(v>1)):raise ValueError('Finite unit backing required')
    linear=decode_srgb(v);peak=linear.max(-1,keepdims=True);ratio=np.divide(linear,peak,out=np.zeros_like(linear),where=peak>0)
    lift=-np.expm1(-exposure*alpha[affected,None]);s=desaturation*lift
    result=(peak+(1-peak)*lift)*((1-s)*ratio+s)
    # A zero-color input has no chromatic direction; keep black fixed.
    result=np.where(peak>0,result,0.);encoded=encode_srgb(result)
    if np.any((encoded<0)|(encoded>1+1e-14)):raise ValueError('Unbounded response')
    out[affected]=encoded
    return out
