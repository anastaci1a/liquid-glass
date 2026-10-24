"""One linear incident-filter arithmetic comparison on fixed physical paths."""
from pathlib import Path
import sys,json,datetime,hashlib,ast
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response,incident_source_filter
from environment_radiance import decode_srgb,encode_srgb,annular_environment
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
helper=ROOT/'research/experiments/miniplayer-outline-light-07/render.py'
for file,names in [(helper,['score','display','to_image']),(ROOT/'research/experiments/miniplayer-neutral-scattering-71/observe.py',['panels'])]:
 tree=ast.parse(file.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(file),'exec'))
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 previous=json.loads((ROOT/'research/experiments/miniplayer-neutral-scattering-71/first-hashes.json').read_text());first={f:sha(ROOT/f) for f in previous};assert first==previous
 for f in [str(Path(__file__).relative_to(ROOT)),str(helper.relative_to(ROOT)),'research/experiments/miniplayer-neutral-scattering-71/observe.py']:first[f]=sha(ROOT/f)
 save('first-hashes.json',first);data={};proof=[];identities=[];PATHS=ROOT/'research/experiments/miniplayer-inverse-forward-18';BASE=ROOT/'research/experiments/miniplayer-incident-material-20'
 for member in ['expanded','compact']:
  q=np.load(PATHS/f'{member}-paths.npz');inside=q['inside'];T=q['primary_power'][inside];charge('environment_direction_queries',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside]);work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for k in ['a','b']:
   charge('Study_constructor_pixels',1360*250 if member=='expanded' else 920*240);s=Study(work/k);H,W=s.valid.shape;L=s.L
   center=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center']
   if member=='compact':
    prior=json.loads((ROOT/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=(np.asarray(s.case['center'])+L*np.array([prior['shape_dx'],prior['shape_dy']])).tolist()
   source=np.load(PATHS/f'{member}-{k}-light4.npz');raw=source['raw_source'];charge('cached_native_samples',inside.size);old=np.load(BASE/f'{member}-{k}-factor0.5.npz');v=raw.copy();coded=neutral_color_response(raw[inside],gain=F['material']['gain'],bias=F['material']['bias']);v[inside]=np.clip(encode_srgb(T[:,None]*decode_srgb(coded)+4*unit[:,None]),0,1);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('identity_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(pre,old['pre_foreground'],equal_nan=True) and np.array_equal(C,old['complete'],equal_nan=True)
   masks=np.load(work/f'{k}-masks.npz') if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz');assert np.array_equal(s.valid,masks['glass']);known=cv2.imread(str(work/k/'known.png'),0)>0;charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
   ix=q['X'][inside]*L+center[0];iy=q['Y'][inside]*L+center[1];a,b=np.floor(ix).astype(int),np.floor(iy).astype(int);assert ((a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0])).all();charge('source_audit_inside_samples',len(a));charge('bilinear_known_lookups',4*len(a));ok=safe[b,a]&safe[b,a+1]&safe[b+1,a]&safe[b+1,a+1];proof.append(dict(member=member,reference=k,lens_subrays=len(a),radius=21,unsupported=int((~ok).sum()),changed_RGB_queries=0,original_required_misses='Unchanged cached clear samples, source and coordinates inherit complete18 proof.'));assert ok.all(),'Unsupported full finite kernel'
   coverage=source['coverage'];frozen=coverage if member=='expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')['coverage'];partial=masks['glass']&(frozen<1);assert partial.sum()==(16 if member=='expanded' else 22);before=json.loads((BASE/f'{member}-{k}-factor0.5-metrics.json').read_text())['scores'];original=next(r['baseline'] for r in json.loads((PATHS/'result.json').read_text())['records'] if r['member']==member and r['reference']==k);crops=json.loads((PATHS/'protocol.json').read_text())['fixed_crops'][member]
   data[(member,k)]=dict(s=s,H=H,W=W,raw=raw,inside=inside,T=T,unit=unit,masks=masks,known=known,safe=safe,partial=partial,crops=crops,before=before,original=original,baseline=C,coverage=coverage,a=a,b=b,wx=(ix-a)[:,None],wy=(iy-b)[:,None]);identities.append(dict(member=member,reference=k,pre_foreground_exact=True,complete_exact=True))
 save('source-FIRST.json',dict(status='ALL_FOUR_FULL_KERNEL_PREFLIGHTS_PASS_BEFORE_CHANGED_RGB',records=proof,observed_truth=False));now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',dict(at=now.isoformat(),identities=identities,ledger=dict(ledger)));print('CHECKPOINT '+now.isoformat()+' four identities and source-first gates PASS',flush=True);rows=[]
 for (member,k),d in data.items():
  charge('incident_fields',1);charge('known_erosions',1);linear_source=decode_srgb(d['s'].source).astype(d['s'].source.dtype);field,known,radius=incident_source_filter(linear_source,d['known'],6.75);assert radius==21 and np.array_equal(known,d['safe']);a,b,wx,wy=d['a'],d['b'],d['wx'],d['wy'];charge('source_RGB_queries',len(a));sample=(field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy;assert np.isfinite(sample).all();coded,preclip=neutral_color_response(encode_srgb(sample),gain=F['material']['gain'],bias=F['material']['bias'],return_preclip=True);encoded=encode_srgb(d['T'][:,None]*decode_srgb(coded)+4*d['unit'][:,None]);clipping=[int((preclip<0).sum()),int((preclip>1).sum()),int((encoded>1).sum())];v=d['raw'].copy();v[d['inside']]=np.clip(encoded,0,1);pre=v.reshape(d['H'],2,d['W'],2,3).mean((1,3)).astype(np.float32);charge('candidate_composites',1);C=d['s'].apply_foreground(pre.copy());now=score(d['s'],C,d['masks'],d['partial'],d['crops'])
  def guards(before):
   checks={n:now[n]['rmse']<=before[n]['rmse'] for n in ['glass','rim','held','interior']};checks.update(E=now['E']<=before['E'],SSIM=now['ssim']>=before['ssim'],exterior=now['exterior']<=before['exterior'],partial=now['partial']['RMSE']<=before['partial']['RMSE']);checks.update({n:x<=before['foreground'][n] for n,x in now['foreground'].items()});return checks
  check=guards(d['before']);clear=~d['inside'].reshape(d['H'],2,d['W'],2).any((1,3));assert np.array_equal(pre[clear],d['baseline'][clear],equal_nan=True);prefix=f'{member}-{k}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C,coverage=d['coverage']);panels(prefix,d['s'],d['baseline'],C,d['crops']);row=dict(member=member,reference=k,scores=now,baseline=d['before'],current_guards=check,original_numerical_guards=guards(d['original']),clipping=clipping,clear_pixels_exact=True,all_current_pass=all(check.values()) and not any(clipping));save(prefix+'-metrics.json',row);rows.append(row);print(member,k,now['E'],row['all_current_pass'],flush=True)
 last={f:sha(ROOT/f) for f in first};assert last==first;save('last-hashes.json',last);save('result.json',dict(status='ONE_LINEAR_INCIDENT_FILTER_COMPLETE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,ledger=ledger,all_family_guards_pass=all(r['all_current_pass'] for r in rows),adopted=False,selected_model_changed=False,new_rays=0,new_heights=0,clear_queries=0,fits=0,retention='Candidate pre/complete/coverage and exact source/filter/query recipes retained; full changed field/sample arrays reproducible, not archived.'))
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),type=type(e).__name__,message=str(e),ledger=ledger));raise
