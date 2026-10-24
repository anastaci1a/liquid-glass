"""Fixed shared contact shadow on the selected family's clear underlay."""
from pathlib import Path
import json,datetime,sys,ast
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from extended_shadow import shadow
from music_miniplayer_family import load_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=load_family();cv2.setNumThreads(1)
ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original shadow deadline'
def charge(k,n):
 gate();d={k:int(n)}
 if k=='score_calls':d.update({'SSIM_Gaussians':5*n,'metric_erosions':n})
 assert all(ledger[key]+v<=P['caps'][key] for key,v in d.items()),d
 for key,v in d.items():ledger[key]+=int(v)
 save('ledger.json',ledger)
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(helper),'exec'))
assert not (OUT/'started.json').exists(),'One shadow family only'
save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
baselines=json.loads((ROOT/'research/experiments/miniplayer-split-surface-09/result.json').read_text())['records'];data={};identity=[]
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 base=ROOT/('research/experiments/expanded-contrast-guard-02' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06')
 paths=np.load(ROOT/('research/experiments/expanded-spline-observation-01/native-paths.npz' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06/compact-paths.npz'));inside=paths['inside'];unit_field=None;case_shape=None
 for k in ['a','b']:
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape
  masks=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz')
  accepted=np.load(base/(f'{k}-candidate.npz' if member=='expanded' else f'compact-{k}-candidate.npz'))
  rawfile=ROOT/f'research/experiments/expanded-spline-observation-01/{k}-candidate.npz' if member=='expanded' else base/f'compact-{k}-candidate.npz'
  raw=np.load(rawfile)['sample_before_response'];coverage=accepted['coverage'];clear=np.where(inside[...,None],0.,raw).reshape(H,2,W,2,3).mean((1,3));pre=accepted['pre_foreground'];C0=accepted['complete']
  charge('identity_composites',1);zero=s.apply_foreground((pre-clear*0).astype(np.float32));assert np.array_equal(zero,C0,equal_nan=True)
  center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
  if member=='compact':
   prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.asarray(s.case['center'])+s.L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
  g=F['geometry'];p=dict(shape_dx=(center[0]-s.case['center'][0])/s.L,shape_dy=(center[1]-s.case['center'][1])/s.L,half_x_delta=F['members'][member]['major_half']-s.half[0],half_y_delta=g['minor_half']-s.half[1],radius_delta=g['corner_radius']-s.radius,cap_join_width=0,shadow={**P['shared_seed'],'opacity':1.})
  shape_key=dict(center=s.case['center'],half=s.case['half'],radius=s.case['radius'],crop=s.crop,L=s.L,params=p)
  if unit_field is None:
   charge('shadow_field_points',H*W);charge('conservative_shadow_helper_points',3*H*W);unit_field=shadow(s,p,s.x,s.y);case_shape=shape_key;assert np.all((unit_field>=0)&(unit_field<=1))
   np.savez_compressed(OUT/f'{member}-unit-field.npz',opacity=unit_field)
  else:assert case_shape==shape_key,'Cannot share unit field between different poses'
  frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'] if member=='compact' else coverage
  partial=masks['glass']&(frozen<1);crops=json.loads((ROOT/'research/experiments/miniplayer-outline-light-07/protocol.json').read_text())['fixed_crops'][member]
  before=next(r['baseline'] for r in baselines if r['member']==member and r['reference']==k)
  data[(member,k)]=dict(s=s,H=H,W=W,pre=pre,C0=C0,clear=clear,unit=unit_field,coverage=coverage,masks=masks,partial=partial,crops=crops,before=before)
  identity.append(dict(member=member,reference=k,zero_exact=True))
save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),identities=identity,whole_fields=2,ledger=ledger))
records=[]
for factor in P['factors']:
 for (member,k),d in data.items():
  opacity=P['shared_seed']['opacity']*factor;pre=(d['pre']-d['clear']*(opacity*d['unit'])[...,None]).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy())
  full=d['coverage']==1;assert np.array_equal(C[full],d['C0'][full])
  now=score(d['s'],C,d['masks'],d['partial'],d['crops']);before=d['before'];guards={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};guards.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);guards.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()})
  prefix=f'{member}-{k}-factor{factor}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage'])
  w=min(1080,d['W']);h=round(d['H']*w/d['W']);canvas=Image.new('RGB',(2*w+2,h+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=16)
  for i,(v,label) in enumerate([(d['s'].target_crop,'Apple reference'),(C,f'Selected family; shared shadow prior x{factor}')]):canvas.paste(to_image(v).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64));draw.text((i*(w+2)+8,20),label,font=font,fill='black')
  canvas.save(OUT/f'{prefix}-comparison.png');row=dict(member=member,reference=k,factor=factor,opacity=opacity,scores=now,baseline=before,guards=guards,all_pass=all(guards.values()),fully_covered_pixels_exact=True);records.append(row);save(prefix+'-metrics.json',row);print(json.dumps(dict(member=member,reference=k,factor=factor,all_pass=row['all_pass'],E=now['E'],exterior=now['exterior'])),flush=True);gate()
save('result.json',dict(status='THREE_SHARED_FIXED_SHADOW_STRENGTHS_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,ledger=ledger,adopted=False,selected_model_changed=False))
