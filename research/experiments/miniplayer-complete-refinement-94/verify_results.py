"""Own algebraic replay: separate formulas, original scoring and fixed masks."""
from material_common import *
from ellipse_edge_effects import pixel_rule_batch
from scipy.special import ellipe
OUT=BASE/'verification';P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
fx=metric_functions(charge);score=fx['score']
def read(p,keys):
 first[str(p.relative_to(ROOT))]=sha(p)
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p) as z:return {k:z[k] for k in keys}
def independent_lift(image,alpha,e,s):
 out=image.copy();use=alpha>0;C=image[use].astype(np.float64)
 linear=np.where(C<=.04045,C/12.92,((C+.055)/1.055)**2.4);m=np.max(linear,axis=1);n=np.divide(linear,m[:,None],out=np.zeros_like(linear),where=m[:,None]>0)
 t=1-np.exp(-e*alpha[use]);peak=m+(1-m)*t
 result=np.empty_like(linear)
 for c in range(3):result[:,c]=peak*((1-s*t)*n[:,c]+s*t)
 result[m==0]=0;encoded=np.where(result<=.0031308,12.92*result,1.055*result**(1/2.4)-.055);out[use]=encoded;return out

def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 # Independent Minkowski area from exact ellipse perimeter, not quadrature mass.
 controls=[]
 for half,radius in [((.4,.25),.1),((.25,.4),.1),((.49,.11),.05)]:
  a,b=np.array(half)-radius;major,minor=max(a,b),min(a,b);expected=np.pi*a*b+4*radius*major*ellipe(1-(minor/major)**2)+np.pi*radius**2
  pts,w,ids=pixel_rule_batch([[0,0]],half,radius,32,charge);err=abs(float(w.sum())-expected);assert err<1e-10;assert np.max(abs(np.sum(w[:,None]*pts,axis=0)))<1e-14;controls.append(dict(half=half,radius=radius,exact_area=float(expected),quadrature_area=float(w.sum()),error=err))
 save('area-controls.json',controls);data=load_data(charge,first);records=[];shadow=json.loads((BASE/'shadow/result.json').read_text());high=json.loads((BASE/'highlight/result.json').read_text());fits=json.loads((BASE/'highlight/fits.json').read_text());fields={}
 for member in ['expanded','compact']:
  fields[member]=read(BASE/f'shadow/{member}-field.npz',['field'])['field'];p=BASE/f'highlight/{member}-order16.npz';alpha=read(p,['alpha'])['alpha'];data[(member,'a')]['alpha']=alpha;data[(member,'b')]['alpha']=alpha
 for (member,k),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;charge('identity_composites',1);C=s.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(C,z['complete'],equal_nan=True);assert score(s,C,d['m'],d['partial'],d['crops'])==d['before']
  tasks=[]
  for row in shadow['records']:
   if (row['member'],row['reference'])!=(member,k):continue
   strength=row['strength'];path=BASE/f'shadow/{member}-{k}-s{strength}.npz';saved=read(path,['pre_foreground','complete']);v=z['encoded_subrays'].copy();clear=~z['inside']&z['supported']
   # Four explicit phase planes, independently checking the exterior multiplier.
   for c in range(3):plane=v[...,c];plane[clear]=z['encoded_subrays'][...,c][clear]*(1-strength*fields[member][clear])
   pre=(v[:,::2]+v[:,1::2]).reshape(H,2,W,3).sum(1)*.25;pre=pre.astype(np.float32);C=s.apply_foreground(pre.copy());full=z['coverage']==1;assert np.array_equal(C[full],z['complete'][full]);tasks.append(('shadow',path,saved['complete'],C,row))
  for row in high['records']:
   if (row['member'],row['reference'])!=(member,k):continue
   f=fits[row['candidate']];path=BASE/f'highlight/{member}-{k}-h{row["candidate"]}.npz';saved=read(path,['complete'])['complete'];C=independent_lift(z['complete'],d['alpha'],f['exposure'],f['desaturation']);tasks.append(('highlight',path,saved,C,row))
  row=next(r for r in high['combined'] if (r['member'],r['reference'])==(member,k));f=high['development'];p=BASE/f'shadow/{member}-{k}-s{high["shadow_strength"]}.npz';base=read(p,['complete'])['complete'];path=BASE/f'highlight/{member}-{k}-combined.npz';saved=read(path,['complete'])['complete'];C=independent_lift(base,d['alpha'],f['exposure'],f['desaturation']);tasks.append(('combined',path,saved,C,row))
  for role,path,saved,C,row in tasks:
   charge('replay_composites',1);assert np.array_equal(np.isnan(saved),np.isnan(C));good=np.isfinite(saved);diff=float(np.max(abs(saved[good]-C[good])));assert diff<=P['response_replay_absolute_tolerance'];now=score(s,saved,d['m'],d['partial'],d['crops']);assert now==row['scores'];assert guards(now,d['original'])==row['original_guards'];records.append(dict(file=str(path.relative_to(BASE)),role=role,maximum_absolute_replay_difference=diff,pixel_exact=bool(np.array_equal(saved,C,equal_nan=True)),original_metrics_and_guards_exact=True))
 assert first=={p:sha(ROOT/p) for p in first};save('hashes.json',first);save('ledger.json',ledger);save('result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,own_verification=True,helper_used=False,all_pass=True));print('OWN REPLAY PASS',len(records),max(r['maximum_absolute_replay_difference'] for r in records),flush=True)
try:run()
except Exception as e:save('failure.json',dict(error=repr(e),at=datetime.datetime.now(datetime.timezone.utc).isoformat()));save('ledger.json',ledger);raise
