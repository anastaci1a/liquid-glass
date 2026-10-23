"""O1: fixed real G05 circle, full scalar/meridional polarization path audit."""
import os,time,json,datetime
from pathlib import Path
import numpy as np
from geometric_optics import RadialCurvatureBack,CircularHeightSolid,trace_flat_front_orthographic,next_convex_boundary,refract,reflect_direction,fresnel_components
os.umask(2);P=Path('/evidence/extended/playback-pipeline-01');D=P/'outline';D.mkdir(exist_ok=True);START=time.time();DEADLINE=min(START+15*60,datetime.datetime(2026,10,22,8,56,2,tzinfo=datetime.timezone.utc).timestamp());MAX_PATHS=1025;MAX_EVENTS=32800;MAX_LEVEL=3000000;MAX_INTERNAL=32;EPS=1e-6
if (D/'path-audit.json').exists():raise RuntimeError('Completed audit cannot repeat')
def gate():
 if time.time()>DEADLINE:raise RuntimeError('O1 original15minute budget reached')
p=np.load('/evidence/extended/geometric-playback-inverse/geometry-513.npz');back=RadialCurvatureBack(p['nodes'],p['curvature']);solid=CircularHeightSolid(back);solid.maximum_level_points=MAX_LEVEL
saved=np.load('/evidence/extended/geometric-playback-inferred/radial-geometry.npz');idx=np.rint(np.linspace(0,len(saved['r'])-1,997)).astype(int);r=saved['r'][idx];primary={k:saved[k][idx] for k in ['back','outward_normal','exit_direction','X','Y','complete']};assert primary['complete'].all();events=0;all_terminals=[]
def run(r,primary,index,label):
 global events
 gate();N=len(r);assert N<=MAX_PATHS;R0=fresnel_components(np.ones(N),1.,index);weight=.5*(1-R0);front=.5*R0
 terminal=[]
 def emit(kind,ids,points,dirs,weights,step,source=None):
  if not len(ids):return
  terminal.append({'kind':kind,'ids':ids.copy(),'point':points.copy(),'direction':dirs.copy(),'weight_sp':weights.copy(),'step':int(step),'source':None if source is None else source.copy()})
 ids=np.arange(N);i=np.zeros((N,3));i[:,2]=-1;frontpoint=np.stack([r,np.zeros(N),np.zeros(N)],-1);up=-i;emit('environment',ids,frontpoint,up,front,0)
 n=primary['outward_normal'];ci=np.sum(i*n,axis=-1);R=fresnel_components(ci,index,1.);events+=N
 emit('background',ids,primary['back'],primary['exit_direction'],weight*(1-R),1,np.stack([primary['X'],primary['Y']],-1));weight*=R;point=primary['back'].copy();direction=reflect_direction(i,n);unresolved=np.zeros((N,2));maxwidth=0.;maxresid=0.;active_counts=[]
 for step in range(2,MAX_INTERNAL+1):
  gate();active=np.flatnonzero(weight.sum(axis=-1)>EPS)
  if not len(active):break
  if events+len(active)>MAX_EVENTS:raise RuntimeError('Internal event budget would be exceeded')
  events+=len(active);active_counts.append(len(active));ev=next_convex_boundary(solid,point[active],direction[active]);maxwidth=max(maxwidth,float(ev['bracket'].max()));maxresid=max(maxresid,float(abs(ev['residual']).max()));bad=active[~ev['complete']]
  if len(bad):unresolved[bad]+=weight[bad];weight[bad]=0
  a=active[ev['complete']]
  if not len(a):continue
  q=ev['point'][ev['complete']];nq=ev['outward_normal'][ev['complete']];d=direction[a];c=np.sum(d*nq,axis=-1);RR=fresnel_components(c,index,1.);e,tir,k=refract(d,-nq,index,1.);tt=weight[a]*(1-RR);good=~tir
  down=good&(e[:,2]<0);env=good&~down
  if down.any():
   qe=q[down];ee=e[down];distance=(-2-qe[:,2])/ee[:,2];assert (distance>0).all();hit=qe+distance[:,None]*ee;emit('background',a[down],qe,ee,tt[down],step,hit[:,:2])
  if env.any():emit('environment',a[env],q[env],e[env],tt[env],step)
  weight[a]*=RR;point[a]=q;direction[a]=reflect_direction(d,nq)
 sums=np.zeros(N)
 for t in terminal:np.add.at(sums,t['ids'],t['weight_sp'].sum(axis=-1))
 remain=weight.sum(axis=-1);missing=unresolved.sum(axis=-1);conservation=sums+remain+missing;assert abs(conservation-1).max()<2e-14
 bg=np.zeros(N);env=np.zeros(N)
 for t in terminal:np.add.at(bg if t['kind']=='background' else env,t['ids'],t['weight_sp'].sum(axis=-1))
 out={'r':r,'background_weight':bg,'environment_weight':env,'residual_weight':remain,'unresolved_weight':missing,'conservation':conservation};np.savez(D/f'{label}-weights.npz',**out)
 flat=r<.7
 if index==1.5:
  rs=.04;expected_bg=(1-rs)/(1+rs);expected_env=2*rs/(1+rs);assert abs(bg[flat]-expected_bg).max()<=EPS and abs(env[flat]-expected_env).max()<=EPS
 else:assert np.array_equal(bg,np.ones(N)) and np.array_equal(env,np.zeros(N))
 stats={'label':label,'incident_paths':N,'primary_reused':index==1.5,'new_primary_queries':0 if index==1.5 else N,'maximum_residual_weight':float(remain.max()),'maximum_unresolved_weight':float(missing.max()),'maximum_conservation_error':float(abs(conservation-1).max()),'active_by_step':active_counts,'maximum_root_bracket_L':maxwidth,'maximum_level_residual':maxresid,'background_weight_min_max':[float(bg.min()),float(bg.max())],'environment_weight_min_max':[float(env.min()),float(env.max())],'flat_core_analytic_slab_check':True,'all_path_energy_resolved_within_tolerance':bool(np.all(remain+missing<=EPS))}
 # Retain every terminal event, without any RGB/environment invention.
 arrays={}
 for j,t in enumerate(terminal):
  for k,v in t.items():
   if isinstance(v,np.ndarray):arrays[f'{j:03d}_{k}']=v
  arrays[f'{j:03d}_kind']=np.array(t['kind']);arrays[f'{j:03d}_step']=np.array(t['step'])
 np.savez(D/f'{label}-terminals.npz',**arrays);return stats
assert 997+12<=MAX_PATHS
row=run(r,primary,1.5,'g05');r1=np.linspace(0,.99,12);unit=trace_flat_front_orthographic(back,r1,np.zeros_like(r1),1.,2.);row1=run(r1,unit,1.,'unit-index');gate()
result={'status':'PASS_COMPLETE_SPARSE_PATH_ENERGY' if row['all_path_energy_resolved_within_tolerance'] else 'INCOMPLETE_REFLECTED_ENERGY_NO_IMAGE_AUTHORITY','rows':[row,row1],'incident_paths_total':1009,'new_primary_geometric_queries':12,'cached_primary_paths_reused':997,'internal_interface_events':events,'level_point_evaluations':solid.level_point_evaluations,'budgets':{'paths':MAX_PATHS,'internal_events':MAX_EVENTS,'level_points':MAX_LEVEL,'internal_per_path':MAX_INTERNAL,'residual_power_tolerance':EPS},'separate_meridional_s_p_weights':True,'assumption':'Rotational circle keeps every path in its own meridional plane; s/p polarization axes do not mix. No claim for arbitrary3D polarization transfer. Geometry/sharedSnell exact to declared root tolerance. No spectral dispersion.', 'wall_seconds':time.time()-START,'deadline':datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat(),'RGB_samples':0,'fits':0,'images':0,'environment':'Terminal directions/weights only; incident radiance NOT inferred from target'}
(D/'path-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
