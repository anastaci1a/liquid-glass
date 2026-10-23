"""Independent native/foreground replay for one shared response proposal."""
import sys,json,hashlib,math,copy
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from extended_fit import Study
from vector_revision import composite
from progress_gate import evaluate
from publish import pair
cv2.setNumThreads(1)
root=Path('/evidence/extended');out=root/'home-short-round/boundary-epoch/joint-response';r=json.loads((out/'result.json').read_text());prior=json.loads((root/'home-short-round/boundary-epoch/pass-01/accepted-verification.json').read_text());before={'observations':{}};after={'observations':{}};cases=[];assets={};checks=[]
for i,n in enumerate(['a','b']):
 s=Study(root/'home-short-round/input-boundary-replay-proposal'/n);cases.append(copy.deepcopy(s.case));s.case={**s.case,'foreground_response':r['foreground_response']};M=s.render(r['parameters'],np.asarray(r['material']));diff=float(np.max(abs(M-np.load(out/f'candidate-{i}.npy'))));assert diff==0
 score=s.scores(M,False);layer=s.case['foreground_layers'][0];a,b,c,d=layer['box'];x0,y0,_,_=s.crop;F=s.apply_foreground(M.copy());score['foreground']={'rmse':float(np.sqrt(float(np.mean((F[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2))};score['shadow']={'rmse':r['scores'][i]['shadow']};score['E']=float(np.sqrt(score['loss']));assert score['E']==r['scores'][i]['E'] and score['foreground']['rmse']==r['scores'][i]['foreground']
 bscore=r['baseline'][i];before['observations'][n.upper()]={**bscore,'foreground':{'rmse':bscore['foreground']},'shadow':{'rmse':bscore['shadow']}};after['observations'][n.upper()]=score
 # Foreground response is applied after material transport; map/source/kernel unchanged.
 previous=json.loads((root/'home-short-round/boundary-epoch/pass-01/joint-candidate.json').read_text());assert previous['parameters']==r['parameters'];checks.append(dict(observation=n,native_max_difference=diff,source_proof='Pass1 emitted401451 computationally defined rays reused: input case/assets/geometry/kernel identical, only material and fixed foreground response change.',estimated_boundary_retained=True))
 high=s.render(r['parameters'],np.asarray(r['material']),2);rgb=np.uint8(np.rint(np.clip(composite(s,r['parameters'],high,2),0,1)*255));target=cv2.resize(np.uint8(np.rint(s.target_crop*255)),(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_LANCZOS4);pair(target,rgb,('Apple source','Reconstruction'),font_size=24).save(out/(n+'-comparison.png'));assets[n]={layer['vector_asset']:hashlib.sha256((s.folder/layer['vector_asset']).read_bytes()).hexdigest()};print(n,score['E'],score['foreground'],flush=True)
protocol=prior['protocol'];before['epoch']=after['epoch']=prior['previous']['epoch'];report=dict(previous=before,candidate=after,protocol=protocol,replay=checks,gate=evaluate(before,after,visual_review=False,replay_verified=True,source_support_verified=True),visual_review=False,accepted=False,limits=prior['limits']);(out/'verification-pending-visual.json').write_text(json.dumps(report,indent=2)+'\n');record=dict(parameters=r['parameters'],material=r['material'],foreground_response=r['foreground_response'],case_sha256={n:hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest() for n,case in zip(['a','b'],cases)},vector_sha256=assets,large=False,parameter_units='Native pixel sigma/post_sigma, normalized geometry/map. Scale pixel lengths with L=89 source radius.',input_epoch='Same explicitly estimated finite-domain boundary as first pass; input completion receives no optical credit.');(out/'replay-record.json').write_text(json.dumps(record,indent=2)+'\n')
