"""Frozen-path, five-option display experiment with durable accounting."""
from pathlib import Path
import json,datetime,hashlib,importlib.util,zipfile,traceback,colorsys
import numpy as np
import cv2
from dataclasses import replace
from PIL import Image
from response import body_grade,endpoint,overlay,VALUE
from music_miniplayer_family import working_contour,working_center,working_composite,working_artwork_study
from miniplayer_refinement_effects import integrate_rims
from environment_radiance import decode_srgb,encode_srgb,annular_environment

B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-three-pass-101';P=OLD/'pass2'
protocol=json.loads((B/'protocol.json').read_text());F=json.loads((B/'frozen-family.json').read_text());end=datetime.datetime.fromisoformat(protocol['deadline'])
ledger=dict.fromkeys(protocol['caps'],0);first={};rows=[];cv2.setNumThreads(1)
def clean(v):
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
    if isinstance(v,list):return [clean(x) for x in v]
    return None if isinstance(v,float) and not np.isfinite(v) else v
def save(name,v):(B/name).write_text(json.dumps(clean(v),indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def charge(k,n):
    assert datetime.datetime.now(datetime.timezone.utc)<end
    assert ledger[k]+n<=protocol['caps'][k],(k,n,ledger[k])
    ledger[k]+=int(n)
    if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def read(p,keys):
    first[str(p.relative_to(R))]=sha(p)
    with zipfile.ZipFile(p) as z:
        for k in keys:
            with z.open(k+'.npy') as f:
                v=np.lib.format.read_magic(f);shape,_,dtype=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f)
                assert not dtype.hasobject;charge('numeric_bytes',int(np.prod(shape))*dtype.itemsize)
    with np.load(p) as z:return {k:z[k] for k in keys}
def png(p,v):Image.fromarray(np.rint(np.clip(np.nan_to_num(v,nan=0),0,1)*255).astype(np.uint8)).save(p)

save('started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),protocol=protocol))
try:
    for p in [B/'run.py',B/'response.py',R/'reconstruction/families/music-mini-player-working.json',R/F['geometry']['back_profile'],R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/miniplayer_color_refinement.py',R/'reconstruction/shoulder_core_coordinate.py',R/'reconstruction/outline_response.py',R/'reconstruction/environment_radiance.py',OLD/'material_common.py',P/'manifest.json',OLD/'native-pass2-resumed/manifest.json']:
        first[str(p.relative_to(R))]=sha(p)
    assert F==json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text())
    spec=importlib.util.spec_from_file_location('common102',OLD/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=OLD/'native-pass2-resumed'
    data=c.load_data(charge,first);score=c.metric_functions(charge)['score'];paths={};raws={};shadows={};identities=[]
    for m in ['expanded','compact']:
        q=read(c.NATIVE/f'{m}-paths.npz',['inside','primary_power','front_reflection_power','front_reflection_direction']);I=q['inside'];charge('environment_points',int(I.sum()));q['light']=4*q['front_reflection_power'][I]*annular_environment(q['front_reflection_direction'][I]);paths[m]=q
        oldalpha=read(P/f'{m}-alpha32.npz',['alpha'])['alpha'][0];shadows[m]=read(P/f'{m}-shadow1.npz',['field'])['field']
        for r in ['a','b']:
            d=data[(m,r)];raw=read(P/f'{m}-{r}-blur6.6825-samples.npz',['raw_source'])['raw_source'];raws[(m,r)]=raw
            charge('composites',2);identity=working_composite(d['s'],raw,I,d['z']['supported'],q['primary_power'],q['light'],oldalpha,shadows[m]);expected=read(P/f'{m}-{r}-final.npz',['pre_foreground','complete'])
            assert all(np.array_equal(identity[k],expected[k],equal_nan=True) for k in expected)
            d['baseline']=expected['complete'];d['baseline_scores']=json.loads((P/f'{m}-{r}-final-metrics.json').read_text())['scores'];identities.append(dict(member=m,reference=r,pixel_exact=True))
    samples=np.array([[0,0,0],[1,1,1],[1,.9,.2],[.3,.6,1],[1,0,0],[0,1,0],[0,0,1],[.2,.2,.2]],float);controls=[]
    for f in protocol['saturation_fractions']:
        actual=endpoint(samples,f);expected=np.array([colorsys.hsv_to_rgb(h,s*f,VALUE) for h,s,v in map(lambda x:colorsys.rgb_to_hsv(*x),samples)])
        error=float(np.max(abs(actual-expected)));assert error<1e-14;assert np.allclose(actual.max(-1),VALUE,atol=1e-15)
        controls.append(dict(fraction=f,maximum_independent_HSV_error=error,white=actual[1].tolist()))
    white=body_grade(np.ones((1,3)),F['material']['bias'],F['material']['low_luminance_lift']);assert np.max(abs(white-VALUE))<1e-15
    assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['checkpoint_deadline'])
    save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),identities=identities,HSV_controls=controls,body_white=white.tolist(),new_gain=VALUE-F['material']['bias'],new_optical_evaluations=0));print('CHECKPOINT PASS',flush=True)
    alphas={};integration=[]
    for m in ['expanded','compact']:
        d=data[(m,'a')];coord=replace(working_contour(m),counter=charge);center=working_center(d['center']);previous=None
        for order in protocol['orders']:
            alpha=integrate_rims(d['s'].crop,coord,center,F['material']['outline']['angular'],[dict(plateau=1.,fade=2.)],order,charge)[0]
            delta=None if previous is None else float(np.max(abs(alpha-previous)));integration.append(dict(member=m,order=order,maximum_difference=delta));save('integration.json',integration);save('ledger.json',ledger)
            np.savez_compressed(B/f'{m}-alpha{order}.npz',alpha=alpha);previous=alpha
            print('ALPHA',m,order,delta,flush=True)
        assert delta<=protocol['maximum_order_difference'];alphas[m]=alpha
    white_rows=[];verification=[]
    for (m,r),d in data.items():
        q=paths[m];I=q['inside'];raw=raws[(m,r)];s=d['s'];H,W=s.valid.shape;sub=raw.copy();graded=body_grade(raw[I],F['material']['bias'],F['material']['low_luminance_lift'])
        encoded=encode_srgb(q['primary_power'][I,None]*decode_srgb(graded)+q['light'][:,None]);clips=int(np.count_nonzero((encoded<0)|(encoded>1)));sub[I]=np.clip(encoded,0,1)
        clear=~I&d['z']['supported'];sub[clear]*=1-F['material']['generated_shadow']['opacity']*shadows[m][clear,None]
        pre=sub.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);fg=working_artwork_study(s);charge('composites',2);body=fg.apply_foreground(pre.copy());guide=fg.apply_foreground(raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32));alpha=alphas[m]
        np.savez_compressed(B/f'{m}-{r}-body.npz',pre_foreground=pre,body=body,guide=guide,graded_inside=graded,encoded_preclip_inside=encoded)
        png(B/f'{m}-{r}-reference.png',s.target_crop);png(B/f'{m}-{r}-previous.png',d['baseline']);png(B/f'{m}-{r}-body.png',body)
        # Fixed whole-pixel angular cohorts, matching the prior own-verification definition.
        x0,y0,_,_=s.crop;yy,xx=np.indices((H,W));cx,cy=working_center(d['center']);coord=working_contour(m);core=coord.half[0]-coord.original_radius;gap=np.zeros((H,W),bool)
        for side in [1,-1]:
            dx=xx+x0-(cx+side*core);dy=-(yy+y0-cy);angle=(np.degrees(np.arctan2(dy,dx))-(180 if side<0 else 0)+180)%360-180
            gap|=(angle>38)&(angle<52)&(side*(xx+x0-cx)>core)&(np.hypot(dx,dy)>coord.original_radius-15)&(np.hypot(dx,dy)<coord.original_radius+1)
        assert gap.any() and np.all(alpha[gap]==0)
        rawmean=raw.reshape(H,2,W,2,3).mean((1,3));white_cohort=d['m']['glass']&(d['z']['coverage']==1)&np.all(rawmean>=1-1e-6,axis=-1)
        ids=np.flatnonzero(white_cohort);selected=ids[np.linspace(0,len(ids)-1,min(8,len(ids)),dtype=int)] if len(ids) else []
        for i in selected:
            y,x=np.unravel_index(i,(H,W));white_rows.append(dict(member=m,reference=r,x=int(x+x0),y=int(y+y0),preimage=(rawmean[y,x]*255).tolist(),target=(s.target_crop[y,x]*255).tolist(),previous=(d['baseline'][y,x]*255).tolist(),new_body=(body[y,x]*255).tolist(),outline_alpha=float(alpha[y,x])))
        for f in protocol['saturation_fractions']:
            label=str(round(100*f));charge('composites',1);C=overlay(body,guide,alpha,f);assert np.array_equal(C[gap],body[gap],equal_nan=True)
            # Independent OpenCV HSV conversion checks the actual active endpoint and composition.
            active=alpha>0;hsv=cv2.cvtColor(guide[active].astype(np.float32).reshape(-1,1,3),cv2.COLOR_RGB2HSV);hsv[:,:,1]*=f;hsv[:,:,2]=VALUE
            independent=cv2.cvtColor(hsv,cv2.COLOR_HSV2RGB).reshape(-1,3);charge('composites',1);replay=body[active]+alpha[active,None]*(independent-body[active]);error=float(np.max(abs(replay-C[active])));assert error<4e-7
            metrics=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=m,reference=r,saturation_fraction=f,scores=metrics,baseline_guards=c.guards(metrics,d['baseline_scores']),preclip_channels=clips,white_body_pixels=int(white_cohort.sum()),independent_HSV_composite_error=error,zero_gap_pixels=int(gap.sum()));rows.append(row)
            np.savez_compressed(B/f'{m}-{r}-s{label}.npz',complete=C);save(f'{m}-{r}-s{label}-metrics.json',row);png(B/f'{m}-{r}-s{label}.png',C)
            verification.append(dict(member=m,reference=r,fraction=f,maximum_error=error,zero_gap_exact=True));print('OPTION',m,r,label,metrics['E'],clips,flush=True)
        save('results.json',rows);save('white-patches.json',white_rows);save('verification.json',verification);save('ledger.json',ledger)
    assert first=={p:sha(R/p) for p in first};save('hashes.json',first);save('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),options=5,completed_images=20,selected_state_changed=False,new_rays=0,new_source_queries=0,new_filters=0,new_fits=0));print('FIVE OPTIONS COMPLETE',flush=True)
except Exception as e:
    save('failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('ledger.json',ledger)
