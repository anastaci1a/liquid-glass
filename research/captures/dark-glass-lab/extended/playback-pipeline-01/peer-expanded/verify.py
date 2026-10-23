"""Primary cached-material verification; no optical/source sampling."""
import os,time,json,hashlib,sys
from pathlib import Path
import numpy as np,cv2
from geometric_render import coverage_blur,neutral_color_response
os.umask(2);cv2.setNumThreads(1);START=time.time();DEADLINE=START+6*60;D=Path('/evidence/extended/playback-pipeline-01/peer-expanded');P=Path('/evidence/extended/agent-pipeline-01');sys.path.insert(0,str(P/'code'))
from extended_fit import Study
result=json.loads((P/'color-grading/result.json').read_text());sel=result['selected'];preflight=json.loads((P/'refraction/h1/source-preflight.json').read_text());blur=json.loads((P/'blurriness/ledger.json').read_text());base=next(x for x in blur if x['sigma_native_px']==6.75);rows={}
for key in ['a','b']:
 assert time.time()<DEADLINE;s=Study(P/f'inputs/{key}');masks=np.load(P/f'historical-{key}-masks.npz');assert np.array_equal(s.valid,masks['glass']);assert np.array_equal(s.rim,masks['rim']);assert np.array_equal(s.held,masks['held']);known=hashlib.sha256((P/f'inputs/{key}/known.png').read_bytes()).hexdigest();assert known==preflight['cases'][key]['source_known_sha256']
 alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');clear=np.load(P/'blurriness'/f'{key}-clear-premultiplied.npy');lens=np.load(P/'blurriness'/f'{key}-lens-color.npy');assert np.isfinite(lens[alpha>0]).all();baseline_lens=coverage_blur(lens,alpha,6.75);baseline_M=(alpha[...,None]*baseline_lens+clear).astype(np.float32);saved_base_M=np.load(P/'blurriness'/f'{key}-sigma6p75-material.npy');assert np.array_equal(baseline_M,saved_base_M,equal_nan=True);baseline_C=s.apply_foreground(baseline_M.copy());assert np.array_equal(baseline_C,np.load(P/'blurriness'/f'{key}-sigma6p75-complete.npy'),equal_nan=True)
 # Independently call the root common response (not the helper's multiply-only expression).
 tone=neutral_color_response(lens,sel['g'],sel['b']);B=coverage_blur(tone,alpha,6.75);M=(alpha[...,None]*B+clear).astype(np.float32);C=s.apply_foreground(M.copy());assert np.array_equal(M,np.load(P/'color-grading'/f'{key}-step0.5-material.npy'),equal_nan=True);assert np.array_equal(C,np.load(P/'color-grading'/f'{key}-step0.5-complete.npy'),equal_nan=True)
 def measure(v):
  scores=s.scores(v);scores['E']=float(np.sqrt(scores['loss']));e=(v-s.target_crop)*255;scores['exterior']={'pixels':int(masks['exterior'].sum()),'rmse':float(np.sqrt(np.mean(e[masks['exterior']]**2)))};scores['foreground_MSE']=[];x0,y0,_,_=s.crop
  for layer in s.case['foreground_layers']:
   a,b,c,d=layer['box'];scores['foreground_MSE'].append(float(np.mean(e[b-y0:d-y0,a-x0:c-x0]**2)))
  return scores
 score=measure(C);before=measure(baseline_C);assert score==sel['cases'][key]['scores'];assert before==base['cases'][key]['scores'];guards={n:score[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};guards.update(E=score['E']<=before['E'],ssim=score['ssim']>=before['ssim']);guards.update({f'foreground{i}':a<=b for i,(a,b) in enumerate(zip(score['foreground_MSE'],before['foreground_MSE']))});assert all(guards.values());np.savez(D/f'{key}-replayed.npz',material=M,complete=C,alpha=alpha)
 rows[key]={'complete_pixel_difference':0,'material_pixel_difference':0,'baseline_pixel_difference':0,'scores_exact':True,'guards':guards,'E':[before['E'],score['E']],'known_sha256':known,'source_proof_transfers':'Same optical map/source/finite kernels/alpha/compositor; only commonneutral gain/bias changes, no new source lookups','case_fingerprint':hashlib.sha256(json.dumps(s.case,sort_keys=True).encode()).hexdigest()}
(D/'verification.json').write_text(json.dumps({'status':'PRIMARY_CACHED_NATIVE_VERIFICATION_PASS','rows':rows,'g':sel['g'],'b':sel['b'],'new_optical_rays':0,'new_source_RGB_queries':0,'full_optical_renders':0,'cached_material_replays':2,'wall_seconds':time.time()-START,'budget_seconds':360,'historical_public_adoption':False},indent=2)+'\n');print((D/'verification.json').read_text())
