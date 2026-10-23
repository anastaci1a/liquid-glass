"""Closed B geometry only. No ray tracer imports, images or source access."""
from pathlib import Path
import sys,json,time,traceback
import numpy as np
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'code'))
from closed_crowned_surface import ClosedCrownedSurface
from crowned_footprint import longitudinal
cfg=json.loads((P/'experiment.json').read_text());deadline=cfg['deadline_unix']
R={'status':'RUNNING','geometry_rays':0,'images':0,'fits':0,'source_work':0,'checks':{},'level_points':0}
rng=np.random.default_rng(222)
def save(name='report.json'):(P/name).write_text(json.dumps(R,indent=2,allow_nan=False))
def level(s,p):
    R['level_points']+=int(np.asarray(p).size//3)
    return s.level_gradient(p)
def check(name,ok,details):
    R['checks'][name]={'pass':bool(ok),'details':details};save()
    if not ok:raise AssertionError(name)
    if time.time()>deadline:raise TimeoutError('Original 15-minute budget exceeded')
def error(a,b):return float(np.max(abs(np.asarray(a)-np.asarray(b))))
def boundary_mesh(s):
    # Geometry vertices use the SAME sheet roots of F, never a decorative mesh.
    a,b=s.half;eta=s.eta;xs=np.linspace(-a,a,33)[1:-1]
    angles=np.arange(64)*2*np.pi/64+np.pi/64
    vertices=[[-a,0.,-eta]]
    for x in xs:
        q,_=longitudinal(x,a,b,s.softness)
        y=np.sqrt(b*b-q*q)*np.sin(angles)
        zf,zb=s.sheet_heights(np.full_like(y,x),y)
        z=np.where(np.cos(angles)>0,zf,zb)
        vertices.extend(np.stack([np.full_like(y,x),y,z],-1).tolist())
    vertices.append([a,0.,-eta]);v=np.array(vertices);faces=[]
    for j in range(64):faces.append([0,1+j,1+(j+1)%64])
    for row in range(len(xs)-1):
        for j in range(64):
            a0=1+row*64+j;a1=1+row*64+(j+1)%64;b0=a0+64;b1=a1+64
            faces.extend([[a0,b0,a1],[a1,b0,b1]])
    end=len(v)-1;start=1+(len(xs)-1)*64
    for j in range(64):faces.append([end,start+(j+1)%64,start+j])
    faces=np.array(faces);_,g=level(s,v)
    normal=np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]])
    reverse=np.sum(normal*g[faces].mean(axis=1),axis=-1)<0
    faces[reverse]=faces[reverse][:,[0,2,1]]
    return v,faces,g
try:
    if '--remaining' not in sys.argv:
        for k in [0.,1/3]:
            s=ClosedCrownedSurface(kappa=k);points=rng.uniform(-1,1,(160,3))*s.half_extents+s.center
            F,G=level(s,points);errors=[]
            for step in [1e-6,5e-7]:
                fd=np.zeros_like(points)
                for axis in range(3):
                    shift=np.eye(3)[axis]*step
                    fd[:,axis]=(level(s,points+shift)[0]-level(s,points-shift)[0])/(2*step)
                errors.append(error(fd,G))
            check(f'gradient_{k}',max(errors)<2e-8,{'steps':[1e-6,5e-7],'absolute_errors':errors})
        c=ClosedCrownedSurface(half=(1.,1.),radial_fixture=True)
        p=rng.uniform(-1,1,(301,3))*c.half_extents+c.center
        u=(p[:,2]+c.eta)/c.eta
        expected=p[:,0]**2+p[:,1]**2+u*u-1
        gradient=np.stack([2*p[:,0],2*p[:,1],2*u/c.eta],axis=-1)
        F,G=level(c,p)
        check('true_circle_ellipsoid',error(F,expected)==0 and error(G,gradient)==0,{'level_error':error(F,expected),'gradient_error':error(G,gradient),'fixture':'True radial T=x²+y², kappa0; not softened equal-half crown. Root circle adapter equality awaits its independently owned implementation.'})
        x=np.array([0.,.3,1.,1.01]);y=np.zeros_like(x);z,inside=c.front_height(x,y)
        exact=-c.eta+c.eta*np.sqrt(1-x[:3]**2)
        check('circle_front_API',error(z[:3],exact)==0 and np.array_equal(inside,[True,True,False,False]) and np.array_equal(c.boundary_mask(x,y),[False,False,True,False]) and np.isnan(z[3]),'Front z finite at tangent but strict_insideFalse, outsideNaN; exact projected tangent separate')
        R['status']='GRADIENT_CIRCLE_CHECKPOINT_PASS';save('checkpoint.json');save();print(json.dumps({'checkpoint':R['status'],'level_points':R['level_points']}),flush=True);sys.exit(0)
    R=json.loads((P/'checkpoint.json').read_text())
    for k in [0.,1/3]:
        s=ClosedCrownedSurface(kappa=k);a,b=s.half;eta=s.eta
        v,faces,g=boundary_mesh(s);F,_=level(s,v)
        check(f'mesh_boundary_{k}',np.isfinite(v).all() and error(F,0)<2e-13,{'vertices':len(v),'triangles':len(faces),'max_F_residual':error(F,0)})
        edges=np.sort(np.concatenate([faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]]),axis=1)
        _,counts=np.unique(edges,axis=0,return_counts=True)
        areas=np.linalg.norm(np.cross(v[faces[:,1]]-v[faces[:,0]],v[faces[:,2]]-v[faces[:,0]]),axis=-1)
        check(f'closed_mesh_{k}',np.all(counts==2) and np.all(areas>0),{'every_edge_faces':2,'minimum_double_area':float(areas.min()),'caveat':'Piecewise planar facets approximate actual smooth boundary; vertices/normals satisfy actual F.'})
        lower=s.regular_gradient_lower_bound;norm=np.linalg.norm(g,axis=-1)
        check(f'regular_boundary_{k}',np.all(norm>=lower),{'analytic_global_lower_bound':lower,'observed_minimum':float(norm.min()),'proof':'Boundary sum q²/b²+y²/b²+s*u²=1; one >=1/3. qprime>=q/a, same-sign kappa term. Thus normgradF>=min(2/(3a),2/(sqrt3 b),2/(sqrt3 eta))>0.'})
        points=rng.uniform(-1,1,(240,3))*s.half_extents+s.center
        F,G=level(s,points);transforms=[]
        for axis in range(3):
            d=points-s.center;d[:,axis]*=-1;Fm,Gm=level(s,d+s.center);target=G.copy();target[:,axis]*=-1
            transforms.extend([error(Fm,F),error(Gm,target)])
        check(f'center_reflections_{k}',max(transforms)<2e-13,{'maximum_error':max(transforms),'z_symmetry':'About z=-eta, not front plane'})
        angle=.731;Q=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1.]])
        world=(points-s.center)@Q.T+s.center
        # Rigidly transformed same surface; no new per-control orientation law.
        Flocal,Glocal=level(s,(world-s.center)@Q+s.center)
        check(f'rigid_rotation_{k}',error(Flocal,F)<2e-13 and error(Glocal@Q.T,G@Q.T)<2e-13,{'level_error':error(Flocal,F),'gradient_error':error(Glocal@Q.T,G@Q.T)})
        scale=2.5;scaled=ClosedCrownedSurface(half=(a*scale,b*scale),eta=eta*scale,kappa=k)
        Fs,Gs=level(scaled,points*scale)
        check(f'all_length_scale_{k}',error(Fs,F)<2e-13 and error(Gs*scale,G)<2e-13,{'level_error':error(Fs,F),'gradient_error':error(Gs*scale,G),'center_extents_scale':bool(np.allclose(scaled.center,s.center*scale) and np.allclose(scaled.half_extents,s.half_extents*scale))})
        # Analytic Hessian certificate on the convex enclosing |x|<=a strip.
        x,y,z=points.T;u=(z+eta)/eta;X=x/a;e=s.softness*b;neck=a-b;radius=np.hypot(x,e)
        sig=1/(1+np.exp(-(radius-neck)/e));den=np.logaddexp(0,(np.hypot(a,e)-neck)/e)-np.logaddexp(0,(e-neck)/e)
        q,qp=longitudinal(x,a,b,s.softness)
        qpp=b/den*(sig*(1-sig)*x*x/(e*e*radius*radius)+sig*e/radius**3)
        Hess=np.zeros((len(points),3,3));Hess[:,0,0]=2*(qp*qp+q*qpp)/(b*b)+2*k*u*u/(a*a);Hess[:,1,1]=2/(b*b);Hess[:,2,2]=2*(1+k*X*X)/(eta*eta);Hess[:,0,2]=Hess[:,2,0]=4*k*x*u/(a*a*eta)
        eig=float(np.linalg.eigvalsh(Hess).min());det=4*k*u*u*(1-3*k*X*X)
        check(f'convexity_certificate_{k}',eig>=-2e-12 and float(det.min())>=-2e-14,{'analytic':'G=u²+kappa*X²u² has nonnegative diagonal Hessian and determinant4*kappa*u²*(1-3*kappa*X²)>=0 on |X|<=1. T convex. F convex on enclosing strip; all F<=0 lies in strip because q(a)=b and added terms nonnegative. Sublevel is convex/compact.','sample_minimum_Hessian_eigenvalue':eig,'sample_minimum_G_determinant':float(det.min()),'numerical_role':'Corroboration, not global proof'})
        # Boundary chords: no fitted geometry, no ray intersections.
        left=v[rng.integers(0,len(v),500)];right=v[rng.integers(0,len(v),500)];t=rng.random((500,1));chords=t*left+(1-t)*right
        fc,_=level(s,chords)
        check(f'convex_chords_{k}',float(fc.max())<2e-13,{'max_chord_F':float(fc.max())})
        eq=np.array([[a,0.,-eta],[-a,0.,-eta],[0.,b,-eta],[0.,-b,-eta]])
        ef,eg=level(s,eq);front,strict=s.front_height(eq[:,0],eq[:,1])
        check(f'equator_tangent_{k}',error(ef,0)<1e-14 and np.all(np.linalg.norm(eg,axis=-1)>0) and np.all(s.boundary_mask(eq[:,0],eq[:,1])) and not np.any(strict) and error(front,-eta)<1e-14,'Smooth regular implicit equator, projected orthographic tangency, NOT A crease. No entry normal fabricated.')
        sx=np.linspace(-a,a,301);sy=np.linspace(-b,b,301);xf,xb=s.section(sx,'x');yf,yb=s.section(sy,'y')
        section=np.concatenate([xf,xb,yf,yb]);sf,_=level(s,section)
        check(f'actual_sections_{k}',np.isfinite(section).all() and error(sf,0)<2e-13 and error(s.front_height(0.,0.)[0],0)==0,{'max_section_F':error(sf,0),'center_back':float(s.sheet_heights(0,0)[1]),'front_center_xx':-eta*k/(a*a),'expected_limit':'kappa0 retains zero centerline longitudinal second curvature; kappa1/3 introduces true curved front/back independent of projected silhouette.'})
        tag='0' if k==0 else 'one-third'
        np.savez(P/f'geometry-{tag}.npz',vertices=v,faces=faces,outward_gradient=g,x_front=xf,x_back=xb,y_front=yf,y_back=yb)
        with (P/f'surface-{tag}.obj').open('w') as f:
            f.write('# Actual F boundary vertices. Units L, center z=-eta; no rays or source.\n')
            for row in v:f.write('v '+' '.join(format(float(q),'.17g') for q in row)+'\n')
            for row in faces:f.write('f '+' '.join(str(int(q)+1) for q in row)+'\n')
        np.savetxt(P/f'sections-{tag}.csv',section,delimiter=',',header='x,y,z; ordered xfront,xback,yfront,yback')
    R['status']='PASS_CLOSED_B_GEOMETRY_ONLY';R['finished_unix']=time.time();save();print(json.dumps({'status':R['status'],'checks':len(R['checks']),'level_points':R['level_points'],'geometry_rays':0}),flush=True)
except Exception as ex:
    R['status']='STOP_FIRST_FAILURE';R['error']=repr(ex);R['traceback']=traceback.format_exc();save();raise
