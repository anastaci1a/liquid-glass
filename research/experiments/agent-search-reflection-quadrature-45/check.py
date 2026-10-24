from pathlib import Path
import sys,json,datetime,math,hashlib
import numpy as np
O=Path(__file__).parent;ROOT=O.parents[2];P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']};records=[];arrays={}
def gate(cp=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if cp else 'deadline'].replace('Z','+00:00')),'Original deadline'
def save(f,v):(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):gate();n=int(n);assert ledger[k]+n<=P['caps'][k],k;ledger[k]+=n
for f,h in json.loads((O/'first-hashes.json').read_text()).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
sys.path.insert(0,str(ROOT/'reconstruction'))
from pixel_quadrature import rounded_rectangle_pixel_rule
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from bevel_footprint_back import BevelFootprintBack
from geometric_optics import reflect_direction,fresnel_components
from environment_radiance import planar_annular_emitter
C=np.array(P['center_native']);Rn=P['radius_native'];L=P['original_L'];R=Rn/L;family=json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text());recipe=json.loads((ROOT/'research/experiments/miniplayer-shallow-front-41/front-geometry.json').read_text());scale=R/family['geometry']['corner_radius'];charge('adapter_units',8192);front=BevelFootprintBack(RoundedRectangleHarmonicBack((R,R),R,cap_join_width=0),recipe['depth']*scale,recipe['power']);assert front.depth==0.019857545736401052 and front.power==33.76385521939009;assert front.slope_bound<1
plan=[]
for direction,v in [('upper',(0,-1)),('lower',(0,1)),('left',(-1,0)),('right',(1,0))]:
 v=np.array(v);anchor=np.floor(C+Rn*v+.5).astype(int)
 for offset in [-1,0,1]:plan.append({'direction':direction,'radial_offset':offset,'native_pixel':(anchor+offset*v).tolist(),'node_coefficient':6 if offset==-1 else (3 if direction in ['upper','lower'] else 11) if offset==0 else 0})
save('frozen-plan.json',{'pixels':plan,'setup_units':8192,'tight_node_bound':69888,'front_points_bound':139776,'adapter_bound':1405952,'static_order_set':[8,16,32],'no_cached42_scalar_reconstruction':True})
status='STARTING'
try:
 for pi,item in enumerate(plan):
  rows=[]
  for order in P['orders']:
   gate();reservation=item['node_coefficient']*order*order;assert ledger['quadrature_nodes']+reservation<=P['caps']['quadrature_nodes'];q=rounded_rectangle_pixel_rule(item['native_pixel'],(Rn,Rn),Rn,center=C,pixel_width=1.,order=order);pts=q['points'];w=q['weights'];N=len(w);charge('quadrature_nodes',N);assert N<=reservation,'Node reservation';key=f"{item['direction']}_{item['radial_offset']}_{order}";arrays[key+'_points']=pts;arrays[key+'_weights']=w;assert np.isfinite(pts).all() and np.isfinite(w).all() and (w>0).all();assert (np.sum((pts-C)**2,axis=1)<Rn*Rn).all(),'Strict footprint';assert (pts>np.array(item['native_pixel'])-.5).all() and (pts<np.array(item['native_pixel'])+.5).all()
   coverage=float(w.sum());signal=0.;mincone=None
   if N:
    assert ledger['front_points']+2*N<=P['caps']['front_points'];charge('adapter_units',20*N);xy=(pts-C)/L;charge('front_points',N);h,hx,hy,inside=front.height_gradient(xy[:,0],xy[:,1]);charge('front_points',N);boundary=front.boundary_mask(xy[:,0],xy[:,1]);assert inside.all() and (h>0).all() and not boundary.any(),'Unresolved crease';normal=np.column_stack([-hx,-hy,np.ones(N)]);normal/=np.linalg.norm(normal,axis=1)[:,None];camera=np.zeros_like(normal);camera[:,2]=-1;charge('reflection_points',N);d=reflect_direction(camera,normal);assert (d[:,2]>0).all() and (np.sum(d[:,:2]*np.column_stack([hx,hy]),axis=1)<=0).all(),'Monotone outward/upward escape';mincone=float(np.min(d[:,2]-front.slope_bound*np.linalg.norm(d[:,:2],axis=1)));charge('Fresnel_points',N);power=fresnel_components(normal[:,2],1.,1.5).mean(-1);positions=np.column_stack([pts,h*L]);assert (positions[:,2]<177).all();charge('panel_intersections',N);panel=planar_annular_emitter(positions,d,panel_z=885.,center_xy=(960.,540.),inner_degrees=30.,outer_degrees=80.,shoulder_degrees=10.);assert panel['reaches_panel'].all() and (panel['distance_parameter']>0).all(),'Panel validity';value=4*power*panel['unit_radiance'];signal=float(w@value);arrays[key+'_normal']=normal;arrays[key+'_directions']=d;arrays[key+'_signal']=value;arrays[key+'_panel_hits']=panel['hit_point']
   rows.append({'order':order,'nodes':N,'fractional_coverage':coverage,'linear_reflected_pixel_signal':signal,'minimum_raw_Lipschitz_margin':mincone,'upward_monotone_escape':bool(N),'empty':N==0});save('current.json',{'pixel':item,'rows':rows,'ledger':ledger});np.savez_compressed(O/'raw-quadratures.npz',**arrays)
   if pi==0 and len(rows)==1:
    gate(True);save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'factory_hashes_rule_first_pixel_all_invariants':True,'first_pixel':item,'row':rows[0],'ledger':ledger.copy()});print('CHECKPOINT_PASS',flush=True)
  a,b,c=rows;delta1=abs(a['linear_reflected_pixel_signal']-b['linear_reflected_pixel_signal']);delta2=abs(b['linear_reflected_pixel_signal']-c['linear_reflected_pixel_signal']);records.append({'pixel':item,'rows':rows,'difference8_16':delta1,'difference16_32':delta2,'successive_orders_within_declared_1e7':max(delta1,delta2)<=1e-7,'empty_at_all_orders':all(x['empty'] for x in rows)});save('records.json',records)
 status='FIXED_TWELVE_PIXEL_COMPONENT_QUADRATURE_COMPLETE'
except Exception as e:status='STOPPED_FIRST_INVARIANT';failure=repr(e);print('STOP',failure,flush=True)
finally:
 save('result.json',{'status':status,'failure':locals().get('failure'),'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'cache_scalar_comparisons':0,'refraction_source_RGB_filter_composite_image_fit':0,'scores_or_selected_state_changed':False});print(status,ledger,flush=True)
