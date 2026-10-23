"""Queue29 controls then preselected native joint proposal; stop on qualifier."""
import sys,json,copy,hashlib,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_response as model
from toolbar_scattering_renderer import load_native_atlas
from progress_gate import error,evaluate
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials');root.mkdir(exist_ok=True);pkg=Path('/tmp/agent-toolbar-evidence-package');p=json.loads((pkg/'recipe.json').read_text());case=p['case'];source=np.asarray(Image.open(pkg/'inputs/source.png'),float)/255;codehash=hashlib.sha256(Path(model.__file__).read_bytes()).hexdigest()
assert hashlib.sha256((pkg/'inputs/source.png').read_bytes()).hexdigest()==p['source_sha256']['source.png']
def write(path,x):path.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def preset(z):
    q=copy.deepcopy(p);q['model']='toolbar_power_response';q['intensity_response']={'kind':'power','gamma':float(np.exp(float(z[0])*np.log(1.25)))};co=np.array(q['material']);co[:3]+=float(z[1])*.03;co[3:6]+=float(z[2])*.015;co[-3:]+=float(z[3])*.03;q['material']=co.tolist();return q
def tests():
    r={'complete':False,'model_sha256':codehash,'tests':{}};write(root/'invariants.json',r);x=np.linspace(0,1,65537)
    for gamma in [.8,1.,1.25]:
        y=model.response(x,gamma);assert y[0]==0 and y[-1]==1 and np.all(np.diff(y)>0)
        if gamma==1:assert np.array_equal(y,x)
        r['tests'][f'power_{gamma}']={'endpoints_exact':True,'dense_strictly_increasing':True,'minimum_increment':float(np.diff(y).min())};write(root/'invariants.json',r)
    minimum_gain=float(min(np.min(np.array(p['material'])[:3]-.03),np.min(np.array(p['material'])[-3:]-.03)));assert minimum_gain>0;r['tests']['full_material_monotonicity']={'minimum_bounded_gain':minimum_gain,'proof':'At allpositions gain is convex mix of bounded positive rim/core gains. Positive power, positive gain, additive source-independent lighting, clip, positive conditional AA/postfilter weights preserve nondecreasing response on ALL[0,1], not just sampled intensities.'};write(root/'invariants.json',r)
    small=copy.deepcopy(case);small['crop']=[900,370,1020,440];q=preset([0,0,0,0]);C,a=model.render(source,small,q);D,b=model.baseline.render(source,small,p);assert np.array_equal(C,D) and np.array_equal(a,b);r['tests']['gamma1_zero_offsets_smallcrop_exact']=True;write(root/'invariants.json',r)
    q=preset([1,0,0,0]);q['material']=np.r_[np.ones(3),np.zeros(len(q['material'])-6),np.ones(3)].tolist()
    for value,scale in [(0.,1),(.43,1),(1.,1),(.43,2)]:
        C,a=model.render(np.full(source.shape,value),small,q,scale=scale);expected=value**1.25;err=float(abs(C[a>0]-expected).max());assert err<3e-7;r['tests'][f'uniform_{value}_scale{scale}']={'expected_response':expected,'max_error':err};write(root/'invariants.json',r)
    r['complete']=True;write(root/'invariants.json',r);print('CONTROLS29',json.dumps(r),flush=True)
def measure(C,a):
    x0,y0,x1,y1=case['crop'];T=np.asarray(Image.open(pkg/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fg=np.load(pkg/'derived-foreground.npz');shadow=model.baseline.gaussian_coverage_shadow(case,p);sc={}
    for n in ['glass','rim']:
        D=(C-T)[masks[n]]*255;sc[n]={'rmse':float(np.sqrt(np.mean(D*D))),'pixels':int(masks[n].sum())}
    full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);sc['shadow']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
    for layer in p['foreground_layers']:
        aa=fg[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    foreground={}
    for layer in p['foreground_layers']:
        b,c,d,e=layer['box'];foreground[layer['name']]=float(np.sqrt(np.mean((full[c-y0:e-y0,b-x0:d-x0]-T[c-y0:e-y0,b-x0:d-x0])**2))*255)
    crops={}
    for n,(b,c,d,e) in {'upper':[650,369,1270,435],'d':[960,450,1120,550],'underside':[650,650,1270,726]}.items():
        sl=(slice(c-y0,e-y0),slice(b-x0,d-x0));m=masks['glass'][sl];crops[n]={'conditional_RMSE':float(np.sqrt(np.mean(((C-T)[sl][m]*255)**2))),'complete_RMSE':float(np.sqrt(np.mean(((full-T)[sl][m]*255)**2)))}
    return sc,foreground,full,crops
def first():
    checks=json.loads((root/'invariants.json').read_text());assert checks['complete'] and checks['model_sha256']==codehash;before=json.loads((pkg/'primary-verification.json').read_text())['candidate'];alpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy');old=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');oldsc,oldfg,_,oldcrops=measure(old,alpha);assert error(oldsc)==error(before['observations']['A']);q=preset([.2,.2,.2,.2]);folder=root/'first-proposal';folder.mkdir(exist_ok=True);write(folder/'recipe.json',q);atlas=load_native_atlas('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-covariance/native-atlas',case,q,p);print('BEGIN_FIRST29',flush=True);C,a=model.render(source,case,q,atlas=atlas,checkpoint=folder);assert np.array_equal(a,alpha);sc,fg,full,crops=measure(C,a);np.save(folder/'complete.npy',full);Image.fromarray(np.uint8(np.rint(np.clip(full,0,1)*255))).save(folder/'complete-preview.png');state={'epoch':before['epoch'],'observations':{'A':sc}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);base=np.array([oldsc['glass']['rmse'],oldsc['rim']['rmse'],oldsc['shadow'],oldfg['archivebox'],oldfg['plus']]);values=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']]);report={'z':[.2]*4,'gamma':q['intensity_response']['gamma'],'shared_offsets':[.006,.003,.006],'native_E':error(sc),'baseline_E':error(oldsc),'relative_reduction':float(1-error(sc)/error(oldsc)),'scores':state,'foreground':fg,'guard_order':['glass','rim','exterior','archivebox','plus'],'guard_before':base.tolist(),'guard_after':values.tolist(),'all_nonregression':bool(np.all(values<=base)),'gate':gate,'numerical_qualifier':bool(np.all(values<=base) and gate['observations']['A']['passed']),'advisory_crops':crops,'advisory_baseline_crops':oldcrops,'source_sha256':p['source_sha256'],'mask_sha256':hashlib.sha256(Path('/tmp/agent-toolbar-run/frozen-masks.npz').read_bytes()).hexdigest(),'coverage_exact':True,'new_native_candidate_renders':1,'new_full_baseline_renders':0,'model_sha256':codehash,'new_accepted_passes':0,'next':'STOP fitting; freshHQ/source/nativepackage and primaryindependentreview required' if np.all(values<=base) and gate['observations']['A']['passed'] else 'Rejectedfirstproposal; boundedcompactcalibration permitted only perpredeclaredmodel.md'};write(folder/'measurement.json',report);print('FIRST29',json.dumps(report),flush=True)
if __name__=='__main__':
    if '--tests' in sys.argv:tests()
    else:first()
