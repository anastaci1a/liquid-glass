"""Queue30 fixture/native/derivative protocol audit, never an optical pass."""
import sys,json,hashlib,importlib.util
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_sampling_precision as m
from progress_gate import error,evaluate
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-sampling-precision');root.mkdir(exist_ok=True);pkg=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((pkg/'recipe.json').read_text());case=p['case'];source=np.asarray(Image.open(pkg/'inputs/source.png'),float)/255;codehash=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest();before=json.loads((pkg/'primary-verification.json').read_text())['candidate'];oldC=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');atlasroot=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-covariance/native-atlas');atlas={k:np.load(atlasroot/f'{k}.npy',mmap_mode='r') for k in ['sx','sy','inside']};mask=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz')
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def controls():
    path=root/'controls.json'
    if path.exists() and json.loads(path.read_text()).get('complete'):assert json.loads(path.read_text())['model_sha256']==codehash;return
    r=json.loads(path.read_text()) if path.exists() else {'complete':False,'opencv_version':cv2.__version__,'INTER_BITS':cv2.INTER_BITS,'INTER_TAB_SIZE':cv2.INTER_TAB_SIZE,'model_sha256':codehash};write(path,r)
    image=np.arange(6*7*3,dtype=float).reshape(6,7,3)/128;v=np.arange(-2,9,dtype=float)/2;xx,yy=np.meshgrid(v,v);a=m.bilinear(image,xx,yy);b=cv2.remap(image,xx.astype(np.float32),yy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0);err=r.get('integer_half_endpoint_partial_border_max_error');
    if err is None:
        err=float(abs(a-b).max());assert err<1e-15;r['integer_half_endpoint_partial_border_max_error']=err;write(path,r)
    rng=np.random.default_rng(30);x=rng.uniform(.1,5.9,(64,64)).astype(np.float32);y=rng.uniform(.1,4.9,(64,64)).astype(np.float32);yy,xx=np.mgrid[:6,:7];ramp=np.stack([.1+.02*xx+.03*yy,.2+.03*xx-.01*yy,.3-.01*xx+.02*yy],axis=-1);expected=np.stack([.1+.02*x.astype(float)+.03*y.astype(float),.2+.03*x.astype(float)-.01*y.astype(float),.3-.01*x.astype(float)+.02*y.astype(float)],axis=-1);out=m.bilinear(ramp,x,y);err=float(abs(out-expected).max());assert err<1e-15;r['analytic_affine_ramp_error_at_same_float32_coords']=err;cv=cv2.remap(ramp,x,y,cv2.INTER_LINEAR);r['cv2_ramp_max_error']=float(abs(cv-expected).max());qx,qy=m.quantized_coordinates(x,y);em=m.bilinear(ramp,qx,qy);err=float(abs(cv-em).max());assert err<1e-15;r['convertMaps_table_emulation_error']=err
    constant=np.full((6,7,3),.625);err=float(abs(m.bilinear(constant,x,y)-.625).max());assert err<1e-15;r['constant_interior_error']=err;r['border_limits']='Constants taper to zero for partial outside footprints under the unchanged constant-zero remap border; no false global constant-preservation claim.';r['complete']=True;write(path,r);print('CONTROLS30',json.dumps(r),flush=True)
def native():
    result=root/'native-comparison.json'
    if result.exists():return
    saved=root/'material.npy'
    if saved.exists():C=np.load(saved);a=np.load(root/'alpha.npy')
    else:C,a=m.render(source,case,p,atlas=atlas);np.save(saved,C);np.save(root/'alpha.npy',a)
    assert np.array_equal(a,alpha)
    spec=importlib.util.spec_from_file_location('score_helper','/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/control-and-first.py');scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer);sc,fg,full,crops=scorer.measure(C,a);oldsc,oldfg,_,_=scorer.measure(oldC,alpha);assert error(oldsc)==error(before['observations']['A']);np.save(root/'complete.npy',full)
    epoch=hashlib.sha256(json.dumps({'accepted_epoch':before['epoch'],'sampler':'full-fraction bilinear at SAME float32 coordinates,constantzero border','sampler_code_sha256':codehash},sort_keys=True).encode()).hexdigest();state={'epoch':epoch,'observations':{'A':sc}}
    try:gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
    except ValueError as exc:gate={'accepted':False,'expected_protocol_epoch_refusal':True,'reason':str(exc)}
    r={'accepted_original_epoch':before['epoch'],'UNADOPTED_numerical_comparator_epoch':epoch,'old_E':error(oldsc),'full_fraction_E_protocol_only':error(sc),'E_delta_is_NOT_optical_gain':True,'new_scores':sc,'old_foreground':oldfg,'new_foreground':fg,'advisory_crops':crops,'source_unchanged_sha256':p['source_sha256'],'model_sha256':codehash,'coverage_exact':True,'gate_expected_protocol_refusal':gate,'cohorts':{},'new_native_protocol_comparison_renders':1,'new_optical_trials_or_passes':0}
    for name in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']:
        mm=cohorts[name];D=(C-oldC)[mm]*255;r['cohorts'][name]={'pixels':int(mm.sum()),'material_change_RMS_255':float(np.sqrt(np.mean(D*D))),'material_change_max_255':float(abs(D).max())}
    write(result,r);print('NATIVE30',json.dumps(r),flush=True)
def derivatives():
    result=root/'derivative-stability.json'
    if result.exists() and json.loads(result.read_text()).get('complete'):return
    eligible=np.repeat(np.repeat(cohorts['observed_kernel_proxy'],4,axis=0),4,axis=1)&np.asarray(atlas['inside'],bool);indices=np.flatnonzero(eligible);selected=indices[np.linspace(0,len(indices)-1,min(4096,len(indices)),dtype=int)];yy,xx=np.unravel_index(selected,eligible.shape);xd=atlas['sx'][yy,xx];yd=atlas['sy'][yy,xx];x=xd.astype(np.float32).reshape(-1,1);y=yd.astype(np.float32).reshape(-1,1);L=min(case['half']);cx,cy=case['center'];a,b,c,d=case['crop'];ox=(a+(xx+.5)/4-.5-cx)/L;oy=(b+(yy+.5)/4-.5-cy)/L;sd,*_=m.baseline.boundary(ox,oy,p);u=np.clip(-sd/p['blur_transition'],0,1);w=(u**3*(u*(6*u-15)+10))[:,None,None];blur=cv2.GaussianBlur(source,(0,0),p['source_sigma']*L)
    def sample(qx,qy,kind):
        f=(lambda I:m.bilinear(I,qx,qy)) if kind=='fractional' else (lambda I:cv2.remap(I,qx,qy,cv2.INTER_LINEAR));C=f(blur);clear=f(source);return clear+(C-clear)*w
    _,bx,by=m.bilinear(blur,x,y,gradient=True);_,sx,sy=m.bilinear(source,x,y,gradient=True);gx=sx+(bx-sx)*w;gy=sy+(by-sy)*w;G=np.stack([gx,gy],axis=-1);rows=json.loads(result.read_text())['rows'] if result.exists() else []
    for h in [.25,.0625,.015625,.00390625,.0009765625,.000244140625]:
        if any(row['h_native_px']==h for row in rows):continue
        no_cross=(np.floor(x-h)==np.floor(x+h))&(np.floor(y-h)==np.floor(y+h));valid=no_cross[:,0];signal=np.linalg.norm(G.reshape(len(x),-1),axis=1)>1e-8
        row={'h_native_px':h,'same_bilinear_cell_samples':int(valid.sum()),'cell_crossing_or_exact_integer_samples':int((~valid).sum()),'methods':{}}
        for kind in ['cv2','fractional']:
            dx=(sample(x+h,y,kind)-sample(x-h,y,kind))/(2*h);dy=(sample(x,y+h,kind)-sample(x,y-h,kind))/(2*h);D=np.stack([dx,dy],axis=-1);err=(D-G)[valid];zero=np.linalg.norm(D.reshape(len(x),-1),axis=1)<1e-14;row['methods'][kind]={'same_cell_gradient_RMS_error_255_per_px':float(np.sqrt(np.mean(err*err))*255),'zero_derivative_fraction_on_nonzero_analytic_signal':float(np.mean(zero[signal]))}
        rows.append(row);write(result,{'complete':len(rows)==6,'native_observed_proxy_rays':len(x),'deterministic_evenly_spaced_original_ray_indices':selected.tolist(),'target_pixels_used_for_selection':False,'max_float64_to_original_float32_coordinate_rounding_native_px':float(max(abs(x[:,0].astype(float)-xd).max(),abs(y[:,0].astype(float)-yd).max())),'fractional_analytic_gradient_uses_same_float32_coords':True,'rows':rows,'limits':'Diagnostic coordinate differences, not fitted/applied image shifts. Full-fraction gradient is piecewise bilinear; cell crossings excluded only from derivative-error diagnostic, never output scoring masks. Current remap table plateaus are not zero optical response. No epoch/sampler adoption.'});print('DERIVATIVE30',h,row['methods'],flush=True)
controls();native();derivatives();print('COMPLETE30',flush=True)
