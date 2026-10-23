"""Source-informed alternative cap branch; frozen rev3 baseline.

A right-rim transmission is plain background although observed A is green.
B's corresponding rim is bright despite gray source in its current map.
A sufficiently inward folded ray can reach the green A track while exiting
B's shifted gray track on its opposite side. Test this EXISTING normal-field
orientation term globally; previous fits stayed near its negative-gain branch.
This is an empirical inverse-map hypothesis, not proof of a physical solid.
"""
import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');sys.path.insert(0,'/evidence/extended')
import cv2,numpy as np
cv2.setNumThreads(1)
from switch_native_cache import NativeCachedStudy
from revision_replay import clean_composite
from source_support import coverage_report,supported
root=Path('/evidence/extended/active-switch');out=root/'rev3-cap-branch-review';out.mkdir(exist_ok=True)
base=json.loads((root/'joint-native-review/candidate.json').read_text());v=json.loads((root/'joint-native-review/hq/verification.json').read_text());old=[v['candidate']['observations'][n] for n in ['A','B']]
S=[NativeCachedStudy(root/'paired'/n,base['parameters']) for n in ['a','b']];co=np.array(base['material']);rows=[]
for c0 in [base['parameters']['c0'],1.,1.4]:
 for cap in [base['parameters']['cap_normal_gain'],0.,.3,.6,1.,1.5,1.8]:
  p=copy.deepcopy(base['parameters']);p.update(c0=c0,cap_normal_gain=cap);sc=[];t=time.time()
  for s in S:
   im=s.render(p,co);m=s.scores(im,include_ssim=False);C=clean_composite(s,p,im);ext=(s.sd>0)&(s.sd<.35);m['shadow']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2)))};sc.append(m)
  ratios=[float(np.sqrt(a['loss']/b['loss'])) for a,b in zip(sc,old)];guard=all(a['glass']['rmse']<=b['glass']['rmse'] and a['rim']['rmse']<=b['rim']['rmse'] for a,b in zip(sc,old))
  row=dict(c0=c0,cap_normal_gain=cap,scores=sc,ratios=ratios,glass_rim_guards=guard,numeric_milestone=guard and max(ratios)<=.995,seconds=time.time()-t);rows.append(row)
  print('CAP',c0,cap,ratios,guard,flush=True)
  (out/'screen.json').write_text(json.dumps(dict(protocol=__doc__,baseline=base,baseline_scores=old,trials=rows,accepted=False,limits='Fixed-material global branch screen. No source support/independent replay/visual acceptance inferred from score.'),indent=2)+'\n')
