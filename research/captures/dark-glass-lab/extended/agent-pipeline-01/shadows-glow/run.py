"""Reuse existing neutral SDF shadow on clear contribution only. No rays."""
from pathlib import Path
import sys,time,json,numpy as np
P=Path('/evidence/extended/agent-pipeline-01');O=P/'shadows-glow';sys.path.insert(0,str(P/'code'))
from extended_fit import Study
from extended_shadow import shadow
from case_metrics import scores
proto=json.loads((O/'protocol.json').read_text());deadline=__import__('datetime').datetime.fromisoformat(proto['deadline'].replace('Z','+00:00')).timestamp()
def gate():assert time.time()<deadline,'Actual15minute shadow cap'
assert not (O/'result.json').exists(),'No completed-study restart';gate();old=json.loads((P/'historical-pass03.json').read_text());p=old['parameters'];p={**p,'shadow':{**p['shadow'],'opacity':1.}};data={};base={};field=None
for key in ['a','b']:
 s=Study(P/f'inputs/{key}');masks=np.load(P/f'historical-{key}-masks.npz');alpha=np.load(P/'blurriness'/f'{key}-coverage.npy');clear=np.load(P/'blurriness'/f'{key}-clear-premultiplied.npy');lens=np.load(P/'color-grading'/f'{key}-step0.5-lens.npy');M0=np.load(P/'color-grading'/f'{key}-step0.5-material.npy');C0=np.load(P/'color-grading'/f'{key}-step0.5-complete.npy')
 if field is None:field=shadow(s,p,s.x,s.y);geom={k:s.case[k] for k in ['center','half','radius','crop']}
 else:assert geom=={k:s.case[k] for k in geom},'Shared field needs exact pose';
 assert field.min()>=0 and field.max()<=1
 zero=(alpha[...,None]*lens+clear).astype(np.float32);finite=np.isfinite(M0);assert np.array_equal(zero[finite],M0[finite]);assert np.array_equal(np.isnan(zero),np.isnan(M0));C=s.apply_foreground(zero.copy());finite=np.isfinite(C0);assert np.array_equal(C[finite],C0[finite]);base[key]=scores(s,masks,C0);data[key]=(s,masks,alpha,clear,lens,M0,C0)
np.save(O/'shared-unit-opacity-field.npy',field);(O/'zero-control.json').write_text(json.dumps({'body_complete_pixel_exact_both':True,'new_rays':0,'new_source_queries':0,'source_maps_kernel_coverage_foreground_unchanged':True,'operator':'Existing extended_shadow.shadow only, no refit/main/Study.render/oldfield/targetcontext'},indent=2));ledger=[];selected=None
for step,opacity in enumerate(proto['opacity_settings']):
 gate();row={'trial':step,'opacity':opacity,'cases':{}}
 for key,(s,masks,alpha,clear,lens,M0,C0) in data.items():
  M=(alpha[...,None]*lens+clear*(1-opacity*field[...,None])).astype(np.float32);C=s.apply_foreground(M.copy());r=scores(s,masks,C);b=base[key];guards={x:r[x]['rmse']<=b[x]['rmse'] for x in ['glass','rim','held','interior','exterior']};guards.update(E=r['E']<=b['E'],ssim=r['ssim']>=b['ssim']);guards.update({f'foreground{k}':z<=b['foreground_MSE'][k] for k,z in enumerate(r['foreground_MSE'])});partial=masks['glass']&(alpha<1);full=masks['glass']&(alpha==1);err=(C-s.target_crop)*255;H,W=alpha.shape;x0,y0,_,_=s.crop;Y,X=np.mgrid[y0:y0+H,x0:x0+W];known=np.isfinite(C).all(2);outside=(alpha==0)&known;cohorts={'all_known_outside':outside,'above':outside&(Y<s.case['center'][1]-s.L),'below':outside&(Y>s.case['center'][1]+s.L),'left':outside&(X<s.case['center'][0]-s.case['half'][0]),'right':outside&(X>s.case['center'][0]+s.case['half'][0])};local={}
  for name,m in cohorts.items():
   if m.any():local[name]={'pixels':int(m.sum()),'rmse':float(np.sqrt(np.mean(err[m]**2))),'signed_RGB':err[m].mean(0).tolist()}
  native=M[np.isfinite(M).all(2)];assert not (native<0).any() and not (native>1).any();row['cases'][key]={'scores':r,'guards':guards,'all_guards':bool(all(guards.values())),'fully_covered_original_glass_pixel_exact':bool(np.array_equal(M[full],M0[full])),'original_glass_partial_pixels':int(partial.sum()),'changed_original_glass_pixels':int(np.any(M[partial]!=M0[partial],axis=1).sum()),'advisory_known_exterior':local,'native_clips':0};np.save(O/f'{key}-trial{step}-material.npy',M);np.save(O/f'{key}-trial{step}-complete.npy',C)
 row['paired_qualifier']=all(v['all_guards'] for v in row['cases'].values());ledger.append(row);(O/'ledger.json').write_text(json.dumps(ledger,indent=2,allow_nan=False));print(json.dumps({'trial':step,'opacity':opacity,'paired_qualifier':row['paired_qualifier'],'E':{k:z['scores']['E'] for k,z in row['cases'].items()},'exterior':{k:z['scores']['exterior']['rmse'] for k,z in row['cases'].items()},'failed':{k:[g for g,b in z['guards'].items() if not b] for k,z in row['cases'].items()}}),flush=True)
 if row['paired_qualifier']:selected=row;break
result={'status':'FIRST_STRICT_SHADOW_CANDIDATE_PENDING_REVIEW' if selected else 'NEGATIVE_ALL_THREE_PRIOR_OPACITIES','selected':selected,'baseline':base,'trials':ledger,'fits':0,'new_geometry_rays':0,'new_ray_source_queries':0,'historical_adoption':False,'claim':'Generated empirical exterior reconstruction only; not traced illumination/refraction improvement. No target residual or source change.','finished_unix':time.time()};(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False))
