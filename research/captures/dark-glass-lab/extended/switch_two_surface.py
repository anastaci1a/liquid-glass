"""Explicit entrance surface above the existing Euclidean-distance backside.

The front is a compact C2 elliptical crown, not an image-space displacement.
Rays enter at normal orthographic view direction, intersect the back by a
monotone root solve, then refract to the background. Material is unchanged.
"""
import numpy as np
from switch_euclidean_surface import EuclideanSurfaceStudy


class TwoSurfaceStudy(EuclideanSurfaceStudy):
    def surface(self,x,y,p):
        xx,yy,half,r,inside,h,hx,hy=super().surface(x,y,p)
        coupling=float(p.get('front_back_coupling',0.))
        if coupling not in [0.,-1.]:raise ValueError('Unsupported front/back coupling')
        if coupling and p.get('front_crown',0.):
            f,fx,fy,_=self.front_state(xx,yy,half,r,p,p['front_crown'])
            h+=coupling*f;hx+=coupling*fx;hy+=coupling*fy
        return xx,yy,half,r,inside,h,hx,hy

    @staticmethod
    def front(x,y,half,r,amplitude):
        u=x/half[0];v=y/half[1];q=np.maximum(1-u*u-v*v,0.)
        return amplitude*r*q**3, -6*amplitude*r*q*q*u/half[0], -6*amplitude*r*q*q*v/half[1]

    def front_state(self,xx,yy,half,r,p,a):
        if p.get('front_profile','ellipse')=='ellipse':
            return (*self.front(xx,yy,half,r,a),6*abs(a)*r/min(half))
        if p['front_profile']!='rim':raise ValueError('Unknown front surface')
        width=float(p.get('front_width',.3))
        if not .1<=width<=.75:raise ValueError('Front transition width outside bracket')
        inside,d,nx,ny=self.distance(xx,yy,half,p['crown_softness'],width*r)
        t=np.clip(d/(width*r),0,1);S=t**3*(10+t*(-15+6*t));derivative=a/width*30*t*t*(1-t)**2
        return np.where(inside,a*r*S,0.),-derivative*nx,-derivative*ny,1.875*abs(a)/width

    def geometry_field(self,x,y,p):
        a=float(p.get('front_crown',0.))
        if not np.isfinite(a) or abs(a)>.08:raise ValueError('Front crown outside declared bracket')
        if a==0:return super().geometry_field(x,y,p)
        X,Y,d,J=super().geometry_field(x,y,p)
        xx,yy,half,r,inside,h,hx,hy=self.surface(x,y,p)
        f,fx,fy,front_slope=self.front_state(xx,yy,half,r,p,a)
        active=inside&((f!=0)|(fx!=0)|(fy!=0))
        if not active.any():return X,Y,d,J
        # Front outward normal (-fx,-fy,1), air-to-solid eta=1/n.
        n=p['euclidean_surface']['n'];eta=1/n
        cf=1/np.sqrt(1+fx[active]**2+fy[active]**2)
        k=eta*cf-np.sqrt(1-eta*eta*(1-cf*cf))
        tx=-k*cf*fx[active];ty=-k*cf*fy[active];tz=-eta+k*cf
        fa=f[active];xa=x[active];ya=y[active]
        if np.any(fa+h[active]<=0):raise ValueError('Nonpositive solid thickness')
        tau=(fa+h[active])/(-tz)
        # Conservative backside slope bound used by the monochromatic model.
        q=p['euclidean_surface'];M=2*np.hypot(abs(q['bx'])*half[0]/r,abs(q['by'])*half[1]/r)+max(abs(v) for v in q['profile'])*(1+abs(q.get('longitudinal',0))*(1+2*q['width']*r/max(half)))
        M+=abs(p.get('front_back_coupling',0.))*front_slope
        if np.any(-tz<=M*np.hypot(tx,ty)):raise ValueError('Back intersection monotonicity not guaranteed')
        if np.any(-tz<=front_slope*np.hypot(tx,ty)):raise ValueError('Front reentry cannot be excluded')
        for iteration in range(12):
            ux=xa+tau*tx;uy=ya+tau*ty
            bx,by,_,_,bin_,bh,bhx,bhy=self.surface(ux,uy,p)
            if not bin_.all():raise ValueError('Ray reaches a side before back')
            residual=fa+tz*tau+bh
            if np.max(abs(residual))<1e-11:break
            derivative=tz+bhx*tx+bhy*ty
            tau-=residual/derivative
            if np.any(tau<0):raise ValueError('Back intersection behind front')
        else:raise ValueError('Back intersection failed tolerance')
        # Exit outward normal (-bhx,-bhy,-1). Snell, solid to air.
        norm=np.sqrt(1+bhx*bhx+bhy*bhy)
        nx=-bhx/norm;ny=-bhy/norm;nz=-1/norm
        ci=tx*nx+ty*ny+tz*nz;disc=1-n*n*(1-ci*ci)
        if np.any((ci<=0)|(disc<=0)):raise ValueError('Exit branch or TIR')
        k=np.sqrt(disc)-n*ci
        vx=n*tx+k*nx;vy=n*ty+k*ny;vz=n*tz+k*nz
        if np.any(-vz<=M*np.hypot(vx,vy)):raise ValueError('Back reentry cannot be excluded')
        G=q['gap']*r
        if np.any((vz>=0)|(G<=bh)):raise ValueError('Invalid transmitted background branch')
        travel=(G-bh)/(-vz)
        X[active]=ux+travel*vx;Y[active]=uy+travel*vy
        return X,Y,d,J
