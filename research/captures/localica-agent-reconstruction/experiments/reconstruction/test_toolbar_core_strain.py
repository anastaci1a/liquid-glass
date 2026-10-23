"""Core-potential correctness/invariants, separate from native optical fitting."""
import json,copy,time
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
from crowned_footprint import longitudinal
import toolbar_candidate as baseline
import toolbar_core_strain as model
cv2.setNumThreads(1)
root=Path('/tmp/agent-toolbar-evidence-package');out=Path('/tmp/agent-toolbar-revision2-core-checks');out.mkdir(exist_ok=True)
p=json.loads((root/'recipe.json').read_text());assert not p.get('curvature_normal',{}).get('amplitude',0.)
L=min(p['shape']['half']);p['core_strain']={'amplitude':0.,'width':.30*L};bound=model.displacement_bound(p,.12);(out/'target-independent-bound.json').write_text(json.dumps(bound,indent=2)+'\n')
rows={};began=time.time()
def record(name,values):
    rows[name]=values;(out/'checks-in-progress.json').write_text(json.dumps(rows,indent=2)+'\n');print('CHECK',name,values,flush=True)
record('declared_geometry_bound',bound)
q=copy.deepcopy(p);q['core_strain']['amplitude']=.5*bound['lambda_max'];amplitude=q['core_strain']['amplitude']
yy,xx=np.meshgrid(np.linspace(-1.1*L,1.1*L,39),np.linspace(-1.03*max(p['shape']['half']),1.03*max(p['shape']['half']),67),indexing='ij');x=xx.ravel();y=yy.ravel();h=1e-5*L
dx,dy=model.addition(x,y,q);fdx=-(model.potential(x+h,y,q)-model.potential(x-h,y,q))/(2*h);fdy=-(model.potential(x,y+h,q)-model.potential(x,y-h,q))/(2*h)
gradient_error=float(np.max(np.hypot(dx-fdx,dy-fdy))/L);assert gradient_error<2e-8
curl=(model.addition(x+h,y,q)[1]-model.addition(x-h,y,q)[1]-model.addition(x,y+h,q)[0]+model.addition(x,y-h,q)[0])/(2*h)
relative_curl=float(np.max(np.abs(curl))/abs(amplitude));assert relative_curl<5e-6
depth,gx,gy=model.depth_gradient(x,y,q);_,nx,ny=baseline.boundary(x,y,q);S,Sp=model.smoothstep(depth/q['core_strain']['width']);z=x;normal=.5*z*z*Sp/q['core_strain']['width']
wrong_x=-amplitude*(z*S-normal*nx);wrong_y=amplitude*normal*ny;wrong_difference=float(np.max(np.hypot(dx-wrong_x,dy-wrong_y))/abs(amplitude)/L)
assert wrong_difference>1e-4
record('actual_depth_gradient_and_added_curl',{'analytic_vs_finite_potential_gradient_error_L':gradient_error,'added_field_curl_over_lambda_max_abs':relative_curl,'unit_normal_substitution_field_error_per_lambda_L':wrong_difference,'scope':'Only added field integrable; inherited total map not claimed integrable'})

D=np.stack([dx,dy]);mirror=np.array(model.addition(-x,y,q));mirror_error=float(np.max(np.abs(mirror-D*np.array([-1,1])[:,None]))/L)
rot=copy.deepcopy(q);rot['shape']['half']=list(reversed(q['shape']['half']));RD=np.array(model.addition(-y,x,rot));rotation_error=float(np.max(np.abs(RD-np.stack([-D[1],D[0]])))/L);scale_errors=[]
for s in [.25,3.,1000.]:
    scaled=copy.deepcopy(q);scaled['shape']['half']=(np.array(q['shape']['half'])*s).tolist();scaled['shape']['radius']*=s;scaled['core_strain']['width']*=s
    scale_errors.append(float(np.max(np.abs(np.array(model.addition(x*s,y*s,scaled))/s-D))/L))
assert max(mirror_error,rotation_error,*scale_errors)<2e-10
record('mirror_rotation_scale',{'mirror_error_L':mirror_error,'rotation_90_error_L':rotation_error,'scale_errors_L':scale_errors,'axis':'Deterministic control-major axis rotates with the footprint'})

u=np.array([0.,1.]);S,Sp=model.smoothstep(u);Spp=60*u*(1-u)*(1-2*u);assert np.array_equal(S,[0,1]) and np.array_equal(Sp,[0,0]) and np.array_equal(Spp,[0,0])
width=q['core_strain']['width'];probe_x=.8*L;Q,_=longitudinal(np.asarray(probe_x),max(p['shape']['half']),L,p['footprint_softness']);eps=1e-5*L;depths=np.array([-eps,0,eps,width-eps,width,width+eps]);ys=np.sqrt((L-depths)**2-Q**2);xs=np.zeros_like(ys)+probe_x;Ax,Ay=model.addition(xs,ys,q)
outer_error=float(np.max(np.hypot(Ax[:3],Ay[:3]))/abs(amplitude)/L);inner_error=float(np.max(np.hypot(Ax[3:]+amplitude*probe_x,Ay[3:]))/abs(amplitude)/L)
assert max(outer_error,inner_error)<1e-6
deep=np.array(model.addition(np.array([-.8,.3])*L,np.array([0.,0.])*L,q));expected=np.stack([-amplitude*np.array([-.8,.3])*L,np.zeros(2)]);assert np.max(np.abs(deep-expected))<1e-14*L
record('support_and_deep_horizontal_strain',{'S_Sprime_Ssecond_endpoint_values_exact':True,'outer_join_error_per_lambda_L':outer_error,'inner_join_error_per_lambda_L':inner_error,'deep_core_field_exact':True,'regularity':'Potential C2, added gradient C1; no C2 added-field claim'})

inside=depth>0;max_gradient=float(np.max(np.hypot(gx[inside],gy[inside])));unit=copy.deepcopy(p);unit['core_strain']['amplitude']=1.;unit_add=np.array(model.addition(x,y,unit));max_unit=float(np.max(np.hypot(*unit_add)));assert max_gradient<=bound['max_depth_gradient_bound']+1e-10 and max_unit<=bound['unit_displacement_bound']+1e-10
record('analytic_bound_checked_on_geometry_grid',{'grid_points':len(x),'max_actual_depth_gradient':max_gradient,'max_unit_added_vector_L':max_unit/L,'analytic_unit_bound_L':bound['unit_displacement_bound']/L})

source=np.asarray(Image.open(root/'inputs/source.png'),float)/255;case=p['case'];C,a=model.render(source,case,p);C0=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a0=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');assert np.array_equal(C,C0) and np.array_equal(a,a0)
record('zero_native_render',{'material_exact':True,'coverage_exact':True,'baseline':'accepted rev2 only; no unverified curvature flag'})
uniform=np.zeros_like(source)+np.array([.4,.55,.7]);view=copy.deepcopy(case);view['crop']=[625,410,1295,555];U0,ua=model.render(uniform,view,p);errors=[]
for sign in [-1.,1.]:
    test=copy.deepcopy(p);test['core_strain']['amplitude']=sign*bound['lambda_max'];U,aa=model.render(uniform,view,test);error=float(np.max(np.abs(U-U0)));errors.append(error);assert error<=1e-6 and np.array_equal(aa,ua)
record('uniform_input',{'endpoint_max_normalized_RGB_errors':errors,'coverage_exact':True,'fixed_incumbent_lighting':True})

x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;nativeL=min(case['half']);count=0;extrema=np.array([np.inf,np.inf,-np.inf,-np.inf]);max_add=0.
for top in range(0,H,16):
    bot=min(top+16,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4];x=(x0+(xx+.5)/4-.5-case['center'][0])/nativeL;y=(y0+(yy+.5)/4-.5-case['center'][1])/nativeL
    X,Y=baseline.mapping(x,y,p);dx,dy=model.addition(x,y,unit);max_add=max(max_add,float(np.max(np.hypot(dx,dy)))*bound['lambda_max']/L)
    for sign in [-1.,1.]:
        sx=(X+sign*bound['lambda_max']*dx)*nativeL+case['center'][0];sy=(Y+sign*bound['lambda_max']*dy)*nativeL+case['center'][1];extrema=np.array([min(extrema[0],sx.min()),min(extrema[1],sy.min()),max(extrema[2],sx.max()),max(extrema[3],sy.max())])
    count+=x.size
margin=float(np.ceil(4*p['source_sigma']*nativeL)+2);safe=bool(extrema[0]>margin and extrema[1]>margin and extrema[2]<source.shape[1]-1-margin and extrema[3]<source.shape[0]-1-margin);assert safe and max_add<=.12+1e-9
record('native_endpoint_ray_domain',{'rays_per_endpoint':count,'endpoint_total_rays':2*count,'bounds_xyxy':extrema.tolist(),'conservative_filter_margin':margin,'maximum_actual_added_displacement_L':max_add,'endpoints_and_between_defined':safe,'hidden_content_still_estimated':True})
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','fixed_width':p['core_strain']['width'],'checks':rows,'optical_fit_trials':0,'counted_passes':0,'seconds':time.time()-began,'scope':'One potential ADDITION, actual crowned-coordinate gradient, original native4x4 sampling/epoch unchanged'};(out/'invariants.json').write_text(json.dumps(report,indent=2)+'\n');print('CORE INVARIANTS COMPLETE',flush=True)
