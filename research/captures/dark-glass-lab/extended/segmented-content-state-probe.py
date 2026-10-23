"""Test a shared selected-content scale, separately from lens geometry.

This is a compositing hypothesis, not proof that Apple rescales source text.
Original source files and accepted checkpoints are never changed.
"""
from pathlib import Path
import sys,json,copy
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np
from extended_fit import Study
from vector_foreground import coverage
from paired_fit import permitted
root=Path('/evidence/extended');folder=root/'active-segmented-selector';out=folder/'content-state-probe';out.mkdir(exist_ok=True)
state=json.loads((folder/'accepted.json').read_text());studies=[Study(folder),Study(folder/'second-observation')];original=[s.source.copy() for s in studies]
base_scores=[s.scores(s.render(state['parameters'],np.array(state['material']))) for s in studies]
def content(study,source,scale):
 result=source.copy();track=study.case['background_estimate']['track_pose'];camera=track[2]/823.5;ink=np.array([1.,.35,.4],np.float32);background=source[500,400].copy()
 for record in study.case['background_estimate']['font_calibration']:
  layer=copy.deepcopy(record['selected']['layer']);box=np.array(layer['vector_box'],float);box[[0,2]]=(box[[0,2]]-957.5)*camera+track[0];box[[1,3]]=(box[[1,3]]-547.5)*camera+track[1]
  cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2;large=np.array([cx,cy,cx,cy])+(box-[cx,cy,cx,cy])*1.25
  layer['box']=[int(large[0]-3),int(large[1]-3),int(large[2]+4),int(large[3]+4)];layer['vector_box']=box.tolist();A=coverage(folder,layer)
  layer['vector_box']=(np.array([cx,cy,cx,cy])+(box-[cx,cy,cx,cy])*scale).tolist();B=coverage(folder,layer);a,b,c,d=layer['box']
  result[b:d,a:c]+= (B-A)[...,None]*(ink-background)
 return np.clip(result,0,1)
archived=json.loads((root/'segmented-biased-track-preparation/accepted.json').read_text())['parameters'];rows=[]
for scale in [1.,1.0625,1.125,1.1875]:
 s=studies[0];s.source=content(s,original[0],scale);s.cache.clear()
 assert scale!=1 or np.array_equal(s.source,original[0])
 for family,seed in [('retained',state['parameters']),('archived-profile-proposal',archived)]:
  for sigma in [0.,.5,1.,2.,4.]:
   for cx in [-.05,0.,.05]:
    for cy in [-.05,0.,.05]:
     p=copy.deepcopy(seed);p.update(sigma=sigma,post_sigma=0.,core_x=cx,core_y=cy);loss,co=s.fit(p);rows.append(dict(content_scale=scale,family=family,training_loss=float(loss),parameters=p,material=co.tolist()))
 print('Completed content scale',scale,'best training',min(r['training_loss'] for r in rows if r['content_scale']==scale),flush=True)
verified=[]
for i,row in enumerate(sorted(rows,key=lambda r:r['training_loss'])[:10]):
 scores=[]
 for j,s in enumerate(studies):
  s.source=content(s,original[j],row['content_scale']);s.cache.clear();pred=s.render(row['parameters'],np.array(row['material']));scores.append(s.scores(pred))
  if i<3:s.comparison(pred,out/f'trial-{i}-{j}.png',row['parameters'],context_completed=True)
 verified.append({**row,'scores':scores,'both_allowed':permitted(scores,base_scores)})
(out/'report.json').write_text(json.dumps(dict(baseline=state,baseline_scores=base_scores,proposal_count=len(rows),verified=verified,limits='Shared selected-content scale is not an identified Apple semantic/optical mechanism. It tests mask-based content deformation against unchanged references. Native optical acceptance still requires a declared complete model and rechecking the then-current incumbent; no state files mutated.'),indent=2)+'\n')
print(json.dumps([dict(scale=r['content_scale'],family=r['family'],loss=[s['loss'] for s in r['scores']],glass=[s['glass']['rmse'] for s in r['scores']],sigma=r['parameters']['sigma'],both_allowed=r['both_allowed']) for r in verified]),flush=True)
