"""One bounded rim_width neighborhood, then authorized thin_width if negative."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
BASE=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
PREV=BASE.parent/'combined-outer-saved'
spec=importlib.util.spec_from_file_location('prior',BASE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec=importlib.util.spec_from_file_location('presentation',BASE/'pass2-material-run.py')
pres=importlib.util.module_from_spec(spec);spec.loader.exec_module(pres)

def save(root,name,value):
    (root/name).write_text(json.dumps(value,indent=2)+'\n')

def run(key):
    root=BASE.parent/(key.replace('_','-')+'-neighborhood')
    if (root/'result.json').exists():
        print(key,'COMPLETE, no repeat',flush=True)
        return json.loads((root/'result.json').read_text())['candidate'] is not None
    if (root/'started.json').exists():raise RuntimeError('Partial neighborhood: inspect before recovery')
    root.mkdir(exist_ok=True)
    save(root,'started.json',dict(pid=os.getpid(),parameter=key,budget='two declared native neighbors ±.00025, no derivatives/optimizer',source_proof='reuse accepted pass1 unchanged map/kernel/emitted rays'))
    old=json.loads((PREV/'candidate-native.json').read_text());p=old['parameters'];co=np.asarray(old['material']);baseline=old['scores']
    studies=[m.Study(BASE/n) for n in ['a','b']]
    trials=[];candidate=None
    for j,delta in enumerate([-.00025,.00025]):
        q={**p,key:p[key]+delta}
        images=[s.render(q,co) for s in studies]
        scores=[m.guards(s,q,a) for s,a in zip(studies,images)]
        row=dict(delta=delta,parameters=q,scores=scores,guarded=m.good(scores,baseline),meaningful=any(o['E']-n['E']>1e-5 for n,o in zip(scores,baseline)))
        for i,a in enumerate(images):np.save(root/f'trial{j}-ref{i}-material.npy',a)
        trials.append(row);save(root,'trials.json',trials)
        print(key,delta,[s['E'] for s in scores],'guarded',row['guarded'],flush=True)
        if not(row['guarded'] and row['meaningful']):continue
        candidate=dict(parameters=q,material=co.tolist(),scores=scores,source_proof='UNCHANGED pass1 source coordinates, source blur and emitted rays; lighting widths only')
        save(root,'candidate-native.json',candidate)
        public=json.loads((PREV/'candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=113.5;qq['post_sigma']/=113.5;public['parameters']=qq;public['scores']=scores;save(root,'candidate-normalized.json',public)
        for i,(s,a) in enumerate(zip(studies,images)):
            np.save(root/f'ref{i}-complete.npy',m.image(s,q,a));np.save(root/f'ref{i}-alpha.npy',s.shape_coverage(q))
            oldimg=np.load(PREV/f'trial0-ref{i}-material.npy')
            panels=[s.target_crop,pres.presentation(s,p,oldimg),pres.presentation(s,q,a)]
            for label,array in zip(['target','baseline','candidate'],panels):
                assert array.shape==(335,1080,3)
                cv2.imwrite(str(root/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(array,0,1)*255).astype(np.uint8)[...,::-1])
            cv2.imwrite(str(root/f'ref{i}-comparison-width1080.png'),np.rint(np.clip(np.concatenate(panels,axis=0),0,1)*255).astype(np.uint8)[...,::-1])
        break
    save(root,'result.json',dict(parameter=key,baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=1,limits='Native strict both-reference E/glass/exterior/all16FG. Lighting-only width change; original ray/source proof reused. No 4x, no new source epoch, public edits or pass count. Primary independent acceptance required.'))
    print(key,'DONE',len(trials),'candidate',candidate is not None,flush=True)
    return candidate is not None

if __name__=='__main__':
    os.umask(0o002)
    # On rim success stop immediately; do not start another qualifying study.
    if not run('rim_width'):run('thin_width')
