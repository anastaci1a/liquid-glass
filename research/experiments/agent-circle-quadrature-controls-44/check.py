from pathlib import Path
import sys,json,datetime,math,hashlib
import numpy as np
O=Path(__file__).parent;ROOT=O.parents[2];P=json.loads((O/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));CP=datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));binding=json.loads((O/'binding.json').read_text());assert hashlib.sha256((ROOT/'reconstruction/pixel_quadrature.py').read_bytes()).hexdigest()==binding['module_sha256']
sys.path.insert(0,str(ROOT/'reconstruction'));from pixel_quadrature import rounded_rectangle_pixel_rule
assert not any(n in sys.modules for n in ['geometric_optics','raised_front_optics','environment_radiance','bevel_footprint_back'])
ledger={'configurations_entered':0,'configurations_complete':0,'rule_calls':0,'reserved_nodes':0,'generated_nodes':0};records=[];raw={};status='STARTING'
def gate():assert datetime.datetime.now(datetime.timezone.utc)<END,'Deadline'
def save(f,v):(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
try:
 for cfg in P['configurations']:
  gate();ledger['configurations_entered']+=1;rows=[];name=cfg['name'];R=cfg['radius'];w=cfg['pixel_width'];center=np.array(cfg['center']);pixel=np.array(cfg['pixel_center']);c=-.25
  exact_segment=R*R*math.acos(c/R)-c*math.sqrt(R*R-c*c)
  exact=exact_segment/(w*w) if 'partial' in name else math.pi*R*R/(w*w) if name=='full_disk' else 1. if name=='full_interior_square' else 0.
  for order in P['orders']:
   gate();reservation=cfg['node_upper_coefficient']*order*order;assert ledger['reserved_nodes']+reservation<=P['caps']['generated_nodes'];ledger['reserved_nodes']+=reservation;ledger['rule_calls']+=1
   q=rounded_rectangle_pixel_rule(cfg['pixel_center'],(R,R),R,center=cfg['center'],pixel_width=w,order=order);points=q['points'];weights=q['weights'];N=len(weights);ledger['generated_nodes']+=N;raw[name+'_'+str(order)+'_points']=points;raw[name+'_'+str(order)+'_weights']=weights
   # Save raw returned data and actual count BEFORE any assertion can stop this task.
   np.savez_compressed(O/'raw-rules.npz',**raw);save('ledger.json',ledger)
   assert N<=reservation and ledger['generated_nodes']<=300000,'Reservation';assert points.shape==(N,2) and np.isfinite(points).all() and np.isfinite(weights).all();assert (weights>0).all(),'Positive raw weights';assert np.all(np.sum((points-center)**2,axis=1)<R*R),'Strict disk membership';assert np.all(points>pixel-w/2) and np.all(points<pixel+w/2),'Strict pixel membership';mass=float(weights.sum());error=abs(mass-exact);row={'order':order,'nodes':N,'reserved':reservation,'mass':mass,'exact_normalized_area':exact,'absolute_error':error,'minimum_weight':float(weights.min()) if N else None,'strict_membership':True,'moment_local':np.sum(weights[:,None]*(points-center),axis=0).tolist() if N else [0.,0.]};rows.append(row);save('current.json',{'configuration':cfg,'rows':rows,'ledger':ledger});assert error<=1e-10,'Area error';assert (N==0)==(exact==0),'Empty/tangent'
  assert abs(rows[1]['mass']-rows[0]['mass'])<=1e-10,'Order mass'
  if name in ['horizontal_mirror_partial','fractional_translation_partial','axis_exchange_partial']:
   previous=records[0]['rows']
   for i in range(2):
    assert abs(rows[i]['mass']-previous[i]['mass'])<=1e-10,'Symmetry mass';m=np.array(previous[i]['moment_local']);expected=m*np.array([-1,1]) if name=='horizontal_mirror_partial' else m[::-1] if name=='axis_exchange_partial' else m;assert np.max(abs(np.array(rows[i]['moment_local'])-expected))<=1e-10,'Symmetry/translation moment'
  ledger['configurations_complete']+=1;records.append({'configuration':cfg,'rows':rows});save('records.json',records)
  if len(records)==1:
   assert datetime.datetime.now(datetime.timezone.utc)<CP,'First checkpoint';save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'first_vertical_edge_segment_pass':True,'rows':rows,'ledger':ledger.copy()});print('CHECKPOINT_PASS',flush=True)
 status='PASS_EIGHT_CIRCLE_AREA_CONFIGURATIONS_ONLY'
except Exception as e:status='STOPPED_FIRST_INVARIANT';failure=repr(e);print('STOP',failure,flush=True)
finally:
 save('result.json',{'status':status,'failure':locals().get('failure'),'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'optical_imports_calls_rays_source_filters_images_fits':0,'original_scores_changed':False});print(status,ledger,flush=True)
