"""Fixed source/profile/shadow contrasts on one reviewed intermediate geometry."""
import material_common as common
from material_common import *
from color_edge_plateau import integrate_profiles,apply_color_rim,profile
from ellipse_core_coordinate import EllipseCoreCoordinate
from edge_color_filter import edge_filter
from environment_radiance import decode_srgb,encode_srgb
OUT=BASE/'display';P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={}
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Display deadline'
 assert ledger[k]+n<=P['caps'][k],(k,ledger[k],n);ledger[k]+=int(n)
 if k=='score_calls':charge('metric_Gaussians',5*n);charge('metric_erosions',n)
def flush():save('ledger.json',ledger)
fx=metric_functions(charge);score=fx['score'];cfg=json.loads((ROOT/'research/experiments/miniplayer-subtle-blur-97/filter-recipe.json').read_text())['parameters']
def independent(body,guide,alpha):
 out=body.copy();ok=alpha>0;v=guide[ok].astype(float);lin=np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4);peak=lin.max(-1,keepdims=True)
 ratio=np.divide(lin,peak,out=np.ones_like(lin),where=peak>0);q=1.4*(peak+cfg['lift'])/(1.4*(peak+cfg['lift'])+1-peak);value=q*ratio
 end=np.where(value<=.0031308,12.92*value,1.055*value**(1/2.4)-.055);end[np.all(v==1,axis=-1)]=1
 out[ok]=body[ok]+alpha[ok,None]*(end-body[ok]);return out

def run():
 assert not (OUT/'started.json').exists();save('started.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat()))
 candidates=[]
 for folder in ['native-r0.75-complete','native-r1.25']:
  path=BASE/folder/'geometry-result.json';first[str(path.relative_to(ROOT))]=sha(path);res=json.loads(path.read_text());assert len(res['records'])==4
  candidates.append(dict(folder=folder,mean_E=float(np.mean([x['scores']['E'] for x in res['records']]))))
 selected=min(candidates,key=lambda x:x['mean_E']);common.NATIVE=BASE/selected['folder'];reduction=1.25 if selected['folder']=='native-r1.25' else .75
 save('shape-selection.json',dict(candidates=candidates,selected=selected,visual_review='Expanded A and compact B inspected for both; no invalid contour. Global local-guard failures remain.',held_out=False))
 for path in [Path(__file__),BASE/'material_common.py',ROOT/'reconstruction/color_edge_plateau.py',ROOT/'reconstruction/ellipse_edge_effects.py',ROOT/'reconstruction/edge_color_filter.py',ROOT/'reconstruction/ellipse_core_coordinate.py']:
  first[str(path.relative_to(ROOT))]=sha(path)
 controls=[]
 for v in [np.array([0.,0.,0.]),np.array([1.,1.,1.]),np.array([.8,.7,.05]),np.array([.95,.89,.38])]:
  for a in [0.,.25,1.]:
   charge('response_controls',1);result=apply_color_rim(v[None],v[None],np.array([a]))[0];assert np.isfinite(result).all() and result.min()>=0 and result.max()<=1
   if a==0:assert np.array_equal(result,v)
   if np.all(v==1):assert np.array_equal(result,v)
   if a==1 and np.all(v==0):assert np.max(abs(result-.65))<1e-7
   controls.append(dict(input=v.tolist(),alpha=a,result=result.tolist()))
 charge('response_controls',7);depths=np.array([0,.3,.6,.600001,1.,2.6,8.]);pr=profile(depths,2.6,2.,.6);assert np.array_equal(pr[:3],np.ones(3)) and np.all(np.diff(pr)<=0)
 save('controls.json',dict(color=controls,profile_depths=depths.tolist(),profile_strength=pr.tolist(),white_fixed=True,black_endpoint=.65))
 data=load_data(charge,first)
 for d in data.values():
  d['radius']-=reduction;s,z=d['s'],d['z'];charge('identity_composites',1);C=s.apply_foreground(z['pre_foreground'].copy());assert np.array_equal(C,z['complete'],equal_nan=True);assert score(s,C,d['m'],d['partial'],d['crops'])==d['before']
  H,W=s.valid.shape;rawpre=z['raw_source'].reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('guide_composites',1);d['guide']=s.apply_foreground(rawpre)
 save('checkpoint.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),four_native_identities_exact=True,source='Retained supported incident-blurred refracted samples before body grade; unchanged original foreground applied to guide.',blur_removed=False));flush()
 angular=json.loads((ROOT/'research/experiments/miniplayer-complete-refinement-94/highlight/protocol.json').read_text())['config'];alphas={};shadows={};integ=[]
 for member in ['expanded','compact']:
  d=data[(member,'a')];old=None
  for order in [8,16,32]:
   a=integrate_profiles(d['s'].crop,d['half'],d['radius'],d['center'],angular,P['profiles'],order,charge);np.savez_compressed(OUT/f'{member}-alpha{order}.npz',alpha=a)
   diff=None if old is None else float(np.max(abs(a-old)));integ.append(dict(member=member,order=order,max_previous_difference=diff));save('integration.json',integ);flush();print('ALPHA',member,order,diff,flush=True)
   if old is not None and diff<=P['maximum_order_difference']:break
   old=a
  assert diff is not None and diff<=P['maximum_order_difference'],'Unconverged edge field';alphas[member]=a
  H,W=d['s'].valid.shape;x0,y0,_,_=d['s'].crop;yy,xx=np.mgrid[:2*H,:2*W];coord=EllipseCoreCoordinate(tuple(d['half']),d['radius']);shadows[member]={}
  for offset in [0,14,18]:
   charge('shadow_points',xx.size);sd,_,_=coord.boundary_distance(x0+xx*.5-.25-d['center'][0],y0+yy*.5-.25-d['center'][1]-offset);shadows[member][offset]=np.exp(-(np.maximum(sd,0)/32)**1.5)
  np.savez_compressed(OUT/f'{member}-shadows.npz',**{f'offset{k}':v for k,v in shadows[member].items()})
 rows=[];yellow=[];replays=[]
 for (member,k),d in data.items():
  s,z=d['s'],d['z'];H,W=s.valid.shape;clear=~z['inside']&z['supported'];bodies={};pres={}
  for offset in [0,14,18]:
   v=z['encoded_subrays'].copy();strength=.08 if offset==0 else 34/255;v[clear]*=1-strength*shadows[member][offset][clear,None];assert np.array_equal(v[z['inside']],z['encoded_subrays'][z['inside']]);pre=v.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);pres[offset]=pre
   # Each distinct shadowed pre-foreground body is a compositor operation.
   charge('shadow_composites',1);bodies[offset]=s.apply_foreground(pre.copy());full=z['coverage']==1;assert np.array_equal(bodies[offset][full],z['complete'][full])
  a0,a1=alphas[member];guide=d['guide'];assert np.isfinite(guide[a1>0]).all()
  observations=[('baseline',0,'legacy',a0),('shadow14',14,'legacy',a0),('shadow18',18,'legacy',a0),('graded',0,'graded',a0),('pregrade',0,'raw',a0),('plateau',0,'raw',a1),('combined',18,'raw',a1)]
  baseline=None
  for label,offset,kind,alpha in observations:
   charge('candidate_composites',1);body=bodies[offset]
   C=edge_filter(body,alpha,**cfg) if kind=='legacy' else apply_color_rim(body,body if kind=='graded' else guide,alpha)
   now=score(s,C,d['m'],d['partial'],d['crops']);baseline=now if baseline is None else baseline
   row=dict(member=member,reference=k,setting=label,scores=now,original_guards=guards(now,d['original']),native_guards=guards(now,d['before']),display_baseline_guards=guards(now,baseline));rows.append(row)
   prefix=f'{member}-{k}-{label}';np.savez_compressed(OUT/f'{prefix}.npz',complete=C,pre_foreground=pres[offset],shadowed_body=body);save(prefix+'-metrics.json',row);charge('presentation_panels',1);panels(OUT,prefix,d,C,fx['to_image'],label+'; blur retained')
   if member=='expanded':
    x0,y0,_,_=s.crop
    for x in P['yellow_diagnostics']['x']:
     for y in P['yellow_diagnostics']['y']:
      charge('diagnostic_pixels',1);i,j=y-y0,x-x0
      yellow.append(dict(reference=k,setting=label,x=x,y=y,target=(s.target_crop[i,j]*255).tolist(),result=(C[i,j]*255).tolist(),blurred_pregrade=(guide[i,j]*255).tolist(),graded=(body[i,j]*255).tolist(),alpha=float(alpha[i,j])))
   if label=='combined':
    charge('replay_composites',1);again=independent(body,guide,alpha);ok=np.isfinite(C);error=float(np.max(abs(again[ok]-C[ok])));assert error<=1e-7 and np.array_equal(np.isnan(again),np.isnan(C));assert score(s,again,d['m'],d['partial'],d['crops'])==now
    replays.append(dict(member=member,reference=k,max_error=error,metrics_exact=True,lens_and_fully_covered_shadow_exact=True))
   print('CANDIDATE',member,k,label,now['E'],[n for n,v in row['original_guards'].items() if not v],flush=True);flush()
 save('yellow-samples.json',yellow);save('result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,own_replays=replays,selected_geometry_reduction=reduction,selected_changed=False,original_family_qualifier=all(all(r['original_guards'].values()) for r in rows if r['setting']=='combined')))
 assert first=={p:sha(ROOT/p) for p in first};save('hashes.json',first);flush()
try:run()
except Exception as e:save('failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e)));flush();raise
