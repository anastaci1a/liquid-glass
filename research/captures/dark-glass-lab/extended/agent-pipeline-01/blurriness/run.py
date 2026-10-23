"""One predeclared ordinary output-color family; no tracing or input changes."""
from pathlib import Path
import sys,time,json,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path('/evidence/extended/agent-pipeline-01');O=P/'blurriness';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
from geometric_render import coverage_blur
proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Actual20minute stage cap'
assert not (O/'result.json').exists(),'Completed study cannot restart'
gate();G=json.loads((P/'refraction/h1/geometry-checkpoint.json').read_text())['scene'];L=G['original_reference_L'];stages={};proof={'new_geometry_rays':0,'original_whole_source_proof':'refraction/h1/source-preflight.json','max_output_radius':27,'cases':{}}
for key in ['a','b']:
 gate();s=Study(P/f'inputs/{key}');assert not s.transmission_layers
 q=np.load(P/'refraction/h1'/f'{key}-native-paths.npz');X=q['X'];Y=q['Y'];inside=q['inside'];support=q['support']&q['complete'];assert support[inside].all();H,W=s.valid.shape
 alpha=inside.reshape(H,2,W,2).mean((1,3));masks=np.load(P/f'historical-{key}-masks.npz');M0=np.load(P/'refraction/h1'/f'{key}-material.npy');C0=np.load(P/'refraction/h1'/f'{key}-complete.npy')
 x0,y0,x1,y1=s.crop;half=np.array(G['surface_half'])*L;center=np.array(G['center']);margin=min(center[0]-half[0]-x0,x1-center[0]-half[0],center[1]-half[1]-y0,y1-center[1]-half[1])-.5
 assert margin>=27
 proof['cases'][key]={'whole_known_subrays':int(inside.sum()),'required_incomplete':int((inside&~q['complete']).sum()),'min_continuous_crop_padding_less_halfpixel':float(margin),'source_finite_kernel':'No new source filter; output kernel sees only certified lens samples. Outside actual coverage exactlyzero weight, not RGB fill.','required_original_glass':int(masks['glass'].sum()),'source_known_hash':hashlib.sha256((P/f'inputs/{key}/known.png').read_bytes()).hexdigest()}
 # Write the output-filter support proof before source RGB lookup/filter work.
 (O/'output-support-FIRST.json').write_text(json.dumps(proof,indent=2))
 C=np.full((*X.shape,3),np.nan,float);i=np.floor(X[support]).astype(int);j=np.floor(Y[support]).astype(int);fx=(X[support]-i)[:,None];fy=(Y[support]-j)[:,None];src=s.source
 C[support]=(src[j,i]*(1-fx)+src[j,i+1]*fx)*(1-fy)+(src[j+1,i]*(1-fx)+src[j+1,i+1]*fx)*fy
 lens_num=np.where(inside[...,None],C,0).reshape(H,2,W,2,3).mean((1,3));lens=np.divide(lens_num,alpha[...,None],out=np.zeros_like(lens_num),where=alpha[...,None]>0);clear=np.where(inside[...,None],0,C).reshape(H,2,W,2,3).mean((1,3))
 zero=(alpha[...,None]*lens+clear).astype(np.float32);assert np.array_equal(np.isnan(zero),np.isnan(M0));ok=np.isfinite(M0);diff=float(abs(zero[ok]-M0[ok]).max());assert np.array_equal(zero[ok],M0[ok]),('Decomposition zero control',key,diff)
 complete=s.apply_foreground(zero.copy());ok=np.isfinite(C0);assert np.array_equal(complete[ok],C0[ok]);assert np.array_equal(np.isnan(complete),np.isnan(C0))
 np.save(O/f'{key}-lens-color.npy',lens);np.save(O/f'{key}-clear-premultiplied.npy',clear);np.save(O/f'{key}-coverage.npy',alpha)
 stages[key]=(s,masks,lens,clear,alpha,M0,C0)
proof['zero_controls']='Both M and complete PIXEL EXACT, NaN/support patterns exact; no source/map/foreground fit';proof['saved_before_candidates_unix']=time.time();(O/'output-support-FIRST.json').write_text(json.dumps(proof,indent=2));ledger=[]
def score(s,masks,C):
 r=s.scores(C);err=(C-s.target_crop)*255;r['E']=float(np.sqrt(r['loss']));r['exterior']={'pixels':int(masks['exterior'].sum()),'rmse':float(np.sqrt(np.mean(err[masks['exterior']]**2)))};fg=[];x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];e=err[b-y0:d-y0,a-x0:c-x0];fg.append(float(np.mean(e*e)))
 r['foreground_MSE']=fg;return r
bases={key:score(v[0],v[1],v[-1]) for key,v in stages.items()}
for sigma in proto['settings_sigma_native_px']:
 gate();row={'sigma_native_px':sigma,'sigma_over_L':sigma/L,'finite_radius':int(np.ceil(3*sigma)),'cases':{}}
 for key,(s,masks,lens,clear,alpha,M0,C0) in stages.items():
  B=coverage_blur(lens,alpha,sigma);M=(B*alpha[...,None]+clear).astype(np.float32);C=s.apply_foreground(M.copy());r=score(s,masks,C);b=bases[key];guards={x:r[x]['rmse']<=b[x]['rmse'] for x in ['glass','rim','held','interior','exterior']};guards.update(E=r['E']<=b['E'],ssim=r['ssim']>=b['ssim']);guards.update({f'foreground{k}':v<=b['foreground_MSE'][k] for k,v in enumerate(r['foreground_MSE'])})
  original_required=masks['glass']|masks['exterior'];raw=B[alpha>0];native=M[np.isfinite(M).all(2)];clips={'lens_float64_min':float(raw.min()),'lens_float64_max':float(raw.max()),'lens_float64_below0':int((raw<0).sum()),'lens_float64_above1':int((raw>1).sum()),'native_float32_below0':int((native<0).sum()),'native_float32_above1':int((native>1).sum())};assert clips['native_float32_below0']==clips['native_float32_above1']==0
  cropstats={};x0,y0,_,_=s.crop
  for name,(a,b,c,d) in json.loads((P/'refraction/h1/protocol.json').read_text())['reference_crops'].items():
   m=np.zeros(s.valid.shape,bool);m[max(0,b-y0):min(M.shape[0],d-y0),max(0,a-x0):min(M.shape[1],c-x0)]=True;m&=s.valid
   if m.any():e=(C-s.target_crop)[m]*255;cropstats[name]={'pixels':int(m.sum()),'RMSE':float(np.sqrt(np.mean(e*e))),'signed_RGB':e.mean(0).tolist()}
  tag=str(sigma).replace('.','p');np.save(O/f'{key}-sigma{tag}-material.npy',M);np.save(O/f'{key}-sigma{tag}-complete.npy',C);row['cases'][key]={'scores':r,'guards':guards,'all_guards':bool(all(guards.values())),'clipping':clips,'advisory_crops':cropstats}
 row['paired_qualifier']=all(v['all_guards'] for v in row['cases'].values());ledger.append(row);(O/'ledger.json').write_text(json.dumps(ledger,indent=2,allow_nan=False));print(json.dumps({'sigma':sigma,'paired_qualifier':row['paired_qualifier'],'E':{k:v['scores']['E'] for k,v in row['cases'].items()},'failed_guards':{k:[g for g,b in v['guards'].items() if not b] for k,v in row['cases'].items()}}),flush=True)
result={'status':'READY_FOR_VISUAL_REVIEW','baseline':bases,'trials':ledger,'new_geometry_rays':0,'native_pair_evaluations':3,'acceptance':False,'historical_public_baseline_unchanged':True,'finished_unix':time.time()};(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
