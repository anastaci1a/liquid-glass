"""Two fixed incident widths, with all-reference support before RGB."""
from pathlib import Path
import json,datetime,sys,ast,hashlib
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import annular_environment,decode_srgb,encode_srgb
from music_miniplayer_family import load_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=load_family();cv2.setNumThreads(1)
ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original stage deadline'
def charge(k,n):
 gate();delta={k:int(n)}
 if k=='score_calls':delta.update({'SSIM_Gaussians':5*n,'metric_erosions':n})
 assert all(ledger[key]+v<=P['caps'][key] for key,v in delta.items()),delta
 for key,v in delta.items():ledger[key]+=int(v)
 save('ledger.json',ledger)
# Frozen scoring and picture definitions only; never execute the old run body.
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(helper),'exec'))
assert not (OUT/'started.json').exists(),'One incident-width study only'
save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
BASE=ROOT/'research/experiments/miniplayer-split-surface-09';data={};proof=[];eligible={v:True for v in P['allowed_widths_native_pixels']}
oldrows=json.loads((BASE/'result.json').read_text())['records']
for member in ['expanded','compact']:
 q=np.load(BASE/f'{member}-paths.npz');inside=q['inside'];charge('environment_direction_queries',int(inside.sum()))
 unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside])
 work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
 for k in ['a','b']:
  charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape;L=s.L;case=s.case
  center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
  if member=='compact':
   prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.asarray(case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
  X=q['X']*L+center[0];Y=q['Y']*L+center[1]
  masks=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz')
  assert np.array_equal(s.valid,masks['glass']);known=cv2.imread(str(work/k/'known.png'),0)>0
  cache=np.load(BASE/f'{member}-{k}-light4.npz');raw=cache['raw_source'];insidevalues=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias'])
  values=raw.copy();values[inside]=np.clip(encode_srgb(decode_srgb(insidevalues)+4*unit[:,None]),0,1)
  pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy())
  assert np.array_equal(pre,cache['pre_foreground'],equal_nan=True) and np.array_equal(C,cache['complete'],equal_nan=True)
  old=next(r for r in oldrows if r['member']==member and r['reference']==k and r['amplitude']==4)
  frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'] if member=='compact' else cache['coverage']
  partial=masks['glass']&(frozen<1);crops=json.loads((BASE/'protocol.json').read_text())['fixed_crops'][member]
  ix,iy=X[inside],Y[inside];a,b=np.floor(ix).astype(int),np.floor(iy).astype(int);bounds=(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);assert bounds.all()
  safe={}
  for width in P['allowed_widths_native_pixels']:
   radius=int(np.ceil(3*width));charge('known_erosions',1);mask=cv2.erode(known.astype(np.uint8),np.ones((2*radius+1,2*radius+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
   charge('source_audit_inside_samples',len(a));charge('bilinear_known_lookups',4*len(a));ok=mask[b,a]&mask[b,a+1]&mask[b+1,a]&mask[b+1,a+1]
   safe[width]=mask;eligible[width]&=bool(ok.all());proof.append(dict(member=member,reference=k,width=width,radius=radius,whole_lens_samples=len(a),unsupported=int((~ok).sum()),RGB_queries=0,original_guard_misses='Unchanged clear coordinates and samples inherit09 complete proof.'))
  data[(member,k)]=dict(s=s,H=H,W=W,inside=inside,unit=unit,masks=masks,known=known,raw=raw,baseline=C,old=old,a=a,b=b,ix=ix,iy=iy,safe=safe,partial=partial,crops=crops,coverage=cache['coverage'])
save('source-FIRST.json',dict(status='ALL_FOUR_REFERENCES_PREFLIGHTED_BEFORE_CHANGED_RGB',records=proof,eligible_widths={str(k):v for k,v in eligible.items()},observed_truth=False))
save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),four_identities_exact=True,source_preflight_complete=True,ledger=ledger))
records=[]
for width in P['allowed_widths_native_pixels']:
 if not eligible[width]:continue
 for (member,k),d in data.items():
  s=d['s'];inside=d['inside'];charge('incident_fields',1);charge('known_erosions',1);field,known,radius=incident_source_filter(s.source,d['known'],width);assert np.array_equal(known,d['safe'][width])
  a,b=d['a'],d['b'];wx=(d['ix']-a)[:,None];wy=(d['iy']-b)[:,None];charge('source_RGB_queries',len(a));sample=(field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
  primary=neutral_color_response(sample,gain=F['material']['gain'],bias=F['material']['bias']);encoded=encode_srgb(decode_srgb(primary)+4*d['unit'][:,None]);clips=int((encoded>1).sum())
  values=d['raw'].copy();values[inside]=np.clip(encoded,0,1);pre=values.reshape(d['H'],2,d['W'],2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=s.apply_foreground(pre.copy())
  now=score(s,C,d['masks'],d['partial'],d['crops'])
  def guards(before):
   g={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};g.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);g.update({n:v<=before['foreground'][n] for n,v in now['foreground'].items()});return g
  held=guards(d['old']['scores']);selected=guards(d['old']['baseline']);prefix=f'{member}-{k}-sigma{width}'
  np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage'],inside_source_samples=sample)
  w=min(1080,d['W']);h=round(d['H']*w/d['W']);canvas=Image.new('RGB',(2*w+2,h+64),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=16)
  for i,(v,label) in enumerate([(s.target_crop,'Apple reference'),(C,f'Held split surfaces; incident sigma {width}')]):canvas.paste(to_image(v).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64));draw.text((i*(w+2)+8,20),label,font=font,fill='black')
  canvas.save(OUT/f'{prefix}-comparison.png')
  row=dict(member=member,reference=k,width=width,radius=radius,scores=now,held_guards=held,selected_guards=selected,held_all_pass=all(held.values()),selected_all_pass=all(selected.values()),clipping=clips,baseline_held_E=d['old']['scores']['E'],baseline_selected_E=d['old']['baseline']['E'])
  records.append(row);save(prefix+'-metrics.json',row);print(json.dumps(dict(member=member,reference=k,width=width,E=now['E'],held_pass=all(held.values()),selected_pass=all(selected.values()))),flush=True);gate()
save('result.json',dict(status='TWO_FIXED_INCIDENT_WIDTHS_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,ledger=ledger,selected_model_changed=False,adopted=False))
