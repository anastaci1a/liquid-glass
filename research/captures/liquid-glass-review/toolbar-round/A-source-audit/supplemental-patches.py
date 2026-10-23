"""New heldout controls only. Preserve original grid and registration evidence."""
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
cv2.setNumThreads(1)
root=Path('/tmp/agent-toolbar-A-source-audit'); out=root/'supplemental-patches';out.mkdir(exist_ok=True)
regs=json.loads((root/'registrations/registrations.json').read_text())['records']
old=json.loads((root/'coverage/summary.json').read_text())
meta=json.loads((root/'frame-provenance.json').read_text())
A=np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png').convert('RGB'));H,W=A.shape[:2]
geom=np.ones((H,W),np.uint8);geom[330:820,490:1430]=0
grayA=cv2.cvtColor(A,cv2.COLOR_RGB2GRAY).astype(np.float32)
gxA=cv2.Sobel(grayA,cv2.CV_32F,1,0,ksize=3)/8;gyA=cv2.Sobel(grayA,cv2.CV_32F,0,1,ksize=3)/8
hist=dict(np.load(root/'coverage/native-query-histograms.npz'));masks=np.load(root/'coverage/union-provenance-masks.npz')
union=np.zeros((H,W),bool);rows=[];r=24;window=cv2.createHanningWindow((48,48),cv2.CV_32F)
def coverage(mask):
    mask=mask.astype(np.uint8);kernel=cv2.erode(mask,np.ones((69,69),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)
    def safe(v):
        a=np.zeros(v.shape,bool);a[:-1,:-1]=(v[:-1,:-1]>0)&(v[1:,:-1]>0)&(v[:-1,1:]>0)&(v[1:,1:]>0);return a
    c=safe(mask);k=safe(kernel)
    return {n:{'center_fraction':float(h[c].sum(dtype=np.uint64)/h.sum(dtype=np.uint64)),'source_kernel_fraction':float(h[k].sum(dtype=np.uint64)/h.sum(dtype=np.uint64))} for n,h in hist.items()}
for reg in regs:
    if 'matrix' not in reg:continue
    t=reg['requested_seconds'];f=next(f for f in meta['frames'] if f['requested_seconds']==t)
    S=np.asarray(Image.open(root/f['local_file']).convert('RGB'));warped=cv2.warpAffine(S,np.array(reg['matrix']),(W,H))
    grayS=cv2.cvtColor(warped,cv2.COLOR_RGB2GRAY).astype(np.float32);gxS=cv2.Sobel(grayS,cv2.CV_32F,1,0,ksize=3)/8;gyS=cv2.Sobel(grayS,cv2.CV_32F,0,1,ksize=3)/8
    geometry=np.asarray(Image.open(root/f'coverage/{t}-geometric-content-proxy.png'))>0
    patches=[]
    for by in range(H//128):
        for bx in range(W//128):
            if (bx+3*by)%4:continue
            for oy in (32,96):
                for ox in (32,96):
                    x=bx*128+ox;y=by*128+oy;sl=(slice(y-r,y+r),slice(x-r,x+r))
                    if not np.all(geom[sl]) or not np.all(geometry[sl]):continue
                    ta=grayA[sl];sa=grayS[sl]
                    if ta.std()<15 or np.hypot(gxA[sl],gyA[sl]).mean()<2:continue
                    ga=np.stack([gxA[sl],gyA[sl]]);gs=np.stack([gxS[sl],gyS[sl]]);ga-=ga.mean((1,2),keepdims=True);gs-=gs.mean((1,2),keepdims=True)
                    ncc=float(np.sum(ga*gs)/max(np.sqrt(np.sum(ga*ga)*np.sum(gs*gs)),1e-20));shift,response=cv2.phaseCorrelate(ta-ta.mean(),sa-sa.mean(),window)
                    patches.append({'center_A_xy':[x,y],'block':[bx,by],'zero_shift_gradient_NCC':ncc,'phase_shift_xy':list(map(float,shift)),'phase_response':float(response)})
    original=next(d for d in old['donors'] if d['requested_seconds']==t)['patches'];combined=original+patches
    ncc=np.array([p['zero_shift_gradient_NCC'] for p in combined]);responsive=[p for p in combined if p['phase_response']>=.25];shifts=np.array([np.hypot(*p['phase_shift_xy']) for p in responsive])
    blocks=set((p['center_A_xy'][0]//128,p['center_A_xy'][1]//128) for p in combined)
    passed=bool(len(combined)>=6 and len(blocks)>=4 and np.median(ncc)>=.9 and (ncc>=.85).mean()>=.8 and len(responsive)>=4 and np.quantile(shifts,.95)<=2)
    eligible=bool(passed and reg['registration_evidence_sufficient'])
    if eligible:union|=geometry
    row={'requested_seconds':t,'NEW_patches':patches,'original_patches_reused_not_recomputed':len(original),'combined_count':len(combined),'heldout_spatial_blocks':len(blocks),'combined_NCC_median':float(np.median(ncc)) if len(ncc) else None,'combined_NCC_fraction_ge_.85':float((ncc>=.85).mean()) if len(ncc) else None,'combined_phase_responsive_count':len(responsive),'combined_responsive_phase_p95':float(np.quantile(shifts,.95)) if len(shifts) else None,'combined_patch_pass':passed,'conditional_geometry_eligible':eligible};rows.append(row)
    print('SUPPLEMENT',t,{k:v for k,v in row.items() if k!='NEW_patches'},flush=True)
summary={'rows':rows,'new_geometry_coverage':coverage(union),'accepted_nominal_plus_new_geometry_coverage':coverage(union|masks['accepted_common_geometry']),'criteria':'All original64-grid and new32/96-grid controls retained. >=6 patches in>=4heldout spatialblocks; medianNCC>=.9, >=80%NCC>=.85; >=4phase responses>=.25 and p95shift<=2px. Conditional registration gate also required. No refit/search/color correction.','limitations':'Same spatial blocks can correlate. This is geometric content evidence, not shadow-free absolute RGB.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');np.savez_compressed(out/'union.npz',new_geometry=union)
