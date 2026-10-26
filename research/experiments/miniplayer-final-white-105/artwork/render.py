"""User-requested artwork-only update of the preserved color/rim candidate."""
from pathlib import Path
import json,datetime,hashlib,importlib.util,zipfile,traceback
import numpy as np
from PIL import Image
from music_miniplayer_family import working_artwork_study,working_center
from miniplayer_artwork_adjustment import resize_and_center_artwork
B=Path(__file__).resolve().parent;PARENT=B.parent;R=B.parents[3];OLD=PARENT.parent/'miniplayer-three-pass-101';P=json.loads((B/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={};rows=[]
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def charge(k,n):
    assert datetime.datetime.now(datetime.timezone.utc)<END;assert ledger[k]+n<=P['caps'][k],(k,n,ledger[k]);ledger[k]+=int(n)
    if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def read(p,keys):
    first[str(p.relative_to(R))]=sha(p)
    with zipfile.ZipFile(p) as z:
        for k in keys:
            with z.open(k+'.npy') as f:
                v=np.lib.format.read_magic(f);shape,_,dt=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f);assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
    with np.load(p) as z:return {k:z[k] for k in keys}
def png(p,v):Image.fromarray(np.rint(np.nan_to_num(v,nan=0)*255).astype(np.uint8)).save(p)
save('started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=P['deadline']))
try:
    assert (PARENT/'finished.json').exists()
    for p in [Path(__file__),B/'protocol.json',R/'reconstruction/miniplayer_artwork_adjustment.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/extended_fit.py',R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/families/music-mini-player-working.json',OLD/'material_common.py',PARENT/'hashes.json']:
        first[str(p.relative_to(R))]=sha(p)
    spec=importlib.util.spec_from_file_location('art105',OLD/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=OLD/'native-pass2-resumed';data=c.load_data(charge,first);score=c.metric_functions(charge)['score'];verifications=[]
    for (m,r),d in data.items():
        s=d['s'];H,W=s.valid.shape;z=read(PARENT/f'{m}-{r}-candidate.npz',['complete','pre_foreground','body']);alpha=read(PARENT/f'{m}-alpha32.npz',['alpha'])['alpha'];charge('artwork_pixels',sum(round((box[2]-box[0])*.95)*round((box[3]-box[1])*.95) for box,_,_ in s.foreground_layers if tuple(box) in s.artwork_layers));old=working_artwork_study(s);cy=float(working_center(d['center'])[1]);boxes=[box for box,_,_ in old.foreground_layers if tuple(box) in old.artwork_layers];assert len(boxes)==1
        box=boxes[0];oldcy=(box[1]+box[3]-1)/2;charge('artwork_pixels',(box[2]-box[0])*(box[3]-box[1]));zero,_=resize_and_center_artwork(old,1.,oldcy,P['radius']);charge('composites',1);identity=zero.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(identity,z['body'],equal_nan=True)
        prior=json.loads((PARENT/f'{m}-{r}-metrics.json').read_text());assert score(s,z['complete'],d['m'],d['partial'],d['crops'])==prior['scores']
        charge('artwork_pixels',round((box[2]-box[0])*P['factor'])*round((box[3]-box[1])*P['factor']));updated,records=resize_and_center_artwork(old,P['factor'],cy,P['radius']);x0,y0,_,_=s.crop;union=np.zeros((H,W),bool)
        for record in records:
            assert record['old_center_x']==record['new_center_x'];assert abs(record['realized_center_y']-cy)<=.5
            for a,b,c0,e in [record['old_box'],record['new_box']]:union[b-y0:e-y0,a-x0:c0-x0]=True
        assert np.all(alpha[union]==0)
        charge('composites',1);body=updated.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(body[~union],z['body'][~union],equal_nan=True);C=z['complete'].copy();C[union]=body[union];assert np.array_equal(C[~union],z['complete'][~union],equal_nan=True)
        # Independently restore the uncovered old footprint, then composite only the new artwork layer.
        replay=z['complete'].copy();replay[union]=z['pre_foreground'][union]
        for box,a,color in updated.foreground_layers:
            if tuple(box) not in updated.artwork_layers:continue
            l,t,right,bottom=box;region=replay[t-y0:bottom-y0,l-x0:right-x0];region[:]=region*(1-a[...,None])+color*a[...,None]
        charge('composites',1);assert np.array_equal(replay,C,equal_nan=True)
        metrics=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=m,reference=r,crop=list(s.crop),scores=metrics,previous104_scores=prior['previous104_scores'],previous104_comparisons=c.guards(metrics,prior['previous104_scores']),before_artwork_scores=prior['scores'],artwork_records=records,clipped_channels=0);rows.append(row)
        np.savez_compressed(B/f'{m}-{r}-candidate.npz',complete=C,body=body);png(B/f'{m}-{r}-candidate.png',C);save(f'{m}-{r}-metrics.json',row);verifications.append(dict(member=m,reference=r,zero_exact=True,manual_layer_replay_exact=True,outside_artwork_union_exact=True,outline_zero_over_artwork_union=True,horizontal_center_exact=True,maximum_vertical_rounding=max(abs(x['realized_center_y']-cy) for x in records)))
        save('results.json',rows);save('verification.json',verifications);save('ledger.json',ledger);print('ARTWORK',m,r,records,metrics['E'],flush=True)
    assert first=={p:sha(R/p) for p in first};save('hashes.json',first);save('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidates=4,new_optics=0,new_source_queries=0,new_filters=0));print('ARTWORK COMPLETE',flush=True)
except Exception as e:save('failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('ledger.json',ledger)
