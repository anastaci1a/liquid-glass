"""Bounded geometry-only verification; no image/source access or fitting."""
import sys,json,time,traceback
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from crowned_bevel import CrownedBevel
from geometric_optics import CircularBevel,refract,trace_flat_front_orthographic
from crowned_footprint import longitudinal
DEADLINE=1792640797.369
report={'status':'RUNNING','rays':0,'checks':{},'image_renders':0,'fits':0,'source_registrations':0}
rng=np.random.default_rng(222)
def save(name='report.json'):
    (ROOT/name).write_text(json.dumps(report,indent=2,allow_nan=False))
def check(name,condition,details):
    report['checks'][name]={'pass':bool(condition),'details':details}
    if not condition:raise AssertionError(name)
    if time.time()>DEADLINE:raise TimeoutError('Declared 15-minute budget exhausted')
def trace(s,x,y,n=1.5,D=2):
    report['rays']+=int(np.broadcast_arrays(x,y)[0].size)
    if report['rays']>50000:raise RuntimeError('Ray budget exhausted')
    if time.time()>DEADLINE:raise TimeoutError('Declared wall budget exhausted')
    return trace_flat_front_orthographic(s,x,y,n,D)
def err(a,b):return float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
def points(s,N):
    x=rng.uniform(-s.half[0],s.half[0],N*3);y=rng.uniform(-s.half[1],s.half[1],N*3)
    m=s.level(x,y)[0]<.95
    return x[m][:N],y[m][:N]
try:
    if '--remaining' in sys.argv:
        report=json.loads((ROOT/'checkpoint.json').read_text())
    else:
        for depth in [.02,.04]:
            s=CrownedBevel(depth=depth);x,y=points(s,400)
            h,hx,hy,_=s.height_gradient(x,y); errors=[]
            for step in [1e-5,5e-6]:
                dx=(s.height_gradient(x+step,y)[0]-s.height_gradient(x-step,y)[0])/(2*step)
                dy=(s.height_gradient(x,y+step)[0]-s.height_gradient(x,y-step)[0])/(2*step)
                errors.append(max(err(dx,hx),err(dy,hy)))
            check(f'gradient_{depth}',max(errors)<2e-8,{'FD_steps':[1e-5,5e-6],'max_errors':errors})
            c=CrownedBevel(half=(1.,1.),depth=depth,radial_fixture=True)
            lead=CircularBevel(core=0.,depth=depth,power=3,edge=0.)
            cx=rng.uniform(-1.1,1.1,600);cy=rng.uniform(-1.1,1.1,600)
            check(f'circle_height_exact_{depth}',all(np.array_equal(a,b) for a,b in zip(c.height_gradient(cx,cy),lead.height_gradient(cx,cy))), 'True radial fixture, not equal-half softened crown')
            a=trace(c,cx,cy);b=trace(lead,cx,cy)
            check(f'circle_trace_exact_{depth}',all(np.array_equal(a[k],b[k],equal_nan=True) for k in a),'All shared tracer output arrays bit-exact')
        report['status']='GRADIENT_AND_CIRCLE_CHECKPOINT_PASS';save('checkpoint.json');save()
        print(json.dumps({'checkpoint':report['status'],'rays':report['rays']}),flush=True)
        # Stop here so the agent can report the mandatory intermediate checkpoint.
        if '--remaining' not in sys.argv:sys.exit(0)
    for depth in [.02,.04]:
        s=CrownedBevel(depth=depth);x,y=points(s,700);h,hx,hy,inside=s.height_gradient(x,y)
        center=[]
        for e in [.01,.005,.0025]:
            # Symmetric gradient difference estimates the center Hessian.
            xx=(s.height_gradient(e,0)[1]-s.height_gradient(-e,0)[1])/(2*e)
            yy=(s.height_gradient(0,e)[2]-s.height_gradient(0,-e)[2])/(2*e)
            center.append(float(max(abs(xx),abs(yy))))
        check(f'C2_center_{depth}',s.height_gradient(0,0)[1]==0 and s.height_gradient(0,0)[2]==0 and all(b<a for a,b in zip(center,center[1:])),{'Hessian_estimates':center,'analytic_limit':'zero; norm(convex smooth coordinate)^3 is C2 at origin'})
        hm,mx,my,_=s.height_gradient(-x,y)
        rotated=CrownedBevel(half=s.half[::-1],depth=depth)
        hr,rx,ry,_=rotated.height_gradient(-y,x)
        symmetry=max(err(h,hm),err(hx,-mx),err(hy,my),err(h,hr),err(rx,-hy),err(ry,hx))
        hyflip,fx,fy,_=s.height_gradient(x,-y)
        symmetry=max(symmetry,err(h,hyflip),err(hx,fx),err(hy,-fy))
        check(f'mirror_rotation_{depth}',symmetry<1e-13,{'max_error':symmetry})
        p=trace(s,x,y);pr=trace(rotated,-y,x)
        check(f'rotation_rays_{depth}',max(err(pr['X'],-p['Y']),err(pr['Y'],p['X']))<1e-13,'Quarter-turn covariance')
        scale=2.5;scaled=CrownedBevel(half=tuple(scale*np.array(s.half)),depth=scale*depth)
        sh,sx,sy,_=scaled.height_gradient(scale*x,scale*y)
        ps=trace(scaled,scale*x,scale*y,D=2*scale)
        se=max(err(sh,scale*h),err(sx,hx),err(sy,hy),err(ps['X'],scale*p['X']),err(ps['Y'],scale*p['Y']))
        check(f'scale_{depth}',se<2e-13,{'scale':scale,'max_error':se,'all_lengths_scaled':True})
        identity=trace(s,x,y,n=1.)
        check(f'n1_identity_{depth}',max(err(identity['X'],x),err(identity['Y'],y))<1e-13,'No displacement at index1')
        # Global certificates are analytic; dense samples below are corroboration.
        xx,yy=np.meshgrid(np.linspace(-s.half[0],s.half[0],141),np.linspace(-1,1,91))
        gh,gx,gy,gi=s.height_gradient(xx,yy)
        observed=float(np.max(np.hypot(gx[gi],gy[gi])))
        check(f'height_slope_{depth}',float(gh[gi].min())>=-1e-14 and float(gh[gi].max())<=depth+1e-14 and observed<=s.slope_bound*(1+1e-12),{'height_range':[float(gh[gi].min()),float(gh[gi].max())],'observed_slope':observed,'analytic_slope_bound':s.slope_bound,'n1.5_limit':float(1/np.sqrt(1.5**2-1))})
        # Hessian from analytic gradients; a grid is not a global proof.
        e=2e-5
        _,xp,yp,_=s.height_gradient(x+e,y);_,xm,ym,_=s.height_gradient(x-e,y)
        _,xq,yq,_=s.height_gradient(x,y+e);_,xr,yr,_=s.height_gradient(x,y-e)
        H=np.zeros((len(x),2,2));H[:,0,0]=(xp-xm)/(2*e);H[:,1,1]=(yq-yr)/(2*e)
        H[:,0,1]=H[:,1,0]=((yp-ym)+(xq-xr))/(4*e)
        maxeig=float(np.linalg.eigvalsh(H).max())
        check(f'concavity_numeric_{depth}',maxeig<2e-8,{'max_eigenvalue':maxeig,'global_proof':'q>=0,q convex; rho=norm(q,abs(y))/b convex; shared profile decreasing concave; hypograph solid convex. Numerical check is corroboration only.'})
        ax=np.array([s.half[0],-s.half[0],0.,0.]);ay=np.array([0.,0.,1.,-1.])
        eh,*_=s.height_gradient(ax,ay)
        check(f'closure_crease_{depth}',err(eh,0)<1e-13 and np.all(s.boundary_kind(ax,ay)=='CREASE'),{'max_front_back_gap':err(eh,0),'edge_normal':'No unique whole-solid normal; back-face limit only. Exact crease rays excluded from fixture.'})
        section=s.section(np.linspace(-s.half[0]*.99,s.half[0]*.99,101))
        check(f'same_section_{depth}',np.array_equal(section['back'],s.back_vertices(section['front'][:,0],section['front'][:,1]),equal_nan=True),'Section and mesh call actual height')
        d=p['exit_direction'];normal=p['outward_normal']
        plane=p['back']+p['path_length'][:,None]*d
        check(f'branch_{depth}',np.all(p['complete']) and np.all(d[:,2]<0) and np.all(p['discriminant']>0) and np.all(np.sum(d*normal,axis=-1)>0) and err(plane[:,2],-2)<1e-12 and max(err(plane[:,0],p['X']),err(plane[:,1],p['Y']))<1e-12 and err(np.linalg.norm(d,axis=-1),1)<1e-12,{'max_plane_z_error':err(plane[:,2],-2),'min_discriminant':float(p['discriminant'].min()),'no_reentry':'Analytic convex-solid/back concavity certificate, not sampled intersections'})
        incident=np.zeros_like(d);incident[:,2]=-1
        it=incident-np.sum(incident*normal,axis=-1)[:,None]*normal
        dt=d-np.sum(d*normal,axis=-1)[:,None]*normal
        reverse,tir,k=refract(-d,normal,1.,1.5);report['rays']+=len(d)
        target=np.zeros_like(d);target[:,2]=1
        check(f'Snell_reciprocity_{depth}',err(1.5*it,dt)<1e-12 and not np.any(tir) and err(reverse,target)<1e-12,{'tangent_error':err(1.5*it,dt),'reverse_error':err(reverse,target)})
        np.savez(ROOT/f'geometry-depth-{depth}.npz',x=x,y=y,h=h,hx=hx,hy=hy,**p)
    s=CrownedBevel(depth=.04); rejected=[]
    for name,n,D in [('insufficient_gap',1.5,.04),('unsupported_global_slope',20.,2.)]:
        try:trace(s,np.array([0.]),np.array([0.]),n,D)
        except ValueError as ex:rejected.append({'fixture':name,'reason':str(ex)})
    check('invalid_scene_rejection',len(rejected)==2,rejected)
    v=np.array([[np.sqrt(3)/2,0.,-.5]])
    out,tir,k=refract(v,np.array([[0.,0.,1.]]),1.5,1.);report['rays']+=1
    check('explicit_TIR',bool(tir[0]) and np.isnan(out).all(),{'discriminant':float(k[0]),'no_replacement_ray':True})
    report['status']='PASS_GEOMETRY_ONLY';report['finished_unix']=time.time();save()
    print(json.dumps({'status':report['status'],'rays':report['rays'],'checks':len(report['checks'])}),flush=True)
except Exception as ex:
    report['status']='STOP_FIRST_FAILURE';report['error']=repr(ex);report['traceback']=traceback.format_exc();save()
    print(json.dumps({'status':report['status'],'error':repr(ex),'rays':report['rays']}),flush=True)
    sys.exit(1)
