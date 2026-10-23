"""Independent target silhouette PROXIES only; no shape/photometric optimization."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from crowned_footprint import longitudinal,field
from toolbar_sampling_precision import bilinear
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-contour-audit');root.mkdir(exist_ok=True);pkg=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((pkg/'recipe.json').read_text());case=p['case'];L=min(case['half']);target=np.asarray(Image.open(pkg/'inputs/target.png'),float)/255;source=np.asarray(Image.open(pkg/'inputs/source.png'),float)/255
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def extract():
    file=root/'raw-profiles.npz'
    if file.exists():return
    xs=np.linspace(-case['half'][0],case['half'][0],50001);q,_=longitudinal(xs,*case['half'],p['footprint_softness']);ys=np.sqrt(np.maximum(L*L-q*q,0));curve=np.r_[np.stack([xs,-ys],-1),np.stack([xs[-2::-1],ys[-2::-1]],-1)];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(curve,axis=0),axis=1))];s=np.arange(0,arc[-1],2.);x=np.interp(s,arc,curve[:,0])/L;y=np.interp(s,arc,curve[:,1])/L
    for _ in range(4):
        T,gx,gy=field(x,y,p['shape']['half'],p['footprint_softness']);step=(T-1)/(gx*gx+gy*gy);x-=step*gx;y-=step*gy
    T,gx,gy=field(x,y,p['shape']['half'],p['footprint_softness']);nx=gx/np.hypot(gx,gy);ny=gy/np.hypot(gx,gy);px=x*L+case['center'][0];py=y*L+case['center'][1];t=np.arange(-8,12.0001,.125);X=px[:,None]+nx[:,None]*t;Y=py[:,None]+ny[:,None]*t;rgb=bilinear(target,X,Y);src=bilinear(source,X,Y);overlap=np.zeros(len(px),bool)
    for a,b,c,d in case['foreground']:overlap|=np.any((X>=a-4)&(X<c+4)&(Y>=b-4)&(Y<d+4),axis=1)
    np.savez_compressed(file,arc_native_px=s,profile_t=t,boundary_x=px,boundary_y=py,nx=nx,ny=ny,target_rgb=rgb,source_rgb=src,foreground_overlap=overlap)
    write(root/'extraction.json',{'target_sha256':hashlib.sha256((pkg/'inputs/target.png').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((pkg/'inputs/source.png').read_bytes()).hexdigest(),'recipe_sha256':hashlib.sha256((pkg/'recipe.json').read_bytes()).hexdigest(),'arc_length_native_px':float(arc[-1]),'profiles':len(px),'arc_step_native_px':2,'profile_step_native_px':.125,'accepted_model_boundary_max_implicit_error':float(abs(T-1).max()),'foreground_overlap_profiles':int(overlap.sum()),'source_profile_model_status':'Mixed observed/estimated source; paired target exterior guard required. Source profiles are NOT newly observed hidden content.','native_score_masks_changed':False,'image_shape_optimization':False});print('EXTRACT31',len(px),flush=True)
def summarize():
    saved=root/'sensitivity.json'
    if saved.exists() and json.loads(saved.read_text()).get('complete'):return
    raw=np.load(root/'raw-profiles.npz');t=raw['profile_t'];I=raw['target_rgb'].mean(-1);S=raw['source_rgb'].mean(-1);ext=(t>=3)&(t<=12);target_min=I[:,ext].min(-1);source_min=S[:,ext].min(-1);target_range=np.ptp(I[:,ext],axis=-1);source_range=np.ptp(S[:,ext],axis=-1);nx=raw['nx'];ny=raw['ny'];s=raw['arc_native_px'];region={'all':np.ones(len(s),bool),'top':ny<-.75,'bottom':ny>.75,'left':nx<-.75,'right':nx>.75,'shoulders':(abs(nx)>=.25)&(abs(nx)<=.75)&(abs(ny)>=.25)};background=np.median(I[:,(t>=8)&(t<=12)],axis=1);allresults=[];rng=np.random.default_rng(31);saved={}
    def parabolic(value,lo,hi,maximum):
        window=np.flatnonzero((t>=lo)&(t<=hi));j=(np.argmax(value[:,window],axis=1) if maximum else np.argmin(value[:,window],axis=1))+window[0];idx=np.arange(len(j));a=value[idx,np.maximum(j-1,0)];b=value[idx,j];c=value[idx,np.minimum(j+1,len(t)-1)];den=a-2*b+c;offset=np.divide(.5*(a-c),den,out=np.zeros_like(a),where=abs(den)>1e-15);offset=np.clip(offset,-.5,.5);valid=(j>window[0])&(j<window[-1]);return t[j]+offset*.125,j,valid
    def stats(values,valid,bootstrap):
        out={}
        for name,rr in region.items():
            use=valid&rr&np.isfinite(values);v=values[use];row={'profiles':int(use.sum())}
            if len(v):
                row.update(median_signed_native_px=float(np.median(v)),mean_signed_native_px=float(v.mean()),q10_q90=np.quantile(v,[.1,.9]).tolist(),fraction_positive=float(np.mean(v>0)))
                if bootstrap:
                    blocks=np.floor(s[use]/32).astype(int);keys=np.unique(blocks);groups=[v[blocks==k] for k in keys];draws=[]
                    for _ in range(1000):draws.append(float(np.median(np.concatenate([groups[k] for k in rng.integers(0,len(keys),len(keys))]))))
                    row['block32px_bootstrap_median_95CI']=np.quantile(draws,[.025,.975]).tolist();row['independent_arc_blocks']=len(keys)
            out[name]=row
        return out
    for sigma in [0.,.5,1.]:
        smooth=gaussian_filter1d(I,sigma/.125,axis=1,mode='nearest') if sigma else I;ridge,j,rv=parabolic(smooth,-4,4,True);peak=smooth[np.arange(len(s)),j];prominence=peak-background;grad=np.gradient(smooth,.125,axis=1);edge,ej,ev=parabolic(grad,-2,6,False);ev&=grad[np.arange(len(s)),ej]<-.001;observables={'ridge':(ridge,rv),'outer_negative_gradient':(edge,ev)}
        for f in [.25,.5,.75]:
            level=background+f*prominence;cross=np.full(len(s),np.nan)
            for i in range(len(s)):
                candidates=np.flatnonzero((np.arange(len(t)-1)>=j[i])&(t[:-1]<=8)&(smooth[i,:-1]>=level[i])&(smooth[i,1:]<=level[i]))
                if len(candidates):k=candidates[0];a=smooth[i,k];b=smooth[i,k+1];cross[i]=t[k]+.125*(a-level[i])/max(a-b,1e-20)
            observables[f'outer_level_{f}']=(cross,np.isfinite(cross)&rv)
        for mincut in [.65,.70,.75]:
            for rangecut in [.06,.08,.10]:
                textgood=(target_min>=mincut)&(source_min>=mincut)&(target_range<=rangecut)&(source_range<=rangecut);common=textgood&~raw['foreground_overlap']&(prominence>=.01);record={'measurement_sigma_native_px':sigma,'exterior_min_luminance_cut':mincut,'exterior_range_cut':rangecut,'text_guard_retained':int(textgood.sum()),'prominent_nonforeground_retained':int(common.sum()),'observables':{}}
                for name,(v,valid) in observables.items():record['observables'][name]=stats(v,valid&common,mincut==.70 and rangecut==.08)
                allresults.append(record)
        saved[f'sigma_{sigma}']={'ridge':ridge,'ridge_valid':rv,'outer_gradient':edge,'outer_gradient_valid':ev,'prominence':prominence}
        write(root/'sensitivity.json',{'complete':False,'shape_fits':0,'optical_renders':0,'variants':allresults});print('SENSITIVITY31',sigma,flush=True)
    np.savez_compressed(root/'observable-proxies.npz',**{f'{key}_{k}':v for key,d in saved.items() for k,v in d.items()});write(root/'sensitivity.json',{'complete':True,'shape_fits':0,'optical_renders':0,'scoring_masks_unchanged':True,'variants':allresults});write(root/'base-controls.json',{'exterior_target_min_quantiles':np.quantile(target_min,[0,.1,.5,.9,1]).tolist(),'exterior_source_min_quantiles':np.quantile(source_min,[0,.1,.5,.9,1]).tolist(),'exterior_target_range_quantiles':np.quantile(target_range,[0,.1,.5,.9,1]).tolist(),'exterior_source_range_quantiles':np.quantile(source_range,[0,.1,.5,.9,1]).tolist(),'foreground_overlap':int(raw['foreground_overlap'].sum()),'physical_alpha_boundary_is_not_observed':True})
    print('COMPLETE31_MEASUREMENT',flush=True)
extract();summarize()
