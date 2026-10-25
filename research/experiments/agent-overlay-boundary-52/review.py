from pathlib import Path
import json,datetime,zipfile,hashlib,struct
import numpy as np
import cv2
O=Path(__file__).parent;ROOT=Path('/research/liquid-glass');B=ROOT/'research/experiments/miniplayer-overlay-outline-88';P=json.loads((O/'protocol.json').read_text());ledger={'numeric_payload_bytes':0,'target_pixels':0,'selected_scalar_observations':0,'header_bytes':0,'mask_selection_cells':0};headers=[];plans=[];records=[]
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Deadline'
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):gate();assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=int(n)
for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h['sha256'],f
F=json.loads((ROOT/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels'];spec={}
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01');center=np.array(json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
 if member=='compact':
  pose=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];case=json.loads((work/'a/case.json').read_text());center=np.array(case['center'])+L*np.array([pose['shape_dx'],pose['shape_dy']])
 half=np.array([F['members'][member]['major_half'],F['geometry']['minor_half']])*L;radius=F['geometry']['corner_radius']*L
 for ref in ['a','b']:
  case=json.loads((work/ref/'case.json').read_text());mask=work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz';base=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{ref}-factor0.5.npz';candidate=B/f'{member}-{ref}.npz';spec[mask]=['glass'];spec[base]=['complete','coverage'];spec[candidate]=['complete','alpha'];raw=None
  if member=='compact':raw=ROOT/f'research/experiments/compact-geometry-01/{ref}-raw.npz';spec[raw]=['coverage']
  path=work/ref/'target.png'
  with path.open('rb') as f:head=f.read(24)
  assert head[:8]==b'\x89PNG\r\n\x1a\n';W,H=struct.unpack('>II',head[16:24]);assert (W,H)==(1920,1080)
  plans.append((member,ref,case,mask,base,candidate,raw,path,W,H,center,half,radius))
for path,names in spec.items():
 with zipfile.ZipFile(path) as z:
  for name in names:
   with z.open(name+'.npy') as f:
    version=np.lib.format.read_magic(f);shape,fortran,dtype=({(1,0):np.lib.format.read_array_header_1_0,(2,0):np.lib.format.read_array_header_2_0}[version])(f);assert not dtype.hasobject;ledger['header_bytes']+=f.tell();headers.append({'file':str(path.relative_to(ROOT)),'member':name,'shape':shape,'dtype':str(dtype),'bytes':int(np.prod(shape))*dtype.itemsize})
reserve={'numeric_payload_bytes':sum(h['bytes'] for h in headers),'target_pixels':sum(x[8]*x[9] for x in plans),'selected_scalar_observations':7296};assert all(v<=P['caps'][k] for k,v in reserve.items());save('headers.json',{'members':headers,'reservation':reserve,'target_header_dims':[1920,1080]});gate(True);save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hashes_and_headers_before_decode':True,'fixed76_cohort_rule':'original glass AND original frozen coverage<1','reservation':reserve});print('CHECKPOINT_PASS',flush=True)
def load(path):
 out={}
 with np.load(path,allow_pickle=False) as z:
  for name in spec[path]:
   h=next(h for h in headers if h['file']==str(path.relative_to(ROOT)) and h['member']==name);charge('numeric_payload_bytes',h['bytes']);out[name]=z[name]
 return out
status='STARTING';summary=[]
try:
 for member,ref,case,mp,bp,cp,rp,tp,W,H,center,half,radius in plans:
  m=load(mp)['glass'];base=load(bp);cand=load(cp);frozen=base['coverage'] if rp is None else load(rp)['coverage'];ledger['mask_selection_cells']+=m.size;partial=m&(frozen<1);yy,xx=np.nonzero(partial);assert len(yy)==(16 if member=='expanded' else 22);charge('selected_scalar_observations',96*len(yy));charge('target_pixels',W*H);target=cv2.imread(str(tp),cv2.IMREAD_COLOR);assert target.shape==(H,W,3);x0,y0,_,_=case['crop'];native=np.column_stack([xx+x0,yy+y0]);T=target[native[:,1],native[:,0],::-1].astype(np.float32)/255;before=base['complete'][yy,xx];after=cand['complete'][yy,xx];alpha=cand['alpha'][yy,xx];cov=frozen[yy,xx];qx=np.abs(native[:,0]-center[0])-(half[0]-radius);qy=np.abs(native[:,1]-center[1])-(half[1]-radius);distance=np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius
  assert np.isfinite(T).all() and np.isfinite(before).all() and np.isfinite(after).all();eb=(before-T)*255;ea=(after-T)*255;delta=after-before;assert (delta>=-1e-7).all();bse=np.sum(eb**2,axis=1);ase=np.sum(ea**2,axis=1)
  for i in range(len(yy)):
   records.append({'member':member,'reference':ref,'native_xy':native[i].tolist(),'frozen_coverage':float(cov[i]),'signed_boundary_distance_native':float(distance[i]),'saved_overlay_alpha':float(alpha[i]),'target_RGB':T[i].tolist(),'working20_RGB':before[i].tolist(),'working88_RGB':after[i].tolist(),'before_error_RGB_levels':eb[i].tolist(),'after_error_RGB_levels':ea[i].tolist(),'delta_MSE_levels':float((ase[i]-bse[i])/3),'before_above_target_channels':(before[i]>T[i]).tolist(),'changed_channels':(after[i]!=before[i]).tolist(),'error_worse':bool(ase[i]>bse[i]),'pixel_center_outside_overlay_contour':bool(distance[i]>0)})
  bm=float(np.sqrt(np.mean(eb**2)));am=float(np.sqrt(np.mean(ea**2)));saved=json.loads((B/f'{member}-{ref}-metrics.json').read_text());assert bm==saved['baseline']['partial']['RMSE'] and am==saved['scores']['partial']['RMSE'],'Partial metrics mismatch'
  summary.append({'member':member,'reference':ref,'pixels':len(yy),'RMSE_before':bm,'RMSE_after':am,'worse_pixels':int((ase>bse).sum()),'better_pixels':int((ase<bse).sum()),'equal_pixels':int((ase==bse).sum()),'already_all_channels_above_target':int(np.all(before>T,axis=1).sum()),'outside_overlay_center_pixels':int((distance>0).sum()),'saved_guard_pass':saved['guards']['partial']});save('records.json',records);print('EXACT',member,ref,flush=True)
 assert len(records)==76;status='COMPLETE_FIXED76_BOUNDARY_DIAGNOSIS'
except Exception as e:status='STOPPED_FIRST_INVARIANT';failure=repr(e)
finally:save('result.json',{'status':status,'failure':locals().get('failure'),'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'summary':summary,'ledger':ledger,'optics_source_integration_composites_filters_images_fits':0});print(status,locals().get('failure'),flush=True)
