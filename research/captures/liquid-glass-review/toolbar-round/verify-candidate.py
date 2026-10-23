import sys,json,copy,hashlib
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image,ImageDraw
import toolbar_candidate as model
from reproduce import CASES,scores
from progress_gate import evaluate,error
out=Path('/tmp/agent-toolbar-run');source=np.asarray(Image.open(out/'source.png')).astype(float)/255;target=np.asarray(Image.open(out/'target.png')).astype(np.float32)/255
case=CASES['regular'];base=json.loads((out/'incumbent-recipe.json').read_text());p=json.loads((out/'candidate-recipe.json').read_text());before=json.loads((out/'incumbent.json').read_text());saved=json.loads((out/'candidate.json').read_text())
rgb,alpha=model.render(source,case,p);cached=np.load(out/'candidate-material.npy');delta=float(np.max(np.abs(rgb-cached)));assert delta<1e-6,delta
sc=scores(rgb,target[285:845,475:1445],case);composite=rgb*alpha[...,None]+source[285:845,475:1445]*(1-alpha[...,None]);ext=np.load(out/'frozen-masks.npz')['exterior'];shadow=float(np.sqrt(np.mean(((composite-target[285:845,475:1445])[ext]*255)**2)))
state={'epoch':before['epoch'],'observations':{'A':{'glass':sc['all_glass'],'rim':sc['rim'],'shadow':shadow}}}
# Validate source-domain bounds at all frozen glass centers + source 3sigma radius.
y,x=np.mgrid[285:845,475:1445];valid=np.load(out/'frozen-masks.npz')['glass'];X,Y=model.mapping((x-960)/170,(y-542)/170,p);X=X*170+960;Y=Y*170+542
margin=3*p['source_sigma']*170+1;support=bool(np.all((X[valid]>=margin)&(X[valid]<1920-margin)&(Y[valid]>=margin)&(Y[valid]<1080-margin)))
report={'native_repeat_max_absolute_difference':delta,'repeat_scores':state,'candidate_saved_scores':saved,'source_support':{'inside_image_with_3sigma_and_bilinear_margin':support,'margin_native_px':margin,'x_range':[float(X[valid].min()),float(X[valid].max())],'y_range':[float(Y[valid].min()),float(Y[valid].max())],'limits':'native-center domain test, not continuous/subpixel certification; source rectangle remains an explicit smooth blank estimate; independent primary review required'},'gate':evaluate(before,state,visual_review=False,replay_verified=False,source_support_verified=False),'local_repeat_not_independent_primary_acceptance':True,'qualifying_passes_counted':0}
(out/'candidate-replay.json').write_text(json.dumps(report,indent=2)+'\n');print('REPLAY',delta,error(state['observations']['A']),shadow,support,flush=True)
# Output 4x fresh optical reevaluation. Reference is native detail enlarged only.
for name,box in [('d-stroke',(1040,370,1210,500)),('upper-rim',(650,369,1270,435)),('underside',(650,650,1270,726))]:
    c=copy.deepcopy(case);c['crop']=list(box);scale=4;x0,y0,x1,y1=box
    Y,X=np.mgrid[0:(y1-y0)*scale,0:(x1-x0)*scale];X=x0+(X+.5)/scale-.5;Y=y0+(Y+.5)/scale-.5
    backdrop=cv2.remap(source,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR)
    ref=cv2.resize(target[y0:y1,x0:x1],None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST)
    panels=[ref]
    for recipe in [base,p]:
        C,a=model.render(source,c,recipe,scale=scale);panels.append(C*a[...,None]+backdrop*(1-a[...,None]))
    w=(x1-x0)*scale;h=(y1-y0)*scale;sheet=Image.new('RGB',(w*3,h+32),'#202020');draw=ImageDraw.Draw(sheet)
    for i,(label,C) in enumerate(zip(['Apple native detail x4','Incumbent fresh 4x','Candidate fresh 4x (unaccepted)'],panels)):
        sheet.paste(Image.fromarray(np.uint8(np.clip(C,0,1)*255)),(i*w,32));draw.text((i*w+6,8),label,fill='white')
    sheet.save(out/f'{name}-4x-comparison.png');print('HQ',name,flush=True)
