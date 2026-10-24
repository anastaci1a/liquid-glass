"""Residual checks on saved outputs only; preserve the as-run score record."""
from pathlib import Path
import datetime,json
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=ROOT/'research/experiments/compact-geometry-01';W=ROOT/'.evidence-working/compact-geometry-01'
assert not (P/'saved-validation.json').exists()
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'));assert datetime.datetime.now(datetime.timezone.utc)<end
rows=[]
for k in ['a','b']:
 new=np.load(P/f'compact-{k}-candidate.npz');old=np.load(B/f'{k}-colour-source-1.npz');raw=np.load(B/f'{k}-raw.npz');m=np.load(B/f'{k}-masks.npz');c=json.loads((W/k/'case.json').read_text());x0,y0,x1,y1=c['crop'];target=cv2.imread(str(W/k/'target.png'))[:,:,::-1].astype(np.float32)/255;T=target[y0:y1,x0:x1]
 A=new['complete'];O=old['complete'];ext=m['exterior'];frozen=m['glass']&(raw['coverage']<1)
 # Match the original exterior expression's float32 multiply-before-float cast.
 prior=float(np.sqrt(np.mean((O[ext]-T[ext])**2))*255);current=float(np.sqrt(np.mean((A[ext]-T[ext])**2))*255)
 old_part=float(np.sqrt(np.mean(((O-T)[frozen]*255)**2))) if frozen.any() else None
 new_part=float(np.sqrt(np.mean(((A-T)[frozen]*255)**2))) if frozen.any() else None
 source_record=next(r['scores']['exterior']['rmse'] for r in json.loads((B/'selected.json').read_text())['material']['references'] if r['reference']==k)
 assert prior==source_record
 rows.append(dict(reference=k,exterior_pixels=int(ext.sum()),exterior_complete_pixels_exact=bool(np.array_equal(A[ext],O[ext])),original_order_prior_exterior=prior,original_order_current_exterior=current,original_order_exterior_nonregress=current<=prior,frozen_old_partial_glass_pixels=int(frozen.sum()),frozen_old_partial_baseline_RMSE=old_part,frozen_old_partial_transfer_RMSE=new_part,frozen_old_partial_nonregress=None if old_part is None else new_part<=old_part,new_shape_partial_scope='The four-pixel field in the as-run result is original glass intersected with new coverage<1; this frozen-old cohort is separately retained.'))
assert datetime.datetime.now(datetime.timezone.utc)<end
(P/'saved-validation.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,new_rays=0,new_model_composites=0,source_queries=0,additional_Study_score_calls=0,exterior_saved_reductions=4,boundary_saved_reductions=4,correction_scope='As-run exterior scalar used Python float conversion before multiplication, unlike original compact score order. Original as-run measurements are preserved; this record restores exact comparison semantics.'),indent=2,allow_nan=False)+'\n');print(json.dumps(rows))
