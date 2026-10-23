from pathlib import Path
import json,numpy as np,cv2
from PIL import Image
from extended_fit import Study
from paired_fit import permitted
from motion_support import complete
root=Path('/evidence/extended/music-home-vector-corrected/paired');out=root.parent/'composited-rim-probe';out.mkdir(exist_ok=True);state=json.loads((root/'accepted.json').read_text());p=state['parameters'];co=np.array(state['material']);parts=[];records=[]
for n in ['a','b']:
 s=Study(root/n);s.case['foreground_response']=state['foreground_response'];raw=s.render(p,co);known=cv2.imread(str(s.folder/'known.png'),0).astype(np.float32)/255;s.source=complete(s,known);s.cache.clear();display=s.render(p,co);cov=s.shape_coverage(p);*_,(sd,_,_)=s.shape(s.x,s.y,p);mask=(sd<=0)&(sd>-.025);file=out/('base-'+n+'.png');s.comparison(display,file,p,context_completed=True);W=s.crop[2]-s.crop[0];H=s.crop[3]-s.crop[1];im=Image.open(file);rgb=np.array(im)[im.height-H:,W+2:].astype(np.float32)/255;parts.append((s,raw,display,cov,-sd,mask,rgb));records.append(dict(sample=n,baseline_composite_mse=float(np.mean(((rgb-s.target_crop)[mask]*255)**2))))
candidates=[]
for width in np.linspace(.001,.012,89):
 for strength in [.25,.5,.75,1.]:
  metrics=[];cost=[]
  for s,raw,display,cov,d,mask,rgb in parts:
   u=np.clip(np.maximum(d,0)/width,0,1);F=strength*(1-u**3*(u*(6*u-15)+10));q=(raw*(1-F[...,None])+F[...,None]).astype(np.float32);metrics.append(s.scores(q,include_ssim=False));qd=(display*(1-F[...,None])+F[...,None]).astype(np.float32);approx=np.rint(np.clip(rgb+cov[...,None]*(qd-display),0,1)*255)/255;cost.append(float(np.mean(((approx-s.target_crop)[mask]*255)**2)))
  if permitted(metrics,state['scores']) and all(v<=r['baseline_composite_mse'] for v,r in zip(cost,records)):candidates.append(dict(width=float(width),strength=strength,scores=metrics,proposal_composite_mse=cost))
candidates.sort(key=lambda r:sum(r['proposal_composite_mse']));verified=[]
for i,q in enumerate(candidates[:5]):
 errors=[]
 for n,(s,raw,display,cov,d,mask,rgb) in zip(['a','b'],parts):
  u=np.clip(np.maximum(d,0)/q['width'],0,1);F=q['strength']*(1-u**3*(u*(6*u-15)+10));qd=(display*(1-F[...,None])+F[...,None]).astype(np.float32);file=out/(f'trial-{i}-'+n+'.png');s.comparison(qd,file,p,context_completed=True);W=s.crop[2]-s.crop[0];H=s.crop[3]-s.crop[1];im=Image.open(file);rgb=np.array(im)[im.height-H:,W+2:].astype(np.float32)/255;errors.append(float(np.mean(((rgb-s.target_crop)[mask]*255)**2)))
 verified.append(dict(**q,actual_composite_mse=errors,allowed=all(v<=r['baseline_composite_mse'] for v,r in zip(errors,records))))
report=dict(baseline=state,region='Fitted inside band0..025L. NativePNG comparison includes actual coverage/shadow/context/quantization, not raw material versus partially covered reference.',backgrounds=records,verified=verified,proposal_count=356,limits='Proposal starts from a quantized baseline, atmost0.5RGB error; finalists independently composed. No accepted-state mutation. Uniformwhiteincidentfield is empirical, not measured Apple lighting.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(backgrounds=records,verified=verified)),flush=True)
