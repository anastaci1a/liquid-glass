"""ONE saved-response balanced rim/thin proposal, max4native backtracks."""
import importlib.util,json,os
from pathlib import Path
import cv2,numpy as np
BASE=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
PREV=BASE.parent/'rim-width-neighborhood';OUT=BASE.parent/'balanced-widths-pass2'
spec=importlib.util.spec_from_file_location('prior',BASE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec=importlib.util.spec_from_file_location('presentation',BASE/'pass2-material-run.py')
pres=importlib.util.module_from_spec(spec);spec.loader.exec_module(pres)

def save(name,v):
    (OUT/name).write_text(json.dumps(v,indent=2)+'\n')

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():print('Completed balance retained; no rerun.');return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial trials before recovery')
    OUT.mkdir(exist_ok=True)
    state=json.loads((PREV/'candidate-native.json').read_text());p=state['parameters'];co=np.asarray(state['material']);baseline=state['scores']
    rim=json.loads((PREV/'result.json').read_text())
    thin=json.loads((BASE.parent/'thin-width-pass2/result.json').read_text())
    # Fixed, previously proposed balance: half observed successful rim step,
    # 8% of observed negative thin step, without new derivative evaluation.
    delta={'rim_width':-.000125,'thin_width':-.00002}
    predicted=[.5*(rim['candidate']['scores'][i]['E']-rim['baseline'][i]['E'])+.08*(thin['trials'][0]['scores'][i]['E']-thin['baseline'][i]['E']) for i in range(2)]
    assert all(v<0 for v in predicted)
    save('started.json',dict(pid=os.getpid(),baseline='accepted navigation pass2/native441d368',budget='ONE declared balance, factors1,.5,.25,.125 max4actualtrialpairs'))
    save('proposal.json',dict(delta=delta,predicted_E_changes=predicted,saved_responses=['rim-width-neighborhood/result.json','thin-width-pass2/result.json'],limits='Saved scalar secants only, not new derivatives or proof. Rim secant starts at previous pass1 width; mixed clipping/curvature unknown. Original native guards alone decide.'))
    studies=[m.Study(BASE/n) for n in ['a','b']];trials=[];candidate=None
    for j,factor in enumerate([1.,.5,.25,.125]):
        q={**p,**{k:p[k]+factor*v for k,v in delta.items()}}
        images=[s.render(q,co) for s in studies];scores=[m.guards(s,q,a) for s,a in zip(studies,images)]
        row=dict(factor=factor,parameters=q,scores=scores,guarded=m.good(scores,baseline),meaningful=any(o['E']-n['E']>1e-5 for n,o in zip(scores,baseline)))
        for i,a in enumerate(images):np.save(OUT/f'trial{j}-ref{i}-material.npy',a)
        trials.append(row);save('trials.json',trials)
        print('BALANCE',factor,[s['E'] for s in scores],'guarded',row['guarded'],flush=True)
        if not(row['guarded'] and row['meaningful']):continue
        candidate=dict(parameters=q,material=co.tolist(),scores=scores,source_proof='UNCHANGED accepted pass2/pass1 map, input and source blur/emitted rays: both changed widths affect lighting only')
        save('candidate-native.json',candidate)
        public=json.loads((PREV/'candidate-normalized.json').read_text());qq=q.copy();qq['sigma']/=113.5;qq['post_sigma']/=113.5;public['parameters']=qq;public['scores']=scores;save('candidate-normalized.json',public)
        for i,(s,a) in enumerate(zip(studies,images)):
            np.save(OUT/f'ref{i}-complete.npy',m.image(s,q,a));np.save(OUT/f'ref{i}-alpha.npy',s.shape_coverage(q))
            old=np.load(PREV/f'trial0-ref{i}-material.npy')
            panels=[s.target_crop,pres.presentation(s,p,old),pres.presentation(s,q,a)]
            for label,array in zip(['target','baseline','candidate'],panels):
                assert array.shape==(335,1080,3)
                cv2.imwrite(str(OUT/f'ref{i}-{label}-width1080.png'),np.rint(np.clip(array,0,1)*255).astype(np.uint8)[...,::-1])
            cv2.imwrite(str(OUT/f'ref{i}-comparison-width1080.png'),np.rint(np.clip(np.concatenate(panels,axis=0),0,1)*255).astype(np.uint8)[...,::-1])
        break
    save('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,accepted_count=2,limits='ONE existing balanced lighting-width proposal; original source/AA/epoch/masks/shape/glyphs/material unchanged. Primary acceptance/commit/push/merge required before third count/rotation.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
