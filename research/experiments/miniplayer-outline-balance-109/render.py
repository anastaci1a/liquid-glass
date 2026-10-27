from pathlib import Path
import json,hashlib,datetime,colorsys
import numpy as np
from PIL import Image
from scipy.interpolate import CubicHermiteSpline
from miniplayer_anchor_color import outline_endpoint,adjusted_outline_endpoint
from miniplayer_outline_taper import compose
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-restored-yellow-108';GEOM=B.parent/'miniplayer-outline-taper-107';RAW=B.parent/'miniplayer-three-pass-101'/'pass2';CAL=json.loads((B/'calibration.json').read_text());CAL0=json.loads((OLD/'calibration.json').read_text());P=json.loads((B/'protocol.json').read_text());hashes={};rows=[];decoded=0

def read(p,keys):
 global decoded
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p) as z:
  result={k:z[k] for k in keys}
 decoded+=sum(x.nbytes for x in result.values());assert decoded<=P['numeric_byte_cap'];return result

def png(n,v):Image.fromarray(np.rint(np.nan_to_num(v,nan=0)*255).astype(np.uint8)).save(B/n)
for p in [Path(__file__),B/'calibration.json',OLD/'calibration.json',R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/miniplayer_outline_taper.py']:
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
for m in ['expanded','compact']:
 moments=read(GEOM/f'{m}-adaptive-moments.npz',['alpha','reduction']);alpha=moments['alpha'];reduction=moments['reduction'];active=alpha>0;H,W=alpha.shape
 for r in ['a','b']:
  case=f'{m}-{r}';old=read(OLD/f'{case}-candidate.npz',['complete','body','endpoint_active']);raw=read(RAW/f'{case}-blur6.6825-samples.npz',['raw_source'])['raw_source'];guide=raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  baseline=adjusted_outline_endpoint(guide[active],CAL0);assert np.array_equal(baseline,old['endpoint_active']);identity=compose(old['body'],guide,baseline,alpha,reduction);plain=outline_endpoint(guide[active],CAL0);assert np.array_equal(identity,old['complete'],equal_nan=True)
  ep=adjusted_outline_endpoint(guide[active],CAL);out=compose(old['body'],guide,ep,alpha,reduction)
  adj=CAL['outline_hue_adjustment'];q=adj['offset_curve'];g=guide[active];ghsv=np.array([colorsys.rgb_to_hsv(*x) for x in g]);ehsv=np.array([colorsys.rgb_to_hsv(*x) for x in plain]);ehsv[:,1]*=.98;v=ghsv[:,2];offset=CubicHermiteSpline(q['x'],q['y'],q['slopes'])(np.clip(v,q['x'][0],q['x'][-1]));dist=(ghsv[:,0]-adj['center_hue']+.5)%1-.5;weight=np.where(abs(dist)<adj['half_width'],.5*(1+np.cos(np.pi*dist/adj['half_width'])),0);ehsv[:,0]=(ehsv[:,0]+offset*weight*(ghsv[:,1]>0))%1;other=np.array([colorsys.hsv_to_rgb(*x) for x in ehsv]);assert np.max(abs(ep-other))<1e-7
  replay=compose(old['body'],guide,other,alpha,reduction);error=float(np.nanmax(abs(replay-out)));assert error<=1e-7;assert np.array_equal(out[~active],old['complete'][~active],equal_nan=True)
  finite=np.isfinite(out);assert out[finite].min()>=0 and out[finite].max()<=1
  np.savez_compressed(B/f'{case}-candidate.npz',complete=out,body=old['body'],endpoint_active=ep);png(f'{case}-candidate.png',out);png(f'{case}-previous.png',old['complete']);(B/f'{case}-reference.png').write_bytes((OLD/f'{case}-reference.png').read_bytes())
  row=json.loads((GEOM/f'{case}-metrics.json').read_text());rows.append(dict(member=m,reference=r,crop=row['crop'],artwork_records=row['artwork_records'],identity_exact=True,raw_guide_endpoint_exact=True,replay_maximum_error=error,body_unchanged=True,clipped_channels=0));print(case,error,flush=True)
probe=np.array([[235,206,72]],float)/255;anchor=adjusted_outline_endpoint(probe,CAL);assert abs(anchor.max()*255-246)<1e-10
assert hashes=={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in hashes};assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'])
for n,v in [('results.json',rows),('hashes.json',hashes),('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),numeric_bytes=decoded,candidates=4,identity_controls=4,independent_replays=4,new_quadrature=0,new_rays=0,new_filters=0,new_scores=0,anchor_rgb=(anchor*255).tolist()))]:(B/n).write_text(json.dumps(v,indent=2)+'\n')
