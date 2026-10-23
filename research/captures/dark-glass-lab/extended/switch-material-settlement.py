"""Refit one shared material after retained reflection/dispersion changes."""
import sys,json,time
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from paired_fit import Cached,material_trial
from progress_gate import evaluate
from source_support import coverage_report,supported
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'material-settlement-review';out.mkdir(exist_ok=True)
old=json.loads((root/'accepted.json').read_text());S=[Study(root/n) for n in ['a','b']];C=[Cached(s,old['parameters']) for s in S]
for s,c in zip(S,C):assert np.max(np.abs(c.render(old['material'])-s.render(old['parameters'],np.array(old['material']))))<2e-6
start=time.time();co,scores,calls=material_trial(C,old,list(range(23)));native=[s.scores(s.render(old['parameters'],co)) for s in S];support=[coverage_report(s,old['parameters']) for s in S]
report=dict(parameters=old['parameters'],material=co.tolist(),scores=native,baseline=old['scores'],source_support=support,source_supported=[supported(s,r) for s,r in zip(S,support)],evaluations=calls,seconds=time.time()-start,accepted=False)
(out/'candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
