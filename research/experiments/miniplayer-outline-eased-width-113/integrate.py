from pathlib import Path
from dataclasses import replace
import json,datetime,numpy as np,hashlib,traceback
from music_miniplayer_family import working_contour
from miniplayer_outline_eased import integrate,profiles
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-outline-range-112';P=json.loads((B/'protocol.json').read_text());C=P['profile'];F=json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text());ledger={k:0 for k in P['caps']};results=[]
def save(n,x):(B/n).write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[Path(__file__),B/'protocol.json',OLD/'integration.json',R/'reconstruction/miniplayer_outline_eased.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/shoulder_core_coordinate.py',R/'reconstruction/outline_response.py',R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/families/music-mini-player-working.json']
hashes={str(p.relative_to(R)):sha(p) for p in files};save('first-hashes.json',hashes)
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline']);assert ledger[k]+n<=P['caps'][k];ledger[k]+=int(n)
try:
 x=np.array([0,C['left_fraction'],.5,C['shoulder_fraction'],C['right_fraction'],1]);s,b=profiles(x,C)
 assert np.allclose(s[[0,1,3,4,5]],.8*np.array([4/7,4/7,1.2,1.45,1.45]),atol=1e-15)
 assert np.array_equal(b,np.array([.01,.01,0,0,0,0]));grid=np.linspace(0,1,10001);ss,bb=profiles(grid,C);assert np.all(np.diff(ss)>=-1e-15) and np.all(np.diff(bb)<=1e-15)
 # Independent scalar implementation verifies both branches and all transition endpoints.
 def scalar(v):
  u=min(1,max(0,(v-C['left_fraction'])/(C['shoulder_fraction']-C['left_fraction'])));t=min(1,max(0,(v-C['shoulder_fraction'])/(C['right_fraction']-C['shoulder_fraction'])));q=min(1,max(0,(v-C['left_fraction'])/(.5-C['left_fraction'])))
  return .8*(4/7+(1.2-4/7)*(3*u*u-2*u*u*u)+.25*t),.01*(1-3*q*q+2*q*q*q)
 independent=np.array([scalar(v) for v in grid]);assert np.max(abs(independent[:,0]-ss))<1e-14 and np.max(abs(independent[:,1]-bb))<1e-14
 save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),fractions=x.tolist(),scales=s.tolist(),reduction=b.tolist(),scalar_controls=10001))
 for rec in json.loads((OLD/'integration.json').read_text()):
  member=rec['member'];center=np.array(rec['center']);meta=json.loads((B.parent/'miniplayer-outline-taper-107'/f'{member}-a-metrics.json').read_text());crop=meta['crop'];coordinate=replace(working_contour(member),counter=charge);levels={}
  for order in P['orders']:
   levels[order]=integrate(crop,coordinate,center,F['material']['outline']['angular'],C,order,charge);np.savez_compressed(B/f'{member}-order{order}.npz',moments=levels[order]);save('ledger.json',ledger);print(member,order,flush=True)
  diff=np.max(abs(levels[16]-levels[32]),axis=0);selected=diff>P['maximum_order_difference']/4;assert selected.sum()<=P['maximum_refined_pixels'];fine={}
  for order in P['refinement_orders']:
   fine[order]=integrate(crop,coordinate,center,F['material']['outline']['angular'],C,order,charge,pixel_mask=selected);np.savez_compressed(B/f'{member}-restricted{order}.npz',moments=fine[order],selected=selected);save('ledger.json',ledger)
  error=float(np.max(abs(fine[64][:,selected]-fine[96][:,selected]))) if selected.any() else 0;assert error<=P['maximum_order_difference'];out=levels[32];out[:,selected]=fine[96][:,selected];np.savez_compressed(B/f'{member}-moments.npz',alpha=out[0],reduction=out[1]);results.append(dict(member=member,center=center.tolist(),refined_pixels=int(selected.sum()),coarse_max=float(diff[~selected].max()),refined_max=error));save('integration.json',results);print('PASS',member,error,flush=True)
 assert hashes=={p:sha(R/p) for p in hashes};save('integration-finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_optical_rays=0))
except Exception as e:save('failure.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
finally:save('ledger.json',ledger)
