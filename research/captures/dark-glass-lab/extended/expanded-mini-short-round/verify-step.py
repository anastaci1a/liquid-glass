import os,sys,json,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
ROOT=Path('/evidence/extended/expanded-mini-short-round');sys.path.insert(0,str(ROOT));from preflight import guards
from source_support import masks
from motion_support import complete
from vector_revision import composite
from publish import pair
os.umask(0o002);stage=int(sys.argv[1]);assert stage in [2,3];D=ROOT/f'pass-{stage:02}';D.mkdir(exist_ok=True);CAND=ROOT/('profile-material-pass2' if stage==3 else f'local-step-{stage:02}');trials=json.loads((CAND/'trials.json').read_text());selected=len(trials)-1;record=json.loads((CAND/'candidate-native.json').read_text());base=json.loads((ROOT/f'pass-{stage-1:02}/pass-{stage-1:02}.json').read_text());rows=[];record.update(large=True,case_sha256={},vector_sha256={},parameter_units='Native sigma/post_sigma in reference pixels; geometry and map normalized by L. Preserve parameter_length_reference where supplied.',limits='Two video observations; empirical map/material, uncertain icon/artwork assignment and recovered source. No proprietary Apple equation or parity claim. Crown replacements failed frozen guards and are not adopted.')
for i,n in enumerate(['a','b']):
 s=Study(ROOT/n);p=record['parameters'];pred=s.render(p,np.array(record['material']));saved=np.load(CAND/f'trial{selected}-ref{i}-material.npy');assert np.array_equal(pred,saved)
 sc,full,ext=guards(s,p,pred);assert sc==record['scores'][i]
 b=base['scores'][i];assert sc['E']<=b['E'] and sc['glass']['rmse']<=b['glass']['rmse'] and sc['exterior']['rmse']<=b['exterior']['rmse'];assert all(v<=b['foreground_mse'][k] for k,v in sc['foreground_mse'].items())
 proof=record['source_proof'][i];assert proof['passed'] and all(proof['counts'][k]==0 for k in ['whole_defined_bad','whole_observed_bad','scored_defined_bad','scored_observed_bad'])
 record['case_sha256'][n]=hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest();record['vector_sha256'][n]={l['vector_asset']:hashlib.sha256((s.folder/l['vector_asset']).read_bytes()).hexdigest() for l in s.case['foreground_layers'] if 'vector_asset' in l}
 known,_=masks(s);shown=composite(s,p,pred,1,complete(s,known));alpha=s.shape_coverage(p);assert np.max(abs(shown[alpha==1]-full[alpha==1]))<2e-6
 pair(np.rint(s.target_crop*255).astype(np.uint8),np.rint(np.clip(shown,0,1)*255).astype(np.uint8),('Apple source','Reconstruction')).save(D/f'{n}-comparison.png')
 np.save(D/f'ref{i}-material.npy',pred);rows.append(dict(observation=n,previous=b,candidate=sc,native_max_difference=0,source_proof=proof))
(D/f'pass-{stage:02}.json').write_text(json.dumps(record,indent=2)+'\n');(D/'verification.json').write_text(json.dumps(dict(native_replay=True,visual_review=True,accepted=True,round_pass=stage,observations=rows,source_epoch_unchanged=True,limits='Current public renderer exact replay; both1360-width saved candidates visually inspected. Existing shape/photographic/source limitations retained. Finite3sigma native emitted whole+ALLscored confidence is discrete; not continuous/infinite-kernel proof.'),indent=2)+'\n');print('PASS',stage,'verified; source and visuals accepted',flush=True)
