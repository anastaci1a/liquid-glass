import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from switch_cap_edge_model import CachedCapEdge,CapEdgeStudy
from revision_replay import clean_composite
root=Path('/evidence/extended/active-switch');out=root/'rev3-cap-edge-review';out.mkdir(exist_ok=True)
base=json.loads((root/'joint-native-review/candidate.json').read_text());v=json.loads((root/'joint-native-review/hq/verification.json').read_text());old=[v['candidate']['observations'][n] for n in ['A','B']]
S=[CachedCapEdge(root/'paired'/n,base['parameters']) for n in ['a','b']];co=np.array(base['material']);rows=[]
for amplitude,tail in [(0.,0.)]+[(a,t) for a in [.5,1.,2.,3.,4.,5.] for t in [0.,.25,.5]]:
 p=copy.deepcopy(base['parameters']);p['cap_edge_profile']=[amplitude,amplitude,amplitude*tail];sc=[];t=time.time()
 for index,s in enumerate(S):
  im=s.render(p,co);m=s.scores(im,include_ssim=False);C=clean_composite(s,p,im);ext=(s.sd>0)&(s.sd<.35);m['shadow']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2)))};sc.append(m)
  if amplitude==0:assert abs(m['loss']-old[index]['loss'])<1e-8
  if amplitude==1 and tail==0:
   ref=CapEdgeStudy(root/'paired'/['a','b'][index]).render(p,co);assert np.max(abs(ref-im))==0
 ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(sc,old)];guard=all(a['glass']['rmse']<=b['glass']['rmse'] and a['rim']['rmse']<=b['rim']['rmse'] for a,b in zip(sc,old))
 row=dict(profile=p['cap_edge_profile'],scores=sc,ratios=ratios,glass_rim_guards=guard,numeric_milestone=guard and max(ratios)<=.995,seconds=time.time()-t);rows.append(row)
 print('EDGE',p['cap_edge_profile'],ratios,guard,flush=True)
 (out/'screen.json').write_text(json.dumps(dict(baseline=base,baseline_scores=old,trials=rows,accepted=False,limits='Screen only. Explicit shape-relative cap-depth profile, common to both references. Source-support, original replay and visual review required before adoption.'),indent=2)+'\n')
