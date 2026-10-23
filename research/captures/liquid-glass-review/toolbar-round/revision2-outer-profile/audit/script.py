"""Queue9 fixed-source contour/coverage/source-coordinate audit, no fit."""
import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-evidence-package/code')
import numpy as np
import cv2
from PIL import Image
from scipy.interpolate import BSpline
import crowned_tensor as model
from render import case_geometry
cv2.setNumThreads(1)
package=Path('/tmp/agent-toolbar-evidence-package');out=Path('/tmp/agent-toolbar-revision2-outer-audit');out.mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text());case=p['case'];L=min(case['half']);x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0
source=np.asarray(Image.open(package/'inputs/source.png'),float)/255
T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255
C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');a=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy')
F=np.load('/tmp/agent-toolbar-revision2-blur/baseline/complete.npy')
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz')
yy,xx=np.mgrid[:H,:W];xs=xx+x0;ys=yy+y0
sd=case_geometry(case,xs-case['center'][0],ys-case['center'][1])[0]
actual=model.boundary((xs-case['center'][0])/L,(ys-case['center'][1])/L,p)[0]*L
weight=.7/masks['glass'].sum()+.3/masks['rim'].sum()
E2=float(.7*np.mean(((C-T)[masks['glass']]*255)**2)+.3*np.mean(((C-T)[masks['rim']]*255)**2))
rows=[]
for lo,hi in [(.75,2),(2,4),(4,8),(8,16),(16,34)]:
    band=masks['glass']&(-sd>=lo)&(-sd<hi);partial=band&(a<1);opaque=band&(a==1)
    entry={'inward_native_px':[lo,hi],'pixels':int(band.sum()),'partial_coverage':int(partial.sum()),'min_alpha':float(a[band].min()),'actual_minus_nominal_SDF_median_px':float(np.median((actual-sd)[band])),'actual_minus_nominal_SDF_max_abs_px':float(np.max(np.abs((actual-sd)[band]))),'confidence_pixels':{k:int((band&cohorts[k]).sum()) for k in ['observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']}}
    for name,mask in [('all',band),('opaque_only',opaque),('partial_only',partial)]:
        if not mask.any():entry[name]={'pixels':0};continue
        R=(C-T)[mask]*255;RF=(F-T)[mask]*255
        contribution=float(weight*np.sum(np.mean(R**2,axis=1)))
        entry[name]={'pixels':int(mask.sum()),'conditional_rmse':float(np.sqrt(np.mean(R**2))),'complete_rmse':float(np.sqrt(np.mean(RF**2))),'E_squared_contribution':contribution,'E_squared_fraction':contribution/E2}
    rows.append(entry)

# Trace actual emitted source coordinates in the newly investigated rim band.
traces={i:{'X':[],'Y':[],'basis':[]} for i in range(3)}
for top in range(0,H,16):
    bot=min(top+16,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4]
    x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L
    X,Y=model.mapping(x,y,p);ds,nx,ny=model.boundary(x,y,p)
    nominal=case_geometry(case,x*L,y*L)[0]
    mask=np.repeat(np.repeat(masks['glass'][top:bot],4,axis=0),4,axis=1)&(ds<=0)
    for i,(lo,hi) in enumerate([(.75,2),(2,4),(4,8)]):
        valid=mask&(-nominal>=lo)&(-nominal<hi)
        if not valid.any():continue
        traces[i]['X'].append(X[valid]*L+case['center'][0]);traces[i]['Y'].append(Y[valid]*L+case['center'][1])
        basis=BSpline.design_matrix(np.clip(-ds[valid]/p['shape']['radius'],0,1),model.KNOTS,3).toarray()[:,:4]
        traces[i]['basis'].append(basis)
ray_reports=[]
for i,trace in traces.items():
    X=np.concatenate(trace['X']);Y=np.concatenate(trace['Y']);basis=np.concatenate(trace['basis'])
    ray_reports.append({'band':[[.75,2],[2,4],[4,8]][i],'rays':len(X),'source_x_min_median_max':np.quantile(X,[0,.5,1]).tolist(),'source_y_min_median_max':np.quantile(Y,[0,.5,1]).tolist(),'outer_basis_mean':basis.mean(0).tolist(),'max_source_shift_for_authorized_delta_.15_px':(np.max(np.abs(basis),axis=0)*L*.15).tolist()})

# Targeted fresh sampling diagnostics. Twelve-native-pixel padding is larger
# than all output-filter support in this accepted recipe, so crops are views.
sampling=[]
for name,box in [('upper',[650,369,1270,435]),('underside',[650,650,1270,726])]:
    a0,b0,c0,d0=box;crop=[a0-12,b0-12,c0+12,d0+12];local=copy.deepcopy(case);local['crop']=crop
    c4,a4=model.render(source,local,p,samples=4);c8,a8=model.render(source,local,p,samples=8)
    hq,ha=model.render(source,local,p,samples=4,scale=4)
    s=(slice(12,12+d0-b0),slice(12,12+c0-a0));global_s=(slice(b0-y0,d0-y0),slice(a0-x0,c0-x0));mask=masks['glass'][global_s]
    exact=float(np.max(np.abs(c4[s]-C[global_s])));assert exact==0
    material_hq=hq[48:48+(d0-b0)*4,48:48+(c0-a0)*4]
    alpha_hq=ha[48:48+(d0-b0)*4,48:48+(c0-a0)*4]
    shape=(d0-b0,4,c0-a0,4)
    den=alpha_hq.reshape(shape).sum((1,3));reduced=(material_hq*alpha_hq[...,None]).reshape((*shape,3)).sum((1,3))/np.maximum(den,1)[...,None]
    nativeT=T[global_s]
    metric=lambda v:float(np.sqrt(np.mean(((v-nativeT)[mask]*255)**2)))
    sampling.append({'name':name,'box':box,'native_patch_matches_saved_full_material_max_abs':exact,'conditional_native4_rmse':metric(c4[s]),'conditional_native8_diagnostic_rmse':metric(c8[s]),'hq4x_area_coverage_weighted_native_diagnostic_rmse':metric(reduced),'complete_native4_rmse':float(np.sqrt(np.mean(((F-T)[global_s][mask]*255)**2))),'native4_vs_native8_material_rmse':float(np.sqrt(np.mean(((c4[s]-c8[s])[mask]*255)**2))),'native4_vs_hq_area_material_rmse':float(np.sqrt(np.mean(((c4[s]-reduced)[mask]*255)**2)))})
    np.save(out/f'{name}-hq4x-material.npy',material_hq);np.save(out/f'{name}-hq4x-alpha.npy',alpha_hq)
    np.save(out/f'{name}-native8-material.npy',c8[s]);np.save(out/f'{name}-native8-alpha.npy',a8[s])
    Image.fromarray(np.uint8(np.rint(np.clip(material_hq,0,1)*255))).save(out/f'{name}-hq4x-conditional.png')
    print('SAMPLING',name,sampling[-1],flush=True)
report={'accepted_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch_unchanged':True,'no_optical_fit_or_gain':True,'baseline_E_squared':E2,'bands':rows,'native_source_ray_traces':ray_reports,'sampling':sampling,'conclusion_limits':['Published upper8.964385936 is complete visible composite over glass mask; conditional native is9.200722694; exact discrepancy resolved without changing protocol','Fresh8grid/HQ checks are diagnostics only; original4x4 conditional native remains gate','Padding independence checked exactly before crop sampling comparison','Coverage/coordinate traces do not identify an Apple physical solid or source hidden content','Outer0–3 affect a distinct narrow normal-profile band; changing silhouette/material/glyphs/source is excluded from any follow-on calibration']}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n');print('AUDIT DONE',flush=True)
