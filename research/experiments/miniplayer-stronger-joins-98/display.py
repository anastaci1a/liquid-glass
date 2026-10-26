"""One fixed final composition, with own independent algebraic verification."""
from material_common import *
from ellipse_edge_effects import integrate_alpha
from ellipse_core_coordinate import EllipseCoreCoordinate
from edge_color_filter import edge_filter
OUT=BASE/'display';P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
fx=metric_functions(charge);score=fx['score']
def independent(C,alpha,cfg):
 out=C.copy();use=alpha>0;v=C[use].astype(float);a=alpha[use,None];lin=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);p=lin.max(-1,keepdims=True);e=1+(cfg['exposure']-1)*a;b=cfg['lift']*a;s=cfg['desaturation']*a;q=e*(p+b)/(e*(p+b)+(1-p));n=np.divide(lin,p,out=np.ones_like(lin),where=p>0);L=q*(n+s*(1-n));E=np.where(L<=.0031308,12.92*L,1.055*L**(1/2.4)-.055);E[np.all(v==1,axis=-1)]=1;out[use]=E;return out

def run():
 assert not (OUT/'started.json').exists();save('started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 recipe=ROOT/'research/experiments/miniplayer-subtle-blur-97/filter-recipe.json';first[str(recipe.relative_to(ROOT))]=sha(recipe);cfg=json.loads(recipe.read_text())['parameters'];config=json.loads((ROOT/'research/experiments/miniplayer-complete-refinement-94/highlight/protocol.json').read_text())['config'];first['reconstruction/edge_color_filter.py']=sha(ROOT/'reconstruction/edge_color_filter.py');first['reconstruction/ellipse_edge_effects.py']=sha(ROOT/'reconstruction/ellipse_edge_effects.py');data=load_data(charge,first)
 for d in data.values():
  d['radius']-=2.;charge('identity_composites',1);C=d['s'].apply_foreground(d['z']['pre_foreground'].copy());assert np.array_equal(C,d['z']['complete'],equal_nan=True);assert score(d['s'],C,d['m'],d['partial'],d['crops'])==d['before']
 save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),native98_zero_and_metrics_exact=True));alpha={};fields={};integrals=[]
 for member in ['expanded','compact']:
  d=data[(member,'a')];pair=[]
  for order in P['orders']:
   a,info=integrate_alpha(d['s'].crop,d['half'],d['radius'],d['center'],config,order,charge);np.savez_compressed(OUT/f'{member}-alpha{order}.npz',alpha=a);pair.append(a);print('FIELD',member,order,flush=True)
  diff=float(np.max(abs(pair[1]-pair[0])));assert diff<=P['maximum_order_difference'];alpha[member]=pair[1];integrals.append(dict(member=member,max_order_difference=diff));save('integration.json',integrals)
  s=d['s'];H,W=s.valid.shape;x0,y0,_,_=s.crop;yy,xx=np.mgrid[:2*H,:2*W];charge('distance_points',xx.size);sd,_,_=EllipseCoreCoordinate(tuple(d['half']),d['radius']).boundary_distance(x0+xx*.5-.25-d['center'][0],y0+yy*.5-.25-d['center'][1]);fields[member]=np.exp(-(np.maximum(sd,0)/32)**1.5);np.savez_compressed(OUT/f'{member}-shadow.npz',field=fields[member])
 rows=[];checks=[]
 for (member,k),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;v=z['encoded_subrays'].copy();clear=~z['inside']&z['supported'];v[clear]*=1-.08*fields[member][clear,None];assert np.array_equal(v[z['inside']],z['encoded_subrays'][z['inside']]);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);body=s.apply_foreground(pre.copy());full=z['coverage']==1;assert np.array_equal(body[full],z['complete'][full]);charge('candidate_composites',1);C=edge_filter(body,alpha[member],**cfg);now=score(s,C,d['m'],d['partial'],d['crops']);previous=json.loads((ROOT/f'research/experiments/miniplayer-complete-refinement-94/highlight/{member}-{k}-combined-metrics.json').read_text())['scores'];row=dict(member=member,reference=k,scores=now,original_guards=guards(now,d['original']),native98_guards=guards(now,d['before']),previous94_guards=guards(now,previous));rows.append(row);prefix=f'{member}-{k}-final';np.savez_compressed(OUT/f'{prefix}.npz',complete=C,pre_foreground=pre,shadowed_body=body);save(prefix+'-metrics.json',row);panels(OUT,prefix,d,C,fx['to_image'],'Inward joins + less blur + broad shadow + finite edge filter')
  charge('replay_composites',1);replay=independent(body,alpha[member],cfg);finite=np.isfinite(C);err=float(np.max(abs(replay[finite]-C[finite])));assert err<=1e-7 and np.array_equal(np.isnan(replay),np.isnan(C));assert score(s,C,d['m'],d['partial'],d['crops'])==now;checks.append(dict(member=member,reference=k,max_replay_error=err,original_metrics_exact=True,all_lens_samples_and_fully_covered_shadow_pixels_exact=True));print('FINAL',member,k,now['E'],[n for n,v in row['original_guards'].items() if not v],flush=True)
 save('result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,filter=cfg,integrals=integrals,own_replay=checks,family_qualifier=all(all(r['original_guards'].values()) for r in rows),selected_changed=False));assert first=={p:sha(ROOT/p) for p in first};save('hashes.json',first);save('ledger.json',ledger)
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e)));save('ledger.json',ledger);raise
