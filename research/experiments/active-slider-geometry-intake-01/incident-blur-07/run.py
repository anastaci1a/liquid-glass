"""Two fixed incident widths from cached H1 coordinates. No trace or surface calls."""
from pathlib import Path
import sys,json,time,datetime,hashlib,os
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parent;REPO=ROOT.parents[2]
sys.path.insert(0,str(REPO/'reconstruction'))
from geometric_render import incident_source_filter
from extended_fit import Study
from PIL import Image,ImageDraw
cv2.setNumThreads(1);os.umask(0o002)
protocol=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['deadline_utc'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Original stage deadline reached'
def save(name,value):(P/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(a):return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
def preflight():
 gate();assert not (P/'source-proof-FIRST.json').exists(),'Do not repeat source proof'
 proofs=[]
 for c in protocol['cases']:
  gate();key=c['key'];z=np.load(ROOT/f'baseline/{key}-coordinates.npz');known=cv2.imread(str(ROOT/f'baseline/inputs/{key}/known.png'),0)>0
  radius=max(t['radius_px'] for t in c['trials']);safe=cv2.erode(known.astype(np.uint8),np.ones((2*radius+1,2*radius+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  inside=z['inside'];required=np.repeat(np.repeat(z['required'],2,0),2,1);ok=np.ones(inside.shape,bool)
  assert z['complete'].all() and z['support'].all()
  for cast in [np.float64,np.float32]:
   X=z['source_X'].astype(cast);Y=z['source_Y'].astype(cast);assert np.isfinite(X).all() and np.isfinite(Y).all();i=np.floor(X).astype(int);j=np.floor(Y).astype(int)
   assert ((i>=0)&(j>=0)&(i+1<known.shape[1])&(j+1<known.shape[0])).all()
   for u,v in [(0,0),(1,0),(0,1),(1,1)]:ok &= np.where(inside,safe[j+v,i+u],known[j+v,i+u])
  assert ok[inside|required].all(),'Undefined required finite footprint: STOP before RGB'
  assert ok.all(),'Unsupported full observation: no fill authorized'
  np.savez_compressed(P/f'{key}-support.npz',support=ok,largest_kernel_safe=safe)
  proofs.append(dict(case=key,radius=radius,whole_subrays=int(inside.sum()),required_subrays=int(required.sum()),union_subrays=int((inside|required).sum()),undefined_required=0,all_grid_supported=True,coordinate_rounding='Both float64 stored positions and float32 OpenCV maps, all four bilinear neighbors',observed_confidence=0,masks={f:dict(count=int(z[f].sum()),sha256=digest(z[f])) for f in ['glass','rim','held','interior','exterior','required','ssim_safe']},source_X_sha256=digest(z['source_X']),source_Y_sha256=digest(z['source_Y'])))
 save('source-proof-FIRST.json',dict(status='PASS_BOTH_LARGEST_KERNELS_BEFORE_RGB',utc=utc(),cases=proofs,new_rays=0,new_graph_evaluations=0,new_RGB_queries=0,smaller_support='Strict finite-radius inclusion; source bytes and bilinear coordinates fixed.'))
 print('Source proof passed both cases before RGB',flush=True)
def guards(now,old,historical=False):
 result={k:now[k]['rmse']<=old[k]['rmse'] for k in ['glass','rim','held','interior']}
 result.update(E=now['E']<=old['E'],ssim=now['ssim']>=old['ssim'],exterior=now['exterior']['rmse']<=old['shadow' if historical else 'exterior']['rmse']);return result
def trial(multiplier):
 gate();assert multiplier in protocol['family'];assert (P/'source-proof-FIRST.json').exists();tag='narrow' if multiplier==.75 else 'wide';assert not (P/f'{tag}-started.json').exists(),'Trial already attempted; inspect existing evidence'
 save(f'{tag}-started.json',dict(multiplier=multiplier,utc=utc()));ledger=json.loads((P/'ledger.json').read_text()) if (P/'ledger.json').exists() else dict(new_rays=0,new_graph_evaluations=0,new_lens_RGB_queries=0,new_clear_RGB_queries=0,new_full_observations=0,new_baseline_renders=0,fits=0)
 observations=[];proposal=json.loads((ROOT/'proposal.json').read_text());base_result=json.loads((ROOT/'baseline/result.json').read_text())
 for c in protocol['cases']:
  gate();key=c['key'];t=next(t for t in c['trials'] if t['multiplier']==multiplier);s=Study(ROOT/f'baseline/inputs/{key}');assert not s.foreground_layers and not s.transmission_layers
  z=np.load(ROOT/f'baseline/{key}-coordinates.npz');old=np.load(ROOT/f'baseline/{key}-native.npz');inside=z['inside'];X=z['source_X'];Y=z['source_Y'];samples=old['sampled_rgb'].copy();known=cv2.imread(str(s.folder/'known.png'),0)>0
  assert np.array_equal(z['glass'],s.valid) and np.array_equal(z['rim'],s.rim) and np.array_equal(z['held'],s.held) and np.array_equal(z['exterior'],(s.sd>0)&(s.sd<.35))
  incident,safe,radius=incident_source_filter(s.source,known,t['sigma_px']);assert radius==t['radius_px'];large=np.load(P/f'{key}-support.npz')['largest_kernel_safe'];assert safe[large].all()
  rr,cc=np.nonzero(inside);ledger['new_lens_RGB_queries']+=len(rr);assert ledger['new_lens_RGB_queries']<=4000000;save('ledger.json',ledger)
  for lo in range(0,len(rr),16000):
   gate();r=rr[lo:lo+16000];col=cc[lo:lo+16000];samples[r,col]=cv2.remap(incident,X[r,col].astype(np.float32)[None],Y[r,col].astype(np.float32)[None],cv2.INTER_LINEAR)[0]
  assert np.isfinite(samples).all();assert np.array_equal(samples[~inside],old['sampled_rgb'][~inside]);H,W=s.valid.shape
  C=samples.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);coverage=old['coverage'];lens=(samples*inside[...,None]).reshape(H,2,W,2,3).mean((1,3));clear=old['clear_premultiplied'];assert np.array_equal((samples*(~inside)[...,None]).reshape(H,2,W,2,3).mean((1,3)),clear)
  lens_color=np.divide(lens,coverage[...,None],out=np.zeros_like(lens),where=coverage[...,None]>0);scores=s.scores(C);scores['E']=float(np.sqrt(scores['loss']));ext=z['exterior'];scores['exterior']=dict(pixels=int(ext.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2))))
  base=next(x['scores'] for x in base_result['observations'] if x['case']==key);historic=next(x['original_scores'] for x in proposal['cases'] if x['key']==key)
  result=dict(case=key,width=t,scores=scores,versus_H1=guards(scores,base),historical_guards=guards(scores,historic,True),clear_samples_exact=True,coverage_exact=True,source_xy_reused=True,clip_counts=dict(below_zero=int((samples<0).sum()),above_one=int((samples>1).sum())))
  np.savez_compressed(P/f'{tag}-{key}-native.npz',sampled_rgb=samples,lens_premultiplied=lens,clear_premultiplied=clear,coverage=coverage,lens_color=lens_color,pre_foreground=C,complete=C)
  sheet=Image.new('RGB',(3*W+4,H+48),'white');draw=ImageDraw.Draw(sheet)
  for col,(label,arr) in enumerate([('Apple',s.target_crop),('H1 seed',old['complete']),(f'Incident multiplier {multiplier}',C)]):sheet.paste(Image.fromarray(np.uint8(np.rint(np.clip(arr,0,1)*255))),(col*(W+2),48));draw.text((col*(W+2)+8,16),label,fill='black')
  sheet.save(P/f'{tag}-{key}-comparison.png');ledger['new_full_observations']+=1;assert ledger['new_full_observations']<=4;save('ledger.json',ledger);observations.append(result);save(f'{tag}-partial.json',observations);print(json.dumps(result),flush=True)
 gate();strict=all(all(x['versus_H1'].values()) for x in observations);save(f'{tag}-result.json',dict(multiplier=multiplier,observations=observations,all_H1_guards=strict,all_historical_guards=all(all(x['historical_guards'].values()) for x in observations),visible_review_pending=True,finished_utc=utc(),ledger=ledger));print('Paired H1 guards:',strict,flush=True)
if __name__=='__main__':
 if sys.argv[1]=='preflight':preflight()
 else:trial(float(sys.argv[1]))
