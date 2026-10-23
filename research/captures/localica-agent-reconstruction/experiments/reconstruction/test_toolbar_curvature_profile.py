"""Independent geometry/invariance checks required before the private fit."""
import sys,json,copy,time
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import toolbar_candidate as baseline
import toolbar_curvature_profile as model
cv2.setNumThreads(1)
root=Path('/tmp/agent-toolbar-evidence-package');out=Path('/tmp/agent-toolbar-revision2-curvature-checks');out.mkdir(exist_ok=True)
p=json.loads((root/'recipe.json').read_text());p['curvature_normal']={'amplitude':0.,'width':.2*p['shape']['radius']}
g=model.geometry(tuple(p['shape']['half']),p['footprint_softness']);rows={};began=time.time()

def record(name,values):
    rows[name]=values;(out/'checks-in-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print('CHECK',name,values,flush=True)

table=g.arc_table(4096);fine=g.arc_table(8192);perimeter_relative=abs(table['perimeter']/fine['perimeter']-1);turn_error=abs(fine['total_turn']-2*np.pi)
assert perimeter_relative<1e-9 and turn_error<5e-8
record('perimeter_and_total_turn',{'perimeter':fine['perimeter'],'relative_4096_to_8192':perimeter_relative,'total_turn_error':turn_error})

theta=(np.arange(63)+.37)*2*np.pi/63;qx,qy=g.radial_boundary(theta);f,fx,fy,*_=g.field_hessian(qx,qy);norm=np.hypot(fx,fy);nx=fx/norm;ny=fy/norm
h=1e-5*g.L
normal=lambda x,y:np.array(g.boundary(x,y)[1:])
div=((normal(qx+h,qy)-normal(qx-h,qy))[0]+(normal(qx,qy+h)-normal(qx,qy-h))[1])/(2*h)
curvature_error=float(np.max(np.abs(div-g.curvature(qx,qy)))*g.L)
assert curvature_error<2e-6 and np.max(np.abs(f))<1e-12
record('analytic_curvature_vs_normal_divergence',{'normalized_max_error':curvature_error,'boundary_field_error':float(np.max(np.abs(f)))})

distance=(.015+.035*(1+np.cos(theta))/2)*g.L;x=qx-distance*nx;y=qy-distance*ny
cx,cy=g.closest_boundary(x,y);projection_error=float(np.max(np.hypot(cx-qx,cy-qy))/g.L)
global_samples=np.sqrt((x[:,None]-fine['x'][None,:])**2+(y[:,None]-fine['y'][None,:])**2).min(1)
global_margin=float(np.min(global_samples-distance)/g.L)
assert projection_error<2e-9 and global_margin>-1e-10
record('true_closest_boundary',{'normalized_point_error':projection_error,'sampled_global_distance_minus_solution_min':global_margin,'samples':len(x)})

circle=model.CrownGeometry((1.,1.),0.)
cp=copy.deepcopy(p);cp['shape']['half']=[1.,1.];cp['shape']['radius']=1.;cp['footprint_softness']=0.;cp['curvature_normal']['amplitude']=.2
circle_delta=model.curvature_delta(.9*np.cos(theta),.9*np.sin(theta),cp)
assert np.array_equal(circle_delta,np.zeros_like(circle_delta))
assert abs(circle.perimeter-2*np.pi)<1e-12
record('true_circle_zero_correction',{'exact_zero':True,'perimeter_error':abs(circle.perimeter-2*np.pi),'note':'Explicit Euclidean circle, not a softened equal-half crown'})

q=copy.deepcopy(p);q['curvature_normal']['amplitude']=.05
def addition(x,y,q):
    d=model.curvature_delta(x,y,q);_,nx,ny=baseline.boundary(x,y,q)
    return np.stack([-d*nx,-d*ny])
D=addition(x,y,q);mirror=addition(-x,y,q);mirror_error=float(np.max(np.abs(mirror-D*np.array([-1,1])[:,None]))/g.L)
rot=copy.deepcopy(q);rot['shape']['half']=list(reversed(q['shape']['half']));RD=addition(-y,x,rot);rotation_error=float(np.max(np.abs(RD-np.stack([-D[1],D[0]])))/g.L)
scale_errors=[]
for s in [.25,3.,1000.]:
    scaled=copy.deepcopy(q);scaled['shape']['half']=(np.array(q['shape']['half'])*s).tolist();scaled['shape']['radius']*=s;scaled['curvature_normal']['width']*=s
    scale_errors.append(float(np.max(np.abs(addition(x*s,y*s,scaled)/s-D))/g.L))
assert max(mirror_error,rotation_error,*scale_errors)<2e-9
record('mirror_rotation_scale',{'mirror_error':mirror_error,'rotation_90_error':rotation_error,'scale_errors':scale_errors})

# Polynomial identities independently establish C2 support at both endpoints.
u=np.array([0.,1.]);B1=192*u**2*(1-u)**2*(1-2*u);B2=384*u*(1-u)*(1-5*u+5*u*u)
assert np.array_equal(model.bump(u),np.zeros(2)) and np.array_equal(B1,np.zeros(2)) and np.array_equal(B2,np.zeros(2)) and model.bump(.5)==1.
oldX,oldY=baseline.mapping(qx,qy,p);newX,newY=model.mapping(qx,qy,q)
edge_difference=float(np.max(np.hypot(newX-oldX,newY-oldY)));baseline_edge=float(np.max(np.hypot(oldX-qx,oldY-qy)))
assert edge_difference<1e-12*g.L and baseline_edge>.1*g.L
record('C2_bump_and_nonzero_baseline_edge',{'B_Bprime_Bsecond_at_endpoints_exact_zero':True,'addition_edge_difference':edge_difference,'baseline_edge_max_displacement':baseline_edge})

bound=g.displacement_bound(.12);(out/'target-independent-bound.json').write_text(json.dumps(bound,indent=2)+'\n');record('declared_displacement_bound',bound)
source=np.asarray(Image.open(root/'inputs/source.png'),float)/255;case=p['case']
C,a=model.render(source,case,p);C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a0=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy')
assert np.array_equal(C,C0) and np.array_equal(a,a0)
record('zero_render_recovery',{'material_exact':True,'coverage_exact':True,'sampling':'original native4x4'})

uniform=np.zeros_like(source)+np.array([.4,.55,.7]);view=copy.deepcopy(case);view['crop']=[625,350,1295,445];U0,ua=model.render(uniform,view,p);uniform_errors=[]
for sign in [-1.,1.]:
    q=copy.deepcopy(p);q['curvature_normal']['amplitude']=sign*bound['lambda_max'];U,aa=model.render(uniform,view,q)
    error=float(np.max(np.abs(U-U0)));uniform_errors.append(error);assert error<=1e-6 and np.array_equal(aa,ua)
record('uniform_input_filter_invariance',{'max_abs_normalized_RGB_error_endpoints':uniform_errors,'coverage_exact':True,'scope':'Added image-map term, fixed incumbent lighting; no claimed baseline lighting symmetry'})

# Endpoints bound every coefficient between them because ray positions are affine
# in the ONE coefficient. This is new-family source proof, no optimization trial.
unit=copy.deepcopy(p);unit['curvature_normal']['amplitude']=1.;x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;L=min(case['half']);extrema=np.array([np.inf,np.inf,-np.inf,-np.inf]);count=0;max_add=0.
for top in range(0,H,16):
    bot=min(top+16,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4]
    x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L
    X,Y=baseline.mapping(x,y,p);delta=model.curvature_delta(x,y,unit);_,nx,ny=baseline.boundary(x,y,p);max_add=max(max_add,float(np.max(np.abs(delta)))*bound['lambda_max']/g.L)
    for sign in [-1.,1.]:
        sx=(X-sign*bound['lambda_max']*delta*nx)*L+case['center'][0];sy=(Y-sign*bound['lambda_max']*delta*ny)*L+case['center'][1]
        extrema=np.array([min(extrema[0],sx.min()),min(extrema[1],sy.min()),max(extrema[2],sx.max()),max(extrema[3],sy.max())])
    count+=x.size
margin=3*p['source_sigma']*L+1;conservative_filter_margin=float(np.ceil(4*p['source_sigma']*L)+2)
safe=bool(extrema[0]>conservative_filter_margin and extrema[1]>conservative_filter_margin and extrema[2]<source.shape[1]-1-conservative_filter_margin and extrema[3]<source.shape[0]-1-conservative_filter_margin)
assert safe and max_add<=.12+1e-9
record('native_endpoint_ray_domain',{'rays_per_endpoint':count,'endpoint_total_rays':2*count,'bounds_xyxy':extrema.tolist(),'maximum_added_displacement_fraction':max_add,'three_sigma_plus_bilinear_margin':margin,'conservative_four_sigma_plus2_margin':conservative_filter_margin,'both_endpoints_and_between_defined':safe,'estimated_source_remains_estimated':True})
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','checks':rows,'optical_fit_trials':0,'counted_passes':0,'seconds':time.time()-began,'scope':'Empirical image-map ADDITION invariants, not identified Apple solid or total-map integrability','fixed_width':p['curvature_normal']['width'],'protocol':'original native4x4 unchanged; crop/uniform/geometry diagnostics not scoring replacements'}
(out/'invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('INVARIANTS COMPLETE',flush=True)
