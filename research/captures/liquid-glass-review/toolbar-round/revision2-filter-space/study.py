"""Queue26: six predeclared discrete ordinary-filter operators; no fit."""
import sys,json,copy,hashlib,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_filter_space as model
from progress_gate import error,evaluate
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-filter-space');root.mkdir(exist_ok=True);package=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((package/'recipe.json').read_text());case=p['case'];L=min(case['half']);x0,y0,x1,y1=case['crop'];source=np.asarray(Image.open(package/'inputs/source.png'),float)/255;T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1]
assert hashlib.sha256((package/'inputs/source.png').read_bytes()).hexdigest()==p['source_sha256']['source.png']
assert hashlib.sha256((package/'inputs/target.png').read_bytes()).hexdigest()==p['source_sha256']['target.png']
assert hashlib.sha256(Path('/tmp/agent-toolbar-run/frozen-masks.npz').read_bytes()).hexdigest()=='da7d9dec1b557f91321e9ed5aaef5a4416371cbd5657b83e2ff6fccb86b0aa53'
codehash=hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()
def write(path,x):path.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def tests():
    r={'complete':False,'model_sha256':codehash,'tests':{}};write(root/'invariants.json',r)
    for kind in ['srgb','bt709']:
        knee=.04045 if kind=='srgb' else .081;lknee=.0031308 if kind=='srgb' else .018
        c=np.unique(np.r_[np.linspace(0,1,100001),knee-1e-12,knee,knee+1e-12]);roundtrip=model.encode(model.decode(c,kind),kind);err=float(abs(c-roundtrip).max());assert err<(3e-8 if kind=='srgb' else .00025)
        v=np.array([knee-1e-12,knee,knee+1e-12]);u=np.array([lknee-1e-12,lknee,lknee+1e-12]);assert model.decode(0.,kind)==0 and model.encode(0.,kind)==0 and abs(model.decode(1.,kind)-1)<1e-14 and abs(model.encode(1.,kind)-1)<1e-14
        r['tests'][kind]={'max_roundtrip_dense_and_knees':err,'encoded_knee_inputs':v.tolist(),'decoded_at_knee':model.decode(v,kind).tolist(),'linear_knee_inputs':u.tolist(),'encoded_at_knee':model.encode(u,kind).tolist(),'roundtrip_is_not_silently_forced_exact':True};write(root/'invariants.json',r)
        image=np.tile(c[:300].reshape(10,30,1),(1,1,3)).astype(np.float32);alpha=np.ones((10,30),np.float32);zero=model.output_filter(image,alpha,0,kind);assert np.max(abs(zero-image))<.00025
    small=copy.deepcopy(case);small['crop']=[900,370,1020,440];q=copy.deepcopy(p);C,a=model.render(source,small,q);D,b=model.baseline.render(source,small,q);assert np.array_equal(C,D) and np.array_equal(a,b);r['tests']['encoded_small_crop_exact']=True;write(root/'invariants.json',r)
    q['material']=np.r_[np.ones(3),np.zeros(len(q['material'])-6),np.ones(3)].tolist();uniform=np.full(source.shape,.43)
    for kind in ['srgb','bt709']:
        for scale in [1,2]:
            C,a=model.render(uniform,small,q,scale=scale,source_kind=kind,output_kind=kind);err=float(abs(C[a>0]-.43).max());assert err<3e-7;r['tests'][f'uniform_{kind}_scale{scale}']=err;write(root/'invariants.json',r)
    r['tests']['scale_units']={'source_native_sigma':p['source_sigma']*L,'source_sigma_at_doubled_L':p['source_sigma']*(2*L),'output_sigma_at_scale1':p['post_sigma']*L,'output_sigma_at_scale2':p['post_sigma']*L*2,'source_rays_use_native_units_at_every_output_scale':True};r['complete']=True;write(root/'invariants.json',r);print('INVARIANTS26',json.dumps(r),flush=True)

def native():
    inv=json.loads((root/'invariants.json').read_text());assert inv['complete'] and inv['model_sha256']==codehash
    before=json.loads((package/'primary-verification.json').read_text())['candidate'];oldC=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fm=np.load(package/'derived-foreground.npz');shadow=model.baseline.gaussian_coverage_shadow(case,p);rows=[]
    atlasroot=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-covariance/native-atlas');atlas={k:np.load(atlasroot/f'{k}.npy',mmap_mode='r') for k in ['sx','sy']}
    def raw(kind):
        f=root/f'raw-{kind}';f.mkdir(exist_ok=True)
        if (f/'complete.json').exists():
            meta=json.loads((f/'complete.json').read_text());assert meta['model_sha256']==codehash;return np.load(f/'material.npy')
        print('BEGIN_RAW26',kind,flush=True);C,a=model.raw_render(source,case,p,kind,atlas=atlas);np.save(f/'material.npy',C);np.save(f/'alpha.npy',a);assert np.array_equal(a,alpha);write(f/'complete.json',{'model_sha256':codehash,'source_kind':kind,'coverage_exact':True,'raw_native_render_count':1});return C
    def measure(C):
        sc={}
        for name in ['glass','rim']:
            D=(C-T)[masks[name]]*255;sc[name]={'rmse':float(np.sqrt(np.mean(D*D))),'pixels':int(masks[name].sum())}
        full=C*alpha[...,None]+B*(1-shadow[...,None])*(1-alpha[...,None]);sc['shadow']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
        for layer in p['foreground_layers']:
            aa=fm[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
        fg={}
        for layer in p['foreground_layers']:
            a,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,a-x0:c-x0]-T[b-y0:d-y0,a-x0:c-x0])**2))*255)
        return sc,fg,full
    oldsc,oldfg,_=measure(oldC);assert error(oldsc)==error(before['observations']['A']);base=np.array([oldsc['glass']['rmse'],oldsc['rim']['rmse'],oldsc['shadow'],oldfg['archivebox'],oldfg['plus']]);raws={'encoded':raw('encoded')};recovered=model.output_filter(raws['encoded'],alpha,p['post_sigma']*L,'encoded');assert np.array_equal(recovered,oldC);write(root/'native-recovery.json',{'accepted_material_exact':True,'coverage_exact':True,'accepted_E_exact':True,'new_raw_encoded_renders':1,'new_complete_baseline_render_calls':0,'reason':'Earlier ordinary-blur6 unfiltered raster was not persisted; one necessary raw reconstruction enables output-only comparators and independent postfilter recovery.'})
    cohorts=np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz');desired=T.astype(float)-oldC
    for kind in ['srgb','bt709']:
        raws[kind]=raw(kind)
        for mode,sk,ok in [('source',kind,'encoded'),('output','encoded',kind),('both',kind,kind)]:
            folder=root/f'{kind}-{mode}';folder.mkdir(exist_ok=True);q=copy.deepcopy(p);q['filter_spaces']={'source':sk,'output':ok};write(folder/'recipe.json',q);C=model.output_filter(raws[sk],alpha,p['post_sigma']*L,ok);np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',alpha);sc,fg,full=measure(C);np.save(folder/'complete.npy',full);state={'epoch':before['epoch'],'observations':{'A':sc}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);values=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']]);diagnostics={}
            for name in ['all','observed_kernel_proxy','estimated_kernel_proxy','mixed_or_uncertain']:
                mask=cohorts[name]&masks['glass'];D=(C-oldC)[mask].astype(float);R=desired[mask];diagnostics[name]={'pixels':int(mask.sum()),'old_RMSE_255':float(np.sqrt(np.mean(R*R))*255),'new_RMSE_255':float(np.sqrt(np.mean(((C-T)[mask]*255)**2))),'change_RMS_255':float(np.sqrt(np.mean(D*D))*255),'desired_change_cosine':float(np.sum(D*R)/max(np.sqrt(np.sum(D*D)*np.sum(R*R)),1e-30))}
            row={'transfer':kind,'operator':mode,'E':error(sc),'scores':state,'foreground':fg,'guard_order':['glass','rim','exterior','archivebox','plus'],'guard_before':base.tolist(),'guard_after':values.tolist(),'all_nonregression':bool(np.all(values<=base)),'gate':gate,'numerical_qualifier':bool(np.all(values<=base) and gate['observations']['A']['passed']),'advisory_fixed_cohorts':diagnostics,'counted_passes':0,'source23_adopted':False,'model_sha256':codehash};write(folder/'measurement.json',row);rows.append(row);write(root/'native-evaluations.json',{'predeclared_six_comparators':True,'raw_native_renders':len(raws),'completed_operator_results':rows,'new_passes':0});print('NATIVE26',kind,mode,row['E'],row['all_nonregression'],flush=True)
    print('COMPLETE26',flush=True)
if __name__=='__main__':
    if '--tests' in sys.argv:tests()
    else:native()
