"""Independent public replay, emitted-ray checks and HQ images; no fitting."""
import sys,json,hashlib,time
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction']
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from revision_replay import clean_composite,subpixel_support,transmission_signature
from source_support import coverage_report,supported
from progress_gate import evaluate
from publish import pair
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-segmented-selector');out=Path('/evidence/extended/selector-short-round/pass-01');candidate=json.loads((out/'candidate.json').read_text());p=candidate['parameters'];co=np.asarray(candidate['material']);studies=[Study(root),Study(root/'second-observation')]
protocol=dict(cases=[s.case for s in studies],metric='E²=.7glassRMSE²+.3rimRMSE²; original native2x2 glass/rim masks. Exterior0<originalsd<.35L, complete clean source composite.')
epoch=hashlib.sha256(json.dumps(protocol,sort_keys=True).encode()).hexdigest();before={'epoch':epoch,'observations':{}};after={'epoch':epoch,'observations':{}};proofs=[]
for i,(name,s) in enumerate(zip(['A','B'],studies)):
 pred=s.render(p,co);saved=np.load(out/f'candidate-{i}.npy');assert np.max(np.abs(pred-saved))==0
 full=clean_composite(s,p,pred);ext=(s.sd>0)&(s.sd<.35);sc=s.scores(pred);sc['shadow']={'rmse':float(np.sqrt(np.mean(((full-s.target_crop)[ext]*255)**2)))}
 before['observations'][name]=candidate['baseline'][i];after['observations'][name]=sc
 proof=dict(observation=name,center=coverage_report(s,p),subpixels=subpixel_support(s,p,4),transmission_signature=transmission_signature(s,p,4))
 proof['passed']=supported(s,proof['center']) and proof['subpixels']['passed'];proofs.append(proof)
 hi=s.render(p,co,4);whole=clean_composite(s,p,hi,4);rgb=np.uint8(np.rint(np.clip(whole,0,1)*255));Image.fromarray(rgb).save(out/f'{name.lower()}-render.png')
 target=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_LANCZOS4)
 pair(target,rgb,('Apple source','Reconstruction (4x)'),font_size=64).save(out/f'{name.lower()}-comparison.png')
 print(name,sc['loss'],proof['subpixels'],flush=True)
report=dict(previous=before,candidate=after,support=proofs,protocol=protocol,gate=evaluate(before,after,visual_review=False,replay_verified=True,source_support_verified=all(p['passed'] for p in proofs)),limits='Independent pixels exactly equal proposal; known legacy blur/refraction mismatch remains. No claim of Apple parity; source colors and hidden selected-text layout remain modeled estimates.')
(out/'verification-pending-visual.json').write_text(json.dumps(report,indent=2)+'\n')
