from pathlib import Path
import copy,itertools,json
import cv2,numpy as np
from extended_fit import Study
from source_support import masks,kernel_safe,fraction

class ChromaticStudy(Study):
 def field(self,x,y,p):
  X,Y,d,J=self.geometry_field(x,y,p);*_,(sd,nx,ny)=self.shape(x,y,p)
  u=np.clip(d/p['chromatic_band'],0,1);w=(1-u)**3*(1+3*u)
  texture=self.blur(self.kernel_sigma(p));channels=[]
  for c,sign in enumerate([1,0,-1]):
   xx=(X+sign*p['chromatic_shift']*w*nx)*self.L+self.case['center'][0]
   yy=(Y+sign*p['chromatic_shift']*w*ny)*self.L+self.case['center'][1]
   sample=cv2.remap(texture[:,:,c],xx.astype(np.float32),yy.astype(np.float32),cv2.INTER_LINEAR)
   if p.get('blur_transition',0)>1e-8:
    clear=cv2.remap(self.source[:,:,c],xx.astype(np.float32),yy.astype(np.float32),cv2.INTER_LINEAR)
    v=np.clip(d/p['blur_transition'],0,1);blend=v**3*(v*(6*v-15)+10);sample=clear+(sample-clear)*blend
   channels.append(sample)
  return np.maximum(np.stack(channels,-1),0)**p['gamma'],J
 def support(self,p):
  X,Y,d,J=self.geometry_field(self.x,self.y,p);*_,(sd,nx,ny)=self.shape(self.x,self.y,p)
  u=np.clip(d/p['chromatic_band'],0,1);w=(1-u)**3*(1+3*u);defined,_=masks(self);safe,_=kernel_safe(defined,self,p)
  return min(fraction(safe,((X+sign*p['chromatic_shift']*w*nx)*self.L+self.case['center'][0]).astype(np.float32),((Y+sign*p['chromatic_shift']*w*ny)*self.L+self.case['center'][1]).astype(np.float32),self.valid) for sign in [1,0,-1])

root=Path('/evidence/extended/active-switch/paired');state=json.loads((root/'pass-06.json').read_text())['current'];out=root.parent/'chromatic-map-probe';out.mkdir(exist_ok=True)
studies=[ChromaticStudy(root/name) for name in ['a','b']];p={**state['parameters'],'chromatic_shift':0.,'chromatic_band':.3};co=np.array(state['material'])
for s in studies:
 expected=Study.render(Study(s.folder),state['parameters'],co);actual=s.render(p,co)
 assert np.max(abs(actual-expected))<1e-7,'Zero channel separation changes baseline'
rows=[]
for band,shift in itertools.product([.15,.35,.7],[-.2,-.1,-.05,.025,.05,.1,.2]):
 q={**p,'chromatic_band':band,'chromatic_shift':shift};scores=[];supported=[]
 for s in studies:
  supported.append(s.support(q));scores.append(s.scores(s.render(q,co)))
 allowed=all(n['loss']<=b['loss']+1e-8 and n['glass']['rmse']<=b['glass']['rmse']+1e-8 for n,b in zip(scores,state['scores'])) and min(supported)>=.999
 row=dict(band=band,shift=shift,scores=scores,support=supported,allowed=allowed);rows.append(row)
 print(json.dumps(dict(band=band,shift=shift,losses=[s['loss'] for s in scores],allowed=allowed)),flush=True)
valid=[r for r in rows if r['allowed']];best=min(valid,key=lambda r:sum(s['loss'] for s in r['scores'])) if valid else None
if best:
 q={**p,'chromatic_band':best['band'],'chromatic_shift':best['shift']}
 for s,name in zip(studies,['a','b']):s.comparison(s.render(q,co),out/f'{name}.png',q)
report=dict(baseline_pass=6,baseline=state['scores'],trials=rows,best=best,model='F_c=F+sign_c*shift*W(d/band)*n; signs=(1,0,-1); W=(1-u)^3(1+3u). Shared fixed material. Empirical first-order RGB ray split, not an identified spectral Apple model.')
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(best=best)),flush=True)
