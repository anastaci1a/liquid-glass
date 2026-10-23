"""One bounded existing-profile neighborhood, original native scoring only."""
import copy, json, math, os, sys
from pathlib import Path
import cv2
import numpy as np

ROOT=Path('/evidence/extended/helper-toolbar-work/navigation-round/short-outer-profile')
sys.path.insert(0,str(ROOT/'code'))
from extended_fit import Study
from profile_cache import ProfileCache
from extended_shadow import shadow
from source_support import coverage_report, supported
cv2.setNumThreads(1)

def write(name,data):
    (ROOT/name).write_text(json.dumps(data,indent=2)+'\n')

def guards(s,p,pred):
    score=s.scores(pred,include_ssim=False)
    score['E']=math.sqrt(score['loss'])
    x0,y0,x1,y1=s.crop
    complete=s.apply_foreground(pred.copy())
    score['foreground_mse']={}
    for layer in s.case['foreground_layers']:
        if 'vector_asset' in layer and layer['mode']!='transmission' and layer.get('fit_style',True):
            a,b,c,d=layer['box']
            key=layer.get('style_key',layer['vector_asset'])
            score['foreground_mse'][key]=float(np.mean((complete[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2
    sd=s.shape(s.x,s.y,p)[-1][0]
    known=cv2.imread(str(s.folder/'known.png'),0)[y0:y1,x0:x1]>0
    mask=(sd>1.5/s.L)&(sd<.2)&known
    X=s.x*s.L+s.case['center'][0];Y=s.y*s.L+s.case['center'][1]
    for a,b,c,d in s.case.get('exterior_exclusions',[]):
        mask&=~((X>=a)&(X<=c)&(Y>=b)&(Y<=d))
    clean=s.source[y0:y1,x0:x1]*(1-shadow(s,p,s.x,s.y)[...,None])
    score['exterior']=dict(pixels=int(mask.sum()),rmse=float(np.sqrt(np.mean((clean[mask]-s.target_crop[mask])**2))*255))
    return score

def good(new,old):
    return all(n['E']<=o['E'] and n['glass']['rmse']<=o['glass']['rmse'] and n['exterior']['rmse']<=o['exterior']['rmse'] and all(n['foreground_mse'][k]<=v for k,v in o['foreground_mse'].items()) for n,o in zip(new,old))

def image(s,p,pred):
    x0,y0,x1,y1=s.crop
    cov=s.shape_coverage(p)
    clean=s.source[y0:y1,x0:x1]*(1-shadow(s,p,s.x,s.y)[...,None])
    return s.apply_foreground((pred*cov[...,None]+clean*(1-cov[...,None])).astype(np.float32))

def main():
    os.umask(0o002)
    if (ROOT/'result.json').exists():
        print('Completed packet retained; no rerun.',flush=True);return
    if (ROOT/'started.json').exists():
        raise RuntimeError('Partial run exists: inspect saved trials before any recovery')
    write('started.json',dict(pid=os.getpid(),budget='c0–2 ±.002, six native neighbors max, no optimization'))
    state=json.loads((ROOT/'baseline-public.json').read_text())
    studies=[Study(ROOT/n) for n in ['a','b']]
    p=copy.deepcopy(state['parameters'])
    length=min(studies[0].case['half']);p['sigma']*=length;p['post_sigma']*=length
    co=np.asarray(state['material'])
    coeff=np.array([p[f'c{i}'] for i in range(7)])
    caches=[];baseline=[];zeros=[];base_images=[]
    for i,s in enumerate(studies):
        pred=s.render(p,co);base_images.append(pred)
        score=guards(s,p,pred);baseline.append(score)
        assert abs(score['loss']-state['scores'][i]['loss'])<1e-6,'Public baseline mismatch'
        np.save(ROOT/f'{i}-baseline-material.npy',pred)
        np.savez_compressed(ROOT/f'{i}-frozen-masks.npz',glass=s.valid,rim=s.rim,held=s.held)
        cache=ProfileCache(s,p,co);cached=cache.render(coeff)
        cached_score=guards(s,p,cached)
        zeros.append(dict(max_pixel_difference=float(np.max(np.abs(cached-pred))),E_difference=cached_score['E']-score['E']))
        assert zeros[-1]['max_pixel_difference']<2e-6,'Cache zero mismatch'
        caches.append(cache)
        print('BASELINE',i,score['E'],score['glass']['rmse'],zeros[-1],flush=True)
    write('baseline.json',baseline);write('zero-controls.json',zeros)
    noise=max(1e-5,10*max(abs(z['E_difference']) for z in zeros))
    trials=[];candidate=None
    for k in range(3):
        for sign in [-1,1]:
            v=coeff.copy();v[k]+=sign*.002
            q=copy.deepcopy(p);q[f'c{k}']=float(v[k])
            predictions=[cache.render(v) for cache in caches]
            scores=[guards(s,q,a) for s,a in zip(studies,predictions)]
            record=dict(coefficient=k,delta=sign*.002,scores=scores,guarded=good(scores,baseline),meaningful=any(o['E']-n['E']>noise for n,o in zip(scores,baseline)))
            trials.append(record);write('trials.json',trials)
            print('TRIAL',k,sign,[r['E'] for r in scores],record['guarded'],flush=True)
            if not (record['guarded'] and record['meaningful']):continue
            direct=[s.render(q,co) for s in studies]
            final=[guards(s,q,a) for s,a in zip(studies,direct)]
            support=[coverage_report(s,q) for s in studies]
            record['direct_scores']=final;record['source_support']=support
            record['direct_guarded']=good(final,baseline)
            record['direct_vs_cache_max']=[float(np.max(abs(a-b))) for a,b in zip(direct,predictions)]
            write('trials.json',trials)
            if not (record['direct_guarded'] and all(supported(s,r) for s,r in zip(studies,support)) and any(o['E']-n['E']>noise for n,o in zip(final,baseline))):continue
            candidate=dict(parameters=q,material=state['material'],scores=final,source_support=support,coefficient=k,delta=sign*.002)
            write('candidate-native-recipe.json',candidate)
            for i,(s,base,pred) in enumerate(zip(studies,base_images,direct)):
                np.save(ROOT/f'{i}-candidate-material.npy',pred)
                np.save(ROOT/f'{i}-candidate-complete.npy',image(s,q,pred))
                panels=[s.target_crop,image(s,p,base),image(s,q,pred)]
                cv2.imwrite(str(ROOT/f'{i}-native-target-baseline-candidate.png'),np.rint(np.clip(np.concatenate(panels,axis=0),0,1)*255).astype(np.uint8)[...,::-1])
            break
        if candidate:break
    write('result.json',dict(baseline=baseline,zero_controls=zeros,trials=len(trials),candidate=candidate,meaningful_absolute_noise_floor=noise,accepted=False,count=0,limits='Native proposal only. Independent primary replay/HQ/visual/source review required; source confidence remains conditional, no Apple physical model identification. No scoring mask/source/shape/material/blur/glyph/epoch changes.'))
    print('DONE',len(trials),'candidate',candidate is not None,flush=True)

if __name__=='__main__':main()
