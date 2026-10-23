import sys,json
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
import toolbar_candidate as model
from reproduce import points
from render import case_geometry
root=Path('/tmp/agent-toolbar-evidence-package');out=Path('/tmp/agent-toolbar-residual-diagnostics');out.mkdir(exist_ok=True)
p=json.loads((root/'recipe.json').read_text());case=p['case'];target=np.asarray(Image.open(root/'inputs/target.png')).astype(np.float32)/255;x0,y0,x1,y1=case['crop'];T=target[y0:y1,x0:x1];C=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');xs,ys,x,y=points(case);sd,*_=case_geometry(case,x,y);residual=(C-T)*255;rows=[]
for lo,hi in [(.75,2),(2,4),(4,8),(8,16),(16,34),(34,68),(68,170)]:
    mask=masks['glass']&(-sd>=lo)&(-sd<hi)
    if mask.sum():rows.append({'inward_native_px':[lo,hi],'pixels':int(mask.sum()),'rmse':float(np.sqrt(np.mean(residual[mask]**2))),'signed_RGB_mean':residual[mask].mean(0).tolist()})
L=min(case['half']);regions=[('upper-rim',[650,369,1270,435]),('d-stroke',[960,450,1120,550]),('underside',[650,650,1270,726])];proxy=[]
for name,(a,b,c,d) in regions:
    sample=masks['glass']&(xs>=a)&(xs<c)&(ys>=b)&(ys<d);X=x[sample]/L;Y=y[sample]/L;boundary=model.boundary(X,Y,p)[0];good=boundary<-2/L;X=X[good];Y=Y[good];h=1e-5
    F=lambda x,y:np.array(model.mapping(x,y,p));dx=(F(X+h,Y)-F(X-h,Y))/(2*h);dy=(F(X,Y+h)-F(X,Y-h))/(2*h);J=np.stack([dx.T,dy.T],axis=-1);singular=np.linalg.svd(J,compute_uv=False);det=np.linalg.det(J);valid=singular[:,1]>.05;sigma=p['source_sigma']*L
    proxy.append({'region':name,'box':list((a,b,c,d)),'fixed_crop_glass_rmse':float(np.sqrt(np.mean(residual[sample]**2))),'derivative_samples':len(X),'inverse_map_singular_medians':np.median(singular,axis=0).tolist(),'negative_determinant_fraction':float((det<0).mean()),'linear_proxy_valid_fraction':float(valid.mean()),'source_sigma_native_px':sigma,'linearized_output_source_blur_major_minor_median_px':[float(np.median(sigma/singular[valid,1])),float(np.median(sigma/singular[valid,0]))],'fixed_post_sigma_native_px':p['post_sigma']*L})
report={'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','fixed_depth_bins':rows,'local_map_blur_proxies':proxy,'limits':['Pure diagnostics, no fit/pixel/mask/epoch changes or optical score gain','Source blur and output blur do not commute with the nonlinear inverse map','Local Jacobian proxy ignores folds/nonlinear kernel integration; do not infer Apple PSF or a physical solid','Advisory regions retain their fixed crop positions; native full-mask gates remain authoritative','No dispersion claim from a neutral page']};(out/'diagnostics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
