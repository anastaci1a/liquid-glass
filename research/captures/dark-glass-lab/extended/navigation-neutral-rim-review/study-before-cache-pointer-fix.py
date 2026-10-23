import os,sys,json,hashlib,copy,math
from pathlib import Path
import cv2,numpy as np
from extended_fit import Study
from neutral_rim import response,render_study
os.umask(2);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/navigation-round');B=R/'short-outer-profile';D=Path('/evidence/extended/navigation-neutral-rim-review');r=json.loads(Path('/workspace/docs/liquid-glass/experiments/reconstruction/studies/music-navigation/review-round/pass-03.json').read_text());n=json.loads((R/'rim-width-neighborhood/candidate-native.json').read_text());assert r['parameters']==n['parameters'] and r['material']==n['material'];sys.path.insert(0,str(B));from run import guards,good
states=[]
for i,label in enumerate(['a','b']):
 s=Study(B/label);assert hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()==r['case_sha256'][label]
 for f,sha in r['vector_sha256'][label].items():assert hashlib.sha256((s.folder/f).read_bytes()).hexdigest()==sha
 for f,sha in s.case['source_sha256'].items():assert hashlib.sha256((s.folder/f).read_bytes()).hexdigest()==sha
 M=np.load(R/f'rim-width-neighborhood/trial0-ref{i}-material.npy');base=guards(s,r['parameters'],M);H=np.empty(M.shape[:2],np.float32)
 for row,bottom,W,x,y in s.raster_tiles(1):H[row:bottom]=response(*s.shape(x,y,r['parameters'])[-1],.028).reshape(bottom-row,2,W,2).mean((1,3))
 sigma=s.kernel_sigma(r['parameters'],'post_sigma');H=cv2.GaussianBlur(H,(0,0),sigma) if sigma>.001 else H;states.append((label,s,M,H,base))
(D/'protocol-FIRST.json').write_text(json.dumps(dict(amplitudes=[.005,.0025],width=.028,baseline=[x[-1] for x in states],all_original_sources_vectors_recipe_exact=True,prediction='Cached material plus integrated shared normal response; no source queries. Actual clipped shading may differ and is final authority.',accepted=False),indent=2)+'\n')
rows=[];actual=[]
for a in [.005,.0025]:
 pred=[]
 for label,s,M,H,base in states:
  v=M+a*H[...,None];score=guards(s,r['parameters'],v);pred.append(score);print(json.dumps(dict(stage='prediction',a=a,observation=label,E=score['E'],glass=score['glass']['rmse'])),flush=True)
 row=dict(amplitude=a,scores=pred,original_guard_pass=good(pred,[x[-1] for x in states]));rows.append(row)
 if row['original_guard_pass'] and all(p['E']<s[-1]['E'] for p,s in zip(pred,states)):
  for label,s,M,H,base in states:
   audit={};v=render_study(s,r['parameters'],np.asarray(r['material']),a,.028,audit=audit);q=guards(s,r['parameters'],v);np.save(D/(label+'-candidate.npy'),v);actual.append(dict(observation=label,scores=q,audit=audit));print(json.dumps(dict(stage='native',observation=label,E=q['E'],audit=audit)),flush=True)
  break
(D/'result.json').write_text(json.dumps(dict(rows=rows,native=actual,accepted=False,original_guard_pass=bool(actual) and good([x['scores'] for x in actual],[x[-1] for x in states]),native_renders=len(actual),source_support='Same frozen map/source/ordinaryfilters and emitted queries; normal response introduces no incident-image samples. Exact original prior domain proof applies, not new observed-source evidence.'),indent=2)+'\n')
