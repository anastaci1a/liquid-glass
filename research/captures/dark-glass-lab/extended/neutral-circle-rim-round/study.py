"""Bounded shared rim-light trials; no source/geometry/camera fitting."""
from pathlib import Path
import json,copy,cv2,numpy as np
import settled
from extended_fit import Study
from vector_revision import composite
from publish import pair
cv2.setNumThreads(1)
D=Path('/evidence/extended/neutral-circle-rim-round');assert not (D/'result.json').exists()
roots=[Path('/evidence/extended/helper-toolbar-work')/n for n in ['flower-next-round','safari-right-circle-round']]
items=[]
for R in roots:
 B=R/('neutral-playback-baseline' if R.name=='flower-next-round' else 'neutral-baseline');s=Study(B/'inputs/a');p=json.loads((R/'neutral-additive-round3/candidate-native.json').read_text());arrays=np.load(R/'neutral-additive-round3/candidate-native.npz');masks=np.load(B/'baseline-native-arrays.npz');items.append((s,p,arrays,masks))
# Shared unit two-sided direction, independent of target pixel positions.
def field(x,y,p,w):
 sd,nx,ny=settled.case_geometry(p['shape'],x,y);d=np.maximum(-sd,0)
 return np.exp(-(d/w)**2)*(.5*(nx+ny)**2)
q=np.linspace(-1.1,1.1,501);x,y=np.meshgrid(q,q);h=field(x,y,items[0][1]['preset'],.02);assert np.isfinite(h).all() and h.min()>=0 and h.max()<=1+1e-12
assert np.allclose(h,field(-x,-y,items[0][1]['preset'],.02),atol=1e-12)
origL,origS=settled.lighting,settled.shade
# This private offline adapter adds a separate geometric scalar channel;
# the prior 15-channel light array and shade operation remain byte-equivalent.
def render(s,p,a,w):
 if a==0:return settled.render(s.source,s.case,p,samples=2)
 def lighting(x,y,p,boundary=None):
  old=origL(x,y,p,boundary);return np.concatenate([old,field(x,y,p,w)[...,None]],axis=-1)
 def shade(sample,light,co):return np.clip(origS(sample,light[...,:-1],co)+a*light[...,-1,None],0,1)
 settled.lighting,settled.shade=lighting,shade
 try:return settled.render(s.source,s.case,p,samples=2)
 finally:settled.lighting,settled.shade=origL,origS

def score(s,M,C,masks):
 q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
 for name,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:
  m=masks[key];q[name]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
 return q
rows=[]
for amplitude in [.025,.0125,.00625]:
 row=dict(amplitude=amplitude,width=.02,items=[]);i=len(rows)+1
 for k,(s,r,arrays,masks) in enumerate(items):
  M=render(s,r['preset'],amplitude,.02);C=composite(s,r['preset'],M);q=score(s,M,C,masks);base=r['scores'];checks={n:q[n]['rmse']<=base[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<=base['E'],ssim=q['ssim']>=base['ssim']);row['items'].append(dict(scores=q,baseline_E=base['E'],checks=checks));out=D/f'trial{i}-{k}';out.mkdir();np.savez_compressed(out/'arrays.npz',material=M,complete=C);pair(np.uint8(np.rint(s.target_crop*255)),np.uint8(np.rint(np.clip(C,0,1)*255)),('Apple','Rim-light candidate')).save(out/'comparison.png')
 row['qualifier']=all(all(t['checks'].values()) for t in row['items']);rows.append(row);(D/'result.json').write_text(json.dumps(dict(rows=rows,accepted_passes=0,pending_visual_review=row['qualifier'],source_support_transferred=True),indent=2)+'\n');print(json.dumps(row),flush=True)
 if row['qualifier']:break
