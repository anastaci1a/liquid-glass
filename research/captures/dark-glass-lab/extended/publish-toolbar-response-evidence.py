"""Assemble independently reviewed toolbar revision3 evidence and fresh figures."""
import sys,json,copy,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from PIL import Image
from publish import pair
from progress_gate import evaluate
from vector_foreground import _coverage
cv2.setNumThreads(1)
repo=Path('/workspace/docs/liquid-glass');public=repo/'experiments/reconstruction/studies/archive-plus/review-round';assets=repo/'assets';root=Path('/evidence/extended');out=root/'toolbar-response-primary-review';proposal=root/'helper-toolbar-work/agent-toolbar-response-trials/first-proposal';inputs=Path('/tmp/agent-toolbar-evidence-package/inputs')
prev=json.loads((public/'pass-02-verification.json').read_text());p=json.loads((proposal/'recipe.json').read_text());measurement=json.loads((proposal/'measurement.json').read_text());replay=json.loads((out/'verification.json').read_text());scores=json.loads((out/'hq/scores.json').read_text());controls=json.loads((out/'public-controls.json').read_text())
assert controls['passed'];assert replay['public_complete_max_difference']==0 and replay['public_material_max_difference']==0
assert scores['glass']['all_glass']['rmse']==replay['scores']['glass'];assert measurement['all_nonregression']
oldp=json.loads((public/'pass-02.json').read_text());keys=set(oldp)|set(p)
assert all(oldp.get(k)==p.get(k) for k in keys-{'model','material','intensity_response'})
for name,digest in p['source_sha256'].items():assert hashlib.sha256((inputs/name).read_bytes()).hexdigest()==digest
for layer in p['foreground_layers']:assert hashlib.sha256((inputs/layer['asset']).read_bytes()).hexdigest()==layer['sha256']
sourceproof=copy.deepcopy(prev['source_support']);sourceproof['reused_from']='pass-02-verification.json';sourceproof['reused_file_sha256']=hashlib.sha256((public/'pass-02-verification.json').read_bytes()).hexdigest();sourceproof['reason']='Exact geometry, source, Gaussian widths, coverage, output grid and foregrounds unchanged; new operation is a pointwise power after existing source lookups. Public code diff and recipe equality reviewed.'
state=measurement['scores'];assert state['epoch']==prev['candidate']['epoch']
for key in ['glass','rim']:assert state['observations']['A'][key]['rmse']==replay['scores'][key]
assert state['observations']['A']['shadow']==replay['scores']['exterior']
fg={name:dict(before=prev['foreground'][name]['rmse'],after=value['rmse'],passed=value['rmse']<=prev['foreground'][name]['rmse']) for name,value in scores['foreground'].items()};assert all(v['passed'] for v in fg.values())
visual=dict(reviewer='primary agent',artifacts=['Independent native Apple/incumbent/candidate stack','Fresh full4x comparison','Fresh upper/d/underside4x crops'],result='Accept incremental color/contrast improvement; no new geometric seam or displaced glyph. Underside tonal error increases slightly and remains explicitly unresolved, rather than treated as a solved feature.',remaining=['Underside reflections remain too distinct and the advisory crop worsens','d-stroke curvature unchanged','Estimated hidden source, provisional shadow width and approximate archive glyph remain'])
gate=evaluate(prev['candidate'],state,visual_review=True,replay_verified=True,source_support_verified=True);assert gate['accepted']
record=dict(epoch=state['epoch'],candidate=state,gate=gate,foreground=fg,source_support=sourceproof,independent_replay=replay,controls=controls,visual_review=visual,qualification='Third verified toolbar improvement in this round; one predeclared shared-power/common-material proposal, not additional passes for controls or renders.',study=dict(gamma=p['intensity_response']['gamma'],shared_offsets=measurement['shared_offsets'],material_only_E=replay['material_only_ablation']['E']),limits='Empirical encoded-RGB power and affine material calibration. Strong parameter/source ambiguity remains; no identified Apple pipeline, physical geometry or independent-background validation.')
# Preserve original visible-composite crop convention and exact positions.
a,b,c,d=p['case']['crop'];T=np.asarray(Image.open(inputs/'target.png'),np.float32)[b:d,a:c]/255;current=np.load(out/'complete.npy');mat=np.load(out/'material.npy');alpha=np.load(out/'alpha.npy');oldmat=np.load('/tmp/agent-toolbar-inner-settlement/material.npy');trans=np.ones_like(alpha)
for layer in p['foreground_layers']:trans*=1-_coverage((inputs/layer['asset']).read_bytes(),tuple(p['case']['crop']),tuple(layer['placement']),1)
previous=current-(mat-oldmat)*alpha[...,None]*trans[...,None];masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');hi=np.asarray(Image.open(out/'hq/render.png'));hiT=cv2.resize(np.uint8(np.rint(T*255)),(hi.shape[1],hi.shape[0]),interpolation=cv2.INTER_LANCZOS4);rows=[]
for name,box,asset in [('upper rim',[650,369,1270,435],'match-regular-rim.png'),('d-stroke',[960,450,1120,550],'toolbar-d-stroke-current.png'),('underside',[650,650,1270,726],'toolbar-underside-current.png')]:
 x0,y0,x1,y1=box;x0-=a;x1-=a;y0-=b;y1-=b;roi=np.zeros(T.shape[:2],bool);roi[y0:y1,x0:x1]=True;mask=roi&masks['glass'];rows.append(dict(name=name,box_native=box,visible_rmse=[float(np.sqrt(np.mean(((im-T)[roi]*255)**2))) for im in [previous,current]],glass_rmse=[float(np.sqrt(np.mean(((im-T)[mask]*255)**2))) for im in [previous,current]],glass_pixels=int(mask.sum())))
 pair(hiT[y0*4:y1*4,x0*4:x1*4],hi[y0*4:y1*4,x0*4:x1*4],('Apple source','Revision 3 (4x)'),font_size=32).save(assets/asset)
oldcrop=json.loads((public/'pass-02-crops.json').read_text())
for old,new in zip(oldcrop['crops'],rows):assert abs(old['glass_rmse'][1]-new['glass_rmse'][0])<1e-6
for name,value in [('pass-03.json',p),('pass-03-verification.json',record),('pass-03-scores.json',scores),('pass-03-crops.json',dict(crops=rows,order=['revision2','revision3'],purpose='Fixed visible-composite crop diagnostics, advisory; underside error increase is retained.'))]:
 with (public/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
shutil.copyfile(out/'hq/comparison.png',assets/'match-regular.png')
(out/'accepted-verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(dict(gate=gate,crops=rows)),flush=True)
