"""Queue21: frozen native residuals + saved ordinary-blur secant, no fits/renders.

One new centroid-anchored RGB-law ANALYTIC direction is computed at zero using
continuous bilinear source gradients. Native remap is quantized: this is not a
native derivative or score improvement. No old optical probes are repeated.
"""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_candidate as model
cv2.setNumThreads(1)
out=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-dispersion-audit');out.mkdir(exist_ok=True)
package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];L=min(case['half']);C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz');Cblur=np.load('/tmp/agent-toolbar-revision2-blur/best-raw/material.npy');blur=(Cblur.astype(float)-C)*255;R=(C.astype(float)-T)*255
assert hashlib.sha256((package/'inputs/source.png').read_bytes()).hexdigest()=='6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b'
def error_parts(D,mask):
    n=int(mask.sum())
    if not n:return {'pixels':0}
    v=D[mask];neutral=v.mean(axis=-1);chroma=v-neutral[:,None]
    return {'pixels':n,'RGB_MSE':float(np.mean(v*v)),'neutral_mean_MSE':float(np.mean(neutral*neutral)),'orthogonal_chroma_MSE':float(np.mean(chroma*chroma)),'encoded_Rec709_luma_proxy_RMSE':float(np.sqrt(np.mean((v@np.array([.2126,.7152,.0722]))**2))),'channel_RMSE':np.sqrt(np.mean(v*v,axis=0)).tolist()}
parts={name:error_parts(R,masks[name]) for name in ['glass','rim']};E=np.sqrt(.7*parts['glass']['RGB_MSE']+.3*parts['rim']['RGB_MSE']);neutral_floor=np.sqrt(.7*parts['glass']['neutral_mean_MSE']+.3*parts['rim']['neutral_mean_MSE']);ceiling=100*(1-neutral_floor/E)
Y,X=np.mgrid[:C.shape[0],:C.shape[1]];xs=X+x0;ys=Y+y0;regions={'full':np.ones(C.shape[:2],bool)}
for name,(a,b,c,d) in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():regions[name]=(xs>=a)&(xs<c)&(ys>=b)&(ys<d)
residual_regions={name:{cohort:error_parts(R,region&cohorts[cohort]) for cohort in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']} for name,region in regions.items()}

# SINGLE declared RGB proxy, before looking at a fitted coefficient. Fixed
# nominal bands, equal-band centroid anchor removes a common-ray scale term.
wavelengths=np.array([.650,.550,.450]);inverse_square=wavelengths**-2;k=inverse_square-inverse_square.mean();q=p['parameters'];a,b=max(p['shape']['half']),min(p['shape']['half']);v_bound=max(map(abs,q['coefficients']))*b+np.hypot(q['core_x']*a,q['core_y']*b)+abs(q['tangent'])*np.hypot(a,b);Bmax=.02*b/(np.max(np.abs(k))*v_bound)
sigma=p['source_sigma']*L;Sblur=cv2.GaussianBlur(source,(0,0),sigma);Dfield=np.zeros_like(C,dtype=np.float64);source_min=np.array([np.inf,np.inf]);source_max=-source_min;co=np.array(p['material']);H,W=C.shape[:2]
(out/'preliminary.json').write_text(json.dumps({'parts':parts,'pure_chroma_ceiling_percent':float(ceiling),'source_cohorts':residual_regions,'Bmax':float(Bmax),'k':k.tolist(),'new_optical_renders':0},indent=2)+'\n')
partial=out/'partial-raw-direction.npy';checkpoint=out/'feature-progress.json';start_top=0
if partial.exists() and checkpoint.exists():
    saved=json.loads(checkpoint.read_text());assert saved['recipe_sha256']==hashlib.sha256((package/'recipe.json').read_bytes()).hexdigest();Dfield=np.lib.format.open_memmap(partial,mode='r+');start_top=saved['next_top'];source_min=np.array(saved['source_min']) if saved['source_min'] is not None else source_min;source_max=np.array(saved['source_max']) if saved['source_max'] is not None else source_max
else:Dfield=np.lib.format.open_memmap(partial,mode='w+',dtype=np.float64,shape=C.shape);Dfield[:]=0
def bilinear_gradient(S,sx,sy):
    ix=np.floor(sx).astype(int);iy=np.floor(sy).astype(int);fx=sx-ix;fy=sy-iy
    assert ix.min()>=0 and iy.min()>=0 and ix.max()<S.shape[1]-1 and iy.max()<S.shape[0]-1
    gx=(1-fy[...,None])*(S[iy,ix+1]-S[iy,ix])+fy[...,None]*(S[iy+1,ix+1]-S[iy+1,ix]);gy=(1-fx[...,None])*(S[iy+1,ix]-S[iy,ix])+fx[...,None]*(S[iy+1,ix+1]-S[iy,ix+1]);return gx,gy
for top in range(start_top,H,16):
    bot=min(top+16,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4];x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L;fx,fy=model.mapping(x,y,p);vx=fx-x;vy=fy-y;sx=fx*L+case['center'][0];sy=fy*L+case['center'][1];sd,*_=model.boundary(x,y,p);inside=sd<=0
    if not np.any(inside):continue  # Derivative is exactly zero outside footprint.
    source_min=np.minimum(source_min,[sx[inside].min(),sy[inside].min()]);source_max=np.maximum(source_max,[sx[inside].max(),sy[inside].max()])
    gbx,gby=bilinear_gradient(Sblur,sx,sy);gcx,gcy=bilinear_gradient(source,sx,sy);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);gx=gcx+(gbx-gcx)*w[...,None];gy=gcy+(gby-gcy)*w[...,None]
    sampleblur=cv2.remap(Sblur,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_LINEAR);sampleclear=cv2.remap(source,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_LINEAR);sample=sampleclear+(sampleblur-sampleclear)*w[...,None];light=model.lighting(x,y,p);core=light[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:];raw=sample*gain+co[3:6]+(light[...,:-1]@co[6:-3])[...,None];dc=(gx*vx[...,None]+gy*vy[...,None])*(L*k)*gain*((raw>0)&(raw<1));shape=(bot-top,4,W,4);weight=inside.reshape(shape).sum((1,3));Dfield[top:bot]=(dc*inside[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(weight,1)[...,None]
    Dfield.flush();checkpoint.write_text(json.dumps({'next_top':bot,'source_min':source_min.tolist(),'source_max':source_max.tolist(),'recipe_sha256':hashlib.sha256((package/'recipe.json').read_bytes()).hexdigest()})+'\n')
if p.get('post_sigma'):
    Dfield=cv2.GaussianBlur(Dfield*alpha[...,None],(0,0),p['post_sigma']*L)/np.maximum(cv2.GaussianBlur(alpha,(0,0),p['post_sigma']*L),1e-12)[...,None]
D=Dfield*255
def feature_stats(mask):
    n=int(mask.sum())
    if not n:return {'pixels':0}
    r=R[mask].ravel();d=D[mask].ravel();v=blur[mask].ravel();den=np.linalg.norm(d)*np.linalg.norm(v);dn=np.linalg.norm(d)*np.linalg.norm(r)
    return {'pixels':n,'spectral_direction_RMS_per_B':float(np.sqrt(np.mean(d*d))),'spectral_cosine_to_desired':float(-d@r/dn) if dn else None,'ordinary_blur_secant_RMS':float(np.sqrt(np.mean(v*v))),'spectral_blur_cosine':float(d@v/den) if den else None,'positive_B_MSE_derivative':float(2*np.mean(r*d)),'direction_neutral_chroma_parts':error_parts(D,mask)}
features={name:{cohort:feature_stats(region&cohorts[cohort]) for cohort in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']} for name,region in regions.items()}
g=.7*np.mean(R[masks['glass']]*D[masks['glass']])+.3*np.mean(R[masks['rim']]*D[masks['rim']]);A=.7*np.mean(D[masks['glass']]**2)+.3*np.mean(D[masks['rim']]**2);proposal=float(np.clip(-g/A,0,Bmax)) if A>0 else 0.
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':json.loads((package/'primary-verification.json').read_text())['candidate']['epoch'],'frozen_native_error_parts':parts,'diagnostic_float64_E':float(E),'perfect_pure_chroma_removal_E_floor':float(neutral_floor),'perfect_pure_chroma_removal_reduction_percent':float(ceiling),'pure_chroma_bound_scope':'Exact RGBmean/orthogonal-chroma decomposition of diagnostic residuals only. Not a bound on dispersion that also changes neutral content. No correction applied. Native float32 E/gates remain authoritative.','source_cohorts':residual_regions,'source_limits':'Saved strict legacy source-kernel proxies are advisory, not new score masks or under-glass RGB truth. A-source-audit found no extra reliable hiddenink. Underside observed cohort zero.','law':{'name':'centroid-anchored one-coefficient Cauchy-form RGB image-map PROXY','F_channel':'x+(1+B*k_channel)*(F0-x)','nominal_wavelength_um':wavelengths.tolist(),'k_inverse_um_squared':k.tolist(),'anchor':'equal-band mean inverse wavelength squared; sumk=0, no common achromatic-ray rescale at first order on neutral input','B_interval_um_squared':[0,float(Bmax)],'geometry_max_displacement_bound_L':float(v_bound),'declared_added_channel_ray_bound_L':.02,'physical_limit':'No inferred IOR/spectra/sensor bands or Apple dispersion. Existing encodedRGB empirical map/material; fixed bands are proxy convention.'},'single_new_analytic_direction':{'source_gradient':'continuous bilinear gradient at original4x4native query locations, actual shade-clipping/gain and common blur/postfilter. Not derivative of quantized cv2.remap;22must validate with new native points if supported','native_source_query_min_xy':source_min.tolist(),'native_source_query_max_xy':source_max.tolist(),'predicted_positive_B_objective_MSE_derivative':float(2*g),'positive_B_quadratic_proposal':proposal,'predicted_E_at_proposal':float(np.sqrt(max(E*E+2*g*proposal+A*proposal*proposal,0)))},'features':features,'saved_blur6_evidence':'Rejected same-baseline best-raw material secant reused, not independent source/outputsigma Jacobians or new blur test','new_optical_renders_or_fits':0,'new_counted_passes':0,'limits':['Channel/luma/edge response is in encodedRGB, not spectral radiometry','A source estimate, material color, environmental highlights or video chroma processing can mimic wavelength response','A directional cosine or linearized coefficient is not a native qualifying optical result']}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');np.savez_compressed(out/'single-direction-evidence.npz',spectral_direction=Dfield,ordinary_blur_secant=blur/255,residual=R/255,k=k,Bmax=Bmax)
print(json.dumps({'chroma_ceiling_percent':ceiling,'Bmax':Bmax,'prediction':report['single_new_analytic_direction'],'full_features':features['full'],'underside_features':features['underside']},indent=2),flush=True)
