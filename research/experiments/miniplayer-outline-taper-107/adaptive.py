"""One tapered, hue-preserving outline on the frozen106 body."""
from pathlib import Path
from dataclasses import replace
import json,datetime,hashlib,importlib.util,zipfile,traceback,colorsys
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from PIL import Image
from music_miniplayer_family import working_artwork_study,working_center,working_contour
from miniplayer_artwork_adjustment import resize_and_center_artwork
from miniplayer_anchor_color import outline_endpoint,adjusted_outline_endpoint
from miniplayer_outline_taper import transition,integrate_taper,compose
B=Path(__file__).resolve().parent;R=B.parents[2];PREV=B.parent/'miniplayer-yellow-match-106';WHITE=B.parent/'miniplayer-final-white-105';OLD=B.parent/'miniplayer-three-pass-101'
P=json.loads((B/'adaptive-protocol.json').read_text());CAL=json.loads((B/'calibration.json').read_text());CAL0=json.loads((PREV/'calibration.json').read_text());F=json.loads((B/'frozen-family.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=json.loads((B/'interrupted-refinement-ledger.json').read_text());first={};rows=[]
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
    N=z['neutral'];V=1/(1+np.exp(-(np.log(N/(1-N))+s*z['value_logit_offset'])));s*=z['saturation_multiplier'];return np.array([colorsys.hsv_to_rgb(*a) for a in zip(h,s,V)])
save('adaptive-started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=P['deadline']))
try:
    for p in [Path(__file__),B/'adaptive-protocol.json',B/'calibration.json',B/'frozen-family.json',PREV/'calibration.json',R/'reconstruction/miniplayer_outline_taper.py',R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/miniplayer_artwork_adjustment.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/shoulder_core_coordinate.py',R/'reconstruction/outline_response.py',R/'reconstruction/extended_fit.py',R/'reconstruction/families/music-mini-player-working.json',OLD/'material_common.py']:
        first[str(p.relative_to(R))]=sha(p)
    assert F==json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text())
    assert CAL['roles']==CAL0['roles'] and 'outline_hue_adjustment' not in CAL
    assert json.loads((B/'checkpoint.json').read_text())['hue_preserved']
    spec=importlib.util.spec_from_file_location('render107shared',OLD/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=OLD/'native-pass2-resumed';data=c.load_data(charge,first);score=c.metric_functions(charge)['score'];identities=[]
    for (m,r),d in data.items():
        s=d['s'];H,W=s.valid.shape;cy=float(working_center(d['center'])[1]);d['alpha']=read(WHITE/f'{m}-alpha32.npz',['alpha'])['alpha'];d['raw']=read(OLD/f'pass2/{m}-{r}-blur6.6825-samples.npz',['raw_source'])['raw_source'];d['old']=read(PREV/f'{m}-{r}-candidate.npz',['complete','body']);d['pre']=read(WHITE/f'{m}-{r}-candidate.npz',['pre_foreground'])['pre_foreground'];d['old_scores']=json.loads((PREV/f'{m}-{r}-metrics.json').read_text())['scores']
        charge('artwork_pixels',sum(round((box[2]-box[0])*.95)*round((box[3]-box[1])*.95) for box,_,_ in s.foreground_layers if tuple(box) in s.artwork_layers));fg=working_artwork_study(s)
        for factor in [.986,1.0183]:
            box=next(box for box,_,_ in fg.foreground_layers if tuple(box) in fg.artwork_layers);charge('artwork_pixels',round((box[2]-box[0])*factor)*round((box[3]-box[1])*factor));fg,_=resize_and_center_artwork(fg,factor,cy,18)
        d['fg']=fg;charge('foreground_applications',2);body=fg.apply_foreground(d['pre'].copy());rawmean=d['raw'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);d['guide']=fg.apply_foreground(rawmean.copy());assert np.array_equal(body,d['old']['body'],equal_nan=True)
    print('BASELINE CHECKPOINT REUSED',flush=True)
    alphas={};integration=[]
    for m in ['expanded','compact']:
        d=data[(m,'a')];coord=replace(working_contour(m),counter=charge);levels={}
        for order in [16,32]:
            if m=='expanded':
                cached=read(B/f'{m}-moments{order}.npz',['alpha','reduction']);levels[order]=np.stack([cached['alpha'],cached['reduction']])
            else:
                levels[order]=integrate_taper(d['s'].crop,coord,working_center(d['center']),F['material']['outline']['angular'],P,order,charge)
                np.savez_compressed(B/f'{m}-moments{order}.npz',alpha=levels[order][0],reduction=levels[order][1])
            save('ledger.json',ledger);print('BASE MOMENTS',m,order,flush=True)
        diff=np.max(abs(levels[16]-levels[32]),axis=0);selected=diff>P['maximum_order_difference']/4;assert selected.sum()<=P['maximum_refined_pixels'];print('REFINE PIXELS',m,int(selected.sum()),flush=True)
        for order in [64,96]:
            levels[order]=integrate_taper(d['s'].crop,coord,working_center(d['center']),F['material']['outline']['angular'],P,order,charge,pixel_mask=selected)
            np.savez_compressed(B/f'{m}-restricted{order}.npz',alpha=levels[order][0],reduction=levels[order][1],selected=selected);save('ledger.json',ledger)
        fine=float(np.max(abs(levels[64][:,selected]-levels[96][:,selected]))) if selected.any() else 0.
        coarse=float(diff[~selected].max());assert fine<=P['maximum_order_difference']
        moments=levels[32].copy();moments[:,selected]=levels[96][:,selected];alphas[m]=moments
        integration.append(dict(member=m,initial16_32_difference=float(diff.max()),refined_pixels=int(selected.sum()),coarse_maximum_difference=coarse,refined64_96_difference=fine,maximum_difference=max(fine,coarse),all_pixels_retained=True))
        save('integration.json',integration);np.savez_compressed(B/f'{m}-adaptive-moments.npz',alpha=moments[0],reduction=moments[1],refined=selected);print('INTEGRATION PASS',m,max(fine,coarse),flush=True)
    verification=[]
    for (m,r),d in data.items():
        s=d['s'];alpha,reduction=alphas[m];body=d['old']['body'];guide=d['guide'];active=alpha>0;charge('color_evaluations',int(active.sum()));ep=outline_endpoint(guide[active],CAL);C=compose(body,guide,ep,alpha,reduction);charge('candidate_composites',1)
        finite=np.isfinite(C);assert C[finite].min()>=0 and C[finite].max()<=1
        charge('color_evaluations',int(active.sum()));other=independent(guide[active]);hsv=np.array([colorsys.rgb_to_hsv(*x) for x in other]);fraction=reduction[active]/alpha[active];hsv[:,2]-=fraction*np.maximum(hsv[:,2]-guide[active].max(-1),0)
        effective=np.array([colorsys.hsv_to_rgb(*x) for x in hsv]);replay=body.copy();replay[active]=body[active]+alpha[active,None]*(effective-body[active]);charge('verification_composites',1);error=float(np.nanmax(abs(replay-C)));assert error<=P['maximum_replay_error'];assert np.array_equal(np.isnan(replay),np.isnan(C));assert np.array_equal(C[alpha==0],body[alpha==0],equal_nan=True)
        assert np.all(alpha[d['alpha']==0]==0)
        oldmeta=json.loads((PREV/f'{m}-{r}-metrics.json').read_text());metrics=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=m,reference=r,crop=list(s.crop),scores=metrics,previous106_scores=d['old_scores'],previous106_comparisons=c.guards(metrics,d['old_scores']),artwork_records=oldmeta['artwork_records'],clipped_channels=0);rows.append(row)
        verification.append(dict(member=m,reference=r,independent_endpoint_error=float(np.max(abs(ep-other))),independent_complete_error=error,unchanged_body_and_artwork=True,zero_gap_preserved=True,hue_preserved=True,convergence_max=integration[0 if m=='expanded' else 1]['maximum_difference']))
        np.savez_compressed(B/f'{m}-{r}-candidate.npz',complete=C,body=body,endpoint_active=ep);png(f'{m}-{r}-candidate.png',C);png(f'{m}-{r}-reference.png',s.target_crop);png(f'{m}-{r}-previous.png',d['old']['complete']);save(f'{m}-{r}-metrics.json',row);save('results.json',rows);save('verification.json',verification);save('ledger.json',ledger);print('CANDIDATE',m,r,metrics['E'],error,flush=True)
    assert first=={p:sha(R/p) for p in first};save('hashes.json',first);save('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_images=4,new_optical_rays=0,new_source_queries=0,new_fields=0,new_filters=0,selected_state_changed=False));print('COMPLETE',flush=True)
except Exception as e:save('adaptive-failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('ledger.json',ledger)
