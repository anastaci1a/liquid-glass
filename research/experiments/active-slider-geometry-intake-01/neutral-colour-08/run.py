"""One train-only bounded neutral affine fit, then fixed-factor cached composites."""
from pathlib import Path
import sys,json,datetime,time,os
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parent;R=ROOT.parents[2];sys.path.insert(0,str(R/'reconstruction'))
from extended_fit import Study
cv2.setNumThreads(1);os.umask(0o002)
protocol=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['deadline_utc'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Original colour deadline reached'
def save(name,x):(P/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def state(key):
 s=Study(ROOT/f'baseline/inputs/{key}');z=np.load(ROOT/f'baseline/{key}-coordinates.npz');n=np.load(ROOT/f'baseline/{key}-native.npz');assert not s.foreground_layers and not s.transmission_layers
 for field,mask in [('glass',s.valid),('rim',s.rim),('held',s.held),('interior',s.valid&~s.rim),('exterior',(s.sd>0)&(s.sd<.35))]:assert np.array_equal(z[field],mask)
 return s,z,n
def feasible(theta):
 g,b=map(float,theta);return np.isfinite(theta).all() and .25<=g<=1.25 and -.1<=b<=.75 and g+b<=1.
def center_rmse(C,T,key):
 l,t,r,b=protocol['center_rectangles'][key];d=(C[t:b,l:r].astype(float)-T[t:b,l:r].astype(float))*255;return float(np.sqrt(np.mean(d*d)))
def fit():
 gate();assert not (P/'fit-started.json').exists(),'Do not repeat fit';save('fit-started.json',dict(utc=utc(),starts=1));Q=np.zeros((2,2));v=np.zeros(2);constant=0.;controls=[];case_models=[]
 for key in ['a','b']:
  gate();s,z,n=state(key);raw=n['sampled_rgb'];inside=z['inside'];H,W=s.valid.shape
  unit=raw.copy();unit[inside]=np.clip(raw[inside].astype(float)*1.+0.,0,1).astype(raw.dtype);C=unit.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);assert np.array_equal(unit,raw) and np.array_equal(C,n['complete']),'Unit response must be exact'
  rr=raw.astype(float);L=(rr*inside[...,None]).reshape(H,2,W,2,3).mean((1,3));clear=(rr*(~inside)[...,None]).reshape(H,2,W,2,3).mean((1,3));A=np.broadcast_to(n['coverage'][...,None],L.shape);residual=clear-s.target_crop.astype(float);train=s.valid&~s.held;assert not (train&s.held).any();x=L[train].ravel();y=A[train].ravel();r=residual[train].ravel();q=np.array([[np.mean(x*x),np.mean(x*y)],[np.mean(x*y),np.mean(y*y)]]);vv=np.array([np.mean(x*r),np.mean(y*r)]);cc=float(np.mean(r*r));Q+=.5*q;v+=.5*vv;constant+=.5*cc
  case_models.append(dict(case=key,training_pixels=int(train.sum()),held_pixels=int(s.held.sum()),Q=q.tolist(),v=vv.tolist(),constant=cc,reference_weight=.5,unclipped_model_unit_max_residual=float(abs((L+clear)-C).max())))
  controls.append(dict(case=key,unit_samples_exact=True,unit_complete_exact=True,center_baseline_rgb_rmse=center_rmse(C,s.target_crop,key),raw_before_material_clips=dict(below_zero=int((raw[inside]<0).sum()),above_one=int((raw[inside]>1).sum()))))
 save('zero-control.json',dict(utc=utc(),controls=controls,new_rays=0,new_graph_calls=0,new_source_queries=0,new_filters=0,new_baseline_renders=0,cached_unit_composite_controls=2))
 vertices=[np.array([.25,-.1]),np.array([1.1,-.1]),np.array([.25,.75])];points=[('baseline',np.array([1.,0.]))]+[(f'vertex{i}',p) for i,p in enumerate(vertices)]
 if np.linalg.det(Q)>0:points.append(('unconstrained_stationary',np.linalg.solve(Q,-v)))
 for i in range(3):
  a=vertices[i];b=vertices[(i+1)%3];d=b-a;den=float(d@Q@d);t=float(np.clip(-(d@(Q@a+v))/den,0,1)) if den>0 else 0.;theta=a+t*d
  if i==1:theta[1]=1.-theta[0]
  if i==0:theta[1]=-.1
  if i==2:theta[0]=.25
  points.append((f'edge{i}',theta))
 evaluations=[];best=None
 for label,theta in points:
  gate();assert len(evaluations)<128;ok=bool(feasible(theta));loss=float(theta@Q@theta+2*v@theta+constant);evaluations.append(dict(label=label,gain=float(theta[0]),bias=float(theta[1]),white_response=float(theta.sum()),strictly_feasible=ok,unclipped_train_mse=loss))
  if ok and (best is None or loss<best['unclipped_train_mse']):best=evaluations[-1]
 assert best and feasible([best['gain'],best['bias']]);save('fit.json',dict(status='ONE_TRAIN_ONLY_PROPOSAL',Q=Q.tolist(),v=v.tolist(),constant=constant,condition_number=float(np.linalg.cond(Q)),case_models=case_models,evaluations=evaluations,quadratic_evaluations=len(evaluations),starts=1,proposal=best,held_used=False,center_guard_used_in_fit=False,center_training_overlap="Original training center pixels participate; held pixels excluded. Supplemental center guard is not optimized.",fit_limits='Unclipped float64 quadratic model. Actual sample response/clipping/float32 composition and all guards decide. Held and centers are checks only.',finished_utc=utc()));print(json.dumps(best),flush=True)
def guards(now,old,hist=False):return {**{k:now[k]['rmse']<=old[k]['rmse'] for k in ['glass','rim','held','interior']},'E':now['E']<=old['E'],'ssim':now['ssim']>=old['ssim'],'exterior':now['exterior']['rmse']<=old['shadow' if hist else 'exterior']['rmse']}
def trial(factor):
 gate();assert factor in protocol['factors'];fit=json.loads((P/'fit.json').read_text());tag=str(factor).replace('.','p');assert not (P/f'{tag}-started.json').exists(),'Trial already attempted';g=1.+factor*(fit['proposal']['gain']-1.);b=factor*fit['proposal']['bias'];assert feasible([g,b]),'Strict parameter feasibility failure; do not project or waive';save(f'{tag}-started.json',dict(utc=utc(),factor=factor,gain=g,bias=b,white_response=g+b))
 results=[];ledger=json.loads((P/'ledger.json').read_text()) if (P/'ledger.json').exists() else dict(candidate_composite_observations=0,candidate_pairs=0,new_rays=0,new_graph_evaluations=0,new_source_queries=0,new_filters=0,new_baseline_renders=0,unit_cached_composite_controls=2,proposal_fits=1,quadratic_evaluations=fit['quadratic_evaluations'])
 original=json.loads((ROOT/'proposal.json').read_text());baseline=json.loads((ROOT/'baseline/result.json').read_text())
 for key in ['a','b']:
  gate();s,z,n=state(key);inside=z['inside'];required=np.repeat(np.repeat(z['required'],2,0),2,1);raw=n['sampled_rgb'];pre=raw[inside].astype(float)*g+b;post=np.clip(pre,0,1);samples=raw.copy();samples[inside]=post.astype(raw.dtype);assert np.array_equal(samples[~inside],raw[~inside]);H,W=s.valid.shape;C=samples.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);lens=(samples*inside[...,None]).reshape(H,2,W,2,3).mean((1,3));clear=n['clear_premultiplied'];assert np.array_equal((samples*(~inside)[...,None]).reshape(H,2,W,2,3).mean((1,3)),clear)
  scores=s.scores(C);scores['E']=float(np.sqrt(scores['loss']));ext=z['exterior'];scores['exterior']=dict(pixels=int(ext.sum()),rmse=float(np.sqrt(np.mean(((C-s.target_crop)[ext]*255)**2))));base=next(x['scores'] for x in baseline['observations'] if x['case']==key);historic=next(x['original_scores'] for x in original['cases'] if x['key']==key);cr=center_rmse(C,s.target_crop,key);br=center_rmse(n['complete'],s.target_crop,key);guard=guards(scores,base);guard['center_rgb']=cr<=br
  clips={}
  for label,mask in [('whole',np.ones(len(pre),bool)),('required',required[inside])]:
   a=raw[inside][mask];q=pre[mask];zpost=post[mask];clips[label]=dict(source_before_response_below=int((a<0).sum()),source_before_response_above=int((a>1).sum()),response_before_clip_below=int((q<0).sum()),response_before_clip_above=int((q>1).sum()),response_after_clip_below=int((zpost<0).sum()),response_after_clip_above=int((zpost>1).sum()))
  rr=raw.astype(float);L=(rr*inside[...,None]).reshape(H,2,W,2,3).mean((1,3));cl=(rr*(~inside)[...,None]).reshape(H,2,W,2,3).mean((1,3));model=g*L+b*n['coverage'][...,None]+cl;train=s.valid&~s.held;actual_train=float(np.mean((C[train].astype(float)-s.target_crop[train].astype(float))**2));model_train=float(np.mean((model[train]-s.target_crop[train])**2));result=dict(case=key,scores=scores,versus_H1_and_center=guard,historical_guards=guards(scores,historic,True),center=dict(baseline_rgb_rmse=br,candidate_rgb_rmse=cr,bounds=protocol['center_rectangles'][key]),clip_counts=clips,model_residual=dict(max_abs=float(abs(model-C).max()),train_model_mse=model_train,train_actual_mse=actual_train),clear_exact=True,coverage_exact=True)
  # Preserve response BEFORE clipping separately; clear input is already retained in H1.
  np.savez_compressed(P/f'{tag}-{key}-native.npz',inside_response_before_clip=pre,sampled_rgb=samples,lens_premultiplied=lens,clear_premultiplied=clear,coverage=n['coverage'],pre_foreground=C,complete=C)
  sheet=Image.new('RGB',(3*W+4,H+48),'white');draw=ImageDraw.Draw(sheet)
  for col,(label,arr) in enumerate([('Apple',s.target_crop),('H1 original seed',n['complete']),(f'Neutral affine factor {factor}',C)]):sheet.paste(Image.fromarray(np.uint8(np.rint(np.clip(arr,0,1)*255))),(col*(W+2),48));draw.text((col*(W+2)+8,16),label,fill='black')
  sheet.save(P/f'{tag}-{key}-comparison.png');ledger['candidate_composite_observations']+=1;assert ledger['candidate_composite_observations']<=8;save('ledger.json',ledger);results.append(result);save(f'{tag}-partial.json',results);print(json.dumps(result),flush=True)
 ledger['candidate_pairs']+=1;assert ledger['candidate_pairs']<=4;save('ledger.json',ledger);save(f'{tag}-result.json',dict(factor=factor,gain=g,bias=b,white_response=g+b,strict_parameter_feasibility=True,observations=results,all_H1_and_center_guards=all(all(x['versus_H1_and_center'].values()) for x in results),historical_all_guards=all(all(x['historical_guards'].values()) for x in results),visible_review_pending=True,finished_utc=utc(),ledger=ledger));print('paired guards',all(all(x['versus_H1_and_center'].values()) for x in results),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='fit':fit()
 else:trial(float(sys.argv[1]))
