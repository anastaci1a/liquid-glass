"""Curvature-conditioned normal ADDITION to an empirical image map.

This does not identify an Apple optical surface. All geometry inputs share one
length unit; render inputs use the incumbent normalized coordinates. Closest
points are true implicit-curve projections, not the inherited r-b coordinate.
"""
from functools import lru_cache
import numpy as np
import cv2
from scipy.special import expit
from scipy.optimize import minimize_scalar
import toolbar_candidate as baseline
from render import shade


class CrownGeometry:
    def __init__(self,half,softness):
        self.half=tuple(map(float,half));self.softness=float(softness)
        self.a=max(self.half);self.b=min(self.half);self.L=self.b
        self.horizontal=self.half[0]>=self.half[1]
        self.circle=self.softness==0 and abs(self.a-self.b)<1e-14*self.b
        if not(self.b>0 and (self.circle or 0<self.softness<=1)):
            raise ValueError('Smooth crown or an explicit true circle is required')
        if not self.circle:
            self.e=self.softness*self.b;self.neck=self.a-self.b
            self.qbase=np.logaddexp(0.,(self.e-self.neck)/self.e)
            self.qden=np.logaddexp(0.,(np.hypot(self.a,self.e)-self.neck)/self.e)-self.qbase

    def field_hessian(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
        if self.circle:
            r2=self.b**2;z=np.zeros_like(x);two=np.full_like(x,2/r2)
            return (x*x+y*y)/r2-1,2*x/r2,2*y/r2,two,z,two
        major,minor=(x,y) if self.horizontal else (y,x)
        radius=np.hypot(major,self.e);s=expit((radius-self.neck)/self.e)
        q=self.b*(np.logaddexp(0.,(radius-self.neck)/self.e)-self.qbase)/self.qden
        qd=self.b/self.qden*s*major/(self.e*radius)
        qdd=self.b/self.qden*(s*(1-s)*major**2/(self.e**2*radius**2)+s*self.e/radius**3)
        f=(q*q+minor*minor)/self.b**2-1;ga=2*q*qd/self.b**2;gb=2*minor/self.b**2
        haa=2*(qd*qd+q*qdd)/self.b**2;hbb=np.full_like(f,2/self.b**2);zero=np.zeros_like(f)
        return (f,ga,gb,haa,zero,hbb) if self.horizontal else (f,gb,ga,hbb,zero,haa)

    def boundary(self,x,y):
        f,gx,gy,*_=self.field_hessian(x,y);norm=np.hypot(gx,gy)
        return self.b*(np.sqrt(np.maximum(f+1,0))-1),gx/np.maximum(norm,1e-30),gy/np.maximum(norm,1e-30)

    def closest_boundary(self,x,y):
        x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float))
        if self.circle:
            radius=np.hypot(x,y)
            if np.any(radius<1e-14*self.b):raise ValueError('Circle center has no unique closest boundary point')
            return self.b*x/radius,self.b*y/radius
        sd,nx,ny=self.boundary(x,y);qx=x-sd*nx;qy=y-sd*ny
        for _ in range(24):
            f,fx,fy,fxx,fxy,fyy=self.field_hessian(qx,qy)
            dx,qdy=qx-x,qy-y;cross=dx*fy-qdy*fx
            if max(float(np.max(np.abs(f))),float(np.max(np.abs(cross))))<2e-13:break
            g1=fy+dx*fxy-qdy*fxx;g2=-fx+dx*fyy-qdy*fxy;det=fx*g2-fy*g1
            if np.any(np.abs(det)<1e-15/self.b**2):raise ValueError('Ambiguous closest-boundary projection')
            sx=(f*g2-fy*cross)/det;sy=(fx*cross-f*g1)/det
            factor=np.minimum(1.,.25*self.b/np.maximum(np.hypot(sx,sy),1e-30));qx-=factor*sx;qy-=factor*sy
        f,fx,fy,*_=self.field_hessian(qx,qy);cross=(qx-x)*fy-(qy-y)*fx
        if max(float(np.max(np.abs(f))),float(np.max(np.abs(cross))))>2e-10:
            raise ValueError('Closest-boundary residual exceeds declared tolerance')
        return qx,qy

    def curvature(self,x,y):
        _,fx,fy,fxx,fxy,fyy=self.field_hessian(x,y)
        return (fxx*fy*fy-2*fxy*fx*fy+fyy*fx*fx)/np.maximum(np.hypot(fx,fy)**3,1e-30)

    def radial_boundary(self,theta):
        theta=np.asarray(theta,float);cos=np.cos(theta);sin=np.sin(theta)
        if self.circle:return self.b*cos,self.b*sin
        lo=np.full_like(theta,self.b);hi=np.full_like(theta,self.a)
        for _ in range(56):
            mid=(lo+hi)/2;outside=self.field_hessian(mid*cos,mid*sin)[0]>0;hi=np.where(outside,mid,hi);lo=np.where(outside,lo,mid)
        radius=(lo+hi)/2
        return radius*cos,radius*sin

    @lru_cache(maxsize=4)
    def arc_table(self,n=4096):
        theta=np.arange(n)*2*np.pi/n;x,y=self.radial_boundary(theta);_,gx,gy,*_=self.field_hessian(x,y)
        radius=np.hypot(x,y);radial=gx*np.cos(theta)+gy*np.sin(theta)
        derivative=-radius*(-gx*np.sin(theta)+gy*np.cos(theta))/radial
        speed=np.hypot(radius,derivative);curvature=self.curvature(x,y);perimeter=float(2*np.pi*np.mean(speed))
        return {'theta':theta,'x':x,'y':y,'speed':speed,'curvature':curvature,'perimeter':perimeter,'total_turn':float(2*np.pi*np.mean(speed*curvature))}

    @property
    def perimeter(self):return self.arc_table(4096)['perimeter']

    def displacement_bound(self,maximum_fraction=.12):
        if self.circle:return {'lambda_max':0.,'feature_abs_max':0.,'maximum_displacement_fraction':maximum_fraction}
        table=self.arc_table(8192);mean=2*np.pi*self.L/table['perimeter'];i=int(np.argmax(table['curvature']));theta=table['theta'][i];h=2*np.pi/8192
        fit=minimize_scalar(lambda t:-float(self.curvature(*self.radial_boundary(t))),bounds=(theta-h,theta+h),method='bounded',options={'xatol':1e-13})
        kmax=max(float(table['curvature'].max()),-float(fit.fun));kmin=min(0.,float(table['curvature'].min()))
        maximum=max(abs(self.L*kmin-mean),abs(self.L*kmax-mean));conservative=maximum*(1+1e-4)+1e-10
        return {'lambda_max':maximum_fraction/conservative,'feature_abs_max':maximum,'feature_abs_bound':conservative,'maximum_displacement_fraction':maximum_fraction,'curvature_min':kmin,'curvature_max':kmax,'perimeter':table['perimeter'],'normalized_mean_curvature':mean,'boundary_samples':8192,'extremum_refined':bool(fit.success)}


@lru_cache(maxsize=8)
def geometry(half,softness):return CrownGeometry(half,softness)


def bump(u):
    u=np.asarray(u,float);v=np.clip(u,0,1)
    return np.where((u>0)&(u<1),64*v**3*(1-v)**3,0.)


def curvature_delta(x,y,p):
    q=p.get('curvature_normal',{});amplitude=float(q.get('amplitude',0.))
    x,y=np.broadcast_arrays(np.asarray(x,float),np.asarray(y,float));result=np.zeros_like(x)
    if amplitude==0:return result
    g=geometry(tuple(p['shape']['half']),p.get('footprint_softness',0.))
    if g.circle:return result
    width=float(q['width'])
    if width<=0:raise ValueError('Fixed positive support width required')
    sd,*_=baseline.boundary(x,y,p);u=-sd/width;active=(u>0)&(u<1)
    if active.any():
        qx,qy=g.closest_boundary(x[active],y[active]);feature=g.L*g.curvature(qx,qy)-2*np.pi*g.L/g.perimeter
        result[active]=amplitude*g.L*bump(u[active])*feature
    return result


def mapping(x,y,p):
    X,Y=baseline.mapping(x,y,p)
    if p.get('curvature_normal',{}).get('amplitude',0.)==0:return X,Y
    delta=curvature_delta(x,y,p);_,nx,ny=baseline.boundary(x,y,p)
    return X-delta*nx,Y-delta*ny


def render(source,case,p,samples=4,scale=1):
    if p.get('curvature_normal',{}).get('amplitude',0.)==0:return baseline.render(source,case,p,samples,scale)
    L=min(case['half']);sigma=p['source_sigma']*L;blur=cv2.GaussianBlur(source,(0,0),sigma) if sigma else source
    x0,y0,x1,y1=case['crop'];H=(y1-y0)*scale;W=(x1-x0)*scale
    result=np.zeros((H,W,3),np.float32);coverage=np.zeros((H,W),np.float32)
    for top in range(0,H,16):
        bot=min(top+16,H);yy,xx=np.mgrid[top*samples:bot*samples,0:W*samples]
        x=(x0+(xx+.5)/(scale*samples)-.5-case['center'][0])/L;y=(y0+(yy+.5)/(scale*samples)-.5-case['center'][1])/L
        X,Y=mapping(x,y,p)
        def at(image):return cv2.remap(image,(X*L+case['center'][0]).astype(np.float32),(Y*L+case['center'][1]).astype(np.float32),cv2.INTER_LINEAR)
        C=at(blur)
        if p.get('blur_transition'):
            sd,*_=baseline.boundary(x,y,p);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);clear=at(source);C=clear+(C-clear)*w[...,None]
        C=shade(C,baseline.lighting(x,y,p),np.asarray(p['material']));sd,*_=baseline.boundary(x,y,p);inside=(sd<=0).astype(float)
        shape=(bot-top,samples,W,samples);weight=inside.reshape(shape).sum((1,3));result[top:bot]=(C*inside[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(weight,1)[...,None];coverage[top:bot]=weight/(samples*samples)
    if p.get('post_sigma'):
        sigma=p['post_sigma']*L*scale;numerator=cv2.GaussianBlur(result*coverage[...,None],(0,0),sigma);denominator=cv2.GaussianBlur(coverage,(0,0),sigma);result=numerator/np.maximum(denominator,1e-12)[...,None]
    return result,coverage
