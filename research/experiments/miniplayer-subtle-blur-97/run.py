"""One slight incident blur reduction and finite black-lifting edge response."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;sys.path.insert(0,str(ROOT/'research/experiments/miniplayer-complete-refinement-94'))
from material_common import *
from edge_color_filter import edge_filter
from geometric_render import incident_source_filter,neutral_color_response
from environment_radiance import decode_srgb,encode_srgb,annular_environment
import cv2
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={};cv2.setNumThreads(1)
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
fx=metric_functions(charge);score=fx['score']
def read(p,keys):
 first[str(p.relative_to(ROOT))]=sha(p)
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p) as z:return {k:z[k] for k in keys}
def run():
 assert not (OUT/'started.json').exists();save('started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 for p in [Path(__file__),ROOT/'reconstruction/edge_color_filter.py',ROOT/'reconstruction/geometric_render.py']:first[str(p.relative_to(ROOT))]=sha(p)
 cfg=dict(P['edge_filter']);black=cfg.pop('black_endpoint_encoded');q=float(decode_srgb(np.array(black)));cfg['lift']=q/((1-q)*cfg['exposure']);charge('response_controls',3);test=edge_filter(np.array([[0.,0.,0.],[1.,1.,1.],[.8,.7,.05]]),np.ones(3),**cfg);assert max(abs(test[0]-black))<1e-14 and np.array_equal(test[1],np.ones(3)) and test[2,0]>test[2,1]>test[2,2];save('filter-recipe.json',dict(parameters=cfg,black_endpoint=black,controls=test.tolist()))
 data=load_data(charge,first);records=[];proofs=[];fields={};alpha={}
 for member in ['expanded','compact']:
  alpha[member]=read(BASE/f'highlight/{member}-order16.npz',['alpha'])['alpha'];fields[member]=read(ROOT/f'research/experiments/miniplayer-edge-filter-96/{member}-broad-shadow-field.npz',['field'])['field']
 for (member,k),d in data.items():
  s,z=d['s'],d['z'];charge('identity_composites',1);ident=s.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(ident,z['complete'],equal_nan=True);assert score(s,ident,d['m'],d['partial'],d['crops'])==d['before']
 save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),baseline_identities_exact=True,black65_control_pass=True))
 for member in ['expanded','compact']:
  q=read(BASE/f'geometry-run-02/{member}-paths.npz',['X','Y','inside','primary_power','front_reflection_power','front_reflection_direction']);I=q['inside'];center=data[(member,'a')]['center'];X=q['X']*L+center[0];Y=q['Y']*L+center[1];a=np.floor(X[I]).astype(int);b=np.floor(Y[I]).astype(int);wx=(X[I]-a)[:,None];wy=(Y[I]-b)[:,None];charge('cached_environment_points',int(I.sum()));unit=q['front_reflection_power'][I]*annular_environment(q['front_reflection_direction'][I])
  # Both sources are certified for the changed finite kernel before either field.
  for k in ['a','b']:
   d=data[(member,k)];p=d['s'].folder/'known.png';charge('bitmap_pixels',1920*1080);known=cv2.imread(str(p),0)>0;charge('known_erosions',1);safe=cv2.erode(known.astype(np.uint8),np.ones((39,39),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0;charge('source_audits',len(a));charge('corner_lookups',4*len(a));assert (a>=0).all() and (a+1<1920).all() and (b>=0).all() and (b+1<1080).all();ok=safe[b,a]&safe[b+1,a]&safe[b,a+1]&safe[b+1,a+1];assert ok.all();d.update(known=known,safe=safe);proofs.append(dict(member=member,reference=k,body_subrays=len(a),all_finite_kernel_corners_known=True,original_clear_and_all_other_guards='Unchanged original94 proof; clear source coordinates and samples reused exactly.'));save('source-FIRST.json',proofs)
  for k in ['a','b']:
   d=data[(member,k)];s,z=d['s'],d['z'];H,W=s.valid.shape;charge('incident_fields',1);charge('known_erosions',1);field,safe,r=incident_source_filter(s.source,d['known'],P['sigma']);assert r==19 and np.array_equal(safe,d['safe']);charge('RGB_queries',len(a));raw=(field[b,a]*(1-wx)+field[b,a+1]*wx)*(1-wy)+(field[b+1,a]*(1-wx)+field[b+1,a+1]*wx)*wy
   values=z['encoded_subrays'].copy();prim=neutral_color_response(raw,gain=F['material']['gain'],bias=F['material']['bias']);v=encode_srgb(q['primary_power'][I,None]*decode_srgb(prim)+4*unit[:,None]);assert ((v>=0)&(v<=1)).all();values[I]=v;clear=~I&z['supported'];assert np.array_equal(values[clear],z['encoded_subrays'][clear]);pre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);C=s.apply_foreground(pre.copy());candidates=[('blur-only',C,pre)]
   oldvalues=z['encoded_subrays'].copy();oldvalues[clear]*=1-.08*fields[member][clear,None];oldpre=oldvalues.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);oldbody=s.apply_foreground(oldpre.copy());sealed=read(ROOT/f'research/experiments/miniplayer-edge-filter-96/{member}-{k}-broad-shadow.npz',['body_complete'])['body_complete'];charge('identity_composites',1);assert np.array_equal(oldbody,sealed,equal_nan=True);candidates.append(('filter-revision',edge_filter(oldbody,alpha[member],**cfg),oldpre))
   values[clear]*=1-.08*fields[member][clear,None];newpre=values.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);newbody=s.apply_foreground(newpre.copy());candidates.append(('combined',edge_filter(newbody,alpha[member],**cfg),newpre))
   previous=read(BASE/f'highlight/{member}-{k}-combined.npz',['complete'])['complete'];oldmetric=json.loads((BASE/f'highlight/{member}-{k}-combined-metrics.json').read_text())['scores']
   for name,C,pp in candidates:
    charge('candidate_composites',1);now=score(s,C,d['m'],d['partial'],d['crops']);row=dict(member=member,reference=k,stage=name,scores=now,original_guards=guards(now,d['original']),previous94_guards=guards(now,oldmetric),geometry94_guards=guards(now,d['before']));records.append(row);prefix=f'{member}-{k}-{name}';np.savez_compressed(OUT/f'{prefix}.npz',complete=C,pre_foreground=pp);save(prefix+'-metrics.json',row);panels(OUT,prefix,d,C,fx['to_image'],name+'; original20 comparison')
   np.savez_compressed(OUT/f'{member}-{k}-source-retained.npz',incident_field=field,raw_lens_samples=raw)
 save('result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,selected_changed=False));assert first=={p:sha(ROOT/p) for p in first};save('hashes.json',first);save('ledger.json',ledger);print('SUBTLE BLUR COMPLETE',flush=True)
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e)));save('ledger.json',ledger);raise
