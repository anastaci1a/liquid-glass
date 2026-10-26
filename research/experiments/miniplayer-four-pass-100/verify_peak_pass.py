"""Own independent arithmetic replay of a frozen completed pass."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile,importlib.util,copy,traceback
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;OUT=BASE/sys.argv[1];P=json.loads((OUT/'protocol.json').read_text());recipe=json.loads((OUT/'final-recipe.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'])
spec=importlib.util.spec_from_file_location('verify_common',ROOT/'research/experiments/miniplayer-middle-ground-99/material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=BASE/P['native']
caps=dict(Studies=4,mask_points=1121600,numeric_bytes=3000000000,bitmap_pixels=50000000,score_calls=4,metric_Gaussians=20,metric_erosions=4,composites=8,environment_points=2243200,diagnostic_pixels=512)
ledger=dict.fromkeys(caps,0);first={};results=[];observations=[]
def finite_record(v):
 if isinstance(v,dict):return {k:finite_record(x) for k,x in v.items()}
 if isinstance(v,list):return [finite_record(x) for x in v]
 return None if isinstance(v,float) and not np.isfinite(v) else v
def save(n,v):(OUT/n).write_text(json.dumps(finite_record(v),indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END;assert ledger[k]+n<=caps[k],(k,n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def load(p,keys):
 first[str(p.relative_to(ROOT))]=c.sha(p)
 with zipfile.ZipFile(p) as z:
  for key in keys:
   with z.open(key+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in keys}
def dec(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
def enc(v):
 assert v.min()>=0
 return np.where(v<=.0031308,12.92*v,1.055*v**(1/2.4)-.055)
def foreground(s,pre,art):
 # Independently rebuild just the declared artwork rectangle; preserve order.
 from extended_fit import geometry
 t=copy.copy(s);t.foreground_layers=[]
 for box,alpha,color in s.foreground_layers:
  if tuple(box) not in s.artwork_layers:t.foreground_layers.append((box,alpha,color));continue
  a,b,e,f=box;w=round((e-a)*art['scale']);h=round((f-b)*art['scale']);x=round((a+e-w)/2);y=round((b+f-h)/2-art['up'])
  source=s.artwork_layers[tuple(box)][0];rgb=cv2.resize(source,(w,h),interpolation=cv2.INTER_AREA)
  iy,ix=np.indices((h,w));distance=geometry(ix-(w-1)*.5,iy-(h-1)*.5,[w*.5,h*.5],art['radius'])[0];coverage=np.clip(.5-distance,0,1)
  t.foreground_layers.append(([x,y,x+w,y+h],coverage,rgb))
 charge('composites',1);return t.apply_foreground(pre.copy())
def rim(body,guide,alpha):
 out=body.copy();ok=alpha>0;B=dec(body[ok].astype(float));G=dec(guide[ok].astype(float));m=np.max(G,axis=1,keepdims=True)
 lift=.4378927114042099*(1-m)**3;ratio=(G+lift)/(m+lift)
 intrinsic=3*(m+.4378927114042099)/(3*(m+.4378927114042099)+1-m)
 maximum=B.max(axis=1,keepdims=True);peak=np.maximum(intrinsic,maximum+.12*(1-maximum))
 E=peak*np.power(ratio,recipe['chroma']);v=enc(E);v[np.all(body[ok]==1,axis=1)]=1.
 out[ok]=body[ok]+alpha[ok,None]*(v-body[ok]);return out
save('verification-start.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'deadline':END.isoformat(),'array_tolerance':1e-7,'optical_calls':0,'new_source_queries':0})
try:
 data=c.load_data(charge,first);score=c.metric_functions(charge)['score'];qcache={};acache={};scache={}
 for m in ['expanded','compact']:
  q=load(c.NATIVE/f'{m}-paths.npz',['primary_power','front_reflection_power','front_reflection_direction','inside']);I=q['inside'];charge('environment_points',int(I.sum()));theta=np.rad2deg(np.arccos(np.clip(q['front_reflection_direction'][I,2],-1,1)));u=np.clip((theta-30)/10,0,1);v=np.clip((80-theta)/10,0,1);q['light']=q['front_reflection_power'][I]*(u*u*(3-2*u))*(v*v*(3-2*v));qcache[m]=q
  integ=json.loads((OUT/'integration.json').read_text());order=max(x['order'] for x in integ if x['member']==m);acache[m]=load(OUT/f'{m}-alpha{order}.npz',['alpha'])['alpha'][recipe['outline_index']];scache[m]=load(OUT/f'{m}-shadow{recipe["shadow_index"]}.npz',['field'])['field']
 for (m,r),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;I=z['inside'];q=qcache[m];raw=z['raw_source'] if recipe['sigma']==6.075 else load(OUT/f'{m}-{r}-blur{recipe["sigma"]}-samples.npz',['raw_source'])['raw_source'];sub=raw.copy();graded=raw[I]*recipe['gain']+recipe['bias'];assert graded.min()>=0 and graded.max()<=1
  sub[I]=enc(q['primary_power'][I,None]*dec(graded)+4*q['light'][:,None]);clear=~I&z['supported'];sub[clear]=sub[clear]*(1-recipe['shadow']['opacity']*scache[m][clear,None]);pre=sub.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  body=foreground(s,pre,recipe['artwork']);guide=foreground(s,raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32),recipe['artwork']);C=rim(body,guide,acache[m]);saved=load(OUT/f'{m}-{r}-final.npz',['complete','pre_foreground']);finite=np.isfinite(saved['complete']);err=float(np.max(abs(C[finite]-saved['complete'][finite])));preerr=float(np.nanmax(abs(pre-saved['pre_foreground'])));assert err<=1e-7 and preerr<=1e-7;assert np.array_equal(np.isnan(C),np.isnan(saved['complete']))
  actual=score(s,C,d['m'],d['partial'],d['crops']);receipt=json.loads((OUT/f'{m}-{r}-final-metrics.json').read_text());assert c.guards(actual,d['original'])==receipt['original_guards'];results.append(dict(member=m,reference=r,max_error=err,pre_foreground_error=preerr,metrics_exact=actual==receipt['scores'],E_difference=actual['E']-receipt['scores']['E'],original_guard_decisions_match=True))
  center=d['center']+np.array([-.5,0]);half=d['half']+np.array([1.5,0]);x0,y0,_,_=s.crop;y=int(np.ceil(center[1]+half[1]+.5));xs=[int(round(center[0])),int(round(center[0]-half[0])),int(round(center[0]+half[0])),x0+1,s.crop[2]-2]
  for x in xs:
   i,j=y-y0,x-x0
   if not(0<=i<H and 0<=j<W):continue
   charge('diagnostic_pixels',1);observations.append(dict(member=m,reference=r,x=x,y=y,target=(s.target_crop[i,j]*255).tolist(),source=(s.source[y,x]*255).tolist(),result=(C[i,j]*255).tolist(),conditional_source=True,shadow_unit_white=float(255*(1-recipe['shadow']['opacity']*scache[m][2*i,2*j]))))
  if m=='expanded':
   for x in [1160,1280,1400]:
    for y in [325,501]:
     i,j=y-y0,x-x0;charge('diagnostic_pixels',1);observations.append(dict(member=m,reference=r,x=x,y=y,role='fixed yellow diagnostic',target=(s.target_crop[i,j]*255).tolist(),result=(C[i,j]*255).tolist(),guide=(guide[i,j]*255).tolist(),alpha=float(acache[m][i,j])))
 assert first=={k:c.sha(ROOT/k) for k in first};save('verification.json',{'passed':True,'records':results,'ledger':ledger,'first_last_hashes':first,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Independent response, power, integration and artwork reconstruction; shared original foreground chain and metrics. No retracing or source sampling.'});save('fixed-diagnostics.json',observations)
 print('FOUR OWN REPLAYS PASS',results,flush=True)
except Exception as e:save('verification-failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'ledger':ledger,'records':results});raise
