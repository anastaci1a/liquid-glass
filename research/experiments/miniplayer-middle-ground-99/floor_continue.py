"""Two fixed highlight brightness floors after the source-color review."""
from material_common import *
import material_common as common
from color_edge_plateau import apply_color_rim,apply_luminance_floor_rim
from environment_radiance import decode_srgb,encode_srgb
OUT=BASE/'brightness-floor';P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);K=json.loads((OUT/'continuation-contract.json').read_text());P['caps']=K['cumulative_caps'];ledger=K['prior_ledger'].copy();first={}
def save(n,v):(OUT/('ledger-resumed.json' if n=='ledger.json' else 'continuation-checkpoint.json' if n=='checkpoint.json' else n)).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def read(p,keys):
 first[str(p.relative_to(ROOT))]=sha(p)
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));assert not dt.hasobject;charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in keys}
fx=metric_functions(charge);score=fx['score']
def independent(body,guide,alpha,k):
 out=body.copy();ok=alpha>0;B=decode_srgb(body[ok].astype(float));G=decode_srgb(guide[ok].astype(float));peak=G.max(-1,keepdims=True);direction=np.divide(G,peak,out=np.ones_like(G),where=peak>0);q=(peak+.4378927114042099)/(peak+.4378927114042099+(1-peak)/1.4);stored=encode_srgb(q*direction).astype(guide.dtype);stored[np.all(guide[ok]==1,axis=-1)]=1.;E=decode_srgb(stored);w=np.array([.2126,.7152,.0722]);Y=E@w;T=B@w+k*(1-B@w);f=np.divide(np.maximum(T-Y,0),1-Y,out=np.zeros_like(Y),where=Y<1);C=encode_srgb((1-f[:,None])*E+f[:,None]);C[np.all(body[ok]==1,axis=-1)]=1;out[ok]=body[ok]+alpha[ok,None]*(C-body[ok]);return out

def run():
 assert not (OUT/'continuation-started.json').exists();save('continuation-started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 for p in [Path(__file__),ROOT/'reconstruction/color_edge_plateau.py',ROOT/'reconstruction/edge_color_filter.py',BASE/'material_common.py']:first[str(p.relative_to(ROOT))]=sha(p)
 common.NATIVE=BASE/'native-r1.25';data=load_data(charge,first);alpha={m:read(BASE/f'display/{m}-alpha32.npz',['alpha'])['alpha'][1] for m in ['expanded','compact']};rows=[];replays=[];samples=[]
 for (m,r),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;charge('guide_composites',1);guide=s.apply_foreground(z['raw_source'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32));old=read(BASE/f'display/{m}-{r}-combined.npz',['complete','shadowed_body','pre_foreground']);body=old['shadowed_body'];oldscore=json.loads((BASE/f'display/{m}-{r}-combined-metrics.json').read_text())['scores']
  if (m,r)!=('expanded','a'):
   charge('identity_composites',1);identity=apply_color_rim(body,guide,alpha[m]);assert np.array_equal(identity,old['complete'],equal_nan=True);assert score(s,identity,d['m'],d['partial'],d['crops'])==oldscore
  save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),last_exact_identity=f'{m}-{r}',shared_input_sha=first))
  for k in P['brightening']:
   prefix=f'{m}-{r}-floor{k}';file=OUT/f'{prefix}.npz'
   if file.exists():
    C=read(file,['complete'])['complete'];row=json.loads((OUT/f'{prefix}-metrics.json').read_text());now=row['scores']
   else:
    charge('candidate_composites',1);C=apply_luminance_floor_rim(body,guide,alpha[m],k);now=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=m,reference=r,brightening=k,scores=now,original_guards=guards(now,d['original']),raw_guide_guards=guards(now,oldscore));np.savez_compressed(file,complete=C,shadowed_body=body,pre_foreground=old['pre_foreground']);save(prefix+'-metrics.json',row);charge('presentation_panels',1);panels(OUT,prefix,d,C,fx['to_image'],f'Color-bearing rim; brightness floor {k}')
   rows.append(row)
   charge('replay_composites',1);replay=independent(body,guide,alpha[m],k);good=np.isfinite(C);err=float(np.max(abs(replay[good]-C[good])));assert err<=1e-7;rs=score(s,replay,d['m'],d['partial'],d['crops']);ag=guards(rs,d['original']);assert ag==row['original_guards'];replays.append(dict(member=m,reference=r,brightening=k,max_array_error=err,E_difference=rs['E']-now['E'],original_guards_equal=True,metrics_exact=rs==now))
   if m=='expanded':
    x0,y0,_,_=s.crop
    for x in [1160,1280,1400]:
     for y in list(range(319,335))+list(range(492,508)):
      charge('diagnostic_pixels',1);i,j=y-y0,x-x0;samples.append(dict(reference=r,brightening=k,x=x,y=y,target=(s.target_crop[i,j]*255).tolist(),result=(C[i,j]*255).tolist(),alpha=float(alpha[m][i,j])))
   print(m,r,k,now['E'],[n for n,v in row['original_guards'].items() if not v],flush=True);save('ledger.json',ledger)
 save('yellow-samples.json',samples);means={str(k):float(np.mean([r['scores']['E'] for r in rows if r['brightening']==k])) for k in P['brightening']};save('result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,mean_errors=means,presentation_choice=float(min(means,key=means.get)),own_replays=replays,selected_changed=False,family_qualifier=any(all(all(r['original_guards'].values()) for r in rows if r['brightening']==k) for k in P['brightening'])));assert first=={p:sha(ROOT/p) for p in first};save('continuation-hashes.json',first);save('ledger.json',ledger)
 for name,h in K['retained_files'].items():assert sha(OUT/name)==h,name
try:run()
except Exception as e:save('continuation-failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e)));save('ledger.json',ledger);raise
