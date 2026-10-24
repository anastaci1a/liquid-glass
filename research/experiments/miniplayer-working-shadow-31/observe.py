"""Fixed shared contact shadow on the selected family's clear underlay."""
from pathlib import Path
import json,datetime,sys,ast,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from extended_shadow import shadow
from music_miniplayer_family import load_working_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=load_working_family();cv2.setNumThreads(1)
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
data={};identity=[];bindings={}
for member in ['expanded','compact']:
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 pathfile=ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-paths.npz';paths=np.load(pathfile);inside=paths['inside'];fieldfile=ROOT/f'research/experiments/miniplayer-shared-shadow-13/{member}-unit-field.npz';charge('cached_unit_field_pixels',1360*250 if member=='expanded' else 920*240);unit_field=np.load(fieldfile)['opacity'];assert np.all((unit_field>=0)&(unit_field<=1));bindings[str(fieldfile.relative_to(ROOT))]=hashlib.sha256(fieldfile.read_bytes()).hexdigest();bindings[str(pathfile.relative_to(ROOT))]=hashlib.sha256(pathfile.read_bytes()).hexdigest()
 # All intervening experiments preserve the exact accepted footprint, pose and AA2. Native lens membership is checked against the original field generation's path cache.
 oldpath=ROOT/('research/experiments/expanded-spline-observation-01/native-paths.npz' if member=='expanded' else 'research/experiments/miniplayer-shared-transfer-06/compact-paths.npz');assert np.array_equal(inside,np.load(oldpath)['inside'])
 for k in ['a','b']:
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape
  masks=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz')
  file=ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5.npz';accepted=np.load(file);bindings[str(file.relative_to(ROOT))]=hashlib.sha256(file.read_bytes()).hexdigest();source=np.load(ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-{k}-light4.npz');raw=source['raw_source'];coverage=source['coverage'];clear=np.where(inside[...,None],0.,raw).reshape(H,2,W,2,3).mean((1,3));pre=accepted['pre_foreground'];C0=accepted['complete']
  charge('identity_composites',1);zero=s.apply_foreground((pre-clear*0).astype(np.float32));assert np.array_equal(zero,C0,equal_nan=True)
  frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'] if member=='compact' else coverage
  partial=masks['glass']&(frozen<1);crops=json.loads((ROOT/'research/experiments/miniplayer-outline-light-07/protocol.json').read_text())['fixed_crops'][member];charge('score_calls',1);before=score(s,C0,masks,partial,crops);assert before==json.loads((ROOT/f'research/experiments/miniplayer-incident-material-20/{member}-{k}-factor0.5-metrics.json').read_text())['scores'];original=json.loads((ROOT/f'research/experiments/miniplayer-inverse-forward-18/{member}-{k}-light4-metrics.json').read_text())['baseline']
  data[(member,k)]=dict(s=s,H=H,W=W,pre=pre,C0=C0,clear=clear,unit=unit_field,coverage=coverage,masks=masks,partial=partial,crops=crops,before=before,original=original)
  identity.append(dict(member=member,reference=k,zero_exact=True,score_exact=True))
save('bindings.json',bindings)
save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),identities=identity,reused_fields=2,ledger=ledger))
records=[]
for factor in P['factors']:
 for (member,k),d in data.items():
  opacity=P['shared_seed']['opacity']*factor;pre=(d['pre']-d['clear']*(opacity*d['unit'])[...,None]).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy())
  full=d['coverage']==1;assert np.array_equal(C[full],d['C0'][full])
  charge('score_calls',1);now=score(d['s'],C,d['masks'],d['partial'],d['crops']);before=d['before'];guards={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};guards.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);guards.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()})
  original=d['original'];original_guards={n:now[n]['rmse']<=original[n]['rmse'] for n in ['glass','rim','held','interior']};original_guards.update(E=now['E']<=original['E'],SSIM=now['ssim']>=original['ssim'],exterior=now['exterior']<=original['exterior'],partial=now['partial']['RMSE']<=original['partial']['RMSE']);original_guards.update({n:v<=original['foreground'][n] for n,v in now['foreground'].items()})
  prefix=f'{member}-{k}-factor{factor}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage'])
  w=min(1080,d['W']);h=round(d['H']*w/d['W']);canvas=Image.new('RGB',(2*w+2,h+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=16)
  for i,(v,label) in enumerate([(d['s'].target_crop,'Apple reference'),(C,f'Working family; shared shadow prior x{factor}')]):canvas.paste(to_image(v).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64));draw.text((i*(w+2)+8,20),label,font=font,fill='black')
  canvas.save(OUT/f'{prefix}-comparison.png');row=dict(member=member,reference=k,factor=factor,opacity=opacity,scores=now,baseline=before,guards=guards,original_guards=original_guards,all_original_pass=all(original_guards.values()),all_pass=all(guards.values()),fully_covered_pixels_exact=True);records.append(row);save(prefix+'-metrics.json',row);print(json.dumps(dict(member=member,reference=k,factor=factor,all_pass=row['all_pass'],E=now['E'],exterior=now['exterior'])),flush=True);gate()
save('result.json',dict(status='THREE_SHARED_FIXED_SHADOW_STRENGTHS_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,ledger=ledger,adopted=False,selected_model_changed=False))
