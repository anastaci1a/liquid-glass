from pathlib import Path
import json,cv2,numpy as np
from extended_fit import Study
from vector_revision import composite
cv2.setNumThreads(1)
D=Path('/evidence/extended/neutral-circle-rim-round');O=D/'width-predictions';assert not O.exists();O.mkdir();widths=[.012,.016,.024,.028];amplitudes=[.075,.1,.12,.125];(O/'protocol.json').write_text(json.dumps(dict(widths=widths,amplitudes=amplitudes,native_source_renders=0,prediction='Existing cached material plus independently integrated normal-light response; floating operation order differs',selection='All original checks vs accepted .1/.02 plus SSIM>=baseline+5e-7 on both; select lowest mean relativeE among feasible, then ONE actual native check.'),indent=2)+'\n');items=[]
for k,name in enumerate(['flower-next-round','safari-right-circle-round']):
 R=Path('/evidence/extended/helper-toolbar-work')/name;B=R/('neutral-playback-baseline' if k==0 else 'neutral-baseline');s=Study(B/'inputs/a');rec=json.loads((R/'neutral-additive-round3/candidate-native.json').read_text());p=rec['preset'];L=min(s.case['half']);cx,cy=s.case['center'];x0,y0,x1,y1=s.crop;base=np.load(R/'neutral-additive-round3/candidate-native.npz')['material'];masks=np.load(B/'baseline-native-arrays.npz');responses={}
 for w in widths:
  P=np.zeros(base.shape[:2],np.float32)
  for top in range(y0,y1,24):
   bot=min(top+24,y1);yy,xx=np.mgrid[top:bot:.5,x0:x1:.5];x=(xx-.25-cx)/L;y=(yy-.25-cy)/L;rad=np.hypot(x,y);d=np.maximum(1-rad,0);H=np.exp(-(d/w)**2)*np.divide((x+y)**2,2*rad**2,out=np.zeros_like(rad),where=rad>0);P[top-y0:bot-y0]=H.reshape(bot-top,2,x1-x0,2).mean((1,3))
  responses[w]=cv2.GaussianBlur(P,(0,0),p['post_sigma']*L)
 items.append((s,p,base,masks,responses))
old=json.loads((D/'pass02/result.json').read_text())['rows'][0];rows=[]
for w in widths:
 for a in amplitudes:
  row=dict(width=w,amplitude=a,items=[])
  for k,(s,p,base,masks,responses) in enumerate(items):
   M=base+a*responses[w][...,None];C=composite(s,p,M);q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
   for n,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=masks[key];q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
   prev=old['items'][k]['scores'];checks={n:q[n]['rmse']<=prev[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<prev['E'],ssim_margin=q['ssim']>=prev['ssim']+5e-7);row['items'].append(dict(scores=q,checks=checks))
  row['predicted_feasible']=all(all(x['checks'].values()) for x in row['items']);row['mean_relative_E']=float(np.mean([t['scores']['E']/old['items'][k]['scores']['E'] for k,t in enumerate(row['items'])]));rows.append(row)
good=[r for r in rows if r['predicted_feasible']];result=dict(rows=rows,native_source_renders=0,best=min(good,key=lambda x:x['mean_relative_E']) if good else None);(O/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['best']))
