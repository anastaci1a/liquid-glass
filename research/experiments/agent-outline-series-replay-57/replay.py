from pathlib import Path
import sys,json,datetime,hashlib,ast,zipfile,struct
import numpy as np
from PIL import Image
O=Path(__file__).parent;ROOT=Path('/research/liquid-glass');SERIES=ROOT/'research/experiments/miniplayer-outline-series-91';P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']};headers=[];bitmap=[];spec={};plans=[];records=[]
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Deadline'
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h['sha256'],f
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 for ref in ['a','b']:
  folder=work/ref;case=json.loads((folder/'case.json').read_text());assert not case.get('exterior_source') and all(x['mode']!='transmission' for x in case['foreground_layers']);crop=case['crop'];H,W=crop[3]-crop[1],crop[2]-crop[0];base=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{ref}-factor0.5.npz';spec[base]=['complete','coverage'];mask=work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz';spec[mask]=['glass','rim','held','exterior'];raw=None
  if member=='compact':raw=ROOT/f'research/experiments/compact-geometry-01/{ref}-raw.npz';spec[raw]=['coverage']
  for name in ['source.png','target.png',case.get('target_observation_mask','known.png')]:
   with Image.open(folder/name) as im:bitmap.append({'file':str((folder/name).relative_to(ROOT)),'role':'Study constructor dependency','pixels':im.width*im.height,'dimensions':[im.width,im.height]})
  for layer in case['foreground_layers']:
   a,b,c,d=layer['box']
   if 'artwork_asset' in layer:
    with Image.open(folder/layer['artwork_asset']) as im:bitmap.append({'file':str((folder/layer['artwork_asset']).relative_to(ROOT)),'role':'Original per-Study artwork decode','pixels':im.width*im.height,'dimensions':[im.width,im.height]})
   if 'vector_asset' in layer:bitmap.append({'file':str((folder/layer['vector_asset']).relative_to(ROOT)),'role':'One original coverage visit, conservative fresh4x raster decode','pixels':16*(c-a)*(d-b),'dimensions':[4*(c-a),4*(d-b)]})
  for pi,j in enumerate(P['indices'],1):
   d=SERIES/f'pass-{pi:02d}';spec[d/f'{member}-alpha.npz']=['order16'];spec[d/f'{member}-{ref}-c{j}.npz']=['complete']
  panel=SERIES/f'pass-05/{member}-{ref}-c2-comparison.png'
  with Image.open(panel) as im:bitmap.append({'file':str(panel.relative_to(ROOT)),'role':'Final saved comparison inspection','pixels':im.width*im.height,'dimensions':[im.width,im.height]})
  plans.append((member,ref,folder,base,mask,raw,H,W))
for path,names in spec.items():
 with zipfile.ZipFile(path) as z:
  for name in names:
   with z.open(name+'.npy') as f:
    version=np.lib.format.read_magic(f);shape,fortran,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f);assert not dtype.hasobject;headers.append({'file':str(path.relative_to(ROOT)),'member':name,'shape':shape,'dtype':str(dtype),'bytes':int(np.prod(shape))*dtype.itemsize,'header_bytes':f.tell()})
reserve={'numeric_payload_bytes':sum(h['bytes'] for h in headers),'bitmap_pixels':sum(x['pixels'] for x in bitmap),'Study_constructors':4,'mask_points':1121600,'composites':20,'scores':20,'metric_Gaussians':100,'metric_erosions':20};assert all(v<=P['caps'][k] for k,v in reserve.items()),reserve;save('headers-and-decode-reservation.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'headers':headers,'bitmaps':bitmap,'reservation':reserve,'metadata_only_before_checkpoint':True});gate(True);save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all_hashes_headers_and_constructor_dependencies_bound_before_decode':True,'reservation':reserve,'zero_completed_composites':True});print('CHECKPOINT_PASS',reserve,flush=True)
def load(path):
 out={}
 with np.load(path,allow_pickle=False) as z:
  for name in spec[path]:
   row=next(x for x in headers if x['file']==str(path.relative_to(ROOT)) and x['member']==name);charge('numeric_payload_bytes',row['bytes']);out[name]=z[name]
 return out
status='STARTING'
try:
 sys.path.insert(0,str(ROOT/'reconstruction'));from extended_fit import Study
 from outline_response import response_delta,composite
 import cv2
 cv2.setNumThreads(1)
 tree=ast.parse((ROOT/'research/experiments/miniplayer-outline-light-07/render.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='score'],type_ignores=[]),'pinned-score','exec'))
 # Alias only the metric counter name; no score/helper implementation change.
 original_charge=charge
 def charge(k,n):
  original_charge('scores' if k=='score_calls' else k,n)
  if k=='score_calls':original_charge('metric_Gaussians',5*n);original_charge('metric_erosions',n)
 crops=json.loads((ROOT/'research/experiments/miniplayer-inverse-forward-18/protocol.json').read_text())['fixed_crops'];alphas={}
 for member in ['expanded','compact']:
  for pi in range(1,6):alphas[(member,pi)]=load(SERIES/f'pass-{pi:02d}/{member}-alpha.npz')['order16']
 for member,ref,folder,basepath,maskpath,rawpath,H,W in plans:
  charge('Study_constructors',1);charge('mask_points',H*W);gate();s=Study(folder);assert not s.transmission_layers;base=load(basepath);mask=load(maskpath);assert np.array_equal(s.valid,mask['glass']) and np.array_equal(s.rim,mask['rim']) and np.array_equal(s.held,mask['held']);frozen=base['coverage'] if rawpath is None else load(rawpath)['coverage'];partial=mask['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22);body=base['complete']
  for pi,j in enumerate(P['indices'],1):
   gate();d=SERIES/f'pass-{pi:02d}';fit=json.loads((d/'fits.json').read_text())[j];assert fit['candidate']==j;cfg=fit['config'];a=alphas[(member,pi)][j];delta=(cfg['white_mix']*response_delta(body,'white')+(1-cfg['white_mix'])*response_delta(body,'linear_lift')) if cfg['response']=='mixed_lift' else response_delta(body,cfg['response']);charge('composites',1);C=composite(body,a,delta,fit['strength']);saved=load(d/f'{member}-{ref}-c{j}.npz')['complete'];assert np.array_equal(C,saved,equal_nan=True),'Completed pixel mismatch';scores=score(s,C,mask,partial,crops[member]);old=json.loads((d/f'{member}-{ref}-c{j}-metrics.json').read_text());assert scores==old['scores'],'Metric discrepancy'
   before=old['baseline'];guards={n:scores[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};guards.update(E=scores['E']<=before['E'],SSIM=scores['ssim']>=before['ssim'],partial=scores['partial']['RMSE']<=before['partial']['RMSE'],exterior=scores['exterior']<=before['exterior']);guards.update({n:v<=before['foreground'][n] for n,v in scores['foreground'].items()});assert guards==old['original_guards'],'Guard mismatch';records.append({'pass':pi,'candidate':j,'member':member,'reference':ref,'complete_exact':True,'all_saved_metrics_exact':True,'original_guards_exact':True,'failed_guards':[k for k,v in guards.items() if not v],'partial':scores['partial'],'E':scores['E'],'SSIM':scores['ssim']});save('progress.json',{'records':records,'ledger':ledger});print('EXACT',pi,member,ref,flush=True)
 # Prospective whole bitmap reservation includes final panel inspection outside this process.
 charge('bitmap_pixels',reserve['bitmap_pixels']);assert len(records)==20;status='PASS20_CACHED_REPLAYS_WITH_FAILURES_PRESERVED'
except Exception as e:status='STOPPED_FIRST_PREREQUISITE_OR_REPLAY_FAILURE';failure=repr(e)
finally:save('result.json',{'status':status,'failure':locals().get('failure'),'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'bitmap_units':'Conservative reserved decode count including panels and every constructor vector visit, even if runtime coverage cache reuses a raster. No hidden subtraction.','optics_source_queries_filters_fields_fits_quadrature_new_images':0});print(status,locals().get('failure'),flush=True)
