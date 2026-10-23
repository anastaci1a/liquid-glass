from pathlib import Path
import sys,json,datetime,time,os
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parent;sys.path.insert(0,str(ROOT.parents[2]/'reconstruction'))
from extended_fit import Study
os.umask(0o002);cv2.setNumThreads(1)
protocol=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['deadline_utc'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Shadow deadline'
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def scores(s,z,C):
 q=s.scores(C);q['E']=float(np.sqrt(q['loss']));m=z['exterior'];q['exterior']={'rmse':float(np.sqrt(np.mean(((C-s.target_crop)[m]*255)**2))),'pixels':int(m.sum())};return q
def guards(q,b):return {**{k:q[k]['rmse']<=b[k]['rmse'] for k in ['glass','rim','held','interior','exterior']},'E':q['E']<=b['E'],'ssim':q['ssim']>=b['ssim']}
assert not (P/'started.json').exists(),'No repeats';save('started.json',{'utc':utc()});p=json.loads((ROOT/'frozen-records/review-round--pass-09.json').read_text())['parameters'];crops=json.loads((ROOT/'frozen-records/review-round--pass-09-crops.json').read_text());accepted=json.loads((ROOT/'neutral-colour-08/0p5-result.json').read_text());states={};points=0
ledger={'shadow_field_points_reserved':934200,'shadow_field_points_evaluated':0,'composites':0,'zero_cached_controls':0,'optical_rays':0,'height_calls':0,'source_queries':0,'filters':0,'fits':0};save('ledger.json',ledger)
for key in ['a','b']:
 gate();s=Study(ROOT/f'baseline/inputs/{key}');z=np.load(ROOT/f'baseline/{key}-coordinates.npz');n=np.load(ROOT/f'neutral-colour-08/0p5-{key}-native.npz');C=n['complete'];clear=n['clear_premultiplied'];coverage=n['coverage'];H,W=coverage.shape
 assert not s.foreground_layers and not s.transmission_layers
 for field,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim),('exterior',(s.sd>0)&(s.sd<.35))]:assert np.array_equal(z[field],mask)
 baseline=scores(s,z,C);record=next(x['scores'] for x in accepted['observations'] if x['case']==key);assert baseline==record
 zero=C-np.float32(0)*clear;assert np.array_equal(zero,C);assert np.all(clear[coverage==1]==0)
 ledger['zero_cached_controls']+=1;ledger['shadow_field_points_evaluated']+=H*W;assert ledger['shadow_field_points_evaluated']<=ledger['shadow_field_points_reserved'];save('ledger.json',ledger)
 x0,y0,_,_=s.crop;yy,xx=np.mgrid[:H,:W].astype(np.float32);x=(x0+xx-s.case['center'][0])/s.L;y=(y0+yy-s.case['center'][1])/s.L;q=p['shadow'];*_,(sd,_,_)=s.shape(x-q['offset'][0],y-q['offset'][1],p);unit=np.exp(-.5*(np.maximum(sd,0)/q['sigma'])**2);assert np.isfinite(unit).all() and (unit>=0).all() and (unit<=1).all()
 np.savez_compressed(P/f'{key}-field.npz',unit_shadow=unit,shadow_boundary_coordinate=sd)
 states[key]=(s,z,n,unit,baseline);save(f'{key}-zero.json',{'complete_exact':True,'fully_covered_clear_zero':True,'masks_exact':True,'scores_exact':True,'field_points':H*W,'partial_scored_pixels':int((z['glass']&(coverage<1)).sum())})
results=[]
for factor in protocol['factors']:
 pair=[]
 for index,key in enumerate(['a','b']):
  gate();s,z,n,unit,base=states[key];C0=n['complete'];clear=n['clear_premultiplied'];cov=n['coverage'];opacity=p['shadow']['opacity']*factor;attenuation=(unit*opacity).astype(np.float32);C=C0-attenuation[...,None]*clear
  assert np.array_equal(C[cov==1],C0[cov==1]);assert np.isfinite(C).all();q=scores(s,z,C);g=guards(q,base);partial=z['glass']&(cov<1)
  metrics={}
  for name,rec in crops['observations'][index]['states'][-1].items():
   l,t,r,b=rec['bounds_pixels'];target=s.target_crop[t:b,l:r];metrics[name]={'bounds_pixels':rec['bounds_pixels'],'baseline_rgb_rmse':float(np.sqrt(np.mean(((C0[t:b,l:r]-target)*255)**2))),'candidate_rgb_rmse':float(np.sqrt(np.mean(((C[t:b,l:r]-target)*255)**2)))}
  item={'case':key,'factor':factor,'opacity':opacity,'scores':q,'guards':g,'fully_covered_exact':True,'partial_scored_pixels':int(partial.sum()),'partial_baseline_rmse':float(np.sqrt(np.mean(((C0-s.target_crop)[partial]*255)**2))),'partial_candidate_rmse':float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2))),'fixed_crops':metrics,'raw_below_zero':int((C<0).sum()),'raw_above_one':int((C>1).sum())};tag=str(factor).replace('.','p');np.savez_compressed(P/f'{tag}-{key}-native.npz',complete=C,pre_foreground=C,attenuation=attenuation,clear_after=clear*(1-attenuation[...,None]),coverage=cov);pair.append(item);ledger['composites']+=1;assert ledger['composites']<=6;save('ledger.json',ledger);save(f'{tag}-{key}-result.json',item);print(key,factor,g,flush=True)
 pair_ok=all(all(x['guards'].values()) for x in pair);results.append({'factor':factor,'observations':pair,'all_original_guards':pair_ok});save('result.json',{'status':'PENDING_VISUAL_REVIEW' if pair_ok else 'REJECTED','trials':results,'ledger':ledger,'last_scientific_evaluation_utc':utc(),'baseline_retained':'Accepted tone with shadow zero','source_proof':'Sampling, finite kernels and all original masks unchanged. Modeled support is not observed radiance.'})
 if pair_ok:break
print('Closed shadow evaluations',utc(),flush=True)
