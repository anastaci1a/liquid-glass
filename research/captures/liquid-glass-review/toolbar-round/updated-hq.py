import sys,json,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image,ImageDraw
import toolbar_candidate as model
from reproduce import CASES,points
from render import case_geometry
out=Path('/tmp/agent-toolbar-run');source=np.asarray(Image.open(out/'source.png')).astype(float)/255;target=np.asarray(Image.open(out/'target.png')).astype(np.float32)/255
case=CASES['regular'];p=json.loads((out/'candidate-with-shadow-recipe.json').read_text());old=json.loads((out/'incumbent-recipe.json').read_text())
C=np.load(out/'candidate-with-shadow-material.npy');a=np.load(out/'candidate-with-shadow-alpha.npy');sh=model.gaussian_coverage_shadow(case,p);B=source[285:845,475:1445];T=target[285:845,475:1445];full=C*a[...,None]+B*(1-sh[...,None])*(1-a[...,None]);_,_,x,y=points(case);sd,*_=case_geometry(case,x,y)
profile=[]
for lo,hi in [(0,10),(10,20),(20,35),(35,55),(55,80)]:
    m=(sd>lo)&(sd<=hi)
    profile.append({'band_native_px':[lo,hi],'pixels':int(m.sum()),'source_rmse':float(np.sqrt(np.mean(((B-T)[m]*255)**2))),'shadow_composite_rmse':float(np.sqrt(np.mean(((full-T)[m]*255)**2)))})
(out/'shadow-profile-diagnostics.json').write_text(json.dumps({'far_bands_advisory_not_acceptance_masks':True,'bands':profile},indent=2)+'\n');print('PROFILES',profile,flush=True)
shadow4=model.gaussian_coverage_shadow(case,p,scale=4);print('SHADOW4',shadow4.shape,flush=True)
for name,box in [('d-stroke-corrected',(960,450,1120,550)),('upper-rim-updated',(650,369,1270,435)),('underside-updated',(650,650,1270,726))]:
    c=copy.deepcopy(case);c['crop']=list(box);scale=4;x0,y0,x1,y1=box
    Y,X=np.mgrid[0:(y1-y0)*scale,0:(x1-x0)*scale];X=x0+(X+.5)/scale-.5;Y=y0+(Y+.5)/scale-.5;back=cv2.remap(source,X.astype(np.float32),Y.astype(np.float32),cv2.INTER_LINEAR)
    ref=cv2.resize(target[y0:y1,x0:x1],None,fx=scale,fy=scale,interpolation=cv2.INTER_NEAREST);panels=[ref]
    for recipe in [old,p]:
        rgb,alpha=model.render(source,c,recipe,scale=scale)
        shadow=shadow4[(y0-285)*4:(y1-285)*4,(x0-475)*4:(x1-475)*4] if recipe is p else 0
        panels.append(rgb*alpha[...,None]+back*(1-np.asarray(shadow)[...,None])*(1-alpha[...,None]))
    w=(x1-x0)*4;h=(y1-y0)*4;sheet=Image.new('RGB',(w*3,h+44),'#202020');draw=ImageDraw.Draw(sheet)
    for i,(label,panel) in enumerate(zip(['Apple native detail x4 (glyph unscored)','Incumbent fresh4x, clean exterior','Pending candidate fresh4x, generated shadow'],panels)):
        sheet.paste(Image.fromarray(np.uint8(np.clip(panel,0,1)*255)),(i*w,44));draw.text((i*w+6,7),label,fill='white')
    sheet.save(out/f'{name}-4x-comparison.png');print('HQ',name,flush=True)
