from pathlib import Path
import json,cv2,numpy as np
from extended_fit import Study
from motion_support import complete
root=Path('/evidence/extended/music-home-vector-corrected');folder=root/'boundary-reflection-fine-probe';report=json.loads((folder/'report.json').read_text());state=report['baseline'];q=report['best'];p=state['parameters'];co=np.array(state['material'])
for n in ['a','b']:
 s=Study(root/'paired'/n);s.case['foreground_response']=state['foreground_response'];known=cv2.imread(str(s.folder/'known.png'),0).astype(np.float32)/255;s.source=complete(s,known);s.cache.clear();base=s.render(p,co,4);a,b,c,d=s.crop;yy,xx=np.mgrid[:base.shape[0],:base.shape[1]];x=(a-.5+(xx+.5)/4-s.case['center'][0])/s.L;y=(b-.5+(yy+.5)/4-s.case['center'][1])/s.L;*_,(sd,_,_)=s.shape(x,y,p);u=np.clip(np.maximum(-sd,0)/q['width'],0,1);F=q['strength']*(1-u**3*(u*(6*u-15)+10));trial=(base*(1-F[...,None])+F[...,None]).astype(np.float32);s.comparison(base,folder/('retained-'+n+'.png'),p,4,context_completed=True);s.comparison(trial,folder/('trial-'+n+'.png'),p,4,context_completed=True)
print('Private4x previews complete; no accepted-state update',flush=True)
