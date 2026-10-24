"""Saved-image lower bounds for nonnegative continuation of a frozen prefix."""
from pathlib import Path
import json,datetime,hashlib,zipfile
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k],k
 ledger[k]+=int(n);save('ledger.json',ledger)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p,keys):
 reservation=0
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    version=np.lib.format.read_magic(f);shape,fortran,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f);assert not dtype.hasobject;reservation+=int(np.prod(shape))*dtype.itemsize
 charge('NPZ_payload_bytes',reservation)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in keys}
def show(c):
 good=np.isfinite(c).all(-1);y,x=np.indices(good.shape);a=np.where(good[...,None],c,np.where(((x//6+y//6)%2)[...,None],.72,.9));return Image.fromarray(np.uint8(np.rint(np.clip(a,0,1)*255)))
def metrics(err,mask):
 n=int(mask.sum());charge('scalar_reduction_entries',12*n)
 if not n:return dict(pixels=0,empty=True)
 e=err[mask];positive=np.maximum(e,0);sq=float(np.sum(e*e));floor=float(np.sum(positive*positive));return dict(pixels=n,positive_any_channel_pixels=int((positive>0).any(-1).sum()),any_channel_above_one_level=int((positive>1).any(-1).sum()),maximum_positive_excess_levels=float(positive.max()),current_RGB_RMSE_f64=float(np.sqrt(sq/e.size)),optimistic_completion_RMSE_floor=float(np.sqrt(floor/e.size)),fraction_of_current_SSE_lower_bound=(floor/sq if sq else None))
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});paths=[];items=[];first={}
 for member in ['expanded','compact']:
  work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for k in ['a','b']:
   case=work/k/'case.json';target=work/k/'target.png';mask=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz';cur=ROOT/f'research/experiments/miniplayer-first-return-native-85/{member}-{k}.npz';old=ROOT/f'research/experiments/miniplayer-codesigned-native-78/{member}-{k}.npz';partial=ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz' if member=='compact' else None;files=[case,target,mask,cur,old]+([partial] if partial else []);paths.extend(files);items.append((member,k,case,target,mask,cur,old,partial))
 paths.append(Path(__file__));first={str(p.relative_to(ROOT)):sha(p) for p in set(paths)};save('first-hashes.json',first);records=[]
 for member,k,cp,tp,mp,current,previous,pp in items:
  case=json.loads(cp.read_text());assert sha(tp)==case['source_sha256']['target.png'];charge('target_cases',1);charge('target_RGB_decoded_pixels',1920*1080);target=cv2.imread(str(tp))[:,:,::-1].astype(np.float32)/255;assert target.shape==(1080,1920,3);x0,y0,x1,y1=case['crop'];target=target[y0:y1,x0:x1];H,W=target.shape[:2];m=load(mp,['glass','rim','held']);new=load(current,['complete','coverage']);old=load(previous,['complete'])['complete'];C=new['complete'];frozen=load(pp,['coverage'])['coverage'] if pp else new['coverage'];partial=m['glass']&(frozen<1);assert int(partial.sum())==(16 if member=='expanded' else 22)
  paint=np.zeros((H,W),bool)
  for layer in case['foreground_layers']:
   a,b,c,d=layer['box'];paint[b-y0:d-y0,a-x0:c-x0]=True
  assert not (paint&m['glass']).any(),'Original scored glass intersects actual foreground boxes'
  assert np.isfinite(C[m['glass']]).all() and np.isfinite(old[m['glass']]).all() and np.isfinite(target[m['glass']]).all();assert (C[m['glass']]>=old[m['glass']]).all(),'Known positive addition unexpectedly darkened original glass'
  if not records:
   now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=now.isoformat(),first_case=member+'-'+k,input_hashes_bound=True,original_glass_foreground_disjoint=True,required_data_finite=True,original_partial_count=16,no_numerical_optics=True));print('CHECKPOINT '+now.isoformat()+' original cohort and monotonic-prefix controls PASS',flush=True)
  cohorts={'glass':m['glass'],'rim':m['rim'],'held':m['held'],'interior':m['glass']&~m['rim'],'partial':partial};charge('scalar_residual_entries',2*H*W*3);e=(C.astype(float)-target.astype(float))*255;before=(old.astype(float)-target.astype(float))*255;cohort_records={name:dict(known85=metrics(e,mask),prior78=metrics(before,mask)) for name,mask in cohorts.items()};row=dict(member=member,reference=k,cohorts=cohort_records,original_glass_has_no_foreground_overlap=True,no_mask_or_score_change=True);records.append(row);save(member+'-'+k+'-result.json',row)
  diagnostic=np.where(m['glass'][...,None],np.maximum(e,0),np.nan);np.savez_compressed(OUT/f'{member}-{k}-positive-excess.npz',positive_RGB_excess_levels=diagnostic,glass=m['glass'],rim=m['rim'],held=m['held'],partial=partial)
  charge('diagnostic_figures',1);strength=np.where(m['glass'],np.minimum(np.maximum(e,0).max(-1),32)/32,0);heat=np.stack([np.ones((H,W)),1-strength,1-strength],-1);heat[~m['glass']]=.72;w=min(W,1080);h=round(H*w/W);im=Image.new('RGB',(3*w+4,h+96),'white');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=16)
  for i,(a,label) in enumerate([(target,'Reference'),(C,'Known prefix85'),(heat,'Positive excess map; not a reconstruction')]):im.paste(show(a).resize((w,h),Image.Resampling.NEAREST if i==2 else Image.Resampling.LANCZOS),(i*(w+2),96));draw.text((i*(w+2)+8,18),label,font=font,fill='black')
  draw.text((10,51),'Map: white = no positive excess; red = 32+ levels; gray = outside original glass cohort.',font=font,fill='black');im.save(OUT/f'{member}-{k}-diagnostic.png');print(member,k,cohort_records['rim']['known85'],flush=True)
 last={str(p.relative_to(ROOT)):sha(p) for p in set(paths)};assert first==last;save('last-hashes.json',last);save('result.json',dict(status='CONDITIONAL_NONNEGATIVE_COMPLETION_ERROR_FLOORS',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,ledger=ledger,scope='Frozen encoded native AA2 prefix with nonnegative incoherent added radiance, unchanged foreground and original scored cohorts only. Not arbitrary physical models or whole continuous pixel integration.',new_model_evaluations=0,source_RGB_queries=0,selected_model_changed=False));print('COMPLETE',flush=True)
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(e).__name__,message=str(e),ledger=ledger));raise
