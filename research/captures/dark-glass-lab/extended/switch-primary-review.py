"""Frozen native masks, source hashes, clean exterior and advisory crop checks."""
import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
cv2.setNumThreads(1)
from extended_fit import Study
from crop_diagnostics import diagnostics
from progress_gate import evaluate
from source_support import coverage_report,supported
from PIL import Image
root=Path('/evidence/extended/active-switch/paired');out=root.parent/'crown-material-review';old=json.loads((root/'accepted.json').read_text());new=json.loads((out/'candidate.json').read_text());S=[Study(root/n) for n in ['a','b']]
def composite(s,p,co):
 pred=s.render(p,np.asarray(co));cov=s.shape_coverage(p);a,b,c,d=s.crop;bg=s.source[b:d,a:c].copy();q=p['shadow'];*_,(sd,_,_)=s.shape(s.x-q['offset'][0],s.y-q['offset'][1],p);bg*=1-q['opacity']*np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2)[...,None];return pred,pred*cov[...,None]+bg*(1-cov[...,None])
inputs=[s.case for s in S];epoch=hashlib.sha256(json.dumps(dict(cases=inputs,metric='E²=.7glassRMSE²+.3rimRMSE²; original native2x2 glass/rim masks. New exterior0<originalsd<.35L, complete clean source composite.'),sort_keys=True).encode()).hexdigest();before={'epoch':epoch,'observations':{}};after={'epoch':epoch,'observations':{}};support=[];cropped=[]
for label,s in zip(['A','B'],S):
 ext=(s.sd>0)&(s.sd<.35)
 for state,model in [(before,old),(after,new)]:
  pred,whole=composite(s,model['parameters'],model['material']);score=s.scores(pred);score['shadow']={'rmse':float(np.sqrt(np.mean(((whole-s.target_crop)[ext]*255)**2))),'pixels':int(ext.sum())};state['observations'][label]=score
 pred,whole=composite(s,new['parameters'],new['material']);Image.fromarray(np.uint8(np.rint(np.clip(whole,0,1)*255))).save(out/f'verified-{label}.png');support.append(coverage_report(s,new['parameters']))
 crops={'upper-left':[.12,.06,.40,.31],'lower-left':[.12,.64,.42,.87],'right-rim':[.72,.28,.91,.70],'center':[.35,.35,.65,.65]};pred0,_=composite(s,old['parameters'],old['material']);cropped.append(dict(label=label,previous=diagnostics(s.target_crop,pred0,crops),candidate=diagnostics(s.target_crop,pred,crops)))
passed=all(supported(s,r) for s,r in zip(S,support));report=dict(previous=before,candidate=after,support=support,cropped=cropped,gate=evaluate(before,after,visual_review=False,replay_verified=True,source_support_verified=passed),limits='Independent full native replay; source hashes frozen. Exterior guard introduced before adoption, same mask/source/compositing for baseline and candidate. No reference shadow copied. Visual review remains separate. Native center support is inherited; not a proof of all continuously sampled rays.')
(out/'primary-review.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['gate']),flush=True)
