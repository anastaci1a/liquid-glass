from pathlib import Path
import json,hashlib,datetime,colorsys
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from PIL import Image
from miniplayer_anchor_color import outline_endpoint,outline_display_endpoint
from miniplayer_outline_taper import compose
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-outline-options-111';BODY=B.parent/'miniplayer-outline-value-110';G=B.parent/'miniplayer-outline-taper-107';RAW=B.parent/'miniplayer-three-pass-101/pass2'
P=json.loads((B/'protocol.json').read_text());BASE=json.loads((OLD/'step5-calibration.json').read_text());hashes={};decoded=0;rows=[]
def read(p,keys):
 global decoded
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p) as z:a={k:z[k] for k in keys}
 decoded+=sum(v.nbytes for v in a.values());assert decoded<=P['numeric_byte_cap'];return a
def png(n,x):Image.fromarray(np.rint(np.nan_to_num(x,nan=0)*255).astype(np.uint8)).save(B/n)
for p in [Path(__file__),B/'protocol.json',OLD/'step5-calibration.json',R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/miniplayer_outline_taper.py']:
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
calibrations=[]
for i in range(1,11):
 p=B/f'step{i}-calibration.json';hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest();calibrations.append(json.loads(p.read_text()))
identities=[]
for m in ['expanded','compact']:
 z=read(G/f'{m}-adaptive-moments.npz',['alpha','reduction']);alpha=z['alpha'];reduction=z['reduction'];active=alpha>0;H,W=alpha.shape
 for r in ['a','b']:
  case=f'{m}-{r}';old=read(OLD/f'{case}-step5.npz',['complete','endpoint_active']);old['body']=read(BODY/f'{case}-candidate.npz',['body'])['body'];raw=read(RAW/f'{case}-blur6.6825-samples.npz',['raw_source'])['raw_source'];guide=raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  base=outline_display_endpoint(guide[active],BASE);assert np.array_equal(base,old['endpoint_active']);assert np.array_equal(compose(old['body'],guide,base,alpha,reduction),old['complete'],equal_nan=True);identities.append(case)
  plain=outline_endpoint(guide[active],BASE);hsv0=np.array([colorsys.rgb_to_hsv(*x) for x in plain]);g=guide[active];ghsv=np.array([colorsys.rgb_to_hsv(*map(float,x)) for x in g]);v=ghsv[:,2];q=BASE['outline_hue_adjustment']['offset_curve'];offset=CubicHermiteSpline(q['x'],q['y'],q['slopes'])(np.clip(v,q['x'][0],q['x'][-1]));adj=BASE['outline_hue_adjustment'];distance=(ghsv[:,0]-adj['center_hue']+.5)%1-.5;weight=np.where(abs(distance)<adj['half_width'],.5*(1+np.cos(np.pi*distance/adj['half_width'])),0)
  for i,cal in enumerate(calibrations,1):
   ep=outline_display_endpoint(g,cal);out=compose(old['body'],guide,ep,alpha,reduction);hsv=hsv0.copy();hsv[:,1]*=P['saturation_step']**i;hsv[:,0]=(hsv[:,0]+offset*(P['hue_shift_step']**i)*weight*(ghsv[:,1]>0))%1;hsv[:,2]=np.minimum(hsv[:,2]+BASE['outline_value_lift']+P['value_step']*i,1);other=np.array([colorsys.hsv_to_rgb(*x) for x in hsv]);assert np.max(abs(other-ep))<1e-7
   replay=compose(old['body'],guide,other,alpha,reduction);error=float(np.nanmax(abs(replay-out)));assert error<=P['replay_tolerance'];assert np.array_equal(out[~active],old['complete'][~active],equal_nan=True);finite=np.isfinite(out);assert out[finite].min()>=0 and out[finite].max()<=1
   np.savez_compressed(B/f'{case}-step{i}.npz',complete=out,endpoint_active=ep);png(f'{case}-step{i}.png',out);rows.append(dict(case=case,step=i,replay_error=error,unchanged_body=True,value_ceiling_count=int((ep.max(-1)==1).sum())));print(case,i,error,flush=True)
assert hashes=={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in hashes};assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'])
for n,x in [('results.json',rows),('hashes.json',hashes),('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),numeric_bytes=decoded,candidates=40,independent_replays=40,baseline_identities=identities,new_rays=0,new_quadrature=0,new_filters=0,new_scores=0))]:(B/n).write_text(json.dumps(x,indent=2)+'\n')
