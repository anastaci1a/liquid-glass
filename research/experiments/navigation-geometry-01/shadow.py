"""Bounded underlay-only test with explicit nonlinear-foreground preconditions."""
import datetime,json,time
import numpy as np
from native import OUT,P,setup,save,metrics,preview
from extended_shadow import shadow
from vector_foreground import coverage
deadline=datetime.datetime.fromisoformat(json.loads((OUT/'protocol.json').read_text())['stages'][4]['deadline']).timestamp()
if (OUT/'shadow-result.json').exists():raise RuntimeError('Completed shadow question cannot repeat')
def gate():
 if time.time()>deadline:raise RuntimeError('Shadow deadline reached')
states=[];controls=[]
for k in ['a','b']:
 gate();s,c,surf,known,ext,required=setup(k);raw=np.load(OUT/f'{k}-raw.npz');factor=np.ones(raw['coverage'].shape);x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  a,b,c0,d=layer['box'];style=s.case.get('foreground_styles',{}).get(layer.get('style_key',layer['vector_asset']),{});sl=np.s_[b-y0:d-y0,a-x0:c0-x0]
  if 'response' in style:
   maximum=float(np.nanmax(abs(raw['clear'][sl])))
   controls.append({'reference':k,'style':layer['vector_asset'],'clear_maximum':maximum})
   if maximum!=0:
    save('shadow-result.json',{'status':'INCOMPLETE_NONLINEAR_FOREGROUND_UNDERLAY','controls':controls,'trials':0,'new_rays':0});raise SystemExit(0)
  factor[sl]*=1-coverage(s.folder,layer)*style.get('opacity',layer.get('opacity',1.))
 states.append((k,s,raw,ext,factor))
save('shadow-preconditions.json',{'status':'PASS','nonlinear_response_boxes':controls,'zero_operator_exact':True})
baseline=json.loads((OUT/'raw-result.json').read_text())['references'];trials=[];selected=None
for step in [1.,.5,.25]:
 gate();rows=[]
 for (k,s,raw,ext,factor),old in zip(states,baseline):
  q=dict(P);q['shadow']=dict(P['shadow']);q['shadow']['opacity']*=step
  opacity=shadow(s,q,s.x,s.y)
  delta=raw['clear'].astype(float)*opacity[...,None]*factor[...,None]
  C=(raw['complete'].astype(float)-delta).astype(np.float32)
  z=metrics(s,raw['material'],C,ext);prev=old['scores'];guards={n:z[n]['rmse']<=prev[n]['rmse'] for n in ['glass','rim','held','interior','exterior']};guards.update(E=z['E']<=prev['E'],ssim=z['ssim']>=prev['ssim']);guards.update({n:z['foreground_mse'][n]<=v for n,v in prev['foreground_mse'].items()})
  np.savez_compressed(OUT/f'{k}-shadow-{step:g}.npz',complete=C)
  rows.append({'reference':k,'scores':z,'guards':guards})
 trial={'factor':step,'opacity':q['shadow']['opacity'],'references':rows};trials.append(trial);save('shadow-ledger.json',trials)
 if all(all(r['guards'].values()) for r in rows):selected=trial;break
save('shadow-result.json',{'status':'CACHED_EXTERIOR_COMPONENT_PENDING_REVIEW' if selected else 'NO_PAIRED_QUALIFIER','selected':selected,'trials':len(trials),'new_rays':0,'source_queries':0,'operator':'Existing shared empirical underlay shadow only, fixed width/offset/shape; no physical-light recovery claim.'})
if selected:
 for k,s,raw,ext,factor in states:preview(s,np.load(OUT/f'{k}-shadow-{selected["factor"]:g}.npz')['complete'],k+'-shadow','Generated underlay shadow only')
print(json.dumps({'selected':selected,'trials':len(trials)}),flush=True)
