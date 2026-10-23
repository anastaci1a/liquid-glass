"""Public-native replay and 720p-sized, two-reference visual evidence."""
import sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from vector_revision import composite
from revision_replay import subpixel_support,transmission_signature
from source_support import coverage_report,supported
from progress_gate import evaluate
from publish import pair
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'home-short-round/pass-01';inputs=root/'music-home-vector-corrected/paired';r=json.loads((out/'joint-candidate.json').read_text());p=r['parameters'];c=np.asarray(r['candidate']['material']);before={'observations':{}};after={'observations':{}};support=[];cases=[];assets={}
for i,name in enumerate(['a','b']):
 s=Study(inputs/name);cases.append(s.case);M=s.render(p,c);diff=float(np.max(np.abs(M-np.load(out/f'joint-candidate-{i}.npy'))));assert diff==0
 # Replay native whole-glass and actual vector-composited foreground independently.
 score=s.scores(M);full=s.apply_foreground(M.copy());layer=s.case['foreground_layers'][0];a,b,C,D=layer['box'];x0,y0,_,_=s.crop;fg=float(np.mean((full[b-y0:D-y0,a-x0:C-x0]-s.target[b:D,a:C])**2))*255**2
 assert abs(fg-r['candidate']['scores'][i]['foreground']**2)<1e-8
 score['foreground']={'rmse':float(np.sqrt(fg))};score['shadow']={'rmse':r['candidate']['scores'][i]['shadow']}
 old=r['baseline'][i];before['observations'][name.upper()]={**old,'shadow':{'rmse':old['shadow']},'foreground':{'rmse':old['foreground']}};after['observations'][name.upper()]=score
 center=coverage_report(s,p);sub=subpixel_support(s,p,2);proof=dict(observation=name.upper(),center=center,subpixels=sub,transmission_signature=transmission_signature(s,p,2),native_pixel_max_difference=diff,passed=supported(s,center) and sub['passed']);support.append(proof)
 hi=s.render(p,c,2);rgb=np.uint8(np.rint(np.clip(composite(s,p,hi,2),0,1)*255));target=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_LANCZOS4);pair(target,rgb,('Apple source','Reconstruction'),font_size=24).save(out/f'{name}-comparison.png');Image.fromarray(rgb).save(out/f'{name}-render.png')
 assets[name]={layer['vector_asset']:hashlib.sha256((s.folder/layer['vector_asset']).read_bytes()).hexdigest()};print(name,score['loss'],sub,flush=True)
protocol=dict(cases=cases,metric='Original native glass/rim masks and actual vector foreground ROI; historical exterior-only shadow mask retained. Previews are 720p-sized, never used as scoring inputs.')
epoch=hashlib.sha256(json.dumps(protocol,sort_keys=True).encode()).hexdigest();before['epoch']=after['epoch']=epoch
record=dict(parameters=p,material=c.tolist(),cases=cases,vector_sha256=assets)
(out/'replay-record.json').write_text(json.dumps(record,indent=2)+'\n')
report=dict(previous=before,candidate=after,support=support,protocol=protocol,gate=evaluate(before,after,visual_review=False,replay_verified=True,source_support_verified=all(s['passed'] for s in support)),limits='Native scores unchanged by preview size. Same two observed backdrops/source/model, not independent device generalization. New figures use source and generated shadow, plus exact reusable SVG shape; no reference shadow copied.')
(out/'verification-pending-visual.json').write_text(json.dumps(report,indent=2)+'\n')
