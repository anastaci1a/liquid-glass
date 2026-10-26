"""Color-aware edge lift and one fixed combined observation."""
from material_common import *
from ellipse_edge_effects import integrate_alpha,pixel_rule_batch,color_lift,extent_at
from ellipse_core_coordinate import EllipseCoreCoordinate
from scipy.optimize import minimize_scalar
OUT=BASE/'highlight';P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original highlight clock'
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
fx=metric_functions(charge);score=fx['score']
def run():
 assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 for p in [Path(__file__),BASE/'material_common.py',ROOT/'reconstruction/ellipse_edge_effects.py',ROOT/'reconstruction/ellipse_core_coordinate.py']:first[str(p.relative_to(ROOT))]=sha(p)
 # Independent exact-area disk fixture, tiny sliver, interior, empty, symmetry.
 controls=[];half=(.4,.4);radius=.2
 for order in [8,16]:
  for pixel,expected in [((0.,0.),np.pi*.4**2),((1.,0.),0.),((.9,0.),0.)]:
   pts,w,ids=pixel_rule_batch([pixel],half,radius,order,charge);error=abs(w.sum()-expected);assert error<1e-10;controls.append(dict(order=order,pixel=pixel,area=float(w.sum()),error=error))
  pts,w,ids=pixel_rule_batch([[.7,0.],[-.7,0.]],half,radius,order,charge);areas=np.bincount(ids,weights=w,minlength=2);expected=.4**2*np.arccos(.2/.4)-.2*np.sqrt(.4**2-.2**2);assert max(abs(areas-expected))<1e-10
  sd,_,_=EllipseCoreCoordinate(half,radius).boundary_distance(pts[:,0],pts[:,1]);assert sd.max()<1e-12
  controls.append(dict(order=order,segment_areas=areas.tolist(),exact_segment=expected))
 samples=np.array([[0.,0.,0.],[1.,1.,1.],[.8,.7,.05],[.1,.4,.8]])
 for sat in P['desaturation']:
  for e in [0.,.5,1.5]:
   charge('response_controls',4);v=color_lift(samples,np.ones(4),e,sat);assert np.isfinite(v).all() and v.min()>=0 and v.max()<=1
   if e==0:assert np.array_equal(v,samples)
   assert v[2,0]>=v[2,1]>=v[2,2] # Yellow channel ordering remains yellow.
 save('controls.json',dict(area_controls=controls,black_white_yellow_and_zero_controls=True))
 data=load_data(charge,first)
 for d in data.values():
  charge('identity_composites',1);C=color_lift(d['z']['complete'],np.ones(d['s'].valid.shape),0,.25);assert np.array_equal(C,d['z']['complete'],equal_nan=True);assert score(d['s'],C,d['m'],d['partial'],d['crops'])==d['before']
 save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'four_zero_identities_and_metrics_exact':True,'area_and_response_controls_pass':True});print('HIGHLIGHT CONTROLS PASS',flush=True)
 fields={};integrals=[]
 for member in ['expanded','compact']:
  d=data[(member,'a')];pair=[];infos=[]
  for order in P['orders']:
   a,info=integrate_alpha(d['s'].crop,d['half'],d['radius'],d['center'],P['config'],order,charge);pair.append(a);infos.append(info);save('ledger.json',ledger);np.savez_compressed(OUT/f'{member}-order{order}.npz',alpha=a);print('ALPHA',member,order,flush=True)
  difference=float(np.max(abs(pair[1]-pair[0])));first_difference=difference
  if difference>P['maximum_order_difference']:
   a,info=integrate_alpha(d['s'].crop,d['half'],d['radius'],d['center'],P['config'],32,charge);difference=float(np.max(abs(a-pair[-1])));pair.append(a);infos.append(info);np.savez_compressed(OUT/f'{member}-order32.npz',alpha=a)
  integral=dict(member=member,orders=infos,first_order_difference=first_difference,final_order_difference=difference,criterion=P['maximum_order_difference']);integrals.append(integral);save('integration.json',integrals)
  assert difference<=P['maximum_order_difference'],'Unresolved highlight integration'
  fields[member]=pair[-1]
 rows=[];fits=[]
 for j,sat in enumerate(P['desaturation']):
  trials=[]
  def objective(e):
   charge('fit_evaluations',1);loss=[]
   for (member,k),d in data.items():
    train=d['train'];pred=color_lift(d['z']['complete'][train],fields[member][train],e,sat);loss.append(float(np.mean((pred-d['s'].target_crop[train])**2)))
   value=float(np.mean(loss));trials.append([float(e),value]);return value
  opt=minimize_scalar(objective,bounds=P['exposure_bounds'],method='bounded',options={'maxiter':24,'xatol':1e-5});fit=dict(candidate=j,desaturation=sat,exposure=float(opt.x),loss=float(opt.fun),solver_success=bool(opt.success),evaluations=trials);fits.append(fit);save('fits.json',fits)
  for (member,k),d in data.items():
   charge('candidate_composites',1);C=color_lift(d['z']['complete'],fields[member],float(opt.x),sat);now=score(d['s'],C,d['m'],d['partial'],d['crops']);gr=guards(now,d['original']);row=dict(member=member,reference=k,candidate=j,scores=now,original_guards=gr,geometry_guards=guards(now,d['before']),all_pass=all(gr.values()),clipped_channels=0);rows.append(row);prefix=f'{member}-{k}-h{j}';np.savez_compressed(OUT/f'{prefix}.npz',complete=C);save(prefix+'-metrics.json',row);panels(OUT,prefix,d,C,fx['to_image'],'Color-aware highlight proposal')
 best=min(fits,key=lambda f:f['loss']);shadow=json.loads((BASE/'shadow/result.json').read_text());strength=shadow['development_strength'];combined=[]
 for (member,k),d in data.items():
  p=BASE/f'shadow/{member}-{k}-s{strength}.npz';first[str(p.relative_to(ROOT))]=sha(p)
  with np.load(p) as z:base=z['complete'];charge('numeric_bytes',base.nbytes)
  charge('candidate_composites',1);C=color_lift(base,fields[member],best['exposure'],best['desaturation']);now=score(d['s'],C,d['m'],d['partial'],d['crops']);gr=guards(now,d['original']);row=dict(member=member,reference=k,scores=now,original_guards=gr,geometry_guards=guards(now,d['before']),all_pass=all(gr.values()));combined.append(row);prefix=f'{member}-{k}-combined';np.savez_compressed(OUT/f'{prefix}.npz',complete=C);save(prefix+'-metrics.json',row);panels(OUT,prefix,d,C,fx['to_image'],'Smooth shape + shadow + color-aware rim')
 save('result.json',dict(records=rows,combined=combined,development=best,shadow_strength=strength,family_qualifier=all(r['all_pass'] for r in combined),selected_state_changed=False,integrals=integrals))
 assert first=={p:sha(ROOT/p) for p in first};save('hashes.json',first);save('ledger.json',ledger);print('HIGHLIGHT COMPLETE',best['candidate'],best['exposure'],all(r['all_pass'] for r in combined),flush=True)
try:run()
except Exception as e:save('failure.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'error':repr(e)});save('ledger.json',ledger);raise
