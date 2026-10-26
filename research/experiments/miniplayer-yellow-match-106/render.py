"""Frozen-body outline endpoint and current-artwork enlargement, one pair per size."""
from pathlib import Path
import json,datetime,hashlib,importlib.util,zipfile,traceback,colorsys
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from PIL import Image
from music_miniplayer_family import working_artwork_study,working_center
from miniplayer_artwork_adjustment import resize_and_center_artwork
from miniplayer_anchor_color import outline_endpoint,adjusted_outline_endpoint
B=Path(__file__).resolve().parent;R=B.parents[2];PREV=B.parent/'miniplayer-final-white-105';OLD=B.parent/'miniplayer-three-pass-101';P=json.loads((B/'protocol.json').read_text());CAL=json.loads((B/'calibration.json').read_text());CAL0=json.loads((PREV/'calibration.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger={k:0 for k in P['caps'] if k not in ['calibration_scalar_points','control_colors']};first={};rows=[]
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
def png(n,v):Image.fromarray(np.rint(np.nan_to_num(v,nan=0)*255).astype(np.uint8)).save(B/n)
def independent(rgb):
    h,s,v=np.array([colorsys.rgb_to_hsv(*map(float,a)) for a in rgb]).T;role=CAL['roles']['outline'];z={}
    for k in ['neutral','saturation_multiplier','value_logit_offset']:
        q=role[k];z[k]=CubicHermiteSpline(q['x'],q['y'],q['slopes'])(np.clip(v,q['x'][0],q['x'][-1]))
    N=z['neutral'];V=1/(1+np.exp(-(np.log(N/(1-N))+s*z['value_logit_offset'])));adj=CAL['outline_hue_adjustment'];q=adj['offset_curve'];shift=CubicHermiteSpline(q['x'],q['y'],q['slopes'])(np.clip(v,q['x'][0],q['x'][-1]));delta=(h-adj['center_hue']+.5)%1-.5;w=np.where(abs(delta)<adj['half_width'],.5*(1+np.cos(np.pi*delta/adj['half_width'])),0.);h=(h+shift*w*(s>0))%1;s*=z['saturation_multiplier'];return np.array([colorsys.hsv_to_rgb(*a) for a in zip(h,s,V)])
save('started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=P['deadline']))
try:
    assert json.loads((B/'calibration-checkpoint.json').read_text())['passed']
    for p in [Path(__file__),B/'protocol.json',B/'calibration.json',R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/miniplayer_artwork_adjustment.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/extended_fit.py',R/'reconstruction/families/music-mini-player-working.json',PREV/'calibration.json',PREV/'body-controls.json',PREV/'artwork/results.json',OLD/'material_common.py']:
        first[str(p.relative_to(R))]=sha(p)
    spec=importlib.util.spec_from_file_location('render106shared',OLD/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=OLD/'native-pass2-resumed';data=c.load_data(charge,first);score=c.metric_functions(charge)['score'];identities=[]
    for (m,r),d in data.items():
        s=d['s'];H,W=s.valid.shape;cy=float(working_center(d['center'])[1]);d['alpha']=read(PREV/f'{m}-alpha32.npz',['alpha'])['alpha'];d['raw']=read(OLD/f'pass2/{m}-{r}-blur6.6825-samples.npz',['raw_source'])['raw_source'];d['old']=read(PREV/'artwork'/f'{m}-{r}-candidate.npz',['complete','body']);d['pre']=read(PREV/f'{m}-{r}-candidate.npz',['pre_foreground'])['pre_foreground'];d['old_scores']=json.loads((PREV/'artwork'/f'{m}-{r}-metrics.json').read_text())['scores'];charge('artwork_pixels',sum(round((box[2]-box[0])*.95)*round((box[3]-box[1])*.95) for box,_,_ in s.foreground_layers if tuple(box) in s.artwork_layers));base=working_artwork_study(s)
        boxes=[box for box,_,_ in base.foreground_layers if tuple(box) in base.artwork_layers];assert len(boxes)==1;a,b,c0,e=boxes[0];charge('artwork_pixels',round((c0-a)*.986)*round((e-b)*.986));d['fg'],_=resize_and_center_artwork(base,.986,cy,18)
        charge('foreground_applications',2);body=d['fg'].apply_foreground(d['pre'].copy());d['rawmean']=d['raw'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);d['guide']=d['fg'].apply_foreground(d['rawmean'].copy());assert np.array_equal(body,d['old']['body'],equal_nan=True);active=d['alpha']>0;charge('color_evaluations',int(active.sum()));endpoint=outline_endpoint(d['guide'][active],CAL0);identity=body.copy();identity[active]=body[active]+d['alpha'][active,None]*(endpoint-body[active]);charge('identity_composites',1);assert np.array_equal(identity,d['old']['complete'],equal_nan=True);assert score(s,identity,d['m'],d['partial'],d['crops'])==d['old_scores'];identities.append(dict(member=m,reference=r,body_exact=True,complete_exact=True,scores_exact=True))
    assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline']);save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),identities=identities));print('CHECKPOINT PASS',flush=True)
    verification=[]
    for (m,r),d in data.items():
        s=d['s'];H,W=s.valid.shape;cy=float(working_center(d['center'])[1]);box=next(box for box,_,_ in d['fg'].foreground_layers if tuple(box) in d['fg'].artwork_layers);charge('artwork_pixels',round((box[2]-box[0])*P['artwork_factor'])*round((box[3]-box[1])*P['artwork_factor']));fg,records=resize_and_center_artwork(d['fg'],P['artwork_factor'],cy,18);x0,y0,_,_=s.crop;union=np.zeros((H,W),bool)
        for record in records:
            assert record['old_center_x']==record['new_center_x'];assert (record['old_box'][1]+record['old_box'][3]-1)/2==record['realized_center_y']
            for a,b,c0,e in [record['old_box'],record['new_box']]:union[b-y0:e-y0,a-x0:c0-x0]=True
        alpha=d['alpha'];assert np.all(alpha[union]==0);charge('foreground_applications',2);body=fg.apply_foreground(d['pre'].copy());guide=fg.apply_foreground(d['rawmean'].copy());assert np.array_equal(body[~union],d['old']['body'][~union],equal_nan=True);assert np.array_equal(guide[~union],d['guide'][~union],equal_nan=True)
        active=alpha>0;charge('color_evaluations',int(active.sum()));endpoint=adjusted_outline_endpoint(guide[active],CAL);C=body.copy();C[active]=body[active]+alpha[active,None]*(endpoint-body[active]);charge('candidate_composites',1);finite=np.isfinite(C);assert C[finite].min()>=0 and C[finite].max()<=1
        # Manual foreground-layer replay and independent scalar HSV endpoint.
        body2=d['old']['body'].copy();body2[union]=d['pre'][union]
        for box,a,color in fg.foreground_layers:
            if tuple(box) not in fg.artwork_layers:continue
            l,t,right,bottom=box;region=body2[t-y0:bottom-y0,l-x0:right-x0];region[:]=region*(1-a[...,None])+color*a[...,None]
        assert np.array_equal(body2,body,equal_nan=True);charge('color_evaluations',int(active.sum()));other=independent(guide[active]);replay=body2.copy();replay[active]=body2[active]+alpha[active,None]*(other-body2[active]);charge('verification_composites',1);error=float(np.nanmax(abs(replay-C)));assert error<=P['maximum_replay_error'];assert np.array_equal(np.isnan(replay),np.isnan(C));assert np.array_equal(C[(alpha==0)&~union],d['old']['complete'][(alpha==0)&~union],equal_nan=True)
        metrics=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=m,reference=r,crop=list(s.crop),scores=metrics,previous105_scores=d['old_scores'],previous105_comparisons=c.guards(metrics,d['old_scores']),artwork_records=records,clipped_channels=0);rows.append(row);verification.append(dict(member=m,reference=r,independent_endpoint_error=float(np.max(abs(endpoint-other))),independent_complete_error=error,body_exact_outside_artwork=True,artwork_manual_replay_exact=True,centers_exact=True,unchanged_alpha=True,unchanged_body_grade_and_optics=True))
        np.savez_compressed(B/f'{m}-{r}-candidate.npz',complete=C,body=body,endpoint_active=endpoint);png(f'{m}-{r}-candidate.png',C);png(f'{m}-{r}-reference.png',s.target_crop);png(f'{m}-{r}-previous.png',d['old']['complete']);save(f'{m}-{r}-metrics.json',row);save('results.json',rows);save('verification.json',verification);save('ledger.json',ledger);print('CANDIDATE',m,r,metrics['E'],error,records,flush=True)
    assert first=={p:sha(R/p) for p in first};save('hashes.json',first);save('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_images=4,new_optical_rays=0,new_source_queries=0,new_fields=0,new_filters=0,new_quadrature=0,selected_state_changed=False));print('COMPLETE',flush=True)
except Exception as e:save('failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('ledger.json',ledger)
