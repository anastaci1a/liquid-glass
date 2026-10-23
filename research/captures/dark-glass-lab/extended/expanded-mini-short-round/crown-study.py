"""Bounded existing crowned-footprint family, frozen native protocol and inputs."""
import os,sys,json,copy
from pathlib import Path
import numpy as np
ROOT=Path('/evidence/extended/expanded-mini-short-round');sys.path.insert(0,str(ROOT));from preflight import Study,guards,emitted
os.umask(0o002)
out=ROOT/'crown-study';out.mkdir(exist_ok=True)
base=json.loads((ROOT/'baseline-native-recipe.json').read_text());p=base['parameters'];co=np.array(base['material']);studies=[Study(ROOT/n) for n in ['a','b']]
rows=[]
for softness in [.02,.05,.10]:
 q={**p,'crown_softness':softness};row={'softness':softness,'observations':[],'accepted':False}
 for i,s in enumerate(studies):
  pred=s.render(q,co);sc,full,ext=guards(s,q,pred);b=base['scores'][i]
  gate=sc['E']<=b['E'] and sc['glass']['rmse']<=b['glass']['rmse'] and sc['exterior']['rmse']<=b['exterior']['rmse'] and all(v<=b['foreground_mse'][k] for k,v in sc['foreground_mse'].items())
  row['observations'].append({'scores':sc,'original_all_guard':gate})
  np.save(out/f'crown-{softness}-ref{i}-material.npy',pred)
  np.save(out/f'crown-{softness}-ref{i}-complete.npy',full)
  print(softness,i,'E',sc['E'],'glass',sc['glass']['rmse'],'gate',gate,flush=True)
 rows.append(row);(out/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n')
 if all(r['original_all_guard'] for r in row['observations']) and any(row['observations'][i]['scores']['E']<b['E'] for i,b in enumerate(base['scores'])):
  support=[emitted(s,q,i) for i,s in enumerate(studies)];row['source_support']=support
  (out/'candidate-native.json').write_text(json.dumps({**base,'parameters':q,'scores':[r['scores'] for r in row['observations']]},indent=2)+'\n');(out/'evaluations.json').write_text(json.dumps(rows,indent=2)+'\n');print('Numerical candidate; primary visual/source review pending',flush=True);break
(out/'review.md').write_text('# Existing crown footprint study\n\nThree predeclared softness nodes .02/.05/.10 or stop at first guarded candidate; source, masks, material, map coefficients, blur and glyphs fixed. The positive-crown branch uses a smooth convex implicit footprint, not a physical solid. It also replaces the old radius with the minor half-size: not a continuous family at zero when original radius is smaller. No claim of an Apple proprietary equation. Scores are original native2x2; no score credited without full source/visual verification.\n')
