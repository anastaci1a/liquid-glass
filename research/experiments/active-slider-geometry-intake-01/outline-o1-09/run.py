"""H1 solid invariants and bounded reflected path roles. No RGB or images."""
from pathlib import Path
import sys,json,datetime,time,os
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parent;REPO=ROOT.parents[2];sys.path.insert(0,str(REPO/'reconstruction'))
from surface import Budget,ClosedH1
from geometric_optics import next_convex_boundary,refract,reflect_direction,fresnel_components
cv2.setNumThreads(1);os.umask(0o002);protocol=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(protocol['subpass_deadline_utc'].replace('Z','+00:00')).timestamp();budget=Budget()
def gate():assert time.time()<end,'O1 deadline reached'
def save(name,x):(P/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fixture(s,key):
 gate();a,b=s.half;xx=np.array([0.,.2*a,-.35*a,.6*a,-.65*a]);yy=np.array([0.,.15*b,-.25*b,-.3*b,.2*b]);x=xx+s.dx;y=yy+s.dy;h,hx,hy,T,_,_,inside=s.geometry(x,y,'fixture_height');assert inside.all() and (h>0).all()
 points=np.concatenate([np.stack([x,y,np.zeros_like(x)],-1),np.stack([x,y,-h],-1),np.stack([x,y,-.5*h],-1)],0);F,G=s.level_gradient(points);assert (abs(F[:10])<1e-14).all() and (F[10:]<0).all();assert (G[:5,2]>0).all() and (G[5:10,2]<0).all()
 # Only regular front/back points, away from max-constraint ties.
 regular=points[:10];e=1e-7*s.scale;fd=[]
 for axis in range(3):
  d=np.zeros(3);d[axis]=e;fa,_=s.level_gradient(regular+d);fb,_=s.level_gradient(regular-d);fd.append((fa-fb)/(2*e))
 err=float(abs(np.stack(fd,-1)-G[:10]).max());assert err<1e-7
 mirrored=points.copy();mirrored[:,0]=2*s.dx-points[:,0];fm,gm=s.level_gradient(mirrored);assert np.allclose(fm,F,atol=1e-14,rtol=0);assert np.allclose(gm[:10],G[:10]*np.array([-1,1,1]),atol=1e-13,rtol=0)
 # Certified convexity plus a bounded midpoint occupancy control.
 midpoint=(points[10:]+points[10:][::-1])/2;fmid,_=s.level_gradient(midpoint);assert (fmid<=0).all()
 # Exact local poles are retained, including representational uncertainty after pose.
 local=ClosedH1(tuple(s.half),0,0,budget,1.);poles=np.array([[a,0,0],[-a,0,0],[0,b,0],[0,-b,0]],float);fp,gp=local.level_gradient(poles);bm=local.boundary_mask(poles[:,0],poles[:,1]);ns=local.nonsmooth_mask(poles,np.zeros(4));front,strict=local.front_height(poles[:,0],poles[:,1]);assert bm.all() and ns.all() and not strict.any() and np.isnan(gp).all()
 # Uniform scale preserves occupancy and actual regular surface normals.
 scaled=ClosedH1(tuple(s.half),s.dx,s.dy,budget,2.);fs,gs=scaled.level_gradient(2*regular);assert np.allclose(fs,0,atol=2e-14);assert np.allclose(gs/np.linalg.norm(gs,axis=-1)[:,None],G[:10]/np.linalg.norm(G[:10],axis=-1)[:,None],atol=1e-13,rtol=0)
 local_regular=regular-np.array([s.dx,s.dy,0]);fl,gl=local.level_gradient(local_regular);assert np.allclose(fl,F[:10],atol=1e-14) and np.allclose(gl,G[:10],atol=1e-13)
 # Bracket-derived ambiguity control near a crease, without changing occupancy.
 near=poles.copy();near[:,2]=-1e-12;assert local.nonsmooth_mask(near,np.full(4,1e-11)).all()
 return dict(case=key,finite_difference_error=err,front_back_winding=True,midpoint_occupancy=True,mirrors_pose_scale=True,exact_crease_unresolved=True,center=s.center.tolist(),half_extents=s.half_extents.tolist(),H=s.H,slope_bound=s.M)
def endpoint(case,point,direction,power,known,safe,event,launch,role):
 if direction[2]>=0:return dict(launch=launch,event=event,role=role,classification='UNOBSERVED_UPPER_ENVIRONMENT' if direction[2]>0 else 'UNOBSERVED_LATERAL_ENVIRONMENT',point=point.tolist(),direction=direction.tolist(),power_interval=list(power),supported=False)
 t=(-2-point[2])/direction[2];assert t>0;xy=point[:2]+t*direction[:2];X=xy[0]*case['L']+case['center'][0];Y=xy[1]*case['L']+case['center'][1];ok=True
 for dtype in [np.float64,np.float32]:
  i,j=int(np.floor(dtype(X))),int(np.floor(dtype(Y)))
  if not(0<=i and 0<=j and i+1<known.shape[1] and j+1<known.shape[0]):ok=False;continue
  for u,v in [(0,0),(1,0),(0,1),(1,1)]:ok=ok and bool(safe[j+v,i+u])
 return dict(launch=launch,event=event,role=role,classification='MODELED_BACKGROUND_D2' if ok else 'UNSUPPORTED_BACKGROUND_D2',point=point.tolist(),direction=direction.tolist(),endpoint_native=[float(X),float(Y)],power_interval=list(power),supported=bool(ok),observed_confidence=0)
def main():
 gate();assert not (P/'started.json').exists(),'No restart';save('started.json',dict(utc=now(),protocol='protocol.json'));cases=json.loads((ROOT/'proposal.json').read_text())['cases'];surfaces={};fixtures=[]
 for c in cases:
  dx=(c['corrected_center'][0]-c['center'][0])/c['L'];dy=(c['corrected_center'][1]-c['center'][1])/c['L'];s=ClosedH1(tuple(c['corrected_half_over_L']),dx,dy,budget);surfaces[c['key']]=s;fixtures.append(fixture(s,c['key']))
 save('fixture-result.json',dict(status='PASS',rows=fixtures,counters=budget.record(),utc=now()));budget.fixture=False;launches=[];events=[];endpoints=[];tails=[]
 for c in cases:
  gate();key=c['key'];s=surfaces[key];z=np.load(ROOT/f'baseline/{key}-coordinates.npz');q=np.load(ROOT/f'distance-03/{key}-paths.npz');zz=np.load(ROOT/f'distance-03/{key}-coordinates.npz');assert np.array_equal(z['inside'],zz['inside']);inside=z['inside'];known=cv2.imread(str(ROOT/f'baseline/inputs/{key}/known.png'),0)>0;r=c['finite_kernel_radius_px'];safe=cv2.erode(known.astype(np.uint8),np.ones((2*r+1,2*r+1),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  entry=q['entry'][inside];exit=q['exit'][inside];normal=q['exit_normal'][inside];direction=q['exit_direction'][inside];positions=np.argwhere(inside);selected=[]
  for cohort,anchor in [('upper',[s.dx,s.dy-.8*s.half[1]]),('lower',[s.dx,s.dy+.8*s.half[1]]),('left',[s.dx-.8*s.half[0],s.dy]),('right',[s.dx+.8*s.half[0],s.dy])]:
   indices=np.argsort(np.sum((entry[:,:2]-anchor)**2,axis=1),kind='stable')[:4]
   for idx in indices:selected.append((cohort,int(idx)))
  assert len({i for _,i in selected})==16
  for cohort,index in selected:
   gate();lid=f'{key}-{cohort}-{index}';p=exit[index].copy();n=normal[index].copy();ent=entry[index];budget.event(2);R0=float(fresnel_components(np.array([1.]),1.,1.5).mean());endpoints.append(endpoint(c,ent,np.array([0.,0.,1.]),(R0,R0),known,safe,1,lid,'initial front reflection'))
   f,g=s.level_gradient(p[None]);assert abs(f[0])<1e-12;assert np.allclose(g[0]/np.linalg.norm(g[0]),n,atol=1e-13,rtol=0);assert not s.nonsmooth_mask(p[None],np.zeros(1))[0]
   inc=np.array([0.,0.,-1.]);out,tir,k=refract(inc[None],-n[None],1.5,1.);assert not tir[0];assert np.allclose(out[0],direction[index],atol=1e-13,rtol=0);rs=fresnel_components(np.array([float(inc@n)]),1.5,1.)[0];rb=float(rs.mean());power=(float((1-R0)*rb),float((1-R0)*rb));endpoints.append(endpoint(c,p,out[0],((1-R0)*(1-rb),(1-R0)*(1-rb)),known,safe,2,lid,'initial back transmission'));d=reflect_direction(inc,n);launches.append(dict(id=lid,case=key,cohort=cohort,native_subray=positions[index].tolist(),entry=ent.tolist(),exit=p.tolist(),exit_normal=n.tolist()));events.append(dict(launch=lid,event=2,point=p.tolist(),normal=n.tolist(),internal_direction=inc.tolist(),reflected_direction=d.tolist(),reflectance_sp=rs.tolist(),remaining_power_interval=list(power),initial_unpolarized_exact=True))
   count=2
   while count<32:
    gate();budget.event(1);count+=1;hit=next_convex_boundary(s,p[None],d[None],tolerance=1e-11,max_iterations=64)
    if not hit['complete'][0]:
     save('partial-paths.json',dict(launches=launches,events=events,endpoints=endpoints,tails=tails,unresolved_launch=lid,unresolved_event=count,counters=budget.record()));raise RuntimeError('First unresolved geometry: stop without repair')
    point=hit['point'][0];n=hit['outward_normal'][0];cosine=float(d@n);rs=fresnel_components(np.array([cosine]),1.5,1.)[0];out,tir,k=refract(d[None],-n[None],1.5,1.);trans=(power[0]*(1-float(rs.max())),power[1]*(1-float(rs.min())))
    if not tir[0] and trans[1]>0:endpoints.append(endpoint(c,point,out[0],trans,known,safe,count,lid,'later transmission'))
    power=(power[0]*float(rs.min()),power[1]*float(rs.max()));ref=reflect_direction(d,n);events.append(dict(launch=lid,event=count,point=point.tolist(),normal=n.tolist(),internal_direction=d.tolist(),reflected_direction=ref.tolist(),reflectance_sp=rs.tolist(),remaining_power_interval=list(power),transmission_power_interval=list(trans),TIR_or_critical=bool(tir[0]),bracket=float(hit['bracket'][0]),level_residual=float(hit['residual'][0]),scalar_unpolarized_exact=False));p=point;d=ref
   tails.append(dict(launch=lid,encounters=count,remaining_power_interval=list(power),status='CAPPED_RESIDUAL_NOT_REPLACED'));save('partial-paths.json',dict(launches=launches,events=events,endpoints=endpoints,tails=tails,counters=budget.record()))
 gate();save('paths.json',dict(launches=launches,events=events,endpoints=endpoints,tails=tails));save('result.json',dict(status='INCOMPLETE_RADIANCE_SCENE',launches=len(launches),counters=budget.record(),endpoint_classes={k:sum(x['classification']==k for x in endpoints) for k in sorted({x['classification'] for x in endpoints})},unobserved_front_reflection_power=.04,maximum_residual_upper_bound=max(t['remaining_power_interval'][1] for t in tails),minimum_residual_lower_bound=min(t['remaining_power_interval'][0] for t in tails),RGB_queries=0,images=0,fits=0,finished_utc=now(),limits='Bounded intensity intervals, not polarization-exact later transport. No unobserved environment is assigned color. Transmission tone/PSF not applied to specular radiance.'))
try:main()
except Exception as e:
 save('stopped.json',dict(status='STOPPED_NO_REPAIR',exception=type(e).__name__,reason=str(e),utc=now(),counters=budget.record(),RGB_queries=0,images=0,fits=0));raise
