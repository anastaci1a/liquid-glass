"""Queue6: one native ordinary source/output blur study, no geometry fitting.

All filtering calls are the accepted renderer's operations. Caching unfiltered
material for repeated source sigmas avoids recomputing a fixed inverse map.
Native4x4 is used for every objective/guard evaluation, not just final scoring.
"""
import sys,json,copy,time,hashlib
from pathlib import Path
from functools import lru_cache
sys.path.insert(0,'/tmp/agent-toolbar-evidence-package/code')
import numpy as np
import cv2
from PIL import Image
from scipy.optimize import minimize
import crowned_tensor as model
from progress_gate import evaluate,error

package=Path('/tmp/agent-toolbar-evidence-package')
out=Path('/tmp/agent-toolbar-revision2-blur');out.mkdir(exist_ok=True)
p=json.loads((package/'recipe.json').read_text())
before=json.loads((package/'primary-verification.json').read_text())['candidate']
case=p['case'];L=min(case['half']);x0,y0,x1,y1=case['crop']
source=np.asarray(Image.open(package/'inputs/source.png')).astype(float)/255
target=np.asarray(Image.open(package/'inputs/target.png')).astype(np.float32)/255
B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1]
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
fm=np.load(package/'derived-foreground.npz')
baseC=np.load('/tmp/agent-toolbar-inner-settlement/material.npy')
basealpha=np.load('/tmp/agent-toolbar-inner-settlement/alpha.npy')
shadow=model.gaussian_coverage_shadow(case,p)
public_fg=json.loads((package/'primary-scores.json').read_text())['foreground']
baseguard=np.array([before['observations']['A']['glass']['rmse'],before['observations']['A']['rim']['rmse'],before['observations']['A']['shadow'],public_fg['archivebox']['rmse'],public_fg['plus']['rmse']])
baseE=error(before['observations']['A'])
limits=np.array([[.045,.085],[.004,.014]])
basev=[p['source_sigma'],p['post_sigma']]
cache={};rows=[];fits=[];phase='baseline';began=time.time()

def preset(v):
    q=copy.deepcopy(p);q['source_sigma']=float(v[0]);q['post_sigma']=float(v[1]);return q

@lru_cache(maxsize=4)
def unfiltered(source_sigma):
    q=preset([source_sigma,0.]);return model.render(source,case,q,samples=4)

def rendered(v):
    C,a=unfiltered(float(v[0]));sigma=float(v[1])*L
    numerator=cv2.GaussianBlur(C*a[...,None],(0,0),sigma)
    denominator=cv2.GaussianBlur(a,(0,0),sigma)
    return numerator/np.maximum(denominator,1e-12)[...,None],a

def measure(C,a):
    metrics={}
    for name in ['glass','rim']:
        D=(C-T)[masks[name]]*255
        metrics[name]={'rmse':float(np.sqrt(np.mean(D**2))),'pixels':int(masks[name].sum())}
    full=C*a[...,None]+B*(1-shadow[...,None])*(1-a[...,None])
    metrics['shadow']=float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
    # Vector glyphs are composited AFTER both ordinary glass filters.
    for layer in p['foreground_layers']:
        aa=fm[layer['name']][...,None];full=full*(1-aa)+np.asarray(layer['color'])*aa
    foreground={}
    for layer in p['foreground_layers']:
        A,b,c,d=layer['box'];foreground[layer['name']]=float(np.sqrt(np.mean((full[b-y0:d-y0,A-x0:c-x0]-T[b-y0:d-y0,A-x0:c-x0])**2))*255)
    return metrics,foreground,full

def native(v,save=None):
    v=np.clip(v,limits[:,0],limits[:,1]);key=tuple(map(float,v))
    if key in cache and save is None:return cache[key]
    t0=time.time();C,a=rendered(v);sc,fg,full=measure(C,a)
    state={'epoch':before['epoch'],'observations':{'A':sc}}
    gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False)
    guards=np.array([sc['glass']['rmse'],sc['rim']['rmse'],sc['shadow'],fg['archivebox'],fg['plus']])
    ok=bool(np.all(guards<=baseguard));E=error(sc)
    record={'v':list(key),'native_E':E,'scores':state,'foreground':fg,'guard_values':guards.tolist(),'nonregression':dict(zip(['glass','rim','exterior','archivebox','plus'],map(bool,guards<=baseguard))),'all_nonregression':ok,'gate':gate,'numerical_qualifier':bool(ok and gate['observations']['A']['passed']),'phase':phase,'seconds':time.time()-t0}
    if key not in cache:
        cache[key]=record;rows.append(record)
        (out/'native-evaluations.json').write_text(json.dumps({'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','before':before,'bounds':limits.tolist(),'evaluations':rows,'fits':fits,'counted_passes':0},indent=2)+'\n')
        print('NATIVE',len(rows),phase,list(key),E,ok,record['numerical_qualifier'],flush=True)
    if save:
        folder=out/save;folder.mkdir(exist_ok=True)
        (folder/'recipe.json').write_text(json.dumps(preset(v),indent=2)+'\n')
        (folder/'scores.json').write_text(json.dumps(state,indent=2)+'\n')
        (folder/'measurement.json').write_text(json.dumps(record,indent=2)+'\n')
        np.save(folder/'material.npy',C);np.save(folder/'alpha.npy',a)
        np.save(folder/'complete.npy',full)
        Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(folder/'complete-preview.png')
    return record

# Exact recovery validates the caching implementation against accepted evidence.
C,a=rendered(basev)
assert np.array_equal(C,baseC) and np.array_equal(a,basealpha)
r0=native(basev,save='baseline')
assert abs(r0['native_E']-baseE)<1e-12
assert np.max(np.abs(np.array(r0['guard_values'])-baseguard))<1e-9
# A nonbaseline filter pair must also equal the stock renderer, byte for byte.
probe=[.078,.011];fast,fa=rendered(probe);stock,sa=model.render(source,case,preset(probe),samples=4)
assert np.array_equal(fast,stock) and np.array_equal(fa,sa)
(out/'recovery.json').write_text(json.dumps({'accepted_material_and_coverage_exact':True,'native_scores_exact':True,'cached_vs_stock_nonbaseline_exact':True,'all_objectives_native_4x4':True,'glyphs_filtered':False,'ordinary_blur_only_no_dispersion':True},indent=2)+'\n')
print('EXACT BASE + NONBASELINE STOCK EQUIVALENCE',flush=True)

for seed,start in enumerate([basev,[.080,.012]],1):
    phase=f'native-Powell-{seed}';start_count=len(rows);t0=time.time()
    def objective(v):return native(v)['native_E']**2
    fit=minimize(objective,start,method='Powell',bounds=limits,options={'maxfev':160,'xtol':.000006,'ftol':1e-9})
    r=native(fit.x,save=f'seed-{seed}')
    fits.append({'seed':seed,'start':start,'final':r,'success':bool(fit.success),'message':str(fit.message),'nfev':int(fit.nfev),'unique_evaluations':len(rows)-start_count,'nit':int(fit.nit),'seconds':time.time()-t0,'near_bounds':[bool(min(v-lo,hi-v)<.02*(hi-lo)) for v,(lo,hi) in zip(fit.x,limits)]})
    (out/'fits.json').write_text(json.dumps(fits,indent=2)+'\n')
    print('FIT',seed,fit.success,fit.nfev,r['native_E'],flush=True)

# Axis boundary measurements distinguish a true bracket from hidden clipping.
phase='native-bound-review'
best=min(rows,key=lambda r:r['native_E']);v=np.array(best['v'])
for i in range(2):
    for bound in limits[i]:
        u=v.copy();u[i]=bound;native(u)
valid=[r for r in rows if r['numerical_qualifier']]
feasible=[r for r in rows if r['all_nonregression']]
best_raw=min(rows,key=lambda r:r['native_E'])
selected=min(valid or feasible,key=lambda r:r['native_E'])
phase='saved-best';native(selected['v'],save='best-feasible')
native(best_raw['v'],save='best-raw')
summary={'baseline_commit':'bb1ee80131d39e7661c3d55174767c4d15182e05','epoch':before['epoch'],'before_E':baseE,'bounds':limits.tolist(),'fits':fits,'best_raw':best_raw,'best_guard_feasible':selected,'any_numerical_qualifier':bool(valid),'unique_native_evaluations':len(rows),'seconds':time.time()-began,'counted_passes':0,'note':'ONE ordinary blur family including starts/probes/bound review. No rejected joint geometry carried forward. Lead independent acceptance and fresh HQ evidence required; no dispersion or physical-PSF identification.'}
(out/'result.json').write_text(json.dumps(summary,indent=2)+'\n')
print('RESULT',summary['any_numerical_qualifier'],selected['native_E'],flush=True)
