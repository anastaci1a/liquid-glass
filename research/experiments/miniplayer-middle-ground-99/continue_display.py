"""Continue from retained fields and candidates; no repeated scientific settings."""
import ast
from pathlib import Path
p=Path(__file__).with_name('display.py');tree=ast.parse(p.read_text());exec(compile(ast.Module(body=[n for n in tree.body if not isinstance(n,ast.Try) and not (isinstance(n,ast.FunctionDef) and n.name=='run')],type_ignores=[]),str(p),'exec'))
K=json.loads((OUT/'continuation-contract.json').read_text());P['caps']=K['cumulative_caps'];ledger=K['prior_ledger'].copy();first={}
def flush():save('ledger-resumed.json',ledger)
def read(p,keys):
 first[str(p.relative_to(ROOT))]=sha(p)
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in keys}
def scalars(x,path=''):
 out={}
 if isinstance(x,dict):
  for k,v in x.items():out.update(scalars(v,path+'/'+k))
 elif isinstance(x,(int,float)):out[path]=float(x)
 return out

def resume():
 assert not (OUT/'continuation-started.json').exists();save('continuation-started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 choice=json.loads((OUT/'shape-selection.json').read_text())['selected']['folder'];common.NATIVE=BASE/choice;reduction=1.25 if choice=='native-r1.25' else .75;data=load_data(charge,first)
 for d in data.values():
  d['radius']-=reduction;H,W=d['s'].valid.shape;charge('guide_composites',1);d['guide']=d['s'].apply_foreground(d['z']['raw_source'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32))
 alphas={m:read(OUT/f'{m}-alpha32.npz',['alpha'])['alpha'] for m in ['expanded','compact']};shadows={m:read(OUT/f'{m}-shadows.npz',['offset0','offset14','offset18']) for m in ['expanded','compact']};rows=[];yellow=[];replays=[]
 for (member,k),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;clear=~z['inside']&z['supported'];bodies={};pres={}
  for offset in [0,14,18]:
   oldname='baseline' if offset==0 else f'shadow{offset}';file=OUT/f'{member}-{k}-{oldname}.npz'
   if file.exists():
    old=read(file,['pre_foreground','shadowed_body']);pres[offset]=old['pre_foreground'];bodies[offset]=old['shadowed_body']
   else:
    v=z['encoded_subrays'].copy();strength=.08 if offset==0 else 34/255;v[clear]*=1-strength*shadows[member][f'offset{offset}'][clear,None];assert np.array_equal(v[z['inside']],z['encoded_subrays'][z['inside']]);pres[offset]=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('shadow_composites',1);bodies[offset]=s.apply_foreground(pres[offset].copy());full=z['coverage']==1;assert np.array_equal(bodies[offset][full],z['complete'][full])
  a0,a1=alphas[member];guide=d['guide'];assert np.isfinite(guide[a1>0]).all();baseline=None
  for label,offset,kind,alpha in [('baseline',0,'legacy',a0),('shadow14',14,'legacy',a0),('shadow18',18,'legacy',a0),('graded',0,'graded',a0),('pregrade',0,'raw',a0),('plateau',0,'raw',a1),('combined',18,'raw',a1)]:
   body=bodies[offset];prefix=f'{member}-{k}-{label}';file=OUT/f'{prefix}.npz'
   if file.exists():C=read(file,['complete'])['complete'];row=json.loads((OUT/f'{prefix}-metrics.json').read_text());now=row['scores'];baseline=now if baseline is None else baseline
   else:
    charge('candidate_composites',1);C=edge_filter(body,alpha,**cfg) if kind=='legacy' else apply_color_rim(body,body if kind=='graded' else guide,alpha);now=score(s,C,d['m'],d['partial'],d['crops']);baseline=now if baseline is None else baseline
    row=dict(member=member,reference=k,setting=label,scores=now,original_guards=guards(now,d['original']),native_guards=guards(now,d['before']),display_baseline_guards=guards(now,baseline));np.savez_compressed(file,complete=C,pre_foreground=pres[offset],shadowed_body=body);save(prefix+'-metrics.json',row);charge('presentation_panels',1);panels(OUT,prefix,d,C,fx['to_image'],label+'; blur retained')
   rows.append(row)
   if member=='expanded':
    x0,y0,_,_=s.crop
    for x in P['yellow_diagnostics']['x']:
     for y in P['yellow_diagnostics']['y']:
      charge('diagnostic_pixels',1);i,j=y-y0,x-x0;yellow.append(dict(reference=k,setting=label,x=x,y=y,target=(s.target_crop[i,j]*255).tolist(),result=(C[i,j]*255).tolist(),blurred_pregrade=(guide[i,j]*255).tolist(),graded=(body[i,j]*255).tolist(),alpha=float(alpha[i,j])))
   if label=='combined':
    charge('replay_composites',1);again=independent(body,guide,alpha);finite=np.isfinite(C);err=float(np.max(abs(again[finite]-C[finite])));assert err<=1e-7 and np.array_equal(np.isnan(again),np.isnan(C));rs=score(s,again,d['m'],d['partial'],d['crops']);sa,sb=scalars(now),scalars(rs);changes={key:sb[key]-sa[key] for key in sa if sb[key]!=sa[key]};sameguards=guards(rs,d['original'])==row['original_guards']
    replays.append(dict(member=member,reference=k,max_array_error=err,within_original_array_tolerance=True,metric_differences=changes,metrics_exact=not bool(changes),original_guard_decisions_equal=sameguards));assert sameguards,'Replay changed original acceptance decisions'
   print('RETAINED' if file.name in K['retained_first_files'] else 'NEW',member,k,label,now['E'],flush=True);flush()
 save('yellow-samples.json',yellow);save('result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,own_replays=replays,selected_geometry_reduction=reduction,selected_changed=False,original_family_qualifier=all(all(r['original_guards'].values()) for r in rows if r['setting']=='combined'),exact_replay_failure_retained=True))
 for name,h in K['retained_first_files'].items():assert sha(OUT/name)==h,name
 assert first=={p:sha(ROOT/p) for p in first};save('continuation-hashes.json',first);flush()
try:resume()
except Exception as e:save('continuation-failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e)));flush();raise
