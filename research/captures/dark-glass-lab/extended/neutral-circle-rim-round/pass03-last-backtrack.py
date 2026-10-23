from pathlib import Path
import json,cv2,numpy as np
from neutral_rim import render
from extended_fit import Study
from vector_revision import composite
from publish import pair
cv2.setNumThreads(1)
D=Path('/evidence/extended/neutral-circle-rim-round');O=D/'pass03-last-backtrack';assert not O.exists();O.mkdir();protocol=dict(previous_amplitude=.1,first_amplitude=.2,backtracks=[.125],width=.02,max_proposals=3,stop_first_qualifier=True,all_original_guards=True,source_proof_transfers=True);(O/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n');old=json.loads((D/'pass02/result.json').read_text())['rows'][0];rows=[]
for trial,a in enumerate([.125]):
 row=dict(amplitude=a,width=.02,items=[])
 for k,name in enumerate(['flower-next-round','safari-right-circle-round']):
  R=Path('/evidence/extended/helper-toolbar-work')/name;B=R/('neutral-playback-baseline' if k==0 else 'neutral-baseline');s=Study(B/'inputs/a');r=json.loads((R/'neutral-additive-round3/candidate-native.json').read_text());p=r['preset'];masks=np.load(B/'baseline-native-arrays.npz');audit={};M=render(s.source,s.case,p,a,.02,audit=audit);C=composite(s,p,M);q=s.scores(M);q['E']=float(np.sqrt(q['loss']))
  for n,key in [('glyph','glyph_mask'),('exterior','exterior_mask'),('full_visible_exterior','full_visible_exterior_mask')]:m=masks[key];q[n]=dict(pixels=int(m.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))))
  prev=old['items'][k]['scores'];checks={n:q[n]['rmse']<=prev[n]['rmse'] for n in ['glass','rim','held','interior','glyph','exterior','full_visible_exterior']};checks.update(E=q['E']<prev['E'],ssim=q['ssim']>=prev['ssim']);bound=max(z['max_unclipped'] for z in r['clipping_counts'].values())+a;checks['no_clipping']=audit['clipped_channels']==0
  base=np.load(R/'neutral-additive-round3/candidate-native.npz')['material'];first=np.load(D/f'trial1-{k}/arrays.npz')['material'];prediction=base+(first-base)*(a/.025);err=float(np.max(abs(prediction-M)));checks['unclipped_linear_equivalence']=err<3e-6
  row['items'].append(dict(scores=q,checks=checks,conservative_upper_bound=bound,actual_unclipped_audit=audit,independent_cached_linear_prediction_error=err));T=O/f'trial{trial}-{k}';T.mkdir();np.savez_compressed(T/'arrays.npz',material=M,complete=C);W,H=2*C.shape[1],2*C.shape[0];imgs=[cv2.resize(np.uint8(np.rint(np.clip(z,0,1)*255)),(W,H),interpolation=cv2.INTER_LANCZOS4) for z in [s.target_crop,C]];pair(*imgs,('Apple source','Reconstruction'),font_size=32).save(T/'comparison.png')
 row['qualifier']=all(all(c['checks'].values()) for c in row['items']);rows.append(row);(O/'result.json').write_text(json.dumps(dict(rows=rows,accepted_primary=False),indent=2)+'\n');print(json.dumps(row),flush=True)
 if row['qualifier']:break
