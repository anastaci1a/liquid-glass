"""New descriptive edge/guard analysis from saved21direction; no render/fit."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
import toolbar_candidate as model
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-dispersion-audit');audit=json.loads((root/'audit.json').read_text());field=np.load(root/'single-direction-evidence.npz');D=field['spectral_direction'];package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;source=np.asarray(Image.open(package/'inputs/source.png'),float)[y0:y1,x0:x1]/255;shadow=model.gaussian_coverage_shadow(case,p);fg=np.load(package/'derived-foreground.npz');masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz');trans=np.ones(a.shape)
def complete(C):
    full=C*a[...,None]+source*(1-shadow[...,None])*(1-a[...,None])
    for layer in p['foreground_layers']:
        aa=fg[layer['name']][...,None];full=full*(1-aa)+np.array(layer['color'])*aa
    return full
for layer in p['foreground_layers']:trans*=1-fg[layer['name']]
F=complete(C);Df=D*(a*trans)[...,None];Fblur=complete(C+field['ordinary_blur_secant']);groups={}
for name in ['glass','rim']:
    groups[name]=(((C.astype(float)-T)[masks[name]]*255).ravel(),(D[masks[name]]*255).ravel())
groups['exterior']=(((F-T)[masks['exterior']]*255).ravel(),(Df[masks['exterior']]*255).ravel())
for layer in p['foreground_layers']:
    aa,b,c,d=layer['box'];sl=(slice(b-y0,d-y0),slice(aa-x0,c-x0));groups[layer['name']]=(((F-T)[sl]*255).ravel(),(Df[sl]*255).ravel())
upper=audit['law']['B_interval_um_squared'][1];guards={}
for name,(r,d) in groups.items():
    A=float(np.mean(d*d));B=float(2*np.mean(r*d));hi=0. if B>0 else (-B/A if A>0 else upper);upper=min(upper,hi);guards[name]={'quadratic_A':A,'linear_B':B,'positive_linearized_nonregression_max_B':hi}
g=.7*guards['glass']['linear_B']+.3*guards['rim']['linear_B'];A=.7*guards['glass']['quadratic_A']+.3*guards['rim']['quadratic_A'];proposal=float(np.clip(-g/(2*A),0,upper)) if A else 0.;baseE=audit['diagnostic_float64_E'];pred=np.sqrt(max(baseE**2+g*proposal+A*proposal**2,0));observed=audit['features']['full']['observed_kernel_proxy']['positive_B_MSE_derivative'];support=bool(g<0 and observed<0 and proposal>0 and pred<baseE)
def edges(I,mask):
    answer={}
    for axis,name in [(1,'x'),(0,'y')]:
        one=[slice(None),slice(None)];two=one.copy();one[axis]=slice(None,-1);two[axis]=slice(1,None);valid=mask[tuple(one)]&mask[tuple(two)];g=np.abs(np.diff(I,axis=axis))*valid[...,None];profile=g.sum(axis=1-axis);mass=profile.sum(0);pos=np.arange(len(profile))+.5;center=np.divide((profile*pos[:,None]).sum(0),mass,out=np.full(3,np.nan),where=mass>1e-15);width=np.divide(mass*mass,(profile*profile).sum(0),out=np.zeros(3),where=(profile*profile).sum(0)>1e-15);neutral=np.abs(np.diff(I.mean(-1),axis=axis))*valid;profile_neutral=neutral.sum(axis=1-axis);nw=float(profile_neutral.sum()**2/np.sum(profile_neutral**2)) if np.sum(profile_neutral**2)>1e-15 else None
        answer[name]={'valid_adjacent_pairs':int(valid.sum()),'RGB_centroid_native_px':center.tolist(),'R_minus_G_B_minus_G_centroid_px':[float(center[0]-center[1]),float(center[2]-center[1])] if np.all(np.isfinite(center)) else None,'participation_width_native_px_RGB':width.tolist(),'neutral_mean_participation_width_native_px':nw,'profile_abs_gradient_RGB':profile.tolist()}
    return answer
profiles={}
for name,(aa,b,c,d) in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
    sl=(slice(b-y0,d-y0),slice(aa-x0,c-x0));profiles[name]={}
    for co in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']:
        mask=cohorts[co][sl]
        profiles[name][co]={'pixels':int(mask.sum()),'target':edges(T[sl],mask) if mask.any() else None,'accepted_complete':edges(F[sl],mask) if mask.any() else None,'saved_ordinary_blur_complete':edges(Fblur[sl],mask) if mask.any() else None}
report={'guard_linearizations':guards,'common_positive_B_nonregression_interval':[0,float(max(upper,0))],'constrained_positive_B_proposal':proposal,'predicted_E':float(pred),'support_for_ONE_native_RGB_proxy_feasibility':support,'physical_dispersion_identified':False,'source_observed_positive_B_MSE_derivative':observed,'fixed_mask_edge_profiles':profiles,'edge_profile_limits':'Descriptive channel centroid/participation widths of fixed masked adjacentpairs; multipleedges/contrast/source colors can shift them. No per-channel/crop parameter fitted or offsets applied, no general physical-blur estimator. EncodedRGBmean is a neutral proxy, not radiometricluminance.','decision_limits':'Analytic continuousbilinear direction is NOT quantizednative cv2 derivative or independent validation;22must validate limits/nativepoints if supported. Positive-B sourceobserved andwholeobjective signs plus linearizedoriginal5guards are checked together; no subset scoring/sourcechange.','new_optical_renders_or_fits':0,'counted_passes':0}
(root/'details.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='fixed_mask_edge_profiles'},indent=2),flush=True)
