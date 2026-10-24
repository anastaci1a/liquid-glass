"""Independent cached replay only. Primary checkout is mounted read-only."""
from pathlib import Path
import sys,json,hashlib,datetime
import numpy as np
import cv2
R=Path('/research/liquid-glass');O=Path('/research/agent-navigation-spline-223/research/experiments/agent-expanded-contrast-peer-09')
sys.path.insert(0,str(R/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
cv2.setNumThreads(1)
P=R/'research/experiments/expanded-contrast-guard-02';S=R/'research/experiments/expanded-spline-observation-01';B=R/'research/experiments/expanded-geometry-02';W=R/'.evidence-working/expanded-geometry-02'
claimed=json.loads((P/'native-result.json').read_text());protocol=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat('2026-10-24T00:22:03.344+00:00')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<deadline
hashes=[]
def record(f):
 z=dict(file=str(f.relative_to(R)),sha256=hashlib.sha256(f.read_bytes()).hexdigest());hashes.append(z);return z['sha256']
for x in claimed['inputs']:assert record(R/x['path'])==x['sha256']
for f in [R/'reconstruction'/x for x in ['extended_fit.py','geometric_render.py','vector_foreground.py','foreground_response.py']]:record(f)
inside=np.load(S/'native-paths.npz')['inside'];rows=[];counts=dict(identity_composites=0,candidate_composites=0,rays=0,height_evaluations=0,RGB_queries=0,filters=0,fits=0)
for k,expected in zip(['a','b'],claimed['records']):
 gate()
 for f in sorted((W/k).iterdir()):
  if f.is_file():record(f)
 record(W/f'{k}-masks.npz');record(B/f'h1-{k}.npz')
 s=Study(W/k);assert not s.transmission_layers and not s.case.get('foreground_styles')
 for f,h in s.case['source_sha256'].items():assert hashlib.sha256((W/k/f).read_bytes()).hexdigest()==h
 for layer in s.case['foreground_layers']:
  if 'vector_asset' in layer:assert hashlib.sha256((W/k/layer['vector_asset']).read_bytes()).hexdigest()==layer['vector_sha256']
  if 'artwork_asset' in layer:assert hashlib.sha256((W/k/layer['artwork_asset']).read_bytes()).hexdigest()==layer['artwork_sha256']
 z=np.load(S/f'{k}-candidate.npz');candidate=np.load(P/f'{k}-candidate.npz');old=np.load(B/f'h1-{k}.npz')['complete'];m=np.load(W/f'{k}-masks.npz');raw=z['sample_before_response'];H,WW=s.valid.shape
 def replay(g,b):
  v,preclip=neutral_color_response(raw,gain=g,bias=b,return_preclip=True)
  integrated=np.where(inside[...,None],v,raw).reshape(H,2,WW,2,3).mean(axis=(1,3)).astype(np.float32)
  return integrated,s.apply_foreground(integrated.copy()),preclip
 zero,Czero,_=replay(protocol['parameters']['original_gain'],protocol['parameters']['original_bias']);counts['identity_composites']+=1
 assert np.array_equal(zero,z['pre_foreground'],equal_nan=True) and np.array_equal(Czero,z['complete'],equal_nan=True)
 pre,C,clip=replay(claimed['gain'],claimed['bias']);counts['candidate_composites']+=1
 assert np.array_equal(pre,candidate['pre_foreground'],equal_nan=True) and np.array_equal(C,candidate['complete'],equal_nan=True)
 assert np.array_equal(candidate['coverage'],z['coverage'])
 assert np.array_equal(m['glass'],s.valid) and np.array_equal(m['rim'],s.rim) and np.array_equal(m['held'],s.held)
 score=s.scores(C);before=s.scores(old)
 for name in ['glass','rim','held','interior']:assert score[name]==expected['scores'][name] and before[name]==expected['baseline_scores'][name]
 for name in ['ssim','loss']:assert score[name]==expected['scores'][name] and before[name]==expected['baseline_scores'][name]
 assert float(np.sqrt(score['loss']))==expected['scores']['E']
 cohorts={n:m[n] for n in ['glass','rim','held','exterior']};cohorts['interior']=s.valid&~s.rim
 x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];mask=np.zeros((H,WW),bool);mask[b-y0:d-y0,a-x0:c-x0]=True;cohorts[layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')))]=mask
 e32=(C-s.target_crop)*255;o32=(old-s.target_crop)*255;e64=(C.astype(np.float64)-s.target_crop.astype(np.float64))*255;o64=(old.astype(np.float64)-s.target_crop.astype(np.float64))*255
 metrics={};guards={}
 for name,mask in cohorts.items():
  now=float(np.mean(e32[mask]**2));prev=float(np.mean(o32[mask]**2));a64=float(np.mean(e64[mask]**2));b64=float(np.mean(o64[mask]**2));guards[name]=now<=prev and a64<=b64
  assert (a64<=b64)==expected['float64_residual_guards'][name]
  if name=='exterior':assert float(np.sqrt(np.mean(e32[mask]**2)))==expected['scores']['exterior_RMSE']
  if name in expected['scores']['foreground_artwork_MSE']:assert now==expected['scores']['foreground_artwork_MSE'][name] and prev==expected['baseline_scores']['foreground_artwork_MSE'][name]
  metrics[name]=dict(candidate_MSE_float32=now,baseline_MSE_float32=prev,candidate_MSE_float64=a64,baseline_MSE_float64=b64)
 partial=m['glass']&(z['coverage']<1);part=dict(pixels=int(partial.sum()),baseline_RMSE=float(np.sqrt(np.mean(o64[partial]**2))),candidate_RMSE=float(np.sqrt(np.mean(e64[partial]**2))))
 for name,value in part.items():assert value==expected['partial_boundary_advisory'][name]
 clips=[int((clip[inside]<0).sum()),int((clip[inside]>1).sum())];assert clips==[0,0]==expected['clip_counts']
 guards['ssim']=score['ssim']>=before['ssim'];guards['E']=score['loss']<=before['loss'];assert all(guards.values())
 rows.append(dict(reference=k,identity_exact=True,candidate_pre_foreground_exact=True,candidate_complete_exact=True,coverage_exact=True,all_claimed_scores_exact=True,guards=guards,metrics=metrics,E=float(np.sqrt(score['loss'])),SSIM=score['ssim'],partial_boundary=part,clips=clips))
 gate()
for x in hashes:assert hashlib.sha256((R/x['file']).read_bytes()).hexdigest()==x['sha256']
(O/'verification.json').write_text(json.dumps(dict(status='PASS_WITH_LIMITS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,counts=counts,input_code_hashes=hashes,scope='Exact independent cached native response and actual ordered compositor; no paths, source sampling or filters.'),indent=2)+'\n')
print('PASS',counts,flush=True)
