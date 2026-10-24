from pathlib import Path
import json,datetime,sys,ast,zipfile,hashlib,struct
import numpy as np
O=Path(__file__).parent;ROOT=Path('/research/liquid-glass');BASE=ROOT/'research/experiments/miniplayer-first-return-native-85';P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']};records=[];headers=[]
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00')),'Deadline'
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
def hdr(path,names):
 with zipfile.ZipFile(path) as z:
  for key in names:
   with z.open(key+'.npy') as f:
    version=np.lib.format.read_magic(f);shape,order,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f)
    assert not dtype.hasobject;size=int(np.prod(shape))*dtype.itemsize;headers.append({'file':str(path.relative_to(ROOT)),'key':key,'shape':shape,'dtype':str(dtype),'payload':size})
def load(path,names):
 with np.load(path,allow_pickle=False) as z:
  out={}
  for key in names:
   h=next(h for h in headers if h['file']==str(path.relative_to(ROOT)) and h['key']==key);charge('numeric_payload_bytes',h['payload']);out[key]=z[key]
 return out
plans=[];bitmap_bound=0;numeric_bound=0;visits=0;boxes=0;maskpoints=0
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 for ref in ['a','b']:
  case=json.loads((work/ref/'case.json').read_text());x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;maskpoints+=H*W
  assert not case.get('exterior_source') and all(x['mode']!='transmission' for x in case['foreground_layers'])
  mpath=work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz';hdr(mpath,['glass','rim','held','exterior']);hdr(BASE/f'{member}-{ref}.npz',['pre_foreground','complete','coverage'])
  if member=='compact':hdr(ROOT/f'research/experiments/compact-geometry-01/{ref}-raw.npz',['coverage'])
  bitmap_bound+=2*1920*1080*15+1920*1080
  for layer in case['foreground_layers']:
   a,b,c,d=layer['box'];boxes+=3*(c-a)*(d-b)
   if 'vector_asset' in layer:visits+=2;bitmap_bound+=2*(c-a)*(d-b)*16*4
   if 'artwork_asset' in layer:bitmap_bound+=1200*1200*15
  plans.append((member,ref,work,mpath,H,W))
numeric_bound=sum(h['payload'] for h in headers)
reserve={'numeric_payload_bytes':numeric_bound,'bitmap_payload_bytes':bitmap_bound,'vector_coverage_visits':visits,'foreground_box_reservations':boxes,'mask_points':maskpoints,'Study_constructors':4,'cached_composites':4,'score_calls':4,'SSIM_Gaussians':20,'metric_erosions':4}
# Header preflight only: no numerical arrays or Study bodies have executed.
save('header-reservations.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headers':headers,'reservations':reserve,'bitmap_semantics':'Conservative uint8 decode plus float32 source/target/artwork and vector supersample buffers; saved comparison decode separately bound by header.'})
status='PREREQUISITE_CHECK'
try:
 assert all(v<=P['caps'][k] for k,v in reserve.items()),'Insufficient declared replay bounds'
 sys.path.insert(0,str(ROOT/'reconstruction'));from extended_fit import Study
 import cv2
 cv2.setNumThreads(1)
 tree=ast.parse((ROOT/'research/experiments/miniplayer-outline-light-07/render.py').read_text());exec(compile(ast.Module(body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='score'],type_ignores=[]),'sealed-score','exec'))
 origcharge=charge
 def charge(k,n):
  origcharge(k,n)
  if k=='score_calls':origcharge('SSIM_Gaussians',5*n);origcharge('metric_erosions',n)
 crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops']
 for member,ref,work,mpath,H,W in plans:
  gate();charge('Study_constructors',1);charge('mask_points',H*W);s=Study(work/ref);assert not s.transmission_layers
  case=s.case;vec=sum('vector_asset' in x for x in case['foreground_layers']);box=sum((x['box'][2]-x['box'][0])*(x['box'][3]-x['box'][1]) for x in case['foreground_layers']);charge('vector_coverage_visits',2*vec);charge('foreground_box_reservations',3*box)
  m=load(mpath,['glass','rim','held','exterior']);assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
  z=load(BASE/f'{member}-{ref}.npz',['pre_foreground','complete','coverage']);frozen=z['coverage'] if member=='expanded' else load(ROOT/f'research/experiments/compact-geometry-01/{ref}-raw.npz',['coverage'])['coverage'];partial=m['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22)
  charge('cached_composites',1);C=s.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(C,z['complete'],equal_nan=True),'Complete array mismatch'
  scores=score(s,C,m,partial,crops[member]);old=json.loads((BASE/f'{member}-{ref}-metrics.json').read_text());assert scores==old['scores'],'Metric mismatch'
  records.append({'member':member,'reference':ref,'pre_foreground':'Sealed input reused unchanged; no optical reconstruction','complete_pixel_exact':True,'scores_exact':True,'E':scores['E'],'SSIM':scores['ssim'],'partial':scores['partial'],'all_foreground_and_fixed_crop_values_exact':True,'matched78_failed_guards':[k for k,v in old['matched78_guards'].items() if not v]});save('replay-progress.json',{'records':records,'ledger':ledger});print('EXACT',member,ref,flush=True)
 # Actual bitmap decode work does not exceed prospective full buffer reservation.
 charge('bitmap_payload_bytes',bitmap_bound);status='PASS_FOUR_CACHED_FOREGROUND_METRIC_REPLAYS'
except Exception as e:status='STOPPED_REPLAY_PREREQUISITE_OR_DISCREPANCY';failure=repr(e)
finally:save('replay-result.json',{'status':status,'failure':locals().get('failure'),'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'bitmap_accounting':'Conservative pre-reserved bound; not a measured device allocation','optical_calls_source_queries_filters_fits_images':0});print(status,locals().get('failure'),flush=True)
