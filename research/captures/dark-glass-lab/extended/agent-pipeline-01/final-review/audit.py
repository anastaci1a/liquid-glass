"""Final data/code ledger audit only; no rays, image formation or fits."""
from pathlib import Path
import json,time,hashlib,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'final-review';proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp();assert time.time()<deadline
initial=json.loads((P/'inspection-inputs.json').read_text());state=json.loads((P/'working-state.json').read_text());R={'status':'FINAL_DATA_AND_PROTOCOL_AUDIT','new_rays':0,'new_images':0,'new_fits':0,'independent_full_public_replay':False,'primary_acceptance':False,'cases':{}}
for key in ['a','b']:
 folder=P/f'inputs/{key}';case=json.loads((folder/'case.json').read_text());finger=hashlib.sha256(json.dumps(case,sort_keys=True).encode()).hexdigest();assert finger==initial[key]['case_sha256'];hashes={}
 for name,digest in initial[key]['hashes'].items():
  actual=hashlib.sha256((folder/name).read_bytes()).hexdigest();assert actual==digest;hashes[name]=actual
 for layer in case['foreground_layers']:
  for namekey,digestkey in [('vector_asset','vector_sha256'),('artwork_asset','artwork_sha256')]:
   if namekey in layer:
    name=layer[namekey];actual=hashlib.sha256((folder/name).read_bytes()).hexdigest();assert actual==layer[digestkey];hashes[name]=actual
 masks=np.load(P/f'historical-{key}-masks.npz');counts={k:int(masks[k].sum()) for k in masks.files};assert all(counts[k]==v for k,v in initial[key]['mask_counts'].items());C=np.load(P/state['arrays'][key]['complete']);M=np.load(P/state['arrays'][key]['material']);required=masks['glass']|masks['exterior'];x0,y0,_,_=case['crop']
 for layer in case['foreground_layers']:
  a,b,c,d=layer['box'];required[b-y0:d-y0,a-x0:c-x0]=True
 assert C.dtype==M.dtype==np.float32;assert C.shape==M.shape==(250,1360,3);assert np.isfinite(C[required]).all();assert np.array_equal(np.isnan(C),np.isnan(M));assert not(C[np.isfinite(C)]<0).any() and not(C[np.isfinite(C)]>1).any()
 R['cases'][key]={'canonical_case_sha256':finger,'input_hashes':hashes,'original_mask_counts':counts,'known_values':np.unique(cv2.imread(str(folder/'known.png'),0)).tolist(),'final_arrays':{n:hashlib.sha256((P/state['arrays'][key][n]).read_bytes()).hexdigest() for n in ['material','complete','lens']},'supported_required_pixels':int(required.sum()),'scores':'Exact stored native color-grading halfstep; no rescore/image here','historical_adoption':False}
R['refraction_trials']=json.loads((P/'refraction/trial-ledger.json').read_text())['native_full_images'];assert R['refraction_trials']==8
R['source_proofs']={}
for setting in ['h1','h2','h3/p4','h3/p5']:
 p=json.loads((P/'refraction'/setting/'source-preflight.json').read_text());assert p['status']=='PASS_REQUIRED_SOURCE';assert all(c['counts']['unsupported_required']==c['counts']['incomplete_required']==0 for c in p['cases'].values());R['source_proofs'][setting]={'status':p['status'],'sha256':hashlib.sha256((P/'refraction'/setting/'source-preflight.json').read_bytes()).hexdigest()}
R['crease_erratum']='refraction/checkpoint-crease-erratum.json: two false regular endpoint checkpoints retained. Native wholehpositive scope proof preserved, no rerender. Rootdbff69 publishes correct safetyguard; helper did not replay/adopt a new optical image.'
R['selected_local_scores']={k:v['scores'] for k,v in json.loads((P/'color-grading/result.json').read_text())['selected']['cases'].items()};R['historical_scores']=json.loads((P/'historical-pass03.json').read_text())['scores'];R['outcome']='Overall physical prototype remains worse than historical accepted full model. Local blur/color improvements only; no new accepted optical replacement.';R['finished_unix']=time.time();assert time.time()<deadline;(O/'verification.json').write_text(json.dumps(R,indent=2));print(json.dumps({'status':R['status'],'case_hashes_preserved':True,'source_masks_SVG_artwork_preserved':True,'native_refraction_observations':8,'new_rays_or_images':0,'new_acceptance':False}))
