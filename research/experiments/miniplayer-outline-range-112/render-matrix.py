from pathlib import Path
import json,hashlib,datetime,colorsys,traceback
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from PIL import Image
from miniplayer_anchor_color import outline_endpoint,outline_display_endpoint
from miniplayer_outline_taper import compose
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-outline-options-111';BODY=B.parent/'miniplayer-outline-value-110';RAW=B.parent/'miniplayer-three-pass-101/pass2';G=B.parent/'miniplayer-outline-taper-107';P=json.loads((B/'two-axis-protocol.json').read_text());BASE=json.loads((OLD/'step5-calibration.json').read_text());hashes={};decoded=0;rows=[]
def read(p,keys):
 global decoded
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with np.load(p) as z:a={k:z[k] for k in keys}
 decoded+=sum(v.nbytes for v in a.values());assert decoded<=P['numeric_byte_cap'];return a
def png(n,x):Image.fromarray(np.rint(np.nan_to_num(x,nan=0)*255).astype(np.uint8)).save(B/n)
for p in [Path(__file__),B/'two-axis-protocol.json',OLD/'step5-calibration.json',R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/miniplayer_outline_taper.py']:
 hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
calibrations=[BASE]
for i in range(1,11):
 p=B/f'step{i}-calibration.json';hashes[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest();calibrations.append(json.loads(p.read_text()))
identities=[]
try:
 assert (B/'integration-finished.json').exists()
 for m in ['expanded','compact']:
  cached=read(B/f'{m}-width-moments.npz',['moments','affected']);moments=cached['moments'];affected=cached['affected'];H,W=moments.shape[-2:]
  for r in ['a','b']:
   case=f'{m}-{r}';old=read(OLD/f'{case}-step5.npz',['complete','endpoint_active']);body=read(BODY/f'{case}-candidate.npz',['body'])['body'];raw=read(RAW/f'{case}-blur6.6825-samples.npz',['raw_source'])['raw_source'];guide=raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);basealpha,basereduction=moments[0];baseactive=basealpha>0;baseline=outline_display_endpoint(guide[baseactive],BASE);assert np.array_equal(baseline,old['endpoint_active']);identity=compose(body,guide,baseline,basealpha,basereduction);assert np.array_equal(identity,old['complete'],equal_nan=True);identities.append(case)
   union=moments[:,0].max(0)>0;g=guide[union];assert np.isfinite(g).all();plain=outline_endpoint(g,BASE);hsv0=np.array([colorsys.rgb_to_hsv(*x) for x in plain]);ghsv=np.array([colorsys.rgb_to_hsv(*map(float,x)) for x in g]);v=ghsv[:,2];q=BASE['outline_hue_adjustment']['offset_curve'];offset=CubicHermiteSpline(q['x'],q['y'],q['slopes'])(np.clip(v,q['x'][0],q['x'][-1]));adj=BASE['outline_hue_adjustment'];distance=(ghsv[:,0]-adj['center_hue']+.5)%1-.5;weight=np.where(abs(distance)<adj['half_width'],.5*(1+np.cos(np.pi*distance/adj['half_width'])),0)
   for color,cal in enumerate(calibrations):
    ep=outline_display_endpoint(g,cal);hsv=hsv0.copy();hsv[:,1]*=P['saturation_step']**color;hsv[:,0]=(hsv[:,0]+offset*(P['hue_shift_step']**color)*weight*(ghsv[:,1]>0))%1;hsv[:,2]=np.minimum(hsv[:,2]+BASE['outline_value_lift']+P['value_step']*color,1);other=np.array([colorsys.hsv_to_rgb(*x) for x in hsv]);assert np.max(abs(other-ep))<1e-7
    endpoint=np.zeros_like(body,dtype=float);endpoint[union]=ep;independent=np.zeros_like(endpoint);independent[union]=other
    for width,(alpha,reduction) in enumerate(moments):
     active=alpha>0;out=compose(body,guide,endpoint[active],alpha,reduction);replay=compose(body,guide,independent[active],alpha,reduction);error=float(np.nanmax(abs(replay-out)));assert error<=P['replay_tolerance'];assert np.array_equal(out[~active],body[~active],equal_nan=True);finite=np.isfinite(out);assert out[finite].min()>=0 and out[finite].max()<=1
     if width==0:left_control=out[~affected].copy()
     else:assert np.array_equal(out[~affected],left_control,equal_nan=True)
     if color==0 and width==0:assert np.array_equal(out,old['complete'],equal_nan=True)
     np.savez_compressed(B/f'{case}-c{color}-w{width}.npz',complete=out);png(f'{case}-c{color}-w{width}.png',out);rows.append(dict(case=case,color=chr(65+color),color_index=color,nonleft_thickness=int(round(P['widths'][width]*100)),width_index=width,replay_error=error,unchanged_body=True,value_ceiling_count=int((endpoint[active].max(-1)==1).sum())));print(case,chr(65+color),int(P['widths'][width]*100),error,flush=True)
   (B/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
 assert hashes=={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in hashes};assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'])
 for n,x in [('hashes.json',hashes),('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),numeric_bytes=decoded,matrix_outputs=220,new_candidates=216,independent_replays=220,baseline_identities=identities,prior_color_only_candidates=3,new_rays=0,new_filters=0,new_scores=0))]:(B/n).write_text(json.dumps(x,indent=2)+'\n')
except Exception as e:(B/'matrix-failure.json').write_text(json.dumps(dict(error=repr(e),traceback=traceback.format_exc(),completed_outputs=len(rows)),indent=2)+'\n');raise
