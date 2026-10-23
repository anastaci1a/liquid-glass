"""Durable queue25 quadrature controls. One full native point per invocation."""
import sys,json,copy,time,hashlib,argparse
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import numpy as np
import cv2
from PIL import Image
import toolbar_scattering_renderer as model
from progress_gate import evaluate,error
cv2.setNumThreads(1)
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-trials')
root.mkdir(exist_ok=True)
package=Path('/tmp/agent-toolbar-evidence-package')
p=json.loads((package/'recipe.json').read_text());case=p['case']
source=np.asarray(Image.open(package/'inputs/source.png'),float)/255
assert hashlib.sha256((package/'inputs/source.png').read_bytes()).hexdigest()==p['source_sha256']['source.png']
assert hashlib.sha256((package/'inputs/target.png').read_bytes()).hexdigest()==p['source_sha256']['target.png']
assert hashlib.sha256(Path('/tmp/agent-toolbar-run/frozen-masks.npz').read_bytes()).hexdigest()=='da7d9dec1b557f91321e9ed5aaef5a4416371cbd5657b83e2ff6fccb86b0aa53'

def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def tests():
    result={'stage':'running','code_hashes':model._CODE_HASHES,'tests':{},'new_full_baseline_renders':0}
    def save():write(root/'invariants.json',result)
    save()
    for order in [3,5,7,9]:
        nodes,w=model.quadrature(order);mean=w@nodes;cov=(nodes*w[:,None]).T@nodes
        assert np.all(w>0) and abs(w.sum()-1)<1e-15 and np.max(abs(mean))<1e-15 and np.max(abs(cov-np.eye(2)))<2e-15
        result['tests'][f'node_moments_{order}']={'weight_sum':float(w.sum()),'mean_max':float(abs(mean).max()),'covariance_error':float(abs(cov-np.eye(2)).max())};save()
    q=copy.deepcopy(p);q['scattering_covariance']={'rho':0.}
    small=copy.deepcopy(case);small['crop']=[900,370,1020,440]
    C,a=model.render(source,small,q);D,b=model.baseline.render(source,small,p)
    assert np.array_equal(C,D) and np.array_equal(a,b)
    result['tests']['rho0_small_crop_exact']={'material_exact':True,'coverage_exact':True,'small_crop_renderer_calls':2,'full_native_renders':0};save()
    q['scattering_covariance']['rho']=.02;co=np.zeros(len(q['material']));co[:3]=1;co[-3:]=1;q['material']=co.tolist();uniform=np.full(source.shape,.43)
    for scale in [1,2]:
        C,a=model.render(uniform,small,q,samples=4,scale=scale,order=3)
        err=float(np.max(abs(C[a>0]-.43)));assert err<2e-7
        result['tests'][f'native_uniform_scale{scale}']={'max_error':err,'coverage_pixels':int((a>0).sum()),'samples':4,'rho':.02};save()
    result['stage']='complete';save();print('INVARIANTS25',json.dumps(result),flush=True)

def native(order,rho):
    invariants=json.loads((root/'invariants.json').read_text());assert invariants['stage']=='complete' and invariants['code_hashes']==model._CODE_HASHES
    folder=root/f'rho-{rho.hex()}-order-{order}';folder.mkdir(exist_ok=True)
    if (folder/'measurement.json').exists():print('REUSE_COMPLETE25',str(folder),flush=True);return
    q=copy.deepcopy(p);q['scattering_covariance']={'rho':rho};write(folder/'recipe.json',q)
    atlas=model.load_native_atlas('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-covariance/native-atlas',case,p,p)
    began=time.time();print('BEGIN_NATIVE25',rho,order,str(folder),flush=True)
    C,a=model.render(source,case,q,samples=4,scale=1,order=order,atlas=atlas,checkpoint=folder)
    # Renderer persisted arrays before this reporting stage; full artifacts are
    # never lost if a score/gate assertion fails.
    assert np.array_equal(a,np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy'))
    before=json.loads((package/'primary-verification.json').read_text())['candidate'];basefg=json.loads((package/'primary-scores.json').read_text())['foreground']
    x0,y0,x1,y1=case['crop'];T=np.asarray(Image.open(package/'inputs/target.png'),np.float32)[y0:y1,x0:x1]/255;B=source[y0:y1,x0:x1];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');fgmask=np.load(package/'derived-foreground.npz');shadow=model.baseline.gaussian_coverage_shadow(case,p)
    def measure(material):
        scores={}
        for name in ['glass','rim']:
            D=(material-T)[masks[name]]*255;scores[name]={'rmse':float(np.sqrt(np.mean(D*D))),'pixels':int(masks[name].sum())}
        full=material*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None]);scores['shadow']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
        for layer in p['foreground_layers']:
            aa=fgmask[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
        fg={}
        for layer in p['foreground_layers']:
            aa,b,c,d=layer['box'];fg[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,aa-x0:c-x0]-T[b-y0:d-y0,aa-x0:c-x0])**2))*255)
        return scores,fg,full
    oldC=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');oldscore,oldfg,_=measure(oldC)
    assert error(oldscore)==error(before['observations']['A']) and oldfg=={n:v['rmse'] for n,v in basefg.items()}
    scores,fg,full=measure(C);state={'epoch':before['epoch'],'observations':{'A':scores}};gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
    base=np.array([oldscore['glass']['rmse'],oldscore['rim']['rmse'],oldscore['shadow'],oldfg['archivebox'],oldfg['plus']]);values=np.array([scores['glass']['rmse'],scores['rim']['rmse'],scores['shadow'],fg['archivebox'],fg['plus']]);np.save(folder/'complete.npy',full)
    report={'rho':rho,'order':order,'scores':state,'E':error(scores),'foreground':fg,'guard_order':['glass','rim','exterior','archivebox','plus'],'guard_before':base.tolist(),'guard_after':values.tolist(),'all_nonregression':bool(np.all(values<=base)),'gate':gate,'numerical_qualifier':bool(np.all(values<=base) and gate['observations']['A']['passed']),'coverage_exact':True,'elapsed_seconds_this_invocation':time.time()-began,'counted_passes':0,'source_proposal23_used':False,'code_hashes':model._CODE_HASHES}
    write(folder/'measurement.json',report);print('COMPLETE_NATIVE25',json.dumps(report),flush=True)
    records=[]
    for path in sorted(root.glob('rho-*/measurement.json')):
        records.append({'folder':str(path.parent),**json.loads(path.read_text())})
    write(root/'native-evaluations.json',{'evaluations':records,'family_count':1,'accepted_passes':0})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--tests',action='store_true');ap.add_argument('--order',type=int);ap.add_argument('--rho',type=float,default=.02);args=ap.parse_args()
    if args.tests:tests()
    else:native(args.order,args.rho)
