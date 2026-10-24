"""One anchor-derived material curve; no optical re-evaluation or target fit."""
from pathlib import Path
import sys,json,datetime,hashlib,ast
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent
sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,annular_environment
from neutral_scattering import match_encoded_material_anchors,white_scattering_response
from music_miniplayer_family import load_working_family
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']};F=load_working_family();cv2.setNumThreads(1)
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Original deadline'
def charge(k,n):
 gate();delta={k:int(n)}
 if k=='score_calls':delta.update(SSIM_Gaussians=5*n,metric_erosions=n)
 assert all(ledger[x]+v<=P['caps'][x] for x,v in delta.items()),delta
 for x,v in delta.items():ledger[x]+=int(v)
 save('ledger.json',ledger)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py';tree=ast.parse(helper.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['score','display','to_image']],type_ignores=[]),str(helper),'exec'))
def panels(prefix,s,baseline,candidate,crops):
 w=min(s.valid.shape[1],1080);h=round(s.valid.shape[0]*w/s.valid.shape[1]);im=Image.new('RGB',(3*w+4,h+64),'white');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=16)
 for i,(v,label) in enumerate([(s.target_crop,'Apple reference'),(baseline,'Working20 encoded response'),(candidate,'Anchor-matched linear scattering')]):
  im.paste(to_image(v).resize((w,h),Image.Resampling.LANCZOS),(i*(w+2),64));draw.text((i*(w+2)+8,20),label,font=font,fill='black')
 im.save(OUT/f'{prefix}-comparison.png');rows=[];x0,y0,_,_=s.crop
 for name,(a,b,c,d) in crops.items():
  w,h=2*(c-a),2*(d-b);row=Image.new('RGB',(3*w+4,h+32),'white');draw=ImageDraw.Draw(row)
  for i,(v,label) in enumerate([(s.target_crop,'Reference'),(baseline,'Working20'),(candidate,'Linear mixture')]):row.paste(to_image(v[b-y0:d-y0,a-x0:c-x0]).resize((w,h),Image.Resampling.NEAREST),(i*(w+2),32));draw.text((i*(w+2)+3,6),f'{name}: {label}',font=font,fill='black')
  rows.append(row)
 sheet=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+8*(len(rows)-1)),'white');y=0
 for row in rows:sheet.paste(row,(0,y));y+=row.height+8
 sheet.save(OUT/f'{prefix}-crops.png')
def run():
 assert not (OUT/'started.json').exists(),'One declared execution only';save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 binding=json.loads((ROOT/'research/experiments/miniplayer-working-blur-64/retained-input-bindings.json').read_text())['entries'];files=set()
 for r in binding:assert sha(ROOT/r['file'])==r['sha256'];files.add(r['file'])
 for name in ['reconstruction/neutral_scattering.py','reconstruction/environment_radiance.py','reconstruction/geometric_render.py','reconstruction/extended_fit.py','reconstruction/music_miniplayer_family.py','reconstruction/families/music-mini-player-working.json',str(Path(__file__).relative_to(ROOT)),str(helper.relative_to(ROOT))]:files.add(name)
 for member in ['expanded','compact']:
  work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for k in ['a','b']:
   case=json.loads((work/k/'case.json').read_text());files.add(str((work/k/'case.json').relative_to(ROOT)))
   for name in ['source.png','target.png','known.png']:
    fp=work/k/name;assert sha(fp)==case['source_sha256'][name];files.add(str(fp.relative_to(ROOT)))
   for layer in case['foreground_layers']:
    name=layer.get('vector_asset',layer.get('artwork_asset'));files.add(str((work/k/name).relative_to(ROOT)))
   mask=work/f'{k}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz';files.add(str(mask.relative_to(ROOT)))
 first={f:sha(ROOT/f) for f in sorted(files)};save('first-hashes.json',first)
 params=match_encoded_material_anchors(F['material']['gain'],F['material']['bias']);save('parameters.json',dict(params,derivation='Old white and encoded-middle-gray material anchors only; no target objective or parameter search.',white_illumination='Assumed normalized neutral scene illumination; not observed radiance.'))
 errors=[]
 for value in [.5,1.]:
  source=np.full(3,value);old=decode_srgb(neutral_color_response(source,gain=F['material']['gain'],bias=F['material']['bias']));new=white_scattering_response(decode_srgb(source),params['transmission'],params['white_level'])
  for power in [0.,.25,1.]:
   for light in [0.,.2]:
    charge('algebraic_checks',1);error=float(np.max(abs(encode_srgb(power*old+light)-encode_srgb(power*new+light))));assert error<2e-15;errors.append(error)
 controls=np.array([[0.,.25,1.],[.2,.5,.8],[1.,1.,1.],[0.,0.,0.]])
 for tau in [0.,1.,params['transmission']]:
  charge('algebraic_checks',1);v=white_scattering_response(controls,tau,params['white_level']);assert (v>=0).all() and (v<=params['white_level']).all()
  if tau==0:assert np.array_equal(v,np.full_like(v,params['white_level']))
  if tau==1:assert np.array_equal(v,params['white_level']*controls)
 data={};identities=[];BASE=ROOT/'research/experiments/miniplayer-incident-material-20';PATHS=ROOT/'research/experiments/miniplayer-inverse-forward-18'
 for member in ['expanded','compact']:
  q=np.load(PATHS/f'{member}-paths.npz');inside=q['inside'];T=q['primary_power'][inside];charge('environment_direction_queries',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for k in ['a','b']:
   charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape;source=np.load(PATHS/f'{member}-{k}-light4.npz');raw=source['raw_source'];charge('cached_native_samples',inside.size);z=np.load(BASE/f'{member}-{k}-factor0.5.npz');coded=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias']);values=raw.copy();values[inside]=np.clip(encode_srgb(T[:,None]*decode_srgb(coded)+4*unit[:,None]),0,1);pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,z['pre_foreground'],equal_nan=True) and np.array_equal(C,z['complete'],equal_nan=True)
   masks=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz');assert np.array_equal(s.valid,masks['glass']);coverage=source['coverage'];frozen=coverage if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'];partial=masks['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22)
   before=json.loads((BASE/f'{member}-{k}-factor0.5-metrics.json').read_text())['scores'];original=next(r['baseline'] for r in json.loads((PATHS/'result.json').read_text())['records'] if r['member']==member and r['reference']==k);crops=json.loads((PATHS/'protocol.json').read_text())['fixed_crops'][member]
   data[(member,k)]=dict(s=s,H=H,W=W,raw=raw,inside=inside,T=T,unit=unit,masks=masks,partial=partial,crops=crops,before=before,original=original,baseline=C,coverage=coverage);identities.append({'member':member,'reference':k,'pre_foreground_exact':True,'complete_exact':True})
 checkpoint=datetime.datetime.now(datetime.timezone.utc);assert checkpoint<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=checkpoint.isoformat(),identities=identities,anchor_max_error=max(errors),source_support='Actual18 coordinates/raw samples, unchanged6.75R21 input bytes and original source-proof transfer; no new query or field.',ledger=dict(ledger)));print('CHECKPOINT '+checkpoint.isoformat()+' all four identities and anchors PASS',flush=True)
 rows=[]
 for (member,k),d in data.items():
  linear_material=white_scattering_response(decode_srgb(d['raw'][d['inside']]),params['transmission'],params['white_level']);linear=d['T'][:,None]*linear_material+4*d['unit'][:,None];encoded=encode_srgb(linear);clipping=[int((linear_material<0).sum()),int((linear_material>1).sum()),int((encoded>1).sum())];v=d['raw'].copy();v[d['inside']]=np.clip(encoded,0,1);pre=v.reshape(d['H'],2,d['W'],2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy());now=score(d['s'],C,d['masks'],d['partial'],d['crops'])
  def guards(before):
   checks={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};checks.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);checks.update({n:x<=before['foreground'][n] for n,x in now['foreground'].items()});return checks
  check=guards(d['before']);clear=~d['inside'].reshape(d['H'],2,d['W'],2).any((1,3));clear_exact=np.array_equal(pre[clear],d['baseline'][clear],equal_nan=True);assert clear_exact
  row=dict(member=member,reference=k,scores=now,baseline=d['before'],current_guards=check,original_numerical_guards=guards(d['original']),clipping=clipping,clear_pixels_exact=clear_exact,all_current_pass=all(check.values()) and not any(clipping));rows.append(row);prefix=f'{member}-{k}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage']);save(prefix+'-metrics.json',row);panels(prefix,d['s'],d['baseline'],C,d['crops']);print(json.dumps({n:row[n] for n in ['member','reference','all_current_pass']}),now['E'],flush=True)
 last={f:sha(ROOT/f) for f in first};assert last==first;save('last-hashes.json',last);save('result.json',dict(status='ONE_ANCHOR_DERIVED_LINEAR_MIXTURE_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),parameters=params,records=rows,all_family_guards_pass=all(r['all_current_pass'] for r in rows),ledger=ledger,adopted=False,selected_model_changed=False,full_radiance=False,fits=0,new_rays=0,new_source_queries=0,new_fields=0,new_filters=0))
try:run()
except Exception as e:
 save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(e).__name__,message=str(e),ledger=ledger));raise
