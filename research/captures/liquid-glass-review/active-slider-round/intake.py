"""Current-main active-switch revision6 native/source intake, no fit."""
import json,os,sys,math
from pathlib import Path
import cv2,numpy as np
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');sys.path.insert(0,str(ROOT/'code'))
from extended_fit import Study
from revision_replay import clean_composite
from source_support import masks,kernel_safe,confidence_at,coverage_report,supported
from chromatic_transmission import enabled,rays,weight
from grazing_reflection import layers
cv2.setNumThreads(1)
def save(n,v):(ROOT/n).write_text(json.dumps(v,indent=2)+'\n')
def score(s,p,pred):
    value=s.scores(pred);value['E']=math.sqrt(value['loss']);whole=clean_composite(s,p,pred);ext=(s.sd>0)&(s.sd<.35);value['shadow']=dict(rmse=float(np.sqrt(np.mean(((whole-s.target_crop)[ext]*255)**2))),pixels=int(ext.sum()));assert not s.foreground_layers and not s.transmission_layers;return value,whole,ext

def audit(s,p,index):
    defined,observed=masks(s);safe,radius=kernel_safe(defined,s,p);osafe,_=kernel_safe(observed,s,p);cohorts={};bad=[]
    for row,bottom,W,x,y in s.raster_tiles(1):
        whole=s.shape(x,y,p)[-1][0]<=0;scored=np.repeat(np.repeat(s.valid[row:bottom],2,axis=0),2,axis=1)
        X,Y,_,_=s.geometry_field(x,y,p);mapping=[('base',X,Y,np.ones_like(whole))]
        if enabled(p):mapping.extend((str(channel),X,Y,weight(s,p,x)>1e-8) for channel,X,Y,_ in rays(s,p,x,y))
        for name,X,Y,active in mapping:
            X=X*s.L+s.case['center'][0];Y=Y*s.L+s.case['center'][1];dc=confidence_at(safe,X,Y);oc=confidence_at(osafe,X,Y)
            for group,mask in [('whole',whole&active),('ALL_scored',scored&active)]:
                key=name+'_'+group;v=cohorts.setdefault(key,dict(rays=0,outside_corrected_outline=0,defined_bad=0,observed_bad=0,minimum_defined=1.,minimum_observed=1.));v['rays']+=int(mask.sum());v['outside_corrected_outline']+=int((mask&~whole).sum());v['defined_bad']+=int((mask&(dc<.999)).sum());v['observed_bad']+=int((mask&(oc<.999)).sum())
                if mask.any():v['minimum_defined']=min(v['minimum_defined'],float(dc[mask].min()));v['minimum_observed']=min(v['minimum_observed'],float(oc[mask].min()))
            unsupported=(whole|scored)&active&(dc<.999)
            if unsupported.any():bad.append(np.stack([x[unsupported]*s.L+s.case['center'][0],y[unsupported]*s.L+s.case['center'][1],X[unsupported],Y[unsupported],dc[unsupported],oc[unsupported],scored[unsupported],np.full(int(unsupported.sum()),-1 if name=='base' else int(name))],axis=1))
    data=np.concatenate(bad) if bad else np.empty((0,8));np.save(ROOT/f'ref{index}-undefined-emitted-rays.npy',data)
    center=coverage_report(s,p);reflection={}
    if 'grazing_reflection' in p:
        w,_=layers(s,p);wholemask=s.shape_coverage(p)>0;Y,X=np.mgrid[s.crop[1]:s.crop[3],s.crop[0]:s.crop[2]].astype(np.float32);r=int(np.ceil(3*p['grazing_reflection']['source_sigma']*s.L))
        for kind,mask in [('defined',defined),('observed',observed)]:
            protected=cv2.erode(mask,np.ones((2*r+1,2*r+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0) if r else mask;c=confidence_at(protected,X,Y)
            for label,scope in [('whole',wholemask),('ALL_scored',s.valid)]:
                active=scope&(w>1e-8);reflection[kind+'_'+label]=dict(samples=int(active.sum()),bad=int((active&(c<.999)).sum()),minimum=float(c[active].min()) if active.any() else 1.)
    allowed=s.case.get('allow_estimated_background',False)
    passed=supported(s,center) and all(v['defined_bad']==0 and (allowed or v['observed_bad']==0) for v in cohorts.values()) and all(v['bad']==0 for k,v in reflection.items() if k.startswith('defined') or not allowed)
    return dict(cohorts=cohorts,reflection_native_output_grid=reflection,center_and_context=center,source_gaussian_radius_native_px=radius,existing_estimated_input_authorized=allowed,passed=passed,representative_undefined=data[:12].tolist(),limits='FRESH original2x2 whole AND ALLscored including outsidecorrectedoutline base+active RGB rays; reflection actualnativeoutputgrid/context nativefootprint separate. 3sigma finite kernels, not continuous/infinite theorem. Observedholes remain originalexplicitestimatedinput, never equated with recoveredsource.')

def main():
    os.umask(0o002)
    if (ROOT/'intake-result.json').exists():print('Intake complete; no repeat');return
    if (ROOT/'intake-started.json').exists():raise RuntimeError('Inspect partial process first')
    save('intake-started.json',dict(pid=os.getpid(),fit=False,baseline='committed main a1b8b1b5 active-switch revision6, native parameters already nativepx; no stalepaired24/privateaccepted'))
    recipe=json.loads((ROOT/'authoritative-revision6.json').read_text());expected=json.loads((ROOT/'authoritative-revision6-verification.json').read_text())['candidate']['observations'];p=recipe['parameters'];co=np.array(recipe['material']);rows=[]
    for i,name in enumerate(['a','b']):
        s=Study(ROOT/name);pred=s.render(p,co);scores,complete,ext=score(s,p,pred);old=expected[name.upper()];assert scores['loss']==old['loss'] and scores['glass']['rmse']==old['glass']['rmse'] and scores['shadow']['rmse']==old['shadow']['rmse'],'Current main native mismatch before fitting'
        np.save(ROOT/f'ref{i}-baseline-material.npy',pred);np.save(ROOT/f'ref{i}-baseline-complete.npy',complete);np.savez_compressed(ROOT/f'ref{i}-frozen-masks.npz',glass=s.valid,rim=s.rim,held=s.held,exterior=ext)
        support=audit(s,p,i);rows.append(dict(reference=name,native_scores=scores,source_support=support));save('intake-partial.json',rows);print(name,'E',scores['E'],'sourcepass',support['passed'],flush=True)
    save('baseline-native-recipe.json',dict(parameters=p,material=co.tolist(),scores=[r['native_scores'] for r in rows]));save('intake-result.json',dict(observations=rows,fit_authorized_by_original_epoch_source=all(r['source_support']['passed'] for r in rows),accepted_count=0,source_epoch_unchanged=True,foreground_guard='Original active-switch cases have ZERO foreground/glyph layers; no protected vector geometry changed.',limits='Original hidden-track source approximation retained explicitly; direct-observed fractions may be0. Undefined rays are a source blocker, not fitted away.'))
    print('DONE sourcegate',all(r['source_support']['passed'] for r in rows),flush=True)
if __name__=='__main__':main()
