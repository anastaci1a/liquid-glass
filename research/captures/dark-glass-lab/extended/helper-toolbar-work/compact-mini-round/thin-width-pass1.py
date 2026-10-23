"""ONE tiny thin-width neighborhood from independently accepted Compact pass1."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
ROOT=Path('/evidence/extended/helper-toolbar-work/compact-mini-round');OUT=ROOT/'thin-width-pass1'
spec=importlib.util.spec_from_file_location('compact_preflight',ROOT/'preflight.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
from motion_support import complete as complete_source
from preview_size import dimensions

def save(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')

def good(scores,baseline):
    return all(s['E']<=b['E'] and s['glass']['rmse']<=b['glass']['rmse'] and s['exterior']['rmse']<=b['exterior']['rmse'] and all(s['foreground_mse'][k]<=v for k,v in b['foreground_mse'].items()) for s,b in zip(scores,baseline))

def composition(s,p,pred,presentation=False):
    x0,y0,x1,y1=s.crop
    source=s.source
    if presentation:
        known=cv2.imread(str(s.folder/'known.png'),0).astype(np.float32)/255
        source=complete_source(s,known)
    background=source[y0:y1,x0:x1]*(1-m.shadow(s,p,s.x,s.y)[...,None])
    alpha=s.shape_coverage(p)
    return s.apply_foreground((pred*alpha[...,None]+background*(1-alpha[...,None])).astype(np.float32))

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Compact neighborhood complete, no rerun.');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial trials before recovery')
    source=json.loads((ROOT/'scored-outside-shape-supplement.json').read_text())
    assert source['fit_authorized_by_full_source'],'FLAG source failure before fitting'
    OUT.mkdir(exist_ok=True)
    save('started.json',dict(pid=os.getpid(),budget='ONE thin_width neighborhood deltas−.00025,+.00025,−.000125,+.000125;max4actualtrialpairs;no derivatives/optimizer',baseline='primary accepted Compact pass1, joint-rim-material/candidate-native.json',source='full emitted whole+ALLnative scored rays including30outsidecorrectedoutline each, minimumconfidence1'))
    native=json.loads((ROOT/'joint-rim-material/candidate-native.json').read_text());p=native['parameters'];co=np.asarray(native['material']);baseline=native['scores']
    studies=[m.Study(ROOT/n) for n in ['a','b']];trials=[];candidate=None
    for j,delta in enumerate([-.00025,.00025,-.000125,.000125]):
        q={**p,'thin_width':p['thin_width']+delta}
        imgs=[s.render(q,co) for s in studies]
        scores=[m.guards(s,q,a)[0] for s,a in zip(studies,imgs)]
        row=dict(delta=delta,parameters=q,scores=scores,guarded=good(scores,baseline),meaningful=any(b['E']-s['E']>4*(.7*b['glass']['rmse']*float(np.spacing(np.float32(b['glass']['rmse'])))+.3*b['rim']['rmse']*float(np.spacing(np.float32(b['rim']['rmse']))))/b['E'] for s,b in zip(scores,baseline)))
        for i,a in enumerate(imgs):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
        trials.append(row);save('trials.json',trials)
        print('THIN',delta,[s['E'] for s in scores],'guarded',row['guarded'],flush=True)
        if not(row['guarded'] and row['meaningful']):continue
        candidate=dict(parameters=q,material=co.tolist(),scores=scores,source_proof='UNCHANGED map/kernel/input/emittedgrid: baseline whole+scored full source proof; thin_width lighting only')
        save('candidate-native.json',candidate)
        public=json.loads((ROOT/'joint-rim-material/candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=studies[0].L;qq['post_sigma']/=studies[0].L;public['parameters']=qq;public['scores']=scores;save('candidate-normalized.json',public)
        for i,(s,a) in enumerate(zip(studies,imgs)):
            np.save(OUT/f'ref{i}-complete.npy',composition(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q))
            old=np.load(ROOT/f'joint-rim-material/trial1-ref{i}-material.npy')
            panels=[s.target_crop,composition(s,p,old,True),composition(s,q,a,True)]
            x0,y0,x1,y1=s.crop;size=dimensions(x1-x0,y1-y0,large=True)
            for label,array in zip(['target','baseline','candidate'],panels):
                image=cv2.resize(array,size,interpolation=cv2.INTER_LINEAR)
                cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(image,0,1)*255).astype(np.uint8)[...,::-1])
            save(f'ref{i}-preview.json',dict(native_size=[x1-x0,y1-y0],preview_size=list(size),native_render_scale=1,resize='approved1080width presentation of saved native920px arrays; no new source/emitted rays or4x; native scores unchanged'))
        break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=1,source_gate_reused=True,limits='Accepted Compact pass1; original frozen epoch, strictbothE/glass/fixedexterior+all8glyphs+2artwork guards. One existing family only; primary verification before count/commit.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
