import sys,json,copy,time
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
from scipy.optimize import minimize
import toolbar_candidate as model
from reproduce import CASES,points
from render import case_geometry
from progress_gate import evaluate,error
root=Path('/tmp/agent-toolbar-run');out=Path('/tmp/agent-toolbar-shadow-extension');out.mkdir(exist_ok=True)
case=CASES['regular'];p=json.loads((root/'candidate-with-shadow-recipe.json').read_text());before=json.loads((root/'candidate-with-shadow.json').read_text());source=np.asarray(Image.open(root/'source.png')).astype(float)/255;target=np.asarray(Image.open(root/'target.png')).astype(np.float32)/255
B=source[285:845,475:1445];T=target[285:845,475:1445];C=np.load(root/'candidate-with-shadow-material.npy');alpha=np.load(root/'candidate-with-shadow-alpha.npy');masks=np.load(root/'frozen-masks.npz');ext=masks['exterior'];Y,X=np.mgrid[:alpha.shape[0],:alpha.shape[1]].astype(np.float32)
D=(C*alpha[...,None]+B*(1-alpha[...,None])-T)[ext];Fbase=(B*(1-alpha[...,None]))[ext];cache={};rows=[];best=None
for seed,start in enumerate([[.3,-.00293,.00777],[.45,0,.03],[.58,0,.05]],1):
    evaluations=[]
    def objective(v,ret=False):
        width,dx,dy=map(float,v)
        if width not in cache:
            if len(cache)>8:cache.clear()
            cache[width]=cv2.GaussianBlur(alpha,(0,0),width*170,borderType=cv2.BORDER_CONSTANT)
        field=cv2.remap(cache[width],X-dx*170,Y-dy*170,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)[ext];F=Fbase*field[:,None];opacity=float(np.clip(np.sum(D*F)/max(np.sum(F*F),1e-15),0,.4));loss=float(np.mean((D-opacity*F)**2));evaluations.append({'v':list(map(float,v)),'opacity':opacity,'exterior_L':loss})
        return (loss,opacity) if ret else loss
    t0=time.time();fit=minimize(objective,start,method='Powell',bounds=[(.012,.6),(-.05,.05),(-.1,.15)],options={'maxfev':350,'xtol':1e-4,'ftol':1e-7});loss,opacity=objective(fit.x,True);q=copy.deepcopy(p);q['shadow']={**q['shadow'],'opacity':opacity,'sigma':float(fit.x[0]),'offset':list(map(float,fit.x[1:3]))};a=model.gaussian_coverage_shadow(case,q);full=C*alpha[...,None]+B*(1-a[...,None])*(1-alpha[...,None]);rmse=float(np.sqrt(np.mean(((full-T)[ext]*255)**2)));state=copy.deepcopy(before);state['observations']['A']['shadow']=rmse
    record={'seed':seed,'start':start,'fit_parameters':q['shadow'],'optimizer_success':bool(fit.success),'optimizer_message':str(fit.message),'seconds':time.time()-t0,'evaluations':evaluations,'fixed_exterior_rmse':rmse,'scores':state,'no_optical_parameter_change':True};rows.append(record);print('SHADOW',seed,rmse,q['shadow'],fit.success,flush=True)
    if best is None or rmse<best[0]:best=(rmse,q,state,full)
    (out/'study.json').write_text(json.dumps({'before':before,'trials':rows,'counted_passes':0,'reason':'shadow-only improvement cannot satisfy optical E milestone'},indent=2)+'\n')
rmse,q,state,full=best
_,_,x,y=points(case);sd,*_=case_geometry(case,x,y);old_a=model.gaussian_coverage_shadow(case,p);old_full=C*alpha[...,None]+B*(1-old_a[...,None])*(1-alpha[...,None]);bands=[]
for lo,hi in [(0,10),(10,20),(20,35),(35,55),(55,80)]:
    mask=(sd>lo)&(sd<=hi);bands.append({'band':[lo,hi],'pixels':int(mask.sum()),'before_rmse':float(np.sqrt(np.mean(((old_full-T)[mask]*255)**2))),'after_rmse':float(np.sqrt(np.mean(((full-T)[mask]*255)**2)))})
(out/'recipe.json').write_text(json.dumps(q,indent=2)+'\n');(out/'scores.json').write_text(json.dumps(state,indent=2)+'\n');Image.fromarray(np.uint8(np.clip(full,0,1)*255)).save(out/'clean-preview.png');(out/'result.json').write_text(json.dumps({'fixed_exterior_rmse':rmse,'tail_bands_advisory':bands,'gate':evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False),'counted_passes':0,'note':'same glass/rim E; separate provisional shadow analysis, not an optical pass; wider bracket/offset and unknown source field do not identify physical lighting'},indent=2)+'\n');print('RESULT',rmse,bands,flush=True)
