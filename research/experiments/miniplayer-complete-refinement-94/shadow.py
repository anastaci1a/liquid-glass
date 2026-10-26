"""Three fixed exterior-only shadow strengths; no new optical sampling."""
from material_common import *
from ellipse_core_coordinate import EllipseCoreCoordinate
OUT=BASE/'shadow';OUT.mkdir(exist_ok=True);P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
fx=metric_functions(charge);score=fx['score']
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});data=load_data(charge,first);rows=[];losses={str(t):[] for t in P['strengths']}
 for (member,k),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;charge('identity_composites',1);C=s.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(C,z['complete'],equal_nan=True);assert score(s,C,d['m'],d['partial'],d['crops'])==d['before']
 save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_complete_and_metric_identities_exact':True})
 fields={}
 for member in ['expanded','compact']:
  d=data[(member,'a')];s=d['s'];H,W=s.valid.shape;x0,y0,_,_=s.crop;yy,xx=np.mgrid[:2*H,:2*W];x=x0+xx*.5-.25-d['center'][0];y=y0+yy*.5-.25-d['center'][1]-P['offset_y'];charge('distance_points',x.size)
  coord=EllipseCoreCoordinate(tuple(d['half']),d['radius']);sd,_,_=coord.boundary_distance(x,y);field=np.exp(-.5*(np.maximum(sd,0)/P['sigma'])**2);fields[member]=field;np.savez_compressed(OUT/f'{member}-field.npz',field=field)
 for strength in P['strengths']:
  for (member,k),d in data.items():
   s,z=d['s'],d['z'];H,W=s.valid.shape;changed=z['encoded_subrays'].copy();clear=~z['inside']&z['supported'];changed[clear]*=(1-strength*fields[member][clear,None]);assert np.array_equal(changed[z['inside']],z['encoded_subrays'][z['inside']])
   pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);full=z['coverage']==1;assert np.array_equal(pre[full],z['pre_foreground'][full]);charge('candidate_composites',1);C=s.apply_foreground(pre.copy());assert np.array_equal(C[full],z['complete'][full]);now=score(s,C,d['m'],d['partial'],d['crops']);original=guards(now,d['original']);component=guards(now,d['before']);row=dict(member=member,reference=k,strength=strength,scores=now,original_guards=original,geometry_guards=component,all_pass=all(original.values()),full_coverage_exact=True)
   prefix=f'{member}-{k}-s{strength}';np.savez_compressed(OUT/f'{prefix}.npz',pre_foreground=pre,complete=C);panels(OUT,prefix,d,C,fx['to_image'],'Exterior shadow proposal');rows.append(row);save(prefix+'-metrics.json',row)
   yy,xx=np.indices(s.valid.shape);train=d['m']['exterior']&((xx+yy)%2==0);losses[str(strength)].append(float(np.mean((C[train]-s.target_crop[train])**2)))
 best=min(P['strengths'],key=lambda t:np.mean(losses[str(t)]));accepted=[t for t in P['strengths'] if all(r['all_pass'] for r in rows if r['strength']==t)]
 save('result.json',dict(records=rows,development_strength=best,accepted_strengths=accepted,training_losses={k:float(np.mean(v)) for k,v in losses.items()},selected_shadow=0,scope='Only original clear subrays darkened. No lens sample, refraction, source or foreground coefficient changed.'))
 for p in [Path(__file__),BASE/'material_common.py',ROOT/'reconstruction/ellipse_core_coordinate.py']:first[str(p.relative_to(ROOT))]=sha(p)
 assert first=={p:sha(ROOT/p) for p in first};save('hashes.json',first);save('ledger.json',ledger);print('SHADOW',best,accepted,flush=True)
try:run()
except Exception as e:save('failure.json',{'error':repr(e),'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});save('ledger.json',ledger);raise
