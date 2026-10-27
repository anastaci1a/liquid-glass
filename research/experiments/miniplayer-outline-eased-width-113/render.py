from pathlib import Path
import json,hashlib,datetime,traceback
import numpy as np
from PIL import Image
from miniplayer_anchor_color import outline_display_endpoint
from miniplayer_outline_taper import compose
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-outline-range-112';BODY=B.parent/'miniplayer-outline-value-110';RAW=B.parent/'miniplayer-three-pass-101/pass2';P=json.loads((B/'protocol.json').read_text());cal=json.loads((OLD/'step1-calibration.json').read_text());hashes={};decoded=0;rows=[]
def read(p,keys):
 global decoded
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p) as z:a={k:z[k] for k in keys}
 decoded+=sum(x.nbytes for x in a.values());assert decoded<=P['numeric_byte_cap'];return a
def save(n,x):(B/n).write_text(json.dumps(x,indent=2)+'\n')
for p in [Path(__file__),OLD/'step1-calibration.json',R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/miniplayer_outline_taper.py']:hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
try:
 assert (B/'integration-finished.json').exists()
 for member in ['expanded','compact']:
  oldmom=read(OLD/f'{member}-width-moments.npz',['moments'])['moments'][1];mom=read(B/f'{member}-moments.npz',['alpha','reduction']);alpha,reduction=mom['alpha'],mom['reduction'];H,W=alpha.shape
  for ref in ['a','b']:
   case=f'{member}-{ref}';body=read(BODY/f'{case}-candidate.npz',['body'])['body'];raw=read(RAW/f'{case}-blur6.6825-samples.npz',['raw_source'])['raw_source'];guide=raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);baseline=read(OLD/f'{case}-c1-w1.npz',['complete'])['complete'];a,r=oldmom
   identity=compose(body,guide,outline_display_endpoint(guide[a>0],cal),a,r);assert np.array_equal(identity,baseline,equal_nan=True)
   active=alpha>0;assert np.isfinite(guide[active]).all();endpoint=outline_display_endpoint(guide[active],cal);out=compose(body,guide,endpoint,alpha,reduction)
   # Independent expanded scalar composition, including the positive-lift-only reduction.
   peak=np.max(endpoint,axis=1);lift=np.maximum(peak-np.max(guide[active],axis=1),0);replay=body.copy()
   for channel in range(3):replay[:,:,channel][active]=body[:,:,channel][active]+alpha[active]*(endpoint[:,channel]-body[:,:,channel][active])-reduction[active]*lift*endpoint[:,channel]/np.where(peak>0,peak,1)
   error=float(np.nanmax(abs(out-replay)));assert error<=1e-7;assert np.array_equal(out[~active],body[~active],equal_nan=True);assert out[np.isfinite(out)].min()>=0 and out[np.isfinite(out)].max()<=1
   np.savez_compressed(B/f'{case}-candidate.npz',complete=out,endpoint_active=endpoint)
   Image.fromarray(np.rint(np.nan_to_num(out,nan=0)*255).astype(np.uint8)).save(B/f'{case}-candidate.png')
   rows.append(dict(case=case,baseline_identity=True,independent_error=error,finite_guide=True,changed_pixels=int(np.any(out!=baseline,axis=-1)[np.isfinite(out).all(-1)].sum()),value_ceiling_count=int((peak==1).sum())));save('results.json',rows);print(case,error,flush=True)
 assert hashes=={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in hashes};assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline']);save('render-hashes.json',hashes);save('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),numeric_bytes=decoded,candidates=4,identities=4,independent_replays=4,new_rays=0,new_filters=0,new_scores=0))
except Exception as e:save('render-failure.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
