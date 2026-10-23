import sys
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from reproduce import *
p=Path('/evidence/apple-matches');s,t,_,_=prepare(p,'regular',CASES['regular'])
s=s.mean(2);t=t.mean(2);xs=slice(860,1080)
for out in range(375,443,3):
 a=t[out,xs];a=a-a.mean();an=np.linalg.norm(a)
 matches=[]
 for sig in [0,1,2,3]:
  source=cv2.GaussianBlur(s,(0,0),sig) if sig else s
  samples=source[360:660,xs];samples=samples-samples.mean(1)[:,None]
  cor=samples@a/np.maximum(np.linalg.norm(samples,axis=1)*an,1e-8)
  for y in np.argpartition(cor,-3)[-3:]:matches.append((float(cor[y]),360+int(y),sig))
 print(out,round(float(an),3),sorted(matches,reverse=True)[:3],flush=True)
