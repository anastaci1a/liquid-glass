"""Geometry checkpoint and analytic derivatives of the SAME height/trace law."""
from pathlib import Path
import sys,json,time
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'code'))
from harmonic_crowned_back import HarmonicCrownedBack
from geometric_optics import HarmonicCircularBack,trace_flat_front_orthographic,harmonic_cap
from crowned_footprint import longitudinal
cfg=json.loads((P/'experiment.json').read_text());R={'rays':0,'checks':{},'status':'RUNNING'}
def trace(s,x,y,n=1.5):
    R['rays']+=int(np.broadcast_arrays(x,y)[0].size)
    if R['rays']>20000 or time.time()>cfg['deadline_unix']:raise RuntimeError('Original checkpoint budget exceeded')
    return trace_flat_front_orthographic(s,x,y,n,2.)
def check(name,ok,details):
    R['checks'][name]={'pass':bool(ok),'details':details};(P/'checkpoint.json').write_text(json.dumps(R,indent=2))
    if not ok:raise AssertionError(name)
def actual_hessian_and_Jxx(s,x,y):
    """Analytic differential diagnostic; NEVER used to generate image addresses."""
    x,y=np.broadcast_arrays(x,y);a,b=s.half;e=s.softness*b;neck=a-b;r=np.hypot(x,e)
    q,qp=longitudinal(x,a,b,s.softness);sig=1/(1+np.exp(-(r-neck)/e));den=np.logaddexp(0,(np.hypot(a,e)-neck)/e)-np.logaddexp(0,(e-neck)/e)
    qpp=b/den*(sig*(1-sig)*x*x/(e*e*r*r)+sig*e/r**3)
    T,tx,ty=s.base.level(x,y);rho=np.sqrt(T);txx=2*(qp*qp+q*qpp)/(b*b)
    h1,g1x,g1y,_=s.base.height_gradient(x,y);h2=s.crown_depth*(1-(x/a)**2);g2x=-2*s.crown_depth*x/(a*a)
    h,w1,w2=harmonic_cap(h1,h2);total=h1+h2
    h1xx=-1.5*s.depth*(np.divide(.5*tx*tx,rho,out=np.zeros_like(rho),where=rho>0)+rho*txx)
    h1xy=-.75*s.depth*np.divide(tx*ty,rho,out=np.zeros_like(rho),where=rho>0)
    H11=-2*h2*h2/total**3;H12=2*h1*h2/total**3;H22=-2*h1*h1/total**3
    hxx=w1*h1xx+w2*(-2*s.crown_depth/(a*a))+H11*g1x*g1x+2*H12*g1x*g2x+H22*g2x*g2x
    hxy=w1*h1xy+H11*g1x*g1y+H12*g2x*g1y
    _,hx,hy,_=s.height_gradient(x,y);n=1.5;v=1+hx*hx+hy*hy;k=1-n*n+n*n/v
    C=n/v-np.sqrt(k/v);Cs=-n/v**2+((1-n*n)/v**2+2*n*n/v**3)/(2*np.sqrt(k/v))
    ratio=C/(n-C);rs=n*Cs/(n-C)**2;sx=2*(hx*hxx+hy*hxy)
    J=1-hx*hx*ratio+(2-h)*(ratio*hxx+hx*rs*sx)
    return hxx,J
if __name__=='__main__':
    try:
        R=json.loads((P/'failed-first/checkpoint.json').read_text());R['status']='RESUMED_ORIGINAL_BUDGET';R.pop('error',None)
        s=HarmonicCrownedBack()
        cx,cy=np.meshgrid(np.linspace(-1,1,21),np.linspace(-1,1,21));own=HarmonicCrownedBack(half=(1.,1.),radial_fixture=True);root=HarmonicCircularBack()
        co=trace(own,cx,cy);cr=trace(root,cx,cy);err={}
        for key in co:
            if co[key].dtype==bool:assert np.array_equal(co[key],cr[key]);continue
            assert np.array_equal(np.isnan(co[key]),np.isnan(cr[key]));m=np.isfinite(co[key]);err[key]=float(abs(co[key][m]-cr[key][m]).max()) if m.any() else 0.
        check('shared_circle_isotropic_fixture',max(err.values())<1e-12,err)
        xx,yy=np.meshgrid(np.linspace(-s.half[0],s.half[0],71),np.linspace(-1,1,71));o=trace(s,xx,yy);valid=o['inside']&~o['boundary_unresolved']
        hh,gx,gy,_=s.height_gradient(xx,yy)
        check('global_certificates',s.slope_bound<1/np.sqrt(1.5**2-1) and np.all(np.hypot(gx,gy)[valid]<=s.slope_bound+1e-12) and np.all(hh>=0) and np.all(hh<=s.maximum_height+1e-12),{'maximum_height':s.maximum_height,'global_slope_bound':s.slope_bound,'observed_slope_max':float(np.hypot(gx,gy)[valid].max()),'proof':'h1,h2 concave and nonnegative; shared H increasing concave with nonnegative weights summing<=1. Gradient bound=max(bounds). Exact crease unresolved, no boundary normal claimed.'})
        check('all_regular_primary_paths_complete',np.all(o['complete'][valid]) and np.all(o['discriminant'][valid]>0) and np.all(o['exit_direction'][valid,2]<0),{'regular_inside':int(valid.sum()),'tangent':int(o['boundary_unresolved'].sum()),'minimum_discriminant':float(o['discriminant'][valid].min())})
        identity=trace(s,xx,yy,n=1.);check('unit_index_identity',np.array_equal(identity['X'][valid],xx[valid]) and np.array_equal(identity['Y'][valid],yy[valid]),'Boundary remains unresolved')
        sx=np.linspace(0,.9,24);sy=np.linspace(-.43,.04,24);hxx,J=actual_hessian_and_Jxx(s,sx,sy);jerrors=[]
        for step in [1e-5,5e-6]:
            plus=trace(s,sx+step,sy)['X'];minus=trace(s,sx-step,sy)['X'];jerrors.append(float(abs((plus-minus)/(2*step)-J).max()))
        check('analytic_actual_source_Jxx',max(jerrors)<2e-8,{'steps':[1e-5,5e-6],'max_errors':jerrors,'meaning':'Analytic derivative of actual h/H and shared flatfront Snell/background equation, not a renderer warp.'})
        center_y=np.array([-.95,-.75,-.5,-.25,0.,.25,.5,.75,.95]);ch,cj=actual_hessian_and_Jxx(s,np.zeros_like(center_y),center_y)
        np.savez(P/'checkpoint-paths.npz',x=xx,y=yy,**o)
        R['centerline']={'y':center_y.tolist(),'hxx':ch.tolist(),'source_X_x':cj.tolist()};R['status']='PASS_CHECKPOINT';R['finished_unix']=time.time();(P/'checkpoint.json').write_text(json.dumps(R,indent=2));print(json.dumps(R))
    except Exception as e:
        R['status']='STOP_FIRST_FAILURE';R['error']=repr(e);(P/'checkpoint.json').write_text(json.dumps(R,indent=2));raise
