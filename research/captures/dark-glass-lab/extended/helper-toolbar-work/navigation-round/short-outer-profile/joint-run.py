"""Last two bounded proposals in the retained outer-profile study; no refit."""
import importlib.util,json,os,sys
from pathlib import Path
import numpy as np
BASE=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
OUT=BASE/'joint-step'
spec=importlib.util.spec_from_file_location('prior',BASE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def dump(name,value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')

def main():
    os.umask(0o002)
    if (OUT/'result.json').exists():
        print('Completed joint proposals retained; no rerun.',flush=True);return
    if (OUT/'started.json').exists():raise RuntimeError('Inspect partial evidence before recovery')
    OUT.mkdir(exist_ok=True)
    dump('started.json',dict(pid=os.getpid(),budget='two native proposals maximum, shared c0/c2 direction, step1 then halfstep; total outer family ≤8'))
    baseline=json.loads((BASE/'baseline.json').read_text())
    state=json.loads((BASE/'baseline-public.json').read_text())
    studies=[m.Study(BASE/n) for n in ['a','b']]
    p=state['parameters'].copy();length=min(studies[0].case['half'])
    p['sigma']*=length;p['post_sigma']*=length
    co=np.asarray(state['material']);trials=[];candidate=None
    for index,factor in enumerate([1.,.5]):
        q={**p,'c0':p['c0']-.000425*factor,'c2':p['c2']-.000075*factor}
        predictions=[s.render(q,co) for s in studies]
        scores=[m.guards(s,q,a) for s,a in zip(studies,predictions)]
        row=dict(factor=factor,parameters=q,scores=scores,guarded=m.good(scores,baseline),meaningful=any(o['E']-n['E']>1e-5 for n,o in zip(scores,baseline)))
        for i,a in enumerate(predictions):np.save(OUT/f'proposal{index}-reference{i}-material.npy',a)
        trials.append(row);dump('trials.json',trials)
        print('JOINT',factor,[s['E'] for s in scores],'guarded',row['guarded'],flush=True)
        if not (row['guarded'] and row['meaningful']):continue
        row['source_support']=[m.coverage_report(s,q) for s in studies]
        dump('trials.json',trials)
        if not all(m.supported(s,r) for s,r in zip(studies,row['source_support'])):continue
        candidate=row
        for i,(s,a) in enumerate(zip(studies,predictions)):
            np.save(OUT/f'{i}-candidate-complete.npy',m.image(s,q,a))
            old=np.load(BASE/f'{i}-baseline-material.npy')
            panel=np.concatenate([s.target_crop,m.image(s,p,old),m.image(s,q,a)],axis=0)
            m.cv2.imwrite(str(OUT/f'{i}-target-baseline-candidate.png'),np.rint(np.clip(panel,0,1)*255).astype(np.uint8)[...,::-1])
        break
    dump('result.json',dict(baseline=baseline,trials=trials,candidate=candidate,accepted=False,count=0,limits='At most8 total proposals with prior6; no optimizer/new derivatives/native baseline rerender. Candidate, if present, requires primary independent replay/HQ/visual/source acceptance.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
