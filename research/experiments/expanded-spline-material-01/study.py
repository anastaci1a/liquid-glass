"""One common affine response on frozen spline rays; no source evaluation."""
from pathlib import Path
import datetime,json
import numpy as np
from scipy.optimize import minimize
from extended_fit import Study
from vector_foreground import coverage
from geometric_render import neutral_color_response
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;P=ROOT/'research/experiments/expanded-spline-observation-01';OLD=ROOT/'research/experiments/expanded-geometry-02';WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'result.json').exists();g0=p['parameters']['original_gain'];b0=p['parameters']['original_bias'];forms=[];contexts={};objective_forms=[];QA=[]
def gate():assert datetime.datetime.now(datetime.timezone.utc)<deadline,'Five-minute compensation cap'
def form(E,J,mask):
 e=E[mask].reshape(-1);a=J[mask].reshape(-1,2);return np.mean(a[:,:,None]*a[:,None,:],axis=0),np.mean(a*e[:,None],axis=0),float(np.mean(e*e))
for k in ['a','b']:
 gate();s=Study(WORK/k);assert not s.transmission_layers and not s.case.get('foreground_styles');z=np.load(P/f'{k}-candidate.npz');old=np.load(OLD/f'h1-{k}.npz')['complete'];q=np.load(P/'native-paths.npz');inside=q['inside'];H,W=s.valid.shape;raw=z['sample_before_response'];A=np.where(inside[...,None],raw,0).reshape(H,2,W,2,3).mean((1,3));B=np.broadcast_to(z['coverage'][...,None],A.shape);tau=np.ones((H,W));x0,y0,_,_=s.crop
 for box,alpha,color in s.foreground_layers:
  vector=s.vector_layers.get(tuple(box));a,b,c,d=box
  if vector:alpha=coverage(s.folder,vector,1)*vector.get('opacity',1.)
  tau[b-y0:d-y0,a-x0:c-x0]*=(1-alpha).astype(float)
 J=np.stack([A*tau[...,None],B*tau[...,None]],-1)*255;C0=z['complete'];E=(C0.astype(float)-s.target_crop)*255;Eold=(old.astype(float)-s.target_crop)*255;m=np.load(WORK/f'{k}-masks.npz');cohorts={n:m[n] for n in ['glass','rim','held','exterior']};cohorts['interior']=m['glass']&~m['rim'];np.testing.assert_array_equal(cohorts['interior'],s.valid&~s.rim)
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];mask=np.zeros((H,W),bool);mask[b-y0:d-y0,a-x0:c-x0]=True;cohorts[layer.get('vector_asset',layer.get('artwork_asset'))]=mask
 for name,mask in cohorts.items():
  HH,v,c=form(E,J,mask);oldloss=float(np.mean(Eold[mask]**2));reserve=.01 if name not in ['glass','rim','held','interior','exterior'] and np.any(J[mask]!=0) else 0.;norm=oldloss+1.;forms.append(dict(reference=k,cohort=name,H=HH/norm,v=v/norm,c=(c-oldloss+reserve)/norm,raw_old_MSE=oldloss,model_reserve=reserve))
 train=s.valid&~s.held;HH,v,c=form(E,J,train);objective_forms.append((HH,v,c));finite=np.isfinite(z['pre_foreground']).all(2);base64=s.apply_foreground(z['pre_foreground'].astype(float));delta=np.array([.0007,-.0003]);control=s.apply_foreground(z['pre_foreground'].astype(float)+delta[0]*A+delta[1]*B);error=float(np.max(abs(control[finite]-base64[finite]-(J@delta/255)[finite])));assert error<1e-12;QA.append(dict(reference=k,compositor_derivative_max_error=error));contexts[k]=(s,m,raw,inside,z['coverage'],old,cohorts)
HH=sum(z[0] for z in objective_forms)/2;v=sum(z[1] for z in objective_forms)/2;scale=sum(z[2] for z in objective_forms)/2;ledger=[];best=None
class BudgetStop(Exception):pass
def residual(x):return np.array([x@f['H']@x+2*f['v']@x+f['c'] for f in forms])
def cost(x):
 global best
 if len(ledger)>=128 or datetime.datetime.now(datetime.timezone.utc)>=deadline:raise BudgetStop()
 loss=float((x@HH@x+2*v@x)/scale);rr=residual(x);entry=dict(delta=x.tolist(),loss=loss,maximum_constraint_residual=float(rr.max()),strictly_feasible=bool(np.all(rr<=0)));ledger.append(entry)
 if entry['strictly_feasible'] and (best is None or loss<best['loss']):best=entry
 return loss
def jac(x):return (2*HH@x+2*v)/scale
success=False;message=''
try:
 solve=minimize(cost,np.zeros(2),jac=jac,method='SLSQP',bounds=[(-.01,.01)]*2,constraints=[dict(type='ineq',fun=lambda x:-residual(x),jac=lambda x:-np.stack([2*f['H']@x+2*f['v'] for f in forms]))],options=dict(maxiter=100,ftol=1e-12));success=bool(solve.success);message=str(solve.message)
except BudgetStop:message='Declared model/deadline cap'
serial=[{**f,'H':f['H'].tolist(),'v':f['v'].tolist()} for f in forms];(OUT/'forms.json').write_text(json.dumps(serial,indent=2)+'\n');native=[];selected=None
if best:
 for factor in [1.,.5]:
  gate();x=np.asarray(best['delta'])*factor;records=[]
  if np.any(residual(x)>0):break
  for k,(s,m,raw,inside,alpha,old,cohorts) in contexts.items():
   response,preclip=neutral_color_response(raw,gain=g0+x[0],bias=b0+x[1],return_preclip=True);assert np.min(preclip[inside])>=0 and np.max(preclip[inside])<=1;value=np.where(inside[...,None],response,raw);H,W=s.valid.shape;pre=value.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);C=s.apply_foreground(pre.copy());now=s.scores(C);before=s.scores(old);guard={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};guard['loss']=now['loss']<=before['loss'];guard['ssim']=now['ssim']>=before['ssim'];e=(C-s.target_crop)*255;eo=(old-s.target_crop)*255;double={}
   for name,mask in cohorts.items():
    if name not in ['glass','rim','held','interior']:guard[name]=bool(np.mean(e[mask]**2)<=np.mean(eo[mask]**2))
    rawerr=(C[mask].astype(float)-s.target_crop[mask].astype(float))*255;olderr=(old[mask].astype(float)-s.target_crop[mask].astype(float))*255;double[name]=bool(np.mean(rawerr**2)<=np.mean(olderr**2))
   np.savez_compressed(OUT/f'{factor}-{k}.npz',pre_foreground=pre,complete=C);records.append(dict(reference=k,E=float(np.sqrt(now['loss'])),guards=guard,double_residual_guards=double,all_pass=all(guard.values()) and all(double.values())))
  row=dict(factor=factor,gain=g0+x[0],bias=b0+x[1],records=records,paired_qualifier=all(r['all_pass'] for r in records));native.append(row)
  if row['paired_qualifier']:selected=row;break
result=dict(status='STRICT_PAIRED_COMBINED_CANDIDATE' if selected else ('NO_STRICT_NATIVE_QUALIFIER' if native else 'NO_STRICT_MODEL_FEASIBLE_PROPOSAL'),solver_success=success,solver_message=message,model_evaluations=len(ledger),model_ledger=ledger,best_model_feasible=best,analytic_QA=QA,native=native,selected=selected,new_rays=0,new_height_calls=0,new_source_queries=0,filters=0,fits=1,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],model_evaluations=len(ledger),best=best,native=native)),flush=True)
