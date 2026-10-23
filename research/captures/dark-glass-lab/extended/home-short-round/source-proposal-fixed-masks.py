"""Input-only finite-domain extension assessment; no optical fitting/count."""
import sys,json,hashlib,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
from motion_support import complete
from source_support import coverage_report,masks
from revision_replay import subpixel_support
cv2.setNumThreads(1)
root=Path('/evidence/extended');old=root/'music-home-vector-corrected/paired';out=root/'home-short-round/input-boundary-fixed-mask-proposal';out.mkdir(exist_ok=True);r=json.loads((old/'pass-21.json').read_text())['current'];rows=[]
for i,n in enumerate(['a','b']):
 s=Study(old/n);defined,observed=masks(s);src=complete(s,defined);raw=np.uint8(np.rint(src*255));original=cv2.imread(str(s.folder/'source.png'))[:,:,::-1];assert np.array_equal(raw[defined>=.999],original[defined>=.999]);d=out/n;d.mkdir(exist_ok=True)
 for name in s.case['source_sha256']:
  if name not in ['source.png','known.png'] and not (d/name).exists():(d/name).symlink_to((s.folder/name).resolve())
 for layer in s.case.get('foreground_layers',[]):
  for k in ['vector_asset','artwork_asset']:
   if k in layer and not (d/layer[k]).exists():(d/layer[k]).symlink_to((s.folder/layer[k]).resolve())
 cv2.imwrite(str(d/'source.png'),raw[:,:,::-1]);cv2.imwrite(str(d/'known.png'),np.full(defined.shape,255,np.uint8));cv2.imwrite(str(d/'observed.png'),np.uint8(np.rint(observed*255)))
 case=copy.deepcopy(s.case);case['source_sha256']['source.png']=hashlib.sha256((d/'source.png').read_bytes()).hexdigest();case['source_sha256']['known.png']=hashlib.sha256((d/'known.png').read_bytes()).hexdigest();case['source_sha256']['observed.png']=hashlib.sha256((d/'observed.png').read_bytes()).hexdigest();case['allow_estimated_background']=True;case['source_observation_mask']='observed.png';case['background_estimate']='Nearest defined incident RGB extends the finite recovered mosaic beyond its observation domain. Original observed pixels remain bit-exact. This boundary assumption is not recovered Apple imagery, not an optical calibration, and may not match offscreen content.';(d/'case.json').write_text(json.dumps(case,indent=2)+'\n')
 ns=Study(d)
 # SOURCE confidence must never silently redefine target scoring masks.
 for attr in ['valid','rim','held','indices','weights']:setattr(ns,attr,getattr(s,attr).copy())
 M=ns.render(r['parameters'],np.asarray(r['material']));oldM=np.load(root/f'home-short-round/pass-01/baseline-{i}.npy');score=ns.scores(M,False);delta=(M-oldM)[ns.valid]*255;proof=subpixel_support(ns,r['parameters'],2);assert proof['passed'];row=dict(observation=n,original_loss=r['scores'][i]['loss'],proposed_loss=score['loss'],native_glass_change_rmse=float(np.sqrt(np.mean(delta**2))),native_glass_max_change=float(abs(delta).max()),scores=score,source_centers=coverage_report(ns,r['parameters']),emitted=proof,original_observed_rgb_exact=True,source_sha256=case['source_sha256']);rows.append(row);np.save(out/(n+'-incumbent.npy'),M);print(row,flush=True)
(out/'assessment.json').write_text(json.dumps(dict(status='INPUT PROPOSAL ONLY; NOT ADOPTED, NO OPTICAL GAIN',observations=rows,policy='Never compare optical scores across old/new input epochs. Do not relabel extension as observed content. Lead review required before a new fixed baseline.'),indent=2)+'\n')
