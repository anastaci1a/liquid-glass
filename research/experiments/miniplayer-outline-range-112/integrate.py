from pathlib import Path
from dataclasses import replace
import json,datetime,numpy as np,hashlib,traceback
from music_miniplayer_family import working_contour
from miniplayer_outline_widths import integrate_widths
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-outline-taper-107';P=json.loads((B/'two-axis-protocol.json').read_text());C=json.loads((OLD/'protocol.json').read_text());F=json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text());ledger={k:0 for k in P['caps']};results=[];hashes={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(B/n).write_text(json.dumps(v,indent=2)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline']);assert ledger[k]+n<=P['caps'][k],(k,n,ledger[k]);ledger[k]+=int(n)
for f in [Path(__file__),B/'two-axis-protocol.json',R/'reconstruction/miniplayer_outline_widths.py',R/'reconstruction/miniplayer_outline_taper.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/shoulder_core_coordinate.py',R/'reconstruction/outline_response.py',R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/families/music-mini-player-working.json',OLD/'protocol.json']:hashes[str(f.relative_to(R))]=sha(f)
try:
 for member in ['expanded','compact']:
  meta=json.loads((OLD/f'{member}-a-metrics.json').read_text());crop=meta['crop'];coordinate=replace(working_contour(member),counter=charge)
  # Native center is recovered from the exact symmetric retained pixel grid.
  # Read the original center from the same frozen load-data declarations.
  base=R/'.evidence-working'/f'{member}-geometry-0{2 if member=="expanded" else 1}'/'a/case.json'
  if member=='expanded':center=np.array(json.loads((R/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
  else:
   case=json.loads(base.read_text());pr=json.loads((R/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];legacy=json.loads((B.parent/'miniplayer-three-pass-101/legacy-numerical-family.json').read_text());center=np.array(case['center'])+legacy['length_unit_native_pixels']*np.array([pr['shape_dx'],pr['shape_dy']])
  center+=F.get('registration',{}).get('center_shift_native',[0,0])
  for f in [base,R/'reconstruction/studies/geometric-expanded-pipeline/summary.json',R/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json',B.parent/'miniplayer-three-pass-101/legacy-numerical-family.json',OLD/f'{member}-adaptive-moments.npz']:hashes[str(f.relative_to(R))]=sha(f)
  with np.load(OLD/f'{member}-adaptive-moments.npz') as z:previous=np.stack([z['alpha'],z['reduction']])
  x0,y0,x1,y1=crop;xx=np.broadcast_to(np.arange(x0,x1),(y1-y0,x1-x0));boundary=center[0]-coordinate.half[0]+2*coordinate.half[0]*C['left_fraction'];affected=xx+.5>boundary
  levels={}
  for order in P['orders']:
   levels[order]=integrate_widths(crop,coordinate,center,F['material']['outline']['angular'],C,P['widths'][1:],order,charge)
   np.savez_compressed(B/f'{member}-widths{order}.npz',moments=levels[order]);save('integration-ledger.json',ledger);print(member,order,flush=True)
  diff=np.max(abs(levels[16]-levels[32]),axis=(0,1));selected=(diff>P['maximum_order_difference']/4)&affected;assert selected.sum()<=P['maximum_refined_pixels'];print('REFINE',member,int(selected.sum()),flush=True)
  fine={}
  for order in P['refinement_orders']:
   fine[order]=integrate_widths(crop,coordinate,center,F['material']['outline']['angular'],C,P['widths'][1:],order,charge,pixel_mask=selected)
   np.savez_compressed(B/f'{member}-widths-restricted{order}.npz',moments=fine[order],selected=selected);save('integration-ledger.json',ledger)
  difference=float(np.max(abs(fine[64][:,:,selected]-fine[96][:,:,selected]))) if selected.any() else 0;assert difference<=P['maximum_order_difference'];out=levels[32];out[:,:,selected]=fine[96][:,:,selected];out[:,:,:,~np.ones(1,dtype=bool)] if False else None
  for k in range(4):out[k][:,~affected]=previous[:,~affected]
  moments=np.concatenate([previous[None],out]);np.savez_compressed(B/f'{member}-width-moments.npz',moments=moments,affected=affected)
  results.append(dict(member=member,center=center.tolist(),affected_pixels=int(affected.sum()),refined_pixels=int(selected.sum()),maximum_coarse_difference=float(diff[~selected].max()),maximum_refined_difference=difference,left_exact=True));save('integration.json',results);print('PASS',member,difference,flush=True)
 assert hashes=={p:sha(R/p) for p in hashes};save('integration-hashes.json',hashes);save('integration-finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),members=2,new_optical_rays=0))
except Exception as e:save('integration-failure.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
finally:save('integration-ledger.json',ledger)
