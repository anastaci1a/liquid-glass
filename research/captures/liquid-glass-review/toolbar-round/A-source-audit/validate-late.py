"""Held-out image controls and source observation coverage, no source promotion."""
import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image,ImageDraw
import toolbar_candidate as optical
cv2.setNumThreads(1)
root=Path('/tmp/agent-toolbar-A-source-audit');out=root/'late-coverage';out.mkdir(exist_ok=True)
meta=json.loads((root/'late-screen/frame-provenance.json').read_text());registrations=json.loads((root/'late-registration/registrations.json').read_text())['records']
A=np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png').convert('RGB'));H,W=A.shape[:2];grayA=cv2.cvtColor(A,cv2.COLOR_RGB2GRAY).astype(np.float32)
gxA=cv2.Sobel(grayA,cv2.CV_32F,1,0,ksize=3)/8;gyA=cv2.Sobel(grayA,cv2.CV_32F,0,1,ksize=3)/8
geom=np.ones((H,W),np.uint8);geom[330:820,490:1430]=0
far=np.ones((H,W),np.uint8);far[200:1030,380:1540]=0
yy,xx=np.mgrid[:H,:W];held=((xx//128+3*(yy//128))%4)==0;lattice=(xx%4==0)&(yy%4==0)
def metric(v):
    v=np.asarray(v)
    return {'n':len(v),'rms':float(np.sqrt(np.mean(v*v))),'median':float(np.median(v)),'p95':float(np.quantile(v,.95)),'max':float(np.max(v))} if len(v) else {'n':0}
def rgbmetric(v):
    return {'pixels':len(v),'rmse_255':float(np.sqrt(np.mean(v*v))),'signed_mean_RGB_255':v.mean(0).tolist(),'channel_rmse_255':np.sqrt(np.mean(v*v,axis=0)).tolist()} if len(v) else {'pixels':0}
def warp_mask(mask,M,erosion=0):
    v=cv2.warpAffine(mask.astype(np.float32),M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)>.999
    if erosion:v=cv2.erode(v.astype(np.uint8),np.ones((2*erosion+1,2*erosion+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
    return v

# Compute the frozen incumbent's source-address histogram once. It is advisory
# source provenance only; no rendering, optical fit, score mask or epoch change.
histpath=root/'coverage/native-query-histograms.npz'
if histpath.exists():
    hist=dict(np.load(histpath))
else:
    p=json.loads(Path('/tmp/agent-toolbar-evidence-package/recipe.json').read_text());case=p['case'];x0,y0,x1,y1=case['crop'];nh,nw=y1-y0,x1-x0;L=min(case['half']);m=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');Y,X=np.mgrid[:nh,:nw];regions={'glass':m['glass'],'rim':m['rim'],'d':m['glass']&(X+x0>=960)&(X+x0<1120)&(Y+y0>=450)&(Y+y0<550),'underside':m['glass']&(X+x0>=650)&(X+x0<1270)&(Y+y0>=650)&(Y+y0<726)};hist={k:np.zeros((H,W),np.uint32) for k in regions}
    for top in range(0,nh,16):
        bot=min(top+16,nh);qy,qx=np.mgrid[top*4:bot*4,0:nw*4];x=(x0+(qx+.5)/4-.5-case['center'][0])/L;y=(y0+(qy+.5)/4-.5-case['center'][1])/L;sx,sy=optical.mapping(x,y,p);ix=np.floor(sx*L+case['center'][0]).astype(int);iy=np.floor(sy*L+case['center'][1]).astype(int);inside=optical.boundary(x,y,p)[0]<=0
        assert ix.min()>=0 and iy.min()>=0 and ix.max()<W-1 and iy.max()<H-1
        for k,mask in regions.items():
            valid=np.repeat(np.repeat(mask[top:bot],4,axis=0),4,axis=1)&inside;hist[k]+=np.bincount((iy[valid]*W+ix[valid]).ravel(),minlength=H*W).reshape(H,W).astype(np.uint32)
    np.savez_compressed(histpath,**hist)
    print('NATIVE QUERY HISTOGRAM SAVED',flush=True)
def coverage(mask):
    mask=mask.astype(np.uint8);eroded=cv2.erode(mask,np.ones((69,69),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
    def safe(v):
        a=np.zeros(v.shape,bool);a[:-1,:-1]=(v[:-1,:-1]>0)&(v[1:,:-1]>0)&(v[:-1,1:]>0)&(v[1:,1:]>0);return a
    center=safe(mask);kernel=safe(eroded)
    return {k:{'rays':int(h.sum()),'center_fraction':float(h[center].sum(dtype=np.uint64)/h.sum(dtype=np.uint64)),'source_kernel_fraction':float(h[kernel].sum(dtype=np.uint64)/h.sum(dtype=np.uint64))} for k,h in hist.items()}

# Historical matrix is reused, not re-estimated. Common mask policies permit a
# nominal comparison; historical registration uncertainty was not quantified.
old=json.loads(Path('/tmp/agent-toolbar-input-audit.json').read_text());oldM=np.array(old['registration']['matrix']);legacy=np.ones((H,W),np.uint8);legacy[350:790,490:1420]=0
baseline={'legacy_nominal_content':coverage(warp_mask(legacy,oldM)),'common_geometry_nominal':coverage(warp_mask(geom,oldM)),'far_RGB_context_nominal':coverage(warp_mask(far,oldM)),'limits':'Old source is photometrically modeled; historical transform reused with unknown registration covariance. Exclusion policies are source diagnostics, not changed output score masks.'}
union_geom=np.zeros((H,W),bool);union_far=np.zeros((H,W),bool);all_geom=np.zeros_like(union_geom);ink_votes=np.zeros((H,W),np.uint8);ink_all=np.zeros((H,W),np.uint8);records=[]
old_estimated=~warp_mask(legacy,oldM);deep_old_est=cv2.erode(old_estimated.astype(np.uint8),np.ones((5,5),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;query_domain=cv2.dilate((hist['glass']>0).astype(np.uint8),np.ones((69,69),np.uint8))>0
for reg in registrations:
    if 'matrix' not in reg:continue
    t=reg['requested_seconds'];f=next(f for f in meta['frames'] if f['requested_seconds']==t);S=np.asarray(Image.open(root/f['local_file']).convert('RGB'));M=np.array(reg['matrix']);warped=cv2.warpAffine(S,M,(W,H));grayS=cv2.cvtColor(warped,cv2.COLOR_RGB2GRAY).astype(np.float32);gxS=cv2.Sobel(grayS,cv2.CV_32F,1,0,ksize=3)/8;gyS=cv2.Sobel(grayS,cv2.CV_32F,0,1,ksize=3)/8
    geometry=warp_mask(geom,M,reg['source_confidence_erosion_px']);rgbfar=warp_mask(far,M,reg['source_confidence_erosion_px']);all_geom|=geometry
    patches=[];r=24;window=cv2.createHanningWindow((2*r,2*r),cv2.CV_32F)
    for by in range(H//128):
        for bx in range(W//128):
            if (bx+3*by)%4:continue
            x=bx*128+64;y=by*128+64;sl=(slice(y-r,y+r),slice(x-r,x+r))
            if not np.all(geom[sl]) or not np.all(geometry[sl]):continue
            ta=grayA[sl];sa=grayS[sl]
            if ta.std()<15 or np.hypot(gxA[sl],gyA[sl]).mean()<2:continue
            ga=np.stack([gxA[sl],gyA[sl]]);gs=np.stack([gxS[sl],gyS[sl]]);ga-=ga.mean((1,2),keepdims=True);gs-=gs.mean((1,2),keepdims=True);ncc=float(np.sum(ga*gs)/max(np.sqrt(np.sum(ga*ga)*np.sum(gs*gs)),1e-20));shift,response=cv2.phaseCorrelate(ta-ta.mean(),sa-sa.mean(),window)
            patches.append({'center_A_xy':[x,y],'zero_shift_gradient_NCC':ncc,'phase_shift_xy':list(map(float,shift)),'phase_response':float(response),'raw_RGB_rmse_255':float(np.sqrt(np.mean((warped[sl].astype(float)-A[sl])**2)))})
    nccs=np.array([p['zero_shift_gradient_NCC'] for p in patches]);responsive=[p for p in patches if p['phase_response']>=.25];shifts=np.array([np.hypot(*p['phase_shift_xy']) for p in responsive]);patchpass=bool(len(patches)>=6 and np.median(nccs)>=.9 and (nccs>=.85).mean()>=.8 and len(responsive)>=4 and np.quantile(shifts,.95)<=2.)
    paper=(far>0)&rgbfar&held&lattice&(A.min(2)>.7*255)&(warped.min(2)>.7*255)&(np.hypot(gxA,gyA)<1)&(np.hypot(gxS,gyS)<1)
    ink=(far>0)&rgbfar&held&lattice&(A.min(2)<.4*255)&(warped.min(2)<.4*255)
    trusted=bool(reg['registration_evidence_sufficient'] and patchpass)
    observed_ink=geometry&(warped.min(2)<.5*255);ink_all+=observed_ink
    if trusted:union_geom|=geometry;union_far|=rgbfar;ink_votes+=observed_ink
    Image.fromarray(np.uint8(geometry)*255).save(out/f'{t}-geometric-content-proxy.png');Image.fromarray(np.uint8(rgbfar)*255).save(out/f'{t}-far-RGB-context-proxy.png');Image.fromarray(np.uint8(observed_ink)*255).save(out/f'{t}-observed-dark-ink-cores.png')
    row={'requested_seconds':t,'patches':patches,'patch_count':len(patches),'gradient_NCC_median':float(np.median(nccs)) if len(nccs) else None,'fraction_NCC_atleast_.85':float((nccs>=.85).mean()) if len(nccs) else None,'phase_responsive_count':len(responsive),'responsive_phase_displacement_px':metric(shifts),'image_patch_check_passed':patchpass,'conditional_geometry_union_eligible':trusted,'heldout_paper_RGB_difference':rgbmetric((warped.astype(float)-A)[paper]),'heldout_dark_ink_RGB_difference':rgbmetric((warped.astype(float)-A)[ink]),'content_coverage':coverage(geometry),'far_RGB_context_coverage':coverage(rgbfar),'new_dark_cores_in_old_estimated_query_domain':int((observed_ink&deep_old_est&query_domain).sum()),'limits':'No patch search/refit or correction applied to M. Phase/NCC are heldout diagnostics. RGB ink residual mixes registration/codec/photometry; paper is flat/far-control only, not under-glass RGB truth.'};records.append(row)
    (out/'per-donor-evidence.json').write_text(json.dumps(records,indent=2)+'\n');print('PATCH COVERAGE',t,len(patches),row['gradient_NCC_median'],patchpass,trusted,row['new_dark_cores_in_old_estimated_query_domain'],flush=True)

accepted_geom=warp_mask(geom,oldM);accepted_far=warp_mask(far,oldM)
summary={'baseline_accepted_source_proxies':baseline,'donors':records,'conditional_new_donor_geometry_union':coverage(union_geom),'conditional_new_donor_far_RGB_union':coverage(union_far),'accepted_nominal_plus_new_geometry_union':coverage(accepted_geom|union_geom),'all_provisional_geometry_upper_scenario':coverage(all_geom),'accepted_nominal_plus_new_far_RGB_union':coverage(accepted_far|union_far),'new_observed_ink_cores_old_estimated_query_domain':int(((ink_votes>0)&deep_old_est&query_domain).sum()),'new_ink_cores_confirmed_by_2donors':int(((ink_votes>=2)&deep_old_est&query_domain).sum()),'all_provisional_new_ink_upper_scenario':int(((ink_all>0)&deep_old_est&query_domain).sum()),'sampling':'Original incumbent native4x4 ray-address histograms, fixed output masks AND actual footprint; bilinear-all4-safe confidence, eroded34sourcepx for Gaussian proxy','scope':'Source-only provenance audit; original source RGB/output masks/registration epoch/history/count unchanged. B714 inactive; no optical fit or proposed clean source yet.','limits':['Source geometry mask excludes control with margin but may include shadow-attenuated paper: content proxy, not clean RGB','Far-RGB context exclusion is conservative, not certification of zero photographic shadow or exact absolute RGB','Bootstrap conditional on correspondences/model; full heldout candidate outliers remain reported','No target glass used for source alignment or color fitting; no source pixels promoted; no gains counted']}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');np.savez_compressed(out/'union-provenance-masks.npz',new_geometry=union_geom,new_far_RGB=union_far,all_provisional_geometry=all_geom,accepted_common_geometry=accepted_geom,accepted_far_RGB=accepted_far,ink_votes=ink_votes,old_estimated=old_estimated,query_kernel_domain=query_domain)
print('SOURCE COVERAGE AUDIT COMPLETE',flush=True)
