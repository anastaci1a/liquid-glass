"""One finite active-set tone proposal and predeclared cached native factors."""
from pathlib import Path
import json,datetime,hashlib,sys,atexit,os
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parents[2];B=P.parent/'agent-music-search-baseline-01';W=ROOT/'.evidence-working/music-search-baseline-01'
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
os.umask(0o002);cv2.setNumThreads(1)
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,x):(P/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<end,'Original deadline'
assert not (P/'started.json').exists(),'No scientific restart';gate();save('started.json',dict(utc=utc()))
ledger={k:0 for k in p['caps']};atexit.register(lambda:save('ledger.json',ledger))
def count(k,n=1):assert ledger[k]+n<=p['caps'][k],k;ledger[k]+=int(n);save('ledger.json',ledger)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
for x in json.loads((B/'manifest.json').read_text())['files']:assert sha(B/x['file'])==x['sha256']
for x in json.loads((B/'code-pin.json').read_text())['files']:assert sha(ROOT/x['file'])==x['sha256']
data={};identity=[]
for key in ['a','b']:
 gate();count('original_reference_mask_points',240*235);s=Study(W/key);case=json.loads((B/'cases'/f'{key}.json').read_text());assert s.case==case and not s.transmission_layers
 assert all('response' not in v for v in case.get('foreground_styles',{}).values())
 m={k:v for k,v in np.load(B/f'{key}-masks.npz').items()};z={k:v for k,v in np.load(B/f'{key}-candidate.npz').items()};inside=z['inside'];raw=z['sample_before_response'];H,Wc=s.valid.shape
 assert np.array_equal(m['glass'],s.valid) and np.array_equal(m['rim'],s.rim) and np.array_equal(m['held'],s.held)
 assert np.isfinite(raw[inside]).all() and np.min(raw[inside])>=0 and np.max(raw[inside])<=1
 unit,preclip=neutral_color_response(raw[inside],gain=1.,bias=0.,return_preclip=True);assert np.array_equal(unit,raw[inside]);r=raw.copy();r[inside]=unit;pre=r.reshape(H,2,Wc,2,3).mean((1,3)).astype(np.float32)
 assert np.array_equal(pre,z['pre_foreground'],equal_nan=True);count('identity_composites');C=s.apply_foreground(pre.copy());assert np.array_equal(C,z['complete'],equal_nan=True)
 train=m['glass']&~m['held']&~m['foreground'];assert not (train&m['held']).any() and not (train&m['foreground']).any()
 L=z['lens_premultiplied'];U=z['clear_premultiplied'];alpha=z['coverage'];assert np.isfinite(L[train]).all() and np.isfinite(U[train]).all()
 model0=L+U;count('model_checks');delta=model0[m['required']]-z['pre_foreground'][m['required']].astype(float)
 identity.append(dict(reference=key,pre_foreground_exact=True,complete_exact=True,raw_unit_exact=True,train_pixels=int(train.sum()),held_excluded=int(m['held'].sum()),foreground_guard_pixels=int(m['foreground'].sum()),real_basis_vs_native_float32_max=float(np.max(abs(delta))),baseline_raw_range=[float(raw[inside].min()),float(raw[inside].max())]))
 data[key]=dict(s=s,m=m,z=z,train=train,L=L,U=U,alpha=alpha)
save('identity.json',dict(utc=utc(),records=identity,ledger=ledger.copy(),note='Only two cached unit controls; no old common.py import, source filter, lookup or optical render.'))
# Real-arithmetic train objective, equal reference weights, foreground excluded.
Q=np.zeros((2,2));f=np.zeros(2);const=0.;train_summary=[]
for key,d in data.items():
 t=d['train'];x=np.stack([d['L'][t].ravel(),np.repeat(d['alpha'][t],3)],-1);y=(d['s'].target_crop.astype(float)[t]-d['U'][t]).ravel();w=.5/len(y);Q+=w*(x.T@x);f+=w*(x.T@y);const+=float(w*(y@y));train_summary.append(dict(reference=key,channels=len(y),weight_per_channel=w))
count('model_checks');eigen=np.linalg.eigvalsh(Q);rank=int(np.linalg.matrix_rank(Q));assert np.isfinite(Q).all() and np.isfinite(f).all() and rank==2,'Unidentified model; stop without extra solve'
proposals=[]
def add(name,theta):
 count('model_checks');theta=np.asarray(theta,float);g,b=map(float,theta);feasible=bool(np.isfinite(theta).all() and 0<=g<=1 and 0<=b<=1-g)
 if not feasible:proposals.append(dict(name=name,gain=g,bias=b,feasible=False,objective=None));return
 for q in proposals:
  if q['feasible'] and q['gain']==g and q['bias']==b:q.setdefault('aliases',[]).append(name);return
 count('complete_quadratic_checks');obj=float(theta@Q@theta-2*f@theta+const);proposals.append(dict(name=name,gain=g,bias=b,feasible=True,objective=obj))
add('identity',[1.,0.]);add('zero_vertex',[0.,0.]);add('white_vertex',[0.,1.])
add('edge_bias_zero',[np.clip(f[0]/Q[0,0],0,1),0.])
add('edge_gain_zero',[0.,np.clip(f[1]/Q[1,1],0,1)])
v=np.array([1.,-1.]);origin=np.array([0.,1.]);edge_t=float(np.clip(v@(f-Q@origin)/(v@Q@v),0,1));add('edge_white_point_one',[edge_t,1-edge_t]);add('unconstrained_interior',np.linalg.solve(Q,f))
best=min((x for x in proposals if x['feasible']),key=lambda x:x['objective']);gstar,bstar=best['gain'],best['bias'];old=next(x['objective'] for x in proposals if x['name']=='identity');assert best['objective']<old,'No supported descent; stop before native factors'
# Verify the retained basis represents the declared train objective; no foreground surrogate.
count('model_checks');direct=0.
for d in data.values():
 pred=gstar*d['L']+bstar*d['alpha'][...,None]+d['U'];err=(pred-d['s'].target_crop.astype(float))[d['train']];direct+=.5*float(np.mean(err*err))
model_difference=direct-best['objective'];assert abs(model_difference)<1e-12,'Quadratic representation failure, not an acceptance tolerance'
save('proposal.json',dict(utc=utc(),Q=Q.tolist(),linear=f.tolist(),constant=const,eigenvalues=eigen.tolist(),condition_number=float(eigen[-1]/eigen[0]),rank=rank,training=train_summary,proposals=proposals,best=best,identity_objective=old,direct_train_objective=direct,quadratic_roundoff_difference=model_difference,solver='Finite active-set algebra, one interior linear solve; no optimizer',ledger=ledger.copy(),scope='Real-arithmetic model only; actual per-ray response/AA/compositor metrics decide every candidate.'))
crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];luma=np.array([.2126,.7152,.0722])
def scores(s,pre,C,m):
 out={}
 for label,img in [('original',pre),('complete',C)]:
  count('score_calls');count('SSIM_metric_Gaussian_calls',5);count('SSIM_metric_mask_erosions');r=s.scores(img);r['E']=float(np.sqrt(r['loss']));err=(C-s.target_crop)*255;r['exterior_RMSE']=float(np.sqrt(np.mean(err[m['exterior']]**2)));r['foreground_RMSE']=float(np.sqrt(np.mean(err[m['foreground']]**2)));out[label]=r
 return out
def diagnostics(im,d):
 out={};s=d['s'];x0,y0,_,_=s.crop
 for name,(a,b,c,e) in crops.items():
  tile=im[b-y0:e-y0,a-x0:c-x0].astype(float);target=s.target_crop[b-y0:e-y0,a-x0:c-x0].astype(float);finite=np.isfinite(tile).all(2);err=(tile-target)[finite]*255;dy=err@luma;dc=err-dy[:,None];valid=d['m']['glass'][b-y0:e-y0,a-x0:c-x0]&(d['alpha'][b-y0:e-y0,a-x0:c-x0]==1)&finite;Y=tile@luma*255;T=target@luma*255;diff=[];td=[]
  for ax in [0,1]:
   v=(valid[1:]&valid[:-1]) if ax==0 else(valid[:,1:]&valid[:,:-1]);diff.extend(np.diff(Y,axis=ax)[v].tolist());td.extend(np.diff(T,axis=ax)[v].tolist())
  diff=np.array(diff);td=np.array(td);out[name]=dict(original_bounds=[a,b,c,e],finite_pixels=int(finite.sum()),RGB_RMSE=float(np.sqrt(np.mean(err**2))),luma_RMSE=float(np.sqrt(np.mean(dy**2))),chroma_RMSE=float(np.sqrt(np.mean(dc**2))),signed_RGB=err.mean(0).tolist(),detail_pairs=len(diff),luma_adjacent_RMS=float(np.sqrt(np.mean(diff**2))) if len(diff) else None,target_luma_adjacent_RMS=float(np.sqrt(np.mean(td**2))) if len(diff) else None,luma_difference_error_RMS=float(np.sqrt(np.mean((diff-td)**2))) if len(diff) else None)
 return out
trials=[];qualifier=None
for factor in p['actual_factors']:
 gate();g=1+factor*(gstar-1);b=factor*bstar;count('model_checks');assert 0<=g<=1 and 0<=b<=1-g,'Actual factor outside triangle; stop without correction';records=[];name={1:'full',.5:'half',.25:'quarter',.125:'eighth'}[factor]
 for key,d in data.items():
  gate();s,m,z=d['s'],d['m'],d['z'];inside=z['inside'];raw=z['sample_before_response'];H,Wc=d['alpha'].shape;graded,preclip=neutral_color_response(raw[inside],gain=g,bias=b,return_preclip=True);after=raw.copy();after[inside]=graded;assert np.array_equal(after[~inside],raw[~inside],equal_nan=True)
  pre64=after.reshape(H,2,Wc,2,3).mean((1,3));pre=pre64.astype(np.float32);count('candidate_composites');C=s.apply_foreground(pre.copy());assert np.isfinite(C[m['required']]).all() and np.array_equal(C[~m['foreground']],pre[~m['foreground']],equal_nan=True)
  count('model_checks');model=g*d['L']+b*d['alpha'][...,None]+d['U'];valid=m['required'];rounding=dict(model_vs_native_before_float32_max=float(np.max(abs(model[valid]-pre64[valid]))),model_cast_vs_native_float32_max=float(np.max(abs(model.astype(np.float32)[valid]-pre[valid]))),model_cast_different_channels=int(np.count_nonzero(model.astype(np.float32)[valid]!=pre[valid])))
  now=scores(s,pre,C,m);old=json.loads((B/f'{key}-result.json').read_text());guards={}
  for label,base in [('original','original_mask_scores_on_physical_pre_foreground'),('complete','completed_image_scores')]:
   a=now[label];o=old[base];gs={k:a[k]['rmse']<=o[k]['rmse'] for k in ['glass','rim','held','interior']};gs.update({k:a[k]<=o[k] for k in ['E','exterior_RMSE','foreground_RMSE']});gs['SSIM']=a['ssim']>=o['ssim'];guards[label]=gs
  part=m['glass']&(d['alpha']<1);assert part.sum()==38;part_err=float(np.sqrt(np.mean(((C-s.target_crop)[part]*255)**2)));guards['partial_boundary']=part_err<=old['partial_boundary']['complete_RMSE'];clips_before=[int((raw[inside]<0).sum()),int((raw[inside]>1).sum())];clips_raw=[int((preclip<0).sum()),int((preclip>1).sum())];clips_after=[int((graded<0).sum()),int((graded>1).sum())];guards['no_clipping_shortcut']=clips_raw==[0,0]
  clear=np.where((~inside)[...,None],after,0).reshape(H,2,Wc,2,3).mean((1,3));assert np.array_equal(clear,d['U'],equal_nan=True)
  row=dict(reference=key,factor=factor,gain=g,bias=b,scores=now,guards=guards,strict_all=bool(all(guards['original'].values()) and all(guards['complete'].values()) and guards['partial_boundary'] and guards['no_clipping_shortcut']),partial_pixels=38,partial_RMSE=part_err,clipping_before_response=clips_before,clipping_before_actual_clip=clips_raw,clipping_after_response=clips_after,preclip_range=[float(preclip.min()),float(preclip.max())],clear_exact=True,rounding=rounding,fixed_crops=diagnostics(C,d))
  np.savez_compressed(P/f'{name}-{key}-candidate.npz',sample_after_response=after,preclip_inside=preclip,inside=inside,coverage=d['alpha'],clear_premultiplied=clear,lens_premultiplied=np.where(inside[...,None],after,0).reshape(H,2,Wc,2,3).mean((1,3)),pre_foreground=pre,complete=C)
  records.append(row);save(f'{name}-{key}-result.json',row);print(name,key,row['strict_all'],now['complete']['E'],flush=True)
 trial=dict(name=name,factor=factor,gain=g,bias=b,records=records,strict_pair=all(x['strict_all'] for x in records));trials.append(trial);save('trials.json',dict(trials=trials,ledger=ledger.copy()));gate()
 if trial['strict_pair']:qualifier=name;break
save('result.json',dict(utc=utc(),status='NUMERICAL_QUALIFIER_PENDING_VISUAL_PRIMARY' if qualifier else 'NO_STRICT_PAIR',qualifier=qualifier,trials=trials,remaining_factors_not_run=p['actual_factors'][len(trials):],proposal=best,ledger=ledger.copy(),selected_state_unchanged=True,new_pass_count=0,source_proof_transfer='Same retained raw samples, inside/coverage/clear, source/known/case/vector/style and source-map finite kernel; no changed source lookup.',limits=['Empirical encoded response before AA; not physical radiance.','Historical recipe receipt mismatch and original ordering deviation retained.','No independent geometry or PSF claim; no automatic adoption.']))
