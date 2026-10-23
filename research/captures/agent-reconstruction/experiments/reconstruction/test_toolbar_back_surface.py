"""Scientific invariants for the one biaxial back-surface comparator."""
import sys,json,copy,itertools
from pathlib import Path
import numpy as np
import toolbar_back_surface as m
out=Path('/tmp/agent-toolbar-back-surface');out.mkdir(exist_ok=True)
p=json.loads(Path('/tmp/agent-toolbar-evidence-package/recipe.json').read_text());p['back_surface']={'thickness':.5,'background':2.5,'ior':1.5,'b_major':-.012,'b_minor':.018,'quartic':-.12}
x,y=np.meshgrid(np.linspace(-2.3,2.3,81),np.linspace(-1,1,37));inside=m.implicit(x,y,p)[0]<.99;x=x[inside];y=y[inside];eps=1e-5
T,h,hx,hy=m.surface_field(x,y,p);hxf=(m.surface_field(x+eps,y,p)[1]-m.surface_field(x-eps,y,p)[1])/(2*eps);hyf=(m.surface_field(x,y+eps,p)[1]-m.surface_field(x,y-eps,p)[1])/(2*eps);gradient_error=max(float(np.max(np.abs(hx-hxf))),float(np.max(np.abs(hy-hyf))));assert gradient_error<1e-8
X,Y,valid,aux=m.rays(x,y,p);assert np.all(valid);G=p['back_surface']['background'];n=p['back_surface']['ior'];V=np.stack([X-x,Y-y,-(G-h)],axis=-1);V/=np.linalg.norm(V,axis=-1)[...,None];normal=np.stack([-hx,-hy,-np.ones_like(hx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1)[...,None];I=np.zeros_like(V);I[...,2]=-1;cross=np.cross(n*I-V,normal);snell_error=float(np.max(np.abs(cross)));assert snell_error<1e-12 and np.all(np.sum(V*normal,axis=-1)>0)
mirror=m.mapping(-x,y,p);mirror_error=max(float(np.max(np.abs(mirror[0]+X))),float(np.max(np.abs(mirror[1]-Y))));assert mirror_error<1e-12
rot=copy.deepcopy(p);rot['shape']['half']=list(reversed(p['shape']['half']));R=m.mapping(-y,x,rot);rotation_error=max(float(np.max(np.abs(R[0]+Y))),float(np.max(np.abs(R[1]-X))));assert rotation_error<1e-12
scaled=copy.deepcopy(p);scaled['shape']['half']=[2*v for v in p['shape']['half']];scaled['shape']['radius']*=2;S=m.mapping(2*x,2*y,scaled);scale_error=max(float(np.max(np.abs(S[0]-2*X))),float(np.max(np.abs(S[1]-2*Y))));assert scale_error<1e-12
flat=copy.deepcopy(p);flat['back_surface'].update(b_major=0.,b_minor=0.,quartic=0.);F=m.mapping(x,y,flat);assert np.array_equal(F[0],x) and np.array_equal(F[1],y)
circle=copy.deepcopy(p);circle['shape']={'half':[1.,1.],'radius':1.};circle['footprint_softness']=0.;circle['back_surface'].update(b_major=-.01,b_minor=-.01,quartic=-.1);xc=.6*np.cos(np.linspace(0,2*np.pi,157));yc=.6*np.sin(np.linspace(0,2*np.pi,157));cx,cy=m.mapping(xc,yc,circle);theta=.33;rx=np.cos(theta)*xc-np.sin(theta)*yc;ry=np.sin(theta)*xc+np.cos(theta)*yc;crx,cry=m.mapping(rx,ry,circle);circle_error=max(float(np.max(np.abs(crx-(np.cos(theta)*cx-np.sin(theta)*cy)))),float(np.max(np.abs(cry-(np.sin(theta)*cx+np.cos(theta)*cy)))));assert circle_error<1e-12
bound_checks=[]
for a,b,c in itertools.product([-.03,.03],[-.03,.03],[-.15,.15]):
    q=copy.deepcopy(p);q['back_surface'].update(b_major=a,b_minor=b,quartic=c);bounds=m.analytic_bounds(q);assert bounds['global_subcritical_positive_clearance'] and bounds['no_reentry_sufficient_product']<1
    _,height,gx,gy=m.surface_field(x,y,q);_,_,valid,aux=m.rays(x,y,q);assert np.all(valid) and height.min()>=bounds['height_lower']-1e-12 and height.max()<=bounds['height_upper']+1e-12 and np.max(np.hypot(gx,gy))<=bounds['gradient_norm_upper']+1e-12
    bound_checks.append({'parameters':[a,b,c],'analytic':bounds,'sampled_min_K':float(aux['discriminant'].min())})
bad=copy.deepcopy(circle);bad['back_surface'].update(ior=3.,b_major=.2,b_minor=.2,quartic=0.);assert not m.rays(np.array([.9]),np.array([0.]),bad)[2][0]
# New nontrivial uniform-source check; no target pixels or fitted optics.
uniform=copy.deepcopy(p);uniform['material']=[1.,1.,1.]+[0.]*(len(p['material'])-6)+[1.,1.,1.];source=np.full((1080,1920,3),.5,float);C,a=m.render(source,p['case'],uniform);covered=a>0;uniform_error=float(np.max(np.abs(C[covered]-.5)));assert uniform_error<1e-6
report={'analytic_gradient_max_error':gradient_error,'Snell_normal_alignment_max_error':snell_error,'mirror_max_error':mirror_error,'rotation90_max_error':rotation_error,'scale2_max_error':scale_error,'flat_surface_identity_exact':True,'explicit_circle_arbitrary_rotation_error':circle_error,'circle_scope':'softness0 true circle; inherited soft equal-half crown is not relabeled circle','parameter_box_corner_bounds':bound_checks,'TIR_rejected':True,'uniform_input_max_error':uniform_error,'material_remains_empirical':True,'new_target_image_fits':0,'native_comparison_not_run_yet':True}
(out/'invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('BACK_SURFACE INVARIANTS PASS',json.dumps({k:v for k,v in report.items() if k!='parameter_box_corner_bounds'}),flush=True)
