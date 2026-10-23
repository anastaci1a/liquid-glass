import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
from scipy.optimize import minimize
import toolbar_candidate as model
from reproduce import CASES,scores
from progress_gate import error,evaluate
out=Path('/tmp/agent-toolbar-run');source=np.asarray(Image.open(out/'source.png')).astype(float)/255;target=np.asarray(Image.open(out/'target.png')).astype(np.float32)/255
case=CASES['regular'];B=source[285:845,475:1445];T=target[285:845,475:1445];masks=np.load(out/'frozen-masks.npz');ext=masks['exterior'];before=json.loads((out/'incumbent.json').read_text());base=json.loads((out/'incumbent-recipe.json').read_text())
trials=[];best=None;bestE=1e10
for softness in [.08,.10,.12]:
    p=copy.deepcopy(base);p['footprint_softness']=softness;raw,alpha=model.render(source,case,p)
    for sigma in [.75,1.,1.25,1.5]:
        C=cv2.GaussianBlur(raw*alpha[...,None],(0,0),sigma)/np.maximum(cv2.GaussianBlur(alpha,(0,0),sigma),1e-12)[...,None]
        sc=scores(C,T,case);full=C*alpha[...,None]+B*(1-alpha[...,None]);shadow=float(np.sqrt(np.mean(((full-T)[ext]*255)**2)));state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':shadow}}};E=error(state['observations']['A'])
        gate=evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False);ok=all(x['passed'] for x in gate['observations'].values())
        q=copy.deepcopy(p);q['post_sigma']=sigma/170;trials.append({'softness':softness,'post_sigma_native_px':sigma,'E':E,'scores':state,'native_pass':ok})
        print('BRACKET',softness,sigma,E,shadow,ok,flush=True)
        if ok and E<bestE:best=(q,C,alpha,state);bestE=E
    (out/'bracket.json').write_text(json.dumps({'experiment':5,'trials':trials,'selection':'lowest native E among bracket proposals passing all frozen gates; not held-out validation','pass_count':0},indent=2)+'\n')
assert best is not None
p,C,alpha,state=best
(out/'bracket-selected-recipe.json').write_text(json.dumps(p,indent=2)+'\n');np.save(out/'bracket-selected-material.npy',C);np.save(out/'bracket-selected-alpha.npy',alpha)
# Neutral attenuation from Gaussian-convolved shape coverage, four parameters.
# Opacity is solved analytically at each width/offset, so only 3 nonlinear variables.
Y,X=np.mgrid[0:alpha.shape[0],0:alpha.shape[1]].astype(np.float32);PX=X[ext];PY=Y[ext];D=(C*alpha[...,None]+B*(1-alpha[...,None])-T)[ext];Fbase=(B*(1-alpha[...,None]))[ext]
cache={};evaluations=0

def evaluate_shadow(v,ret=False):
    global evaluations
    width,dx,dy=map(float,v);key=width
    if key not in cache:
        if len(cache)>8:cache.clear()
        cache[key]=cv2.GaussianBlur(alpha,(0,0),width*170,borderType=cv2.BORDER_CONSTANT)
    field=cv2.remap(cache[key],X-dx*170,Y-dy*170,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)[ext]
    F=Fbase*field[:,None];opacity=float(np.clip(np.sum(D*F)/max(np.sum(F*F),1e-15),0,.4));mse=float(np.mean((D-opacity*F)**2));evaluations+=1
    if ret:return mse,opacity,cache[key]
    return mse
records=[];bestv=None;fun=1e10
for start in [[.05,0,.025],[.12,0,.05],[.25,0,.075]]:
    fit=minimize(evaluate_shadow,start,method='Powell',bounds=[(.012,.3),(-.05,.05),(-.1,.15)],options={'maxfev':220,'xtol':2e-4,'ftol':1e-6});records.append({'start':start,'solution':fit.x.tolist(),'rmse':float(np.sqrt(fit.fun)*255),'evaluations':fit.nfev})
    print('SHADOW',records[-1],flush=True)
    if fit.fun<fun:bestv=fit.x;fun=fit.fun
mse,opacity,blur=evaluate_shadow(bestv,True);width,dx,dy=map(float,bestv);a=opacity*cv2.remap(blur,X-dx*170,Y-dy*170,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
composite=C*alpha[...,None]+B*(1-a[...,None])*(1-alpha[...,None]);shadow=float(np.sqrt(np.mean(((composite-T)[ext]*255)**2)));state['observations']['A']['shadow']=shadow
p['shadow']={'kind':'gaussian_coverage','opacity':opacity,'sigma':width,'offset':[dx,dy],'color':'neutral black attenuation','compositing':'behind independent glass coverage'}
(out/'candidate-with-shadow-recipe.json').write_text(json.dumps(p,indent=2)+'\n');(out/'candidate-with-shadow.json').write_text(json.dumps(state,indent=2)+'\n');np.save(out/'candidate-with-shadow-material.npy',C);np.save(out/'candidate-with-shadow-alpha.npy',alpha);Image.fromarray(np.uint8(np.clip(composite,0,1)*255)).save(out/'candidate-with-shadow-clean.png')
report={'experiment':6,'fits':records,'evaluations':evaluations,'shadow':p['shadow'],'scores':state,'E':error(state['observations']['A']),'glass_parameters_preserved_during_shadow_fit':True,'mask_coverage_min':float(alpha[masks['glass']].min()),'actual_composite_glass_scores_advisory':scores(composite,T,case),'gate':evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False),'qualifying_passes_counted':0,'limits':'shadow model and bracket optimized on one observed frame; source blank estimate retained; not an identified Apple light rig'}
(out/'shadow-fit.json').write_text(json.dumps(report,indent=2)+'\n');print('FINAL',report['E'],shadow,p['shadow'],flush=True)
