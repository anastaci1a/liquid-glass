"""Own independent arithmetic replay of a frozen completed pass."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile,importlib.util,copy,traceback
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent;OUT=BASE/sys.argv[1];P=json.loads((OUT/'protocol.json').read_text());recipe=json.loads((OUT/'final-recipe.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'])
spec=importlib.util.spec_from_file_location('verify_common',BASE/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=BASE/P['native']
caps=dict(source_parity_points=64,gap_pixels=20000,Studies=4,mask_points=1121600,numeric_bytes=3000000000,bitmap_pixels=50000000,score_calls=4,metric_Gaussians=20,metric_erosions=4,composites=8,environment_points=2243200,diagnostic_pixels=512)
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
 Y=G@np.array([.2126,.7152,.0722]);floor=.12+.38*(1-Y)**2
 E=1-(1-floor[:,None])*np.power(1-G,1.75);maximum=B.max(axis=1,keepdims=True)
 E*=np.maximum(1,(maximum+.12*(1-maximum))/E.max(axis=1,keepdims=True))
 v=enc(E)
 v=v.astype(body.dtype).astype(float)
 if recipe['endpoint']['exposure']!=1:
  effective=recipe['endpoint']['exposure']
  if recipe['endpoint'].get('chroma_weighted',False):
   raw=guide[ok].astype(float);peak=raw.max(-1);strength=np.divide(peak-raw.min(-1),peak,out=np.zeros_like(peak),where=peak>0);effective=(1+(effective-1)*strength)[:,None]
  v=enc(1-(1-dec(v))**effective)
 if recipe['endpoint']['saturation']!=1:
  peak=v.max(-1,keepdims=True);spread=peak-v;maximum=spread.max(-1,keepdims=True);limit=np.divide(peak,maximum,out=np.full_like(peak,np.inf),where=maximum>0);factor=np.minimum(recipe['endpoint']['saturation'],np.nextafter(limit,0));v=peak-factor*spread
 v[np.all(body[ok]==1,axis=1)]=1.
 out[ok]=body[ok]+alpha[ok,None]*(v-body[ok]);return out
save('verification-start.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'deadline':END.isoformat(),'array_tolerance':1e-7,'optical_calls':0,'new_source_queries':0})
try:
 data=c.load_data(charge,first);score=c.metric_functions(charge)['score'];qcache={};acache={};scache={}
 for m in ['expanded','compact']:
  q=load(c.NATIVE/f'{m}-paths.npz',['X','Y','primary_power','front_reflection_power','front_reflection_direction','inside']);I=q['inside'];charge('environment_points',int(I.sum()));theta=np.rad2deg(np.arccos(np.clip(q['front_reflection_direction'][I,2],-1,1)));u=np.clip((theta-30)/10,0,1);v=np.clip((80-theta)/10,0,1);q['light']=q['front_reflection_power'][I]*(u*u*(3-2*u))*(v*v*(3-2*v));qcache[m]=q
  integ=json.loads((OUT/'integration.json').read_text());order=max(x['order'] for x in integ if x['member']==m);acache[m]=load(OUT/f'{m}-alpha{order}.npz',['alpha'])['alpha'][recipe['outline_index']];scache[m]=load(OUT/f'{m}-shadow{recipe["shadow_index"]}.npz',['field'])['field']
 for (m,r),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;I=z['inside'];q=qcache[m];raw=z['raw_source'] if recipe['sigma']==6.075 else load(OUT/f'{m}-{r}-blur{recipe["sigma"]}-samples.npz',['raw_source'])['raw_source'];sub=raw.copy();graded=raw[I]*recipe['gain']+recipe['bias'];Y=dec(raw[I])@np.array([.2126,.7152,.0722]);graded=graded+recipe['low_lift']*(1-Y[:,None])**3*(1-graded);assert graded.min()>=0 and graded.max()<=1
  if recipe['chroma']!=1:
   linear=dec(graded);lum=linear@np.array([.2126,.7152,.0722]);delta=linear-lum[:,None];upper=np.full_like(delta,np.inf);lower=np.full_like(delta,np.inf);np.divide(1-lum[:,None],delta,out=upper,where=delta>0);np.divide(-lum[:,None],delta,out=lower,where=delta<0);scale=np.minimum(recipe['chroma'],np.nextafter(np.minimum(upper,lower).min(-1),0));graded=enc(lum[:,None]+scale[:,None]*delta)
  sub[I]=enc(q['primary_power'][I,None]*dec(graded)+4*q['light'][:,None]);clear=~I&z['supported'];sub[clear]=sub[clear]*(1-recipe['shadow']['opacity']*scache[m][clear,None]);pre=sub.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  body=foreground(s,pre,recipe['artwork']);guide=foreground(s,raw.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32),recipe['artwork']);C=rim(body,guide,acache[m]);saved=load(OUT/f'{m}-{r}-final.npz',['complete','pre_foreground']);finite=np.isfinite(saved['complete']);err=float(np.max(abs(C[finite]-saved['complete'][finite])));preerr=float(np.nanmax(abs(pre-saved['pre_foreground'])));assert err<=1e-7 and preerr<=1e-7;assert np.array_equal(np.isnan(C),np.isnan(saved['complete']))
  fieldpath=(BASE/P['native']/f'{m}-{r}-geometry.npz') if recipe['sigma']==6.075 else OUT/f'{m}-{r}-blur{recipe["sigma"]}-field.npz'
  field=load(fieldpath,['incident_field'])['incident_field'];ids=np.flatnonzero(I);sel=ids[np.linspace(0,len(ids)-1,8,dtype=int)];ii,jj=np.unravel_index(sel,I.shape);center=d['center']+[-.5,0];X=q['X'][ii,jj]*c.L+center[0];Y=q['Y'][ii,jj]*c.L+center[1];a=np.floor(X).astype(int);b=np.floor(Y).astype(int);wx=X-a;wy=Y-b;charge('source_parity_points',len(sel));corners=np.stack([field[b,a],field[b,a+1],field[b+1,a],field[b+1,a+1]],1);weights=np.stack([(1-wx)*(1-wy),wx*(1-wy),(1-wx)*wy,wx*wy],1);parity=(corners*weights[:,:,None]).sum(1);assert np.max(abs(parity-raw[ii,jj]))<2e-15
  # Fixed whole-pixel cap sectors sit strictly within the zero-angle interval.
  x0,y0,_,_=s.crop;yy,xx=np.indices((H,W));cx,cy=center;core=d['half'][0]+1.5-(d['radius']-P['dilation_reduction_native']);gap=np.zeros((H,W),bool)
  for side in [1,-1]:
   dx=xx+x0-(cx+side*core);dy=-(yy+y0-cy);ang=(np.degrees(np.arctan2(dy,dx))-(180 if side<0 else 0)+180)%360-180
   gap|=(ang>38)&(ang<52)&(side*(xx+x0-cx)>core)&(np.hypot(dx,dy)>d['radius']-15)&(np.hypot(dx,dy)<d['radius']+1)
  charge('gap_pixels',int(gap.sum()));assert np.all(acache[m][gap]==0) and np.array_equal(C[gap],body[gap],equal_nan=True)
  actual=score(s,C,d['m'],d['partial'],d['crops']);receipt=json.loads((OUT/f'{m}-{r}-final-metrics.json').read_text());assert c.guards(actual,d['original'])==receipt['original_guards'];results.append(dict(member=m,reference=r,max_error=err,pre_foreground_error=preerr,metrics_exact=actual==receipt['scores'],scores=actual,E_difference=actual['E']-receipt['scores']['E'],original_guard_decisions_match=True,source_coordinate_parity_error=float(np.max(abs(parity-raw[ii,jj]))),zero_gap_pixels=int(gap.sum())))
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
