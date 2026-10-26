"""One held final-color candidate on unchanged supported refraction samples."""
from pathlib import Path
import json,datetime,hashlib,importlib.util,zipfile,traceback
import numpy as np
from scipy.interpolate import CubicHermiteSpline
from PIL import Image
from music_miniplayer_family import working_artwork_study,working_outline,working_contour,working_center
from miniplayer_anchor_color import outline_endpoint
from miniplayer_refinement_effects import low_luminance_body,integrate_rims
from environment_radiance import decode_srgb,encode_srgb,annular_environment
from dataclasses import replace
B=Path(__file__).resolve().parent;R=B.parents[2];OLD=B.parent/'miniplayer-three-pass-101';PREV=OLD/'pass2';WIDTH=B.parent/'miniplayer-hsv-options-102';ANCHOR=B.parent/'miniplayer-anchor-color-103';LAST=B.parent/'miniplayer-restored-grade-104'
P=json.loads((B/'protocol.json').read_text());F=json.loads((B/'frozen-family.json').read_text());CAL=json.loads((B/'calibration.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger={k:0 for k in P['caps'] if k not in ['calibration_scalar_points','control_colors']};first={};rows=[]
def save(n,v):(B/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def charge(k,n):
    assert datetime.datetime.now(datetime.timezone.utc)<END;assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
    if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def read(p,keys):
    first[str(p.relative_to(R))]=sha(p)
    with zipfile.ZipFile(p) as z:
        for k in keys:
            with z.open(k+'.npy') as f:
                v=np.lib.format.read_magic(f);shape,_,dt=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f);assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
    with np.load(p) as z:return {k:z[k] for k in keys}
def png(name,v):Image.fromarray(np.rint(np.nan_to_num(v,nan=0)*255).astype(np.uint8)).save(B/name)
def independent(rgb,role):
    """Separate SciPy Hermite evaluation, explicit RGB/HSV sector conversion."""
    rgb=np.asarray(rgb,float);sc=CAL['roles'][role];mx=rgb.max(-1);mn=rgb.min(-1);delta=mx-mn
    s=np.divide(delta,mx,out=np.zeros_like(mx),where=mx>0);h=np.zeros_like(mx);nonzero=delta>0
    for channel in [2,1,0]:
        take=nonzero&(mx==rgb[:,channel]);a,b=((0,1) if channel==2 else (2,0) if channel==1 else (1,2));h[take]=((rgb[take,a]-rgb[take,b])/delta[take]+2*channel)%6
    h/=6
    z={}
    for k in ['neutral','saturation_multiplier','value_logit_offset']:
        sp=sc[k];z[k]=CubicHermiteSpline(sp['x'],sp['y'],sp['slopes'])(np.clip(mx,sp['x'][0],sp['x'][-1]))
    N=z['neutral'];v=1/(1+np.exp(-(np.log(N/(1-N))+s*z['value_logit_offset'])));s*=z['saturation_multiplier'];hh=6*h;i=np.floor(hh).astype(int)%6;f=hh-np.floor(hh);p=v*(1-s);q=v*(1-s*f);t=v*(1-s*(1-f));result=np.empty_like(rgb)
    for sector,channels in enumerate([(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)]):
        mask=i==sector;result[mask]=np.stack([x[mask] for x in channels],axis=-1)
    return result
save('render-start.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=END.isoformat(),caps=P['caps']))
try:
    assert json.loads((B/'calibration-checkpoint.json').read_text())['passed'];assert F==json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text())
    for p in [Path(__file__),ANCHOR/'calibration.json',B/'frozen-family.json',B/'calibration.json',B/'calibration-checkpoint.json',R/'reconstruction/families/music-mini-player-working.json',R/F['geometry']['back_profile'],R/'reconstruction/miniplayer_anchor_color.py',R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/miniplayer_color_refinement.py',R/'reconstruction/environment_radiance.py',OLD/'material_common.py',WIDTH/'manifest.json',PREV/'manifest.json',OLD/'native-pass2-resumed/manifest.json',PREV/'blur-source-FIRST.json']:
        first[str(p.relative_to(R))]=sha(p)
    spec=importlib.util.spec_from_file_location('common103',OLD/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=OLD/'native-pass2-resumed';data=c.load_data(charge,first);score=c.metric_functions(charge)['score']
    alphas={};shadows={};paths={};identities=[];width_manifest=json.loads((WIDTH/'manifest.json').read_text())['files']
    for m in ['expanded','compact']:
        assert sha(WIDTH/f'{m}-alpha32.npz')==width_manifest[f'{m}-alpha32.npz'];alphas[m]=read(WIDTH/f'{m}-alpha32.npz',['alpha'])['alpha'];shadows[m]=read(PREV/f'{m}-shadow1.npz',['field'])['field']
        q=read(c.NATIVE/f'{m}-paths.npz',['inside','primary_power','front_reflection_power','front_reflection_direction']);charge('environment_points',int(q['inside'].sum()));q['light']=4*q['front_reflection_power'][q['inside']]*annular_environment(q['front_reflection_direction'][q['inside']]);paths[m]=q
        oldalpha=read(PREV/f'{m}-alpha32.npz',['alpha'])['alpha'][0]
        for r in ['a','b']:
            d=data[(m,r)];d['raw']=read(PREV/f'{m}-{r}-blur6.6825-samples.npz',['raw_source'])['raw_source'];d['selected']=read(PREV/f'{m}-{r}-final.npz',['complete','pre_foreground']);d['selected_scores']=json.loads((PREV/f'{m}-{r}-final-metrics.json').read_text())['scores'];s=d['s'];H,W=s.valid.shape;d['foreground']=working_artwork_study(s)
            charge('foreground_applications',2);d['guide']=d['foreground'].apply_foreground(d['raw'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32));body=d['foreground'].apply_foreground(d['selected']['pre_foreground'].copy());charge('identity_composites',1);actual=working_outline(body,d['guide'],oldalpha)
            assert np.array_equal(actual,d['selected']['complete'],equal_nan=True);assert score(s,actual,d['m'],d['partial'],d['crops'])==d['selected_scores'];identities.append(dict(member=m,reference=r,complete_exact=True,metrics_exact=True))
    save('render-checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),identities=identities,geometry_and_source_support_reused=True))
    assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline'])
    # Calibrate final white on a fixed, foreground-free central expanded-B cohort.
    d=data[('expanded','b')];s=d['s'];H,W=s.valid.shape;q=paths['expanded'];I=q['inside'];raw=d['raw'];yy,xx=np.indices((H,W));x0,y0,_,_=s.crop;cx,cy=working_center(d['center']);coord=working_contour('expanded');core=coord.half[0]-coord.original_radius
    nearwhite=np.all(raw.reshape(H,2,W,2,3)>=250/255,axis=(1,3,4));cohort=d['m']['glass']&~d['m']['held']&~d['m']['rim']&(d['z']['coverage']==1)&nearwhite&(abs(xx+x0-cx)<core-30)&(abs(yy+y0-cy)<coord.half[1]-30)
    for layer in s.case['foreground_layers']:
        a,b,c0,e=layer['box'];assert not cohort[b-y0:e-y0,a-x0:c0-x0].any()
    assert cohort.sum()>=100
    take=np.repeat(np.repeat(cohort,2,0),2,1);assert I[take].all();T=q['primary_power'][take];full_light=np.zeros(I.shape);full_light[I]=q['light'];E=full_light[take];trace=[]
    def final_white(g):
        charge('white_calibration_points',len(T));out=encode_srgb(T*decode_srgb(np.array(g+P['bias']))+E);trace.append(dict(gain=float(g),mean_final=float(out.mean())));return out
    lo=0.;hi=1-P['bias'];assert final_white(lo).mean()<P['final_white_target']<final_white(hi).mean()
    for _ in range(48):
        mid=(lo+hi)/2
        if final_white(mid).mean()<P['final_white_target']:lo=mid
        else:hi=mid
    P['gain']=(lo+hi)/2;white_out=final_white(P['gain']);assert abs(white_out.mean()-P['final_white_target'])<1e-12
    white_endpoint=low_luminance_body(np.ones((1,3)),P['gain'],P['bias'],P['dark_lift'])
    np.savez_compressed(B/'white-calibration-cohort.npz',cohort=cohort,primary_power=T,direct_light=E,final_white=white_out)
    save('body-controls.json',dict(gain=P['gain'],bias=P['bias'],dark_lift=P['dark_lift'],cohort_pixels=int(cohort.sum()),grading_white=white_endpoint.tolist(),final_white_mean=float(white_out.mean()*255),final_white_min=float(white_out.min()*255),final_white_max=float(white_out.max()*255),bisection=trace,normal_transmitted_white=(encode_srgb(.9216*decode_srgb(white_endpoint))*255).tolist()))
    print('FINAL WHITE CALIBRATION',P['gain'],white_out.mean()*255,flush=True)
    integration=[]
    for m in ['expanded','compact']:
        d=data[(m,'a')];coord=replace(working_contour(m),counter=charge);previous=None
        for order in P['orders']:
            alpha=integrate_rims(d['s'].crop,coord,working_center(d['center']),F['material']['outline']['angular'],[dict(plateau=P['plateau_native'],fade=P['fade_native'])],order,charge)[0]
            delta=None if previous is None else float(np.max(abs(alpha-previous)));integration.append(dict(member=m,order=order,maximum_difference=delta));save('integration.json',integration);save('render-ledger.json',ledger);np.savez_compressed(B/f'{m}-alpha{order}.npz',alpha=alpha);previous=alpha
            print('ALPHA',m,order,delta,flush=True)
        assert delta<=P['maximum_order_difference'];alphas[m]=alpha
    white=[];verify=[]
    for (m,r),d in data.items():
        s=d['s'];H,W=s.valid.shape;I=d['z']['inside'];supported=d['z']['supported'];raw=d['raw'];assert np.isfinite(raw[I]).all() and supported[I].all();alpha=alphas[m];values=raw.copy();charge('color_evaluations',int(I.sum()));graded=low_luminance_body(raw[I],P['gain'],P['bias'],P['dark_lift']);q=paths[m];assert np.array_equal(I,q['inside']);mapped=encode_srgb(q['primary_power'][I,None]*decode_srgb(graded)+q['light'][:,None]);values[I]=mapped
        # Restored original optical composition after the existing bounded body grade.
        clear=~I&supported;clear_values=raw[clear]*(1-F['material']['generated_shadow']['opacity']*shadows[m][clear,None]);values[clear]=clear_values;assert np.array_equal(values[clear],clear_values)
        pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('foreground_applications',1);body=d['foreground'].apply_foreground(pre.copy());C=body.copy();active=alpha>0;charge('color_evaluations',int(active.sum()));endpoint=outline_endpoint(d['guide'][active],CAL);C[active]=body[active]+alpha[active,None]*(endpoint-body[active]);charge('candidate_composites',1)
        assert np.isfinite(C[d['m']['glass']]).all();finite=np.isfinite(C);assert C[finite].min()>=0 and C[finite].max()<=1
        # Full independent response, integration and final composition replay.
        check=raw.copy();charge('color_evaluations',int(I.sum()));x=raw[I].astype(float);linear=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4);y=linear@np.array([.2126,.7152,.0722]);base=x*P['gain']+P['bias'];g=base+P['dark_lift']*(1-y[:,None])**3*(1-base);gl=np.where(g<=.04045,g/12.92,((g+.055)/1.055)**2.4);light=q['primary_power'][I,None]*gl+q['light'][:,None];replayed=np.where(light<=.0031308,12.92*light,1.055*light**(1/2.4)-.055);map_error=float(np.max(abs(mapped-replayed)));assert map_error<2e-14;check[I]=replayed;check[clear]=clear_values
        pre_check=((check[0::2,0::2]+check[0::2,1::2])+(check[1::2,0::2]+check[1::2,1::2]))*.25;pre_check=pre_check.astype(np.float32);charge('foreground_applications',1);body_check=d['foreground'].apply_foreground(pre_check.copy());charge('color_evaluations',int(active.sum()));endpoint_check=independent(d['guide'][active],'outline');out_check=body_check.copy();out_check[active]=body_check[active]+alpha[active,None]*(endpoint_check-body_check[active]);charge('verification_composites',1)
        error=float(np.nanmax(abs(out_check-C)));assert error<=P['maximum_replay_error'] and np.array_equal(np.isnan(out_check),np.isnan(C))
        x0,y0,_,_=s.crop;yy,xx=np.indices((H,W));cx,cy=working_center(d['center']);coord=working_contour(m);core=coord.half[0]-coord.original_radius;gap=np.zeros((H,W),bool)
        for side in [1,-1]:
            dx=xx+x0-(cx+side*core);dy=-(yy+y0-cy);angle=(np.degrees(np.arctan2(dy,dx))-(180 if side<0 else 0)+180)%360-180
            gap|=(angle>38)&(angle<52)&(side*(xx+x0-cx)>core)&(np.hypot(dx,dy)>coord.original_radius-15)&(np.hypot(dx,dy)<coord.original_radius+1)
        assert gap.any() and np.all(alpha[gap]==0) and np.array_equal(C[gap],body[gap],equal_nan=True)
        metrics=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=m,reference=r,scores=metrics,selected_comparisons=c.guards(metrics,d['selected_scores']),compact_is_diagnostic_only=m=='compact',clipped_channels=0,zero_gap_pixels=int(gap.sum()));anchor_metrics=json.loads((LAST/f'{m}-{r}-metrics.json').read_text())['scores'];row['previous104_scores']=anchor_metrics;row['previous104_comparisons']=c.guards(metrics,anchor_metrics);rows.append(row)
        verify.append(dict(member=m,reference=r,independent_response_error=map_error,independent_complete_error=error,clear_samples_exact=True,zero_gap_exact=True,original_optical_composition_restored=True))
        np.savez_compressed(B/f'{m}-{r}-candidate.npz',complete=C,pre_foreground=pre,body=body,mapped_inside=mapped,graded_inside=graded);png(f'{m}-{r}-candidate.png',C);png(f'{m}-{r}-reference.png',s.target_crop);anchor=read(LAST/f'{m}-{r}-candidate.npz',['complete'])['complete'];png(f'{m}-{r}-previous.png',anchor);png(f'{m}-{r}-selected.png',d['selected']['complete']);save(f'{m}-{r}-metrics.json',row)
        positions=[(725,65),(735,65),(725,185),(735,185)] if m=='compact' else [(1160-x0,325-y0),(1280-x0,325-y0),(1400-x0,325-y0),(1160-x0,501-y0),(1280-x0,501-y0),(1400-x0,501-y0)]
        for x,y in positions:
            white.append(dict(member=m,reference=r,local_x=x,local_y=y,preimage=(d['guide'][y,x]*255).tolist(),target=(s.target_crop[y,x]*255).tolist(),old=(d['selected']['complete'][y,x]*255).tolist(),new_body=(body[y,x]*255).tolist(),new_complete=(C[y,x]*255).tolist(),outline_alpha=float(alpha[y,x])))

        if m=='expanded' and r=='b':
            save('actual-white-cohort.json',dict(pixels=int(cohort.sum()),mean_body=(body[cohort].mean(0)*255).tolist(),mean_complete=(C[cohort].mean(0)*255).tolist(),mean_reference=(s.target_crop[cohort].mean(0)*255).tolist(),maximum_outline_alpha=float(alpha[cohort].max()),white_probe_mean=float(white_out.mean()*255)))
        save('results.json',rows);save('verification.json',verify);save('fixed-color-patches.json',white);save('render-ledger.json',ledger);print('CANDIDATE',m,r,metrics['E'],'replay',error,flush=True)
    assert first=={p:sha(R/p) for p in first};save('hashes.json',first);save('finished.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate_images=4,selected_model_changed=False,new_rays=0,new_source_queries=0,new_filters=0,new_geometry=0,overlay_distance_quadrature_changed=True));print('ONE CANDIDATE COMPLETE',flush=True)
except Exception as e:save('render-failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
finally:save('render-ledger.json',ledger)
