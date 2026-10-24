"""Independent two-case cached family replay; no optical sampling or filtering."""
import sys,json,hashlib,datetime,ast
from pathlib import Path
import numpy as np,cv2
OUT=Path(__file__).resolve().parent;OWN=OUT.parents[2]
PRIMARY=Path('/research/liquid-glass');P=PRIMARY/'research/experiments/miniplayer-shared-transfer-06';B=PRIMARY/'research/experiments/compact-geometry-01';WORK=PRIMARY/'.evidence-working/compact-geometry-01'
proto=json.loads((OUT/'protocol.json').read_text());ledger={'candidate_composites':0,'Study_constructors':0,'mask_pixels':0,'score_calls':0,'SSIM_Gaussians':0,'metric_erosions':0,'expanded_composites':0}
def clock():
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')):raise RuntimeError('Deadline')
def charge(k,n):
 clock()
 if ledger[k]+n>proto['caps'][k]:raise RuntimeError('Cap '+k)
 ledger[k]+=n
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
 clock();(OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
assert not (OUT/'started.json').exists(),'No repeated replay'
result={'status':'STARTING','ledger':ledger,'records':[],'zero_work':['rays','heights','source/remapping queries','optical filters','fits','new images','expanded composites']}
try:
 clock();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 first=json.loads((OUT/'first-hashes.json').read_text())
 for name,value in first['hashes'].items():assert sha(PRIMARY/name)==value,'First binding changed '+name
 family=json.loads((PRIMARY/'reconstruction/families/music-mini-player.json').read_text())
 assert family['members']=={'expanded':{'major_half':7.225022904390323},'compact':{'major_half':4.906563038095225}}
 g=family['geometry'];assert g['minor_half']==1.012503164339156 and g['corner_radius']==1.0043663048754772 and g['cap_join_width']==0
 selected=json.loads((PRIMARY/family['provenance']['expanded_height_record']).read_text());assert g['height_controls']==selected['best']['heights'] and g['breaks']==selected['breaks']
 decision=json.loads((PRIMARY/family['provenance']['expanded_response_record']).read_text())
 material=family['material'];gain=material['gain'];bias=material['bias']
 assert gain==decision['material']['gain']==.596189238519786 and bias==decision['material']['bias']==.3290237590837732
 assert family['length_unit_native_pixels']==88.5 and family['optics']['index']==1.5 and family['optics']['background_distance']==2.1
 assert material['incident_sigma_native_pixels']==6.75 and material['incident_kernel_radius']==21 and material['generated_shadow']==0 and material['output_sigma']==0
 assert family['sampling']=={'samples_per_axis':2,'bilinear':'exact'}
 # Static factory and its actual observer consumption; never construct a surface here.
 factory=ast.parse((PRIMARY/'reconstruction/music_miniplayer_family.py').read_text())
 functions={n.name:n for n in factory.body if isinstance(n,ast.FunctionDef)}
 assert [a.arg for a in functions['surface_for_length'].args.args]==['major_half']
 assert set(functions)=={'load_family','surface_for_length','surface_for_member'}
 observer=(P/'observe.py').read_text();assert "surface_for_member('compact')" in observer and "surface_for_member('expanded')" in observer
 zeros=json.loads((P/'expanded-zero-controls.json').read_text());assert zeros['status']=='EXACT' and len(zeros['records'])==2 and all(x['pre_foreground_exact'] and x['complete_exact'] for x in zeros['records'])
 proof=json.loads((P/'source-proof-FIRST.json').read_text());assert proof['status']=='PASS_BOTH_BEFORE_RGB' and all(x['unsupported_required']==0 and x['kernel_radius']==21 and x['scored_outside_outline']==4 for x in proof['references'])
 parity=json.loads((P/'parity.json').read_text());assert parity['all_exact'] and len(parity['records'])==4
 preservation=json.loads((P/'preservation.json').read_text());inputs={}
 for row in preservation['rows']:
  folder=PRIMARY/'.evidence-working'/('compact-geometry-01' if row['member']=='compact' else 'expanded-geometry-02')/row['reference']
  record={'case.json':sha(folder/'case.json')};assert record['case.json']==row['case_sha256']
  for name,digest in row['hashes'].items():record[name]=sha(folder/name);assert record[name]==digest,'Input hash '+name
  inputs[row['member']+'-'+row['reference']]=record
 save('input-hashes-first.json',inputs)
 sys.path.insert(0,str(OWN/'reconstruction'))
 from extended_fit import Study
 from geometric_render import neutral_color_response
 cv2.setNumThreads(1)
 for name in ('extended_fit.py','geometric_render.py','vector_foreground.py','foreground_response.py','geometric_optics.py'):
  assert sha(OWN/'reconstruction'/name)==sha(PRIMARY/'reconstruction'/name),'Imported module mismatch '+name
 q=np.load(P/'compact-paths.npz',allow_pickle=False);inside=q['inside'];H,W=240,920
 assert inside.shape==(H*2,W*2)
 coverage=inside.reshape(H,2,W,2).mean((1,3));validation=json.loads((P/'saved-validation.json').read_text())['records']
 prior_params=json.loads((PRIMARY/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters']
 for k in ('a','b'):
  clock();charge('Study_constructors',1);charge('mask_pixels',920*240);s=Study(WORK/k)
  masks=dict(np.load(B/f'{k}-masks.npz',allow_pickle=False));assert s.L==88.5 and not s.transmission_layers
  for name,v in [('glass',s.valid),('rim',s.rim),('held',s.held)]:assert np.array_equal(v,masks[name]),'Mask mismatch'
  expected=np.load(P/f'compact-{k}-candidate.npz',allow_pickle=False);raw=expected['sample_before_response']
  assert raw.shape==(H*2,W*2,3) and np.array_equal(coverage,expected['coverage'])
  # Per-ray response on retained inside samples; raw clear is untouched.
  values=raw.copy();graded,preclip=neutral_color_response(raw[inside],gain=gain,bias=bias,return_preclip=True);values[inside]=graded
  assert np.array_equal(values[~inside],raw[~inside],equal_nan=True),'Clear samples changed'
  clipping=[int((preclip<0).sum()),int((preclip>1).sum())];assert clipping==[0,0]
  pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  assert np.array_equal(pre,expected['pre_foreground'],equal_nan=True),'Pre-foreground mismatch'
  charge('candidate_composites',1);complete=s.apply_foreground(pre.copy())
  assert np.array_equal(complete,expected['complete'],equal_nan=True),'Completed mismatch'
  lens=np.where(inside[...,None],values,0).reshape(H,2,W,2,3).mean((1,3))
  M=np.divide(lens,coverage[...,None],out=np.zeros_like(lens),where=coverage[...,None]>0).astype(np.float32)
  assert np.array_equal(M,expected['material'],equal_nan=True),'Normalized material mismatch'
  reported=json.loads((P/f'compact-{k}-metrics.json').read_text());scores={}
  for scope,pixels in [('legacy_material',M),('completed_image',complete)]:
   charge('score_calls',1);charge('SSIM_Gaussians',5);charge('metric_erosions',1)
   z=s.scores(pixels);z['E']=float(np.sqrt(z['loss']));assert z==reported['scores'][scope],'Score mismatch '+scope;scores[scope]=z
  x0,y0,x1,y1=s.crop;fg={}
  for layer in s.case['foreground_layers']:
   a,b,c,d=layer['box'];key=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')))
   tile=(complete[b-y0:d-y0,a-x0:c-x0].astype(float)-s.target[b:d,a:c])*255
   fg[key]=float(np.mean(tile**2))
  assert fg==reported['scores']['foreground_artwork_MSE'] and len(fg)==5,'Foreground/artwork mismatch'
  old=np.load(B/f'{k}-colour-source-1.npz',allow_pickle=False)['complete'];oldraw=np.load(B/f'{k}-raw.npz',allow_pickle=False)['coverage'];ext=masks['exterior'];frozen=masks['glass']&(oldraw<1);newpartial=masks['glass']&(coverage<1)
  ext_old=float(np.sqrt(np.mean((old[ext]-s.target_crop[ext])**2))*255);ext_new=float(np.sqrt(np.mean((complete[ext]-s.target_crop[ext])**2))*255)
  asrun=float(np.sqrt(np.mean((complete[ext]-s.target_crop[ext])**2)))*255
  row=next(x for x in validation if x['reference']==k)
  assert np.array_equal(complete[ext],old[ext]),'Exterior pixels differ'
  assert ext_old==row['original_order_prior_exterior'] and ext_new==row['original_order_current_exterior'] and asrun==reported['scores']['exterior']['rmse']
  partial_old=float(np.sqrt(np.mean(((old-s.target_crop)[frozen]*255)**2)));partial_new=float(np.sqrt(np.mean(((complete-s.target_crop)[frozen]*255)**2)))
  assert int(frozen.sum())==22 and partial_old==row['frozen_old_partial_baseline_RMSE'] and partial_new==row['frozen_old_partial_transfer_RMSE']
  assert int(newpartial.sum())==4 and int(newpartial.sum())==reported['partial_original_glass']['pixels']
  newerr=(complete-s.target_crop)*255;assert float(np.sqrt(np.mean(newerr[newpartial]**2)))==reported['partial_original_glass']['RMSE']
  old_scores=reported['prior_separate_model_scores'];guards={}
  for scope in ('legacy_material','completed_image'):
   for name in ('glass','rim','held','interior'):guards[scope+':'+name]=scores[scope][name]['rmse']<=old_scores[scope][name]['rmse']
   guards[scope+':E']=scores[scope]['E']<=old_scores[scope]['E'];guards[scope+':SSIM']=scores[scope]['ssim']>=old_scores[scope]['ssim']
  guards['exterior']=ext_new<=ext_old
  guards.update({name:value<=old_scores['foreground_artwork_MSE'][name] for name,value in fg.items()})
  assert all(guards.values()),'Original aggregate or foreground guard failed'
  result['records'].append({'reference':k,'pre_foreground_exact':True,'complete_exact':True,'normalized_material_exact':True,'clear_samples_exact':True,'clipping':clipping,'scores_exact':scores,'foreground_artwork_exact':fg,'original_guards':guards,'corrected_center':(np.asarray(s.case['center'])+s.L*np.array([prior_params['shape_dx'],prior_params['shape_dy']])).tolist(),'frozen_partial':{'pixels':22,'old':partial_old,'new':partial_new,'nonregress':partial_new<=partial_old},'new_coverage_partial':reported['partial_original_glass'],'exterior':{'complete_pixels_exact':True,'original_order_old':ext_old,'original_order_new':ext_new,'asrun_order_preserved':asrun}})
  save('progress.json',{'references_completed':len(result['records']),'ledger':ledger})
 result['status']='PASS_IMPLEMENTATION_WITH_LOCAL_LIMITS';result['family_static_consumption']='One config; exact expanded controls and response; only major half differs; no surface constructed by peer.';result['expanded_zero_controls_reused']=zeros
except Exception as exc:
 result['status']='STOPPED_FIRST_DISCREPANCY';result['failure']=repr(exc)
finally:
 result['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (OUT/'verification.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 print(json.dumps({'status':result['status'],'failure':result.get('failure'),'records':len(result['records']),'ledger':ledger}),flush=True)
