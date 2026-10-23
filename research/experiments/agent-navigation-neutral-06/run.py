"""One shared neutral-tone proposal on exact cached H1; no optical work."""
from pathlib import Path
import sys,os,json,datetime,hashlib,atexit
import numpy as np,cv2
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;ROOT=P.parents[2];Q=P.parent/'agent-navigation-spline-03';PRIMARY=ROOT.parent/'liquid-glass';CACHE=PRIMARY/'research/experiments/navigation-geometry-01';WORK=PRIMARY/'.evidence-working/navigation-geometry-01';sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
os.umask(0o002);cv2.setNumThreads(1);protocol=json.loads((P/'protocol.json').read_text())
ledger=dict(identity_composites=0,quadratic_evaluations=0,solves=0,paired_trials=0,candidate_composites=0,rays=0,height_evaluations=0,source_queries=0,incident_filters=0,output_filters=0,baseline_material_renders=0)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(n,v):(P/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
atexit.register(lambda:save('ledger.json',ledger))
def gate():assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(protocol['deadline'].replace('Z','+00:00')),'Original stage cap'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metric(s,M,C,ext):
 z=s.scores(M);z['E']=float(np.sqrt(z['loss']));z['foreground_mse']={};x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  if layer.get('fit_style',True) and layer['mode']!='transmission':
   a,b,c,d=layer['box'];z['foreground_mse'][layer.get('style_key',layer['vector_asset'])]=float(np.mean((C[b-y0:d-y0,a-x0:c-x0]-s.target[b:d,a:c])**2))*255**2
 z['exterior']={'pixels':int(ext.sum()),'rmse':float(np.sqrt(np.mean((C[ext]-s.target_crop[ext])**2))*255)};return z
def guards(z,b):
 out={k:z[k]['rmse']<=b[k]['rmse'] for k in ['glass','rim','held','interior','exterior']};out.update(E=z['E']<=b['E'],ssim=z['ssim']>=b['ssim']);out.update({k:z['foreground_mse'][k]<=v for k,v in b['foreground_mse'].items()});return out
# Apply only to actual contributing lens colors. Exact native identity comes
# from the original integrated backing plus the changed lens contribution.
def compose_input(M,P0,alpha,g,b):
 response,preclip=neutral_color_response(M,g,b,return_preclip=True);covered=alpha>0;graded=M.copy();graded[covered]=response[covered].astype(M.dtype);pre=P0.copy();pre[covered]=(P0[covered].astype(float)+alpha[covered,None]*(graded[covered].astype(float)-M[covered].astype(float))).astype(P0.dtype)
 return graded,pre,preclip
assert not (P/'started.json').exists(),'No repeated stage';save('started.json',dict(utc=utc()));gate()
for rec in json.loads((Q/'code-pin.json').read_text())['files']:assert sha(ROOT/rec['file'])==rec['sha256']
assert json.loads((Q/'contract-result.json').read_text())['status']=='PASS'
integrity=json.loads((Q/'input-integrity.json').read_text());cases=[];records=[];H=np.zeros((2,2));f=np.zeros(2);const=0.;lo=1.;hi=0.
for ci in integrity['cases']:
 key=ci['case'];assert sha(WORK/key/'case.json')==ci['case_sha256']
 for rec in ci['input_hashes']+ci['vector_hashes']:assert sha(WORK/key/rec['file'])==rec['sha256']
for key in ['a','b']:
 gate();s=Study(WORK/key);old=np.load(CACHE/f'{key}-source-blur.npz');raw=np.load(CACHE/f'{key}-raw.npz');m=np.load(CACHE/f'{key}-masks.npz');zero=np.load(Q/f'{key}-zero-control.npz');M=old['material'];P0=zero['pre_foreground'];alpha=raw['coverage'];clear=raw['clear'];covered=alpha>0;assert np.isfinite(M[covered]).all();assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.held,m['held']);assert (alpha[zero['paint_mask']]==1).all();np.testing.assert_array_equal(P0[covered&(alpha==1)],M[covered&(alpha==1)])
 graded,pre,pc=compose_input(M,P0,alpha,1.,0.);assert np.array_equal(M,graded,equal_nan=True) and np.array_equal(P0,pre,equal_nan=True);assert ledger['identity_composites']<2;ledger['identity_composites']+=1;save('ledger.json',ledger);C=s.apply_foreground(pre.copy());same=np.array_equal(C,old['complete'],equal_nan=True);np.savez_compressed(P/f'{key}-identity.npz',material=M,pre_foreground=P0,complete=C,coverage=alpha,clear=clear);assert same,'Identity mismatch: stop before fit'
 baseline=metric(s,M,C,m['exterior']);prior=next(r['scores'] for r in json.loads((CACHE/'blur-result.json').read_text())['references'] if r['reference']==key);assert baseline==prior
 partial=m['glass']&(alpha<1);pbase=float(np.sqrt(np.mean(((C-s.target_crop)[partial]*255)**2)));train=m['glass']&~m['held']&~zero['paint_mask']&covered;np.savez_compressed(P/f'{key}-train-mask.npz',train=train,original_glass=m['glass'],original_held=m['held']);xx=M[train].astype(float).ravel();yy=s.target_crop[train].astype(float).ravel();weight=.5/len(xx);H+=weight*np.array([[xx@xx,xx.sum()],[xx.sum(),len(xx)]]);f+=weight*np.array([xx@yy,yy.sum()]);const+=weight*(yy@yy);lo=min(lo,float(M[covered].min()));hi=max(hi,float(M[covered].max()));rec=dict(case=key,identity_exact=True,baseline_scores=baseline,baseline_completed_scores=metric(s,C,C,m['exterior']),partial_pixels=int(partial.sum()),partial_RMSE=pbase,train_pixels=int(train.sum()),held_excluded=True,actual_paint_excluded=True,finite_lens_min=float(M[covered].min()),finite_lens_max=float(M[covered].max()),contributing_lens_pixels=int(covered.sum()),before_clips_low=int((M[covered]<0).sum()),before_clips_high=int((M[covered]>1).sum()),dtype=dict(material=str(M.dtype),pre_foreground=str(P0.dtype),clear=str(clear.dtype),coverage=str(alpha.dtype)),inputs={str(p.relative_to(PRIMARY)) if str(p).startswith(str(PRIMARY)) else str(p.relative_to(ROOT)):sha(p) for p in [CACHE/f'{key}-source-blur.npz',CACHE/f'{key}-raw.npz',CACHE/f'{key}-masks.npz',Q/f'{key}-zero-control.npz']});records.append(rec);cases.append(dict(key=key,s=s,M=M,P0=P0,alpha=alpha,clear=clear,oldC=C,m=m,partial=partial,baseline=baseline,completed=rec['baseline_completed_scores'],partial_RMSE=pbase))
save('identity.json',dict(status='PASS_BOTH_EXACT',records=records,utc=utc(),ledger=ledger.copy()));gate()
# One bounded two-variable QP. Halfspaces A theta <= c include exact retained
# finite lens extrema. Edge minimizers use algebraic feasible intervals; each
# unique candidate gets one full constraint+objective evaluation, capped at16.
A=np.array([[-1,0],[1,0],[0,-1],[0,1],[-lo,-1],[hi,1]],float);c=np.array([-.5,1.2,.1,.25,0,1],float);names=['gain_min','gain_max','bias_min','bias_max','actual_min_nonnegative','actual_max_at_most_one'];eig=np.linalg.eigvalsh(H);rank=int(np.linalg.matrix_rank(H));cond=float(np.linalg.cond(H));solver=dict(H=H.tolist(),linear=f.tolist(),constant=const,eigenvalues=eig.tolist(),rank=rank,condition=cond,constraints=[dict(name=n,A=a.tolist(),bound=float(v)) for n,a,v in zip(names,A,c)],range=[lo,hi],evaluations=[],edge_construction=[])
assert rank==2 and np.isfinite(cond),'Rank-deficient proposal: inconclusive, no trial';ledger['solves']=1
cache={}
def evaluate(theta,origin):
 k=tuple(float(t) for t in theta)
 if k in cache:return cache[k]
 assert ledger['quadratic_evaluations']<16;ledger['quadratic_evaluations']+=1;save('ledger.json',ledger);res=A@theta-c;value=float(theta@H@theta-2*f@theta+const);row=dict(origin=origin,coefficients=list(k),residuals=res.tolist(),feasible=bool((res<=0).all()),objective=value);solver['evaluations'].append(row);cache[k]=row;return row
identity=evaluate(np.array([1.,0.]),'identity');candidates=[evaluate(np.linalg.solve(H,f),'unconstrained_interior')]
for i,(normal,bound) in enumerate(zip(A,c)):
 point=normal*(bound/(normal@normal));direction=np.array([-normal[1],normal[0]]);lower=-np.inf;upper=np.inf;empty=False
 for nn,bb in zip(A,c):
  den=float(nn@direction);num=float(bb-nn@point)
  if den>0:upper=min(upper,num/den)
  elif den<0:lower=max(lower,num/den)
  elif num<0:empty=True
 if empty or lower>upper:solver['edge_construction'].append(dict(edge=names[i],empty=True));continue
 den=float(direction@H@direction);assert den>0;t=float(direction@(f-H@point)/den);chosen=min(max(t,lower),upper);theta=point+chosen*direction;solver['edge_construction'].append(dict(edge=names[i],interval=[float(lower),float(upper)],unconstrained_t=t,chosen_t=chosen));candidates.append(evaluate(theta,'edge_'+names[i]))
feasible=[r for r in candidates if r['feasible']];best=min(feasible,key=lambda z:z['objective']) if feasible else None;solver.update(status='PROPOSAL' if best and best['objective']<identity['objective'] else 'NO_SUPPORTED_DESCENT',selected=best,identity=identity,ledger=ledger.copy(),utc=utc());save('proposal.json',solver)
if solver['status']!='PROPOSAL':save('result.json',dict(status='INCONCLUSIVE_OR_NO_SUPPORTED_DIRECTION',solver=solver['status'],ledger=ledger,utc=utc()));sys.exit(0)
gp,bp=best['coefficients'];results=[];luma=np.array([.2126,.7152,.0722]);gate()
for factor in protocol['factors']:
 gate();assert ledger['paired_trials']<4;ledger['paired_trials']+=1;g=1+factor*(gp-1);b=factor*bp;theta=np.array([g,b]);parameter_residuals=A@theta-c;folder=P/f'trial-{ledger["paired_trials"]:02d}';folder.mkdir();pair=[]
 if not (parameter_residuals<=0).all():save('result.json',dict(status='STOP_PARAMETER_INFEASIBLE_NO_WAIVER',factor=factor,residuals=parameter_residuals.tolist(),ledger=ledger,utc=utc()));sys.exit(0)
 for item in cases:
  gate();key,s,M,P0,alpha,clear=item['key'],item['s'],item['M'],item['P0'],item['alpha'],item['clear'];graded,pre,raw=compose_input(M,P0,alpha,g,b);covered=alpha>0;clips=[int((raw[covered]<0).sum()),int((raw[covered]>1).sum())];clear_exact=np.array_equal(clear,item['clear'],equal_nan=True);assert clear_exact and np.array_equal(pre[~covered],P0[~covered],equal_nan=True);assert ledger['candidate_composites']<8;ledger['candidate_composites']+=1;save('ledger.json',ledger);C=s.apply_foreground(pre.copy());required=np.load(Q/f'{key}-support.npz')['required_pixels'];assert np.isfinite(C[required]).all();score=metric(s,graded,C,item['m']['exterior']);completed=metric(s,C,C,item['m']['exterior']);guard=guards(score,item['baseline']);cg=guards(completed,item['completed']);partial=float(np.sqrt(np.mean(((C-s.target_crop)[item['partial']]*255)**2)));extra=dict(partial_boundary=partial<=item['partial_RMSE'],no_actual_clipping=clips==[0,0],clear_exact=clear_exact)
  crops={};x0,y0,_,_=s.crop
  for name,(aa,bb,cc,dd) in protocol['crops'].items():
   aa-=x0;cc-=x0;bb-=y0;dd-=y0;tar=s.target_crop[bb:dd,aa:cc].astype(float);v={}
   for title,arr in [('H1',item['oldC']),('candidate',C)]:
    tile=arr[bb:dd,aa:cc].astype(float);err=(tile-tar)*255;dy=err@luma;ch=err-dy[...,None];lum=tile@luma;v[title]=dict(RGB_RMSE=float(np.sqrt(np.mean(err*err))),luma_RMSE=float(np.sqrt(np.mean(dy*dy))),chroma_RMSE=float(np.sqrt(np.mean(ch*ch))),signed_RGB=err.mean((0,1)).tolist(),luma_std=float(lum.std()*255),horizontal_difference_RMS=float(np.sqrt(np.mean(np.diff(lum,axis=1)**2))*255))
   crops[name]=dict(original_frame_bounds=protocol['crops'][name],native_bounds=[aa,bb,cc,dd],values=v)
  np.savez_compressed(folder/f'{key}-candidate.npz',material=graded,raw_preclip=raw,pre_foreground=pre,complete=C,coverage=alpha,clear=clear)
  Hh,Ww=C.shape[:2];panel=Image.new('RGB',(3*Ww+4,Hh+64),'white');draw=ImageDraw.Draw(panel)
  for i,(title,arr) in enumerate([('Apple',s.target_crop),('Current incident H1',item['oldC']),(f'Neutral factor {factor:g}',C)]):
   valid=np.isfinite(arr).all(2);yy,xx=np.indices(valid.shape);view=np.where(valid[...,None],arr,np.where(((xx//6+yy//6)%2)[...,None],.72,.9));panel.paste(Image.fromarray(np.uint8(np.rint(np.clip(view,0,1)*255))),(i*(Ww+2),64));draw.text((i*(Ww+2)+8,20),title,fill='black')
  panel.save(folder/f'{key}-comparison.png');rec=dict(case=key,factor=factor,gain=g,bias=b,scores=score,completed_scores=completed,guards=guard,completed_guards=cg,supplemental=extra,partial_boundary_RMSE=partial,raw_preclip_range=[float(raw[covered].min()),float(raw[covered].max())],raw_clip_counts=clips,fixed_crops=crops);pair.append(rec)
  (folder/f'{key}-result.json').write_text(json.dumps(rec,indent=2,allow_nan=False)+'\n');print('TRIAL',factor,key,score['E'],guard,cg,extra,flush=True)
 pairgood=all(all(z['guards'].values()) and all(z['completed_guards'].values()) and all(z['supplemental'].values()) for z in pair);record=dict(factor=factor,gain=g,bias=b,parameter_residuals=parameter_residuals.tolist(),records=pair,strict_numeric=pairgood);results.append(record);(folder/'result.json').write_text(json.dumps(record,indent=2)+'\n');save('result.json',dict(status='STRICT_NUMERIC_PENDING_VISIBLE_REVIEW' if pairgood else 'NO_QUALIFIER_SO_FAR',trials=results,ledger=ledger.copy(),utc=utc()));gate()
 if pairgood:break
save('result.json',dict(status='STRICT_NUMERIC_PENDING_VISIBLE_REVIEW' if results[-1]['strict_numeric'] else 'ALL_PREDECLARED_FACTORS_REJECTED',trials=results,ledger=ledger.copy(),finished_utc=utc()));print('STAGE CLOSED',utc(),ledger,flush=True)
