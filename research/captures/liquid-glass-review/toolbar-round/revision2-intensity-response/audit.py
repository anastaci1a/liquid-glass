"""Native analytical power-response/material identifiability, no new opticalfit."""
import sys,json,time,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_candidate as model
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-intensity-response');root.mkdir(exist_ok=True);package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());case=p['case'];L=min(case['half']);x0,y0,x1,y1=case['crop'];H=y1-y0;W=x1-x0;source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz');old=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');co=np.asarray(p['material']);atlasroot=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-covariance/native-atlas');sx=np.load(atlasroot/'sx.npy',mmap_mode='r');sy=np.load(atlasroot/'sy.npy',mmap_mode='r');blur=cv2.GaussianBlur(source,(0,0),p['source_sigma']*L)
assert hashlib.sha256((package/'inputs/source.png').read_bytes()).hexdigest()==p['source_sha256']['source.png']
def write(path,x):path.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def features():
    signature=hashlib.sha256(Path(__file__).read_bytes()+Path(model.__file__).read_bytes()+(package/'recipe.json').read_bytes()).hexdigest();meta=root/'feature-progress.json'
    if meta.exists():
        state=json.loads(meta.read_text());assert state['signature']==signature
        if state.get('complete'):return
        start=state['next_top'];basis=np.load(root/'raw-affine-design.npy',mmap_mode='r+');deriv=np.load(root/'raw-gamma-derivative.npy',mmap_mode='r+');intensity=np.load(root/'source-intensity.npy',mmap_mode='r+');chroma=np.load(root/'source-chroma.npy',mmap_mode='r+')
    else:
        start=0;state={'signature':signature,'next_top':0,'complete':False,'inside_ray_channels':0,'clipped_ray_channels':0,'exact_clip_knee_channels':0,'zero_source_channels':0,'one_source_channels':0,'preclip_min':1e30,'preclip_max':-1e30};basis=np.lib.format.open_memmap(root/'raw-affine-design.npy',mode='w+',dtype=np.float32,shape=(H,W,3,23));deriv=np.lib.format.open_memmap(root/'raw-gamma-derivative.npy',mode='w+',dtype=np.float32,shape=(H,W,3));intensity=np.lib.format.open_memmap(root/'source-intensity.npy',mode='w+',dtype=np.float32,shape=(H,W));chroma=np.lib.format.open_memmap(root/'source-chroma.npy',mode='w+',dtype=np.float32,shape=(H,W));write(meta,state)
    for top in range(start,H,8):
        bot=min(top+8,H);yy,xx=np.mgrid[top*4:bot*4,0:W*4];x=(x0+(xx+.5)/4-.5-case['center'][0])/L;y=(y0+(yy+.5)/4-.5-case['center'][1])/L;sd,*_=model.boundary(x,y,p);inside=sd<=0;sh=(bot-top,4,W,4);weight=inside.reshape(sh).sum((1,3));mx=sx[top*4:bot*4].astype(np.float32);my=sy[top*4:bot*4].astype(np.float32);C=cv2.remap(blur,mx,my,cv2.INTER_LINEAR);clear=cv2.remap(source,mx,my,cv2.INTER_LINEAR);u=np.clip(-sd/p['blur_transition'],0,1);w=u**3*(u*(6*u-15)+10);C=clear+(C-clear)*w[...,None];light=model.lighting(x,y,p);core=light[...,-1];gain=(1-core[...,None])*co[:3]+core[...,None]*co[-3:];Z=C*gain+co[3:6]+(light[...,:-1]@co[6:-3])[...,None];active=(Z>0)&(Z<1);state['inside_ray_channels']+=int(inside.sum())*3;state['clipped_ray_channels']+=int(((Z<0)|(Z>1))[inside].sum());state['exact_clip_knee_channels']+=int(((Z==0)|(Z==1))[inside].sum());state['zero_source_channels']+=int((C[inside]==0).sum());state['one_source_channels']+=int((C[inside]==1).sum())
        if inside.any():state['preclip_min']=min(state['preclip_min'],float(Z[inside].min()));state['preclip_max']=max(state['preclip_max'],float(Z[inside].max()))
        def average(value):return (value*inside.reshape((*inside.shape,*([1]*(value.ndim-2))))).reshape((*sh,*value.shape[2:])).sum((1,3))/np.maximum(weight,1).reshape((*weight.shape,*([1]*(value.ndim-2))))
        h=np.zeros_like(C);np.log(C,out=h,where=C>0);h*=C;deriv[top:bot]=average(h*gain*active);intensity[top:bot]=average(C.mean(-1));chroma[top:bot]=average(C.max(-1)-C.min(-1))
        # Bound working memory: form one native derivative column at a time.
        for k in range(23):
            D=np.zeros_like(C)
            if k<3:D[...,k]=C[...,k]*(1-core)
            elif k<6:D[...,k-3]=1
            elif k<20:D[:]=light[...,k-6,None]
            else:D[...,k-20]=C[...,k-20]*core
            basis[top:bot,...,k]=average(D*active)
        basis.flush();deriv.flush();intensity.flush();chroma.flush();state['next_top']=bot;write(meta,state)
    sigma=p['post_sigma']*L;den=cv2.GaussianBlur(alpha,(0,0),sigma)
    np.save(root/'gamma-derivative.npy',cv2.GaussianBlur(np.asarray(deriv)*alpha[...,None],(0,0),sigma)/np.maximum(den,1e-12)[...,None]);filtered=np.lib.format.open_memmap(root/'affine-design.npy',mode='w+',dtype=np.float32,shape=basis.shape)
    for k in range(23):filtered[...,k]=cv2.GaussianBlur(np.asarray(basis[...,k])*alpha[...,None],(0,0),sigma)/np.maximum(den,1e-12)[...,None]
    filtered.flush();state['complete']=True;write(meta,state)

def analyze():
    g=np.load(root/'gamma-derivative.npy');A=np.load(root/'affine-design.npy',mmap_mode='r');I=np.load(root/'source-intensity.npy');ch=np.load(root/'source-chroma.npy');R=T.astype(float)-old;report={'task':28,'candidate_curve':'ONE shared c^gamma after encoded clear/blur blend before affine material','gamma_identity':1,'initial_declared_bounds':[.8,1.25],'feature_traversal':json.loads((root/'feature-progress.json').read_text()),'cohorts':{},'new_candidate_renders':0,'native_nonlinear_fits':0,'new_optical_passes':0,'linear_diagnostics_are_not_optical_gains':True}
    sets={'all':masks['glass'],'observed':cohorts['observed_kernel_proxy'],'estimated':cohorts['estimated_kernel_proxy'],'mixed':cohorts['mixed_or_uncertain'],'observed_held':cohorts['observed_kernel_proxy']&masks['held'],'observed_train':cohorts['observed_kernel_proxy']&~masks['held'],'observed_neutral_text':cohorts['observed_kernel_proxy']&(ch<=.02)&(I<.8),'observed_neutral_paper':cohorts['observed_kernel_proxy']&(ch<=.02)&(I>=.8)}
    for name,mask in sets.items():
        X=np.asarray(A[mask],float).reshape(-1,23)*255;v=g[mask].ravel().astype(float)*255;r=R[mask].ravel()*255;norm=np.linalg.norm(X,axis=0);safe=np.maximum(norm,1e-20);scaled=X/safe;u,s,vt=np.linalg.svd(scaled,full_matrices=False);keep=s>s[0]*1e-8;proj=u[:,keep]@(u[:,keep].T@v);novel=v-proj;desired_novel=r-u[:,keep]@(u[:,keep].T@r)
        corr=lambda a,b:float(a@b/max(np.linalg.norm(a)*np.linalg.norm(b),1e-30))
        row={'pixels':int(mask.sum()),'source_intensity_range':[float(I[mask].min()),float(I[mask].max())],'gamma_tangent_RMS_255':float(np.sqrt(np.mean(v*v))),'gamma_desired_cosine':corr(v,r),'affine_scaled_rank':int(keep.sum()),'affine_singular_values':s.tolist(),'gamma_outside_affine_energy_fraction':float(novel@novel/max(v@v,1e-30)),'gamma_after_affine_desired_cosine':corr(novel,desired_novel),'MSE_first_derivative_per_gamma':float(-2*np.mean(r*v)),'advisory_intensity_bins':[]}
        for low,high in zip([0,.2,.4,.6,.8],[.2,.4,.6,.8,1.000001]):
            m=mask&(I>=low)&(I<high)
            if m.any():row['advisory_intensity_bins'].append({'range':[low,min(high,1)],'pixels':int(m.sum()),'residual_RGB_mean_255':(R[m].mean(0)*255).tolist(),'gamma_tangent_RGB_mean_255':(g[m].mean(0)*255).tolist()})
        report['cohorts'][name]=row;write(root/'audit.json',report);print('RESPONSE28',name,row['gamma_desired_cosine'],row['gamma_outside_affine_energy_fraction'],row['gamma_after_affine_desired_cosine'],flush=True)
    direction_comparisons={};old_source_alt=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-A-typography/input-proposal/material.npy');paths={'source23_unadopted_input_alternative':old_source_alt}
    for kind in ['srgb','bt709']:
        for mode in ['source','output','both']:paths[f'26_{kind}_{mode}']=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-filter-space')/f'{kind}-{mode}'/'material.npy'
    for name,path in paths.items():
        D=np.load(path)-old;direction_comparisons[name]={}
        for cname in ['all','observed','estimated']:
            m=sets[cname];a=g[m].ravel().astype(float);b=D[m].ravel().astype(float);direction_comparisons[name][cname]={'gamma_change_cosine':float(a@b/max(np.linalg.norm(a)*np.linalg.norm(b),1e-30)),'change_RMS_255':float(np.sqrt(np.mean(b*b))*255)}
    report['saved_operator_and_input_uncertainty_comparisons']=direction_comparisons;write(root/'audit.json',report);print('COMPLETE28',flush=True)
features();analyze()
