from pathlib import Path
import datetime,json,hashlib,sys
import numpy as np
sys.path.insert(0,'/repo/reconstruction')
from extended_fit import Study
from geometric_render import neutral_color_response
P=Path(__file__).resolve().parent
H=Path('/helper'); B=H/'research/experiments/agent-music-search-baseline-01'; C=H/'research/experiments/agent-music-search-neutral-05'
W=H/'.evidence-working/music-search-baseline-01'
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
assert not (P/'verification.json').exists()
def gate(): assert datetime.datetime.now(datetime.timezone.utc)<end
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
files=[B/'native-paths.npz',B/'source-preflight.json',C/'proposal.json',C/'result.json']
for k in ['a','b']:files += [B/f'{k}-candidate.npz',B/f'{k}-masks.npz',C/f'full-{k}-candidate.npz',C/f'full-{k}-result.json',W/k/'case.json',W/k/'source.png',W/k/'target.png',W/k/'known.png']
for row in json.loads((B/'code-pin.json').read_text())['files']:
 f=Path('/repo')/row['file'];assert sha(f)==row['sha256'];files.append(f)
first={str(f):sha(f) for f in files};rows=[]
for k in ['a','b']:
 gate();s=Study(W/k);z=np.load(B/f'{k}-candidate.npz');a=np.load(C/f'full-{k}-candidate.npz');m=np.load(B/f'{k}-masks.npz');r=json.loads((C/f'full-{k}-result.json').read_text())
 raw=z['sample_before_response'];inside=z['inside'];height,width=s.valid.shape
 assert np.isfinite(raw[inside]).all()
 identity=raw.reshape(height,2,width,2,3).mean((1,3)).astype(np.float32)
 assert np.array_equal(identity,z['pre_foreground'],equal_nan=True)
 assert np.array_equal(s.apply_foreground(identity.copy()),z['complete'],equal_nan=True)
 g=r['gain'];b=r['bias'];assert g==0.5193880051291454 and b==0.4473611800152188
 samples=raw.copy();samples[inside]=neutral_color_response(raw[inside],gain=g,bias=b)
 pre=samples.reshape(height,2,width,2,3).mean((1,3)).astype(np.float32)
 complete=s.apply_foreground(pre.copy())
 assert np.array_equal(samples,a['sample_after_response'],equal_nan=True)
 assert np.array_equal(pre,a['pre_foreground'],equal_nan=True)
 assert np.array_equal(complete,a['complete'],equal_nan=True)
 assert np.array_equal(samples[~inside],raw[~inside],equal_nan=True)
 assert np.array_equal(m['glass'],s.valid) and np.array_equal(m['held'],s.held)
 err=(complete-s.target_crop)*255
 for label,img in [('original',pre),('complete',complete)]:
  score=s.scores(img);score['E']=float(np.sqrt(score['loss']));score['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));score['foreground_RMSE']=float(np.sqrt(np.mean(err[m['foreground']]**2)))
  assert score==r['scores'][label],(k,label)
 part=m['glass']&(z['coverage']<1);assert part.sum()==38
 partial=float(np.sqrt(np.mean(err[part]**2)));assert partial==r['partial_RMSE']
 old=z['complete'].astype(float);new=complete.astype(float);target=s.target_crop.astype(float)
 residuals={}
 for name in ['glass','rim','held','interior','exterior','foreground']:
  mask=m[name];old_mse=float(np.mean(((old-target)[mask]*255)**2));new_mse=float(np.mean(((new-target)[mask]*255)**2));assert new_mse<=old_mse
  residuals[name]={'baseline_MSE_f64':old_mse,'candidate_MSE_f64':new_mse}
 rows.append(dict(reference=k,identity_exact=True,graded_samples_exact=True,pre_foreground_exact=True,complete_exact=True,all_reported_scores_exact=True,partial_pixels=int(part.sum()),partial_RMSE=partial,all_f64_residual_guards_pass=True,residuals=residuals))
last={str(f):sha(f) for f in files};assert first==last
gate();out=dict(status='EXACT_REPLAY_AND_RESIDUAL_GUARDS_PASS_PENDING_VISUAL_DECISION',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),references=rows,first_last_hashes_identical=True,inputs=first,counts=dict(identity_composites=2,candidate_composites=2,score_calls=4,original_reference_mask_points=112800,rays=0,height_evaluations=0,source_queries=0,material_filters=0,fits=0),limits='Cached conditional source only. Shared code unchanged. No claim of geometry, radiance or historical epoch equivalence.')
(P/'verification.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print(out['status'])
