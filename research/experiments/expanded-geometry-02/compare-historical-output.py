"""Score saved current/old composites only; no renderer or source queries."""
import json
from pathlib import Path
import numpy as np
from extended_fit import Study
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;rows=[]
assert not (OUT/'historical-output-guards.json').exists()
current=json.loads((OUT/'result.json').read_text())
for k in ['a','b']:
 s=Study(ROOT/'.evidence-working/expanded-geometry-02'/k);C=np.load(ROOT/f'.evidence-working/geometric-gallery/expanded-{k}.npy');m=np.load(ROOT/f'.evidence-working/expanded-geometry-02/{k}-masks.npz')
 old=s.scores(C);old['E']=float(np.sqrt(old['loss']));err=(C-s.target_crop)*255;old['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));old['foreground_artwork_MSE']={};x0,y0,_,_=s.crop
 for l in s.case['foreground_layers']:
  a,b,c,d=l['box'];name=l.get('style_key',l.get('vector_asset',l.get('artwork_asset')));old['foreground_artwork_MSE'][name]=float(np.mean(err[b-y0:d-y0,a-x0:c-x0]**2))
 new=next(r['scores'] for r in current['records'] if r['hypothesis']=='h1' and r['reference']==k)
 guards={name:new[name]['rmse']<=old[name]['rmse'] for name in ['glass','rim','held','interior']};guards.update({name:new[name]<=old[name] for name in ['E','exterior_RMSE']});guards['ssim']=new['ssim']>=old['ssim'];guards.update({name:new['foreground_artwork_MSE'][name]<=v for name,v in old['foreground_artwork_MSE'].items()})
 rows.append(dict(reference=k,historical_output_scores=old,source_h1_guards=guards,status='PASS' if all(guards.values()) else 'NO_STRICT_QUALIFIER'));print(k,old['E'],guards,flush=True)
(OUT/'historical-output-guards.json').write_text(json.dumps(dict(records=rows,new_rays=0,RGB_queries=0,new_images=0),indent=2)+'\n')
