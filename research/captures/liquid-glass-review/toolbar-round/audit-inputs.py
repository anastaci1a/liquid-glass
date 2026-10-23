import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/tmp/agent-toolbar-code')
import cv2,numpy as np
from PIL import Image
import settled
from reproduce import CASES,points,masks,scores
from progress_gate import error
root=Path('/evidence/apple-matches/public-settled-confirm');out=Path('/tmp/agent-toolbar-run');out.mkdir(exist_ok=True)
source=np.array(Image.open(root/'regular-source.png').convert('RGB')).astype(float)/255
target=np.array(Image.open(root/'regular-target.png').convert('RGB')).astype(np.float32)/255
case=copy.deepcopy(CASES['regular']);p=copy.deepcopy(settled.RECIPES['regular'])
xs,ys,x,y=points(case);sd,train,held,valid=masks(case,xs,ys,x,y)
np.savez(out/'frozen-masks.npz',glass=valid,rim=valid&(-sd<34),held=held,exterior=(sd>0)&(sd<35))
for n in ['source','target']:(out/f'{n}.png').write_bytes((root/f'regular-{n}.png').read_bytes())
(out/'incumbent-recipe.json').write_text(json.dumps(p,indent=2)+'\n')
protocol={'case':case,'native_size':[1920,1080],'subpixels_per_axis':4,'color':'encoded RGB','quantization':'8-bit PNG source, unquantized float32 output, original target PNG /255','mask_rule':'frozen original masks: sd<-.75, foreground boxes excluded, rim inward<34','exterior':'new fixed diagnostic region 0<sd<35; clean source only, no reconstructed shadow exists','foreground':'copied symbols in legacy display unscored; this trial exports glass and clean backdrop, no pasted symbols'}
(out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
files=['source.png','target.png','frozen-masks.npz','protocol.json'];hashes={f:hashlib.sha256((out/f).read_bytes()).hexdigest() for f in files};epoch=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
material=settled.render(source,case,p);sc=scores(material,target[285:845,475:1445],case);obs={'glass':sc['all_glass'],'rim':sc['rim']}
prior=json.loads((root/'settled-scores.json').read_text())['regular']['scores']
base={'epoch':epoch,'observations':{'A':obs}}
(out/'incumbent.json').write_text(json.dumps(base,indent=2)+'\n');np.save(out/'incumbent-material.npy',material)
# Source is the archived uncovered/registered input, not legacy composed output.
# Source reconstruction explicitly erases the 12:00 lens and its rectangle via paper field.
registration=json.loads((root/'settled-scores.json').read_text())['regular']['registration']
A=np.array(registration['matrix']);contam=np.zeros((1080,1920),np.uint8);contam[350:790,490:1420]=1
estimated=cv2.warpAffine(contam,A,(1920,1080))>0
# Check measured source RGB in estimated area is a smooth field, not the original lens.
blur=cv2.GaussianBlur(source,(0,0),8);region=estimated[285:845,475:1445]
source_crop=source[285:845,475:1445];clean=source_crop.copy();alpha=(sd<=0)[...,None];composite=np.where(alpha,material,clean)
Image.fromarray(np.uint8(np.clip(composite,0,1)*255)).save(out/'incumbent-clean-exterior.png')
Image.fromarray(np.uint8(np.clip(source_crop,0,1)*255)).save(out/'source-crop.png')
Image.fromarray(np.uint8(np.clip(target[285:845,475:1445],0,1)*255)).save(out/'target-crop.png')
report={'epoch':epoch,'input_hashes':hashes,'incumbent_scores':sc,'E':error(obs),'archived_E':error({'glass':prior['all_glass'],'rim':prior['rim']}),'glass_replay_delta':sc['all_glass']['rmse']-prior['all_glass']['rmse'],'source_epoch_change':False,'registration':registration,'source_estimation':{'method':'registered unoccluded text + robust smooth paper; source lens/shadow rectangle erased before applying paper field','estimated_source_pixels_inside_glass':int((region&valid).sum()),'glass_pixels':int(valid.sum()),'estimated_rectangle_high_frequency_rmse_255':float(np.sqrt(np.mean((source-blur)[estimated]**2))*255),'limits':'rectangle replacement assumes blank hidden content; no original shadow copied in this rectangle; exterior estimates and contact residual in legacy compose are not a generated shadow'},'shadow_gate':'unsupported baseline shadow: no generated shadow recipe. New clean-composite exterior diagnostic must be frozen before fitting; any source cleanup is not an improvement.'}
(out/'input-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
