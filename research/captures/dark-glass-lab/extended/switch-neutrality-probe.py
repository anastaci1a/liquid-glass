from pathlib import Path
import json,numpy as np
from extended_fit import Study
root=Path('/evidence/extended/active-switch/paired');state=json.loads((root/'pass-02.json').read_text())['current'];out=root.parent/'neutrality-probe';out.mkdir(exist_ok=True)
rows=[]
for name in ['a','b']:
 s=Study(root/name);p=state['parameters'];pred=s.render(p,np.array(state['material']));x0,y0,x1,y1=s.crop
 source=s.source[y0:y1,x0:x1][s.valid].mean(0);chroma=float(source.max()-source.min())
 results=[]
 for floor in [0.,.1,.25,.5]:
  for sensitivity in [5.,10.,20.]:
   factor=floor+(1-floor)*min(1.,sensitivity*chroma)
   luma=pred@np.array([.2126,.7152,.0722],np.float32)
   proposal=luma[...,None]+factor*(pred-luma[...,None])
   score=s.scores(proposal);results.append(dict(floor=floor,sensitivity=sensitivity,factor=factor,scores=score))
 best=min(results,key=lambda r:r['scores']['loss']);luma=pred@np.array([.2126,.7152,.0722],np.float32);proposal=luma[...,None]+best['factor']*(pred-luma[...,None]);s.comparison(proposal,out/f'{name}.png',p)
 rows.append(dict(name=name,source_mean=source.tolist(),source_chroma=chroma,before=s.scores(pred),trials=results,best=best))
(out/'report.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ['name','source_mean','source_chroma','before','best']} for r in rows]))
