"""One actual Search inverse back construction; no source or image input."""
from pathlib import Path
import sys,json,datetime,hashlib
from fractions import Fraction
import numpy as np
from scipy.integrate import solve_ivp
O=Path(__file__).parent;ROOT=O.parents[2];P=json.loads((O/'protocol.json').read_text());ledger={k:0 for k in P['caps']};ledger.update(edge_limit_kinematics=0)
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def gate(checkpoint=False):assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['checkpoint_deadline' if checkpoint else 'deadline'].replace('Z','+00:00')),'Original deadline'
def reserve(delta):
 gate()
 for k,n in delta.items():assert ledger[k]+n<=P['caps'][k],k
 for k,n in delta.items():ledger[k]+=int(n)
def save(f,v):gate();(O/f).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert not (O/'started.json').exists(),'One solve only'
save('started.json',{'at':now()});result={'status':'STARTING','ledger':ledger}
try:
 sys.path.insert(0,str(ROOT/'reconstruction'));from geometric_optics import HarmonicCircularBack,refract
 hpdir=Path('/research/liquid-glass/research/experiments/miniplayer-inverse-geometry-17');sys.path.insert(0,str(hpdir));from hermite_height_profile import HermiteProfile
 R=P['fixed']['R'];n=1.5;D=2.;d=.15;c=.4;base=HarmonicCircularBack(depth=d,crown_depth=c)
 def radial(r):
  a=np.asarray(r,float);reserve({'profile_scalar_queries':3*a.size});assert np.all((a>=0)&(a<=R));t=a/R
  A=1+t+t*t;Ap=1+2*t;B=1+t;Q=d*A+c*B;Qp=d*Ap+c;Qpp=2*d
  N=d*c*(1-t)*A*B;Np=d*c*(-A*B+(1-t)*(Ap*B+A));Npp=d*c*(-2*(Ap*B+A)+(1-t)*(2*B+2*Ap))
  h=N/Q;h1=(Np*Q-N*Qp)/(Q*Q);h2=Npp/Q-(N*Qpp+2*Np*Qp)/(Q*Q)+2*N*Qp*Qp/(Q**3)
  return h,h1/R,h2/(R*R)
 def original_api(r):
  a=np.asarray(r,float);reserve({'profile_scalar_queries':12*a.size});h,hx,hy,inside=base.height_gradient(a/R,np.zeros_like(a));assert inside.all();return h,hx/R
 def snell(i,normal,nf,nt):
  reserve({'shared_Snell_points':np.asarray(i).size//3});return refract(i,normal,nf,nt)
 # Same mathematical harmonic law factored only to retain its one-sided edge limit.
 rv=R*np.array([.1,.3,.5,.7,.9,.99]);eps=R*1e-6;h,h1,h2=radial(rv);actual,actual1=original_api(rv);left,left1=original_api(rv-eps);right,right1=original_api(rv+eps)
 err0=float(abs(h-actual).max());err1=float(abs(h1-actual1).max());err2=float(abs(h2-(right1-left1)/(2*eps)).max())
 assert err0<1e-12 and err1<1e-12 and err2<1e-6
 def kin(r):
  h,hp,hpp=map(float,radial(r));f=.5*h;fp=.5*hp;fpp=.5*hpp
  nf=np.array([-fp,0.,1.]);nf/=np.linalg.norm(nf);nb=np.array([-hp,0.,-1.]);nb/=np.linalg.norm(nb);i=np.array([0.,0.,-1.])
  v,tir,_=snell(i,nf,1.,n);old,oldtir,_=snell(i,-nb,n,1.);assert not tir and not oldtir and v[2]<0 and old[2]<0
  target=r+(-D+h)*old[0]/old[2];alpha=np.arctan(fp);beta=np.arcsin(np.sin(alpha)/n);delta=alpha-beta;k=v[0]/v[2];kp=-(1+k*k)*(1-np.cos(alpha)/(n*np.cos(beta)))*fpp/(1+fp*fp)
  assert abs(k+np.tan(delta))<1e-12
  if r==R:ledger['edge_limit_kinematics']+=1
  return f,fp,v,k,kp,target
 checks=[]
 for frac in [.2,.4,.6,.8,.95]:
  rr=R*frac;mid=kin(rr);lo=kin(rr-eps);hi=kin(rr+eps);error=abs((hi[3]-lo[3])/(2*eps)-mid[4]);assert error<5e-6;checks.append({'r':rr,'k_derivative_error':float(error)})
 gate(True);save('checkpoint.json',{'status':'PASS_EXACT_RADIAL_CHAIN_AND_K_DERIVATIVE','at':now(),'h_error_vs_original_API':err0,'hp_error_vs_original_API':err1,'hpp_FD_check_error':err2,'controls':checks,'edge':'Factored one-sided limit only; harmonic_cap zero weights at exact edge are never used as a normal or traced tangent ray.','ledger':ledger.copy()});print('CHECKPOINT_PASS',now(),flush=True)
 def equation(r,B,keep=False):
  reserve({'ODE_RHS':1});f,fp,v,k,kp,target=kin(r);b=float(np.asarray(B).reshape(-1)[0]);s=r-k*(b+f)
  w=np.array([target-s,0.,-D+b]);w/=np.linalg.norm(w);den=n*v[2]-w[2];assert den<0 and abs(den)>1e-8,'Snell branch denominator'
  m=(n*v[0]-w[0])/den;condition=1+m*k;assert condition>1e-6,'Radius-map branch';bp=m*(1-k*fp-kp*(b+f))/condition;mapping=1-k*(bp+fp)-kp*(b+f)
  save('last-design-state.json',{'input_radius':float(r),'height':b,'back_radius':float(s),'condition':float(condition),'mapping_derivative':float(mapping)})
  assert np.isfinite([b,s,m,bp,mapping]).all() and 0<=b<D and s>=0,'Physical branch/height'
  if keep:return {'input_radius':float(r),'back_radius':float(s),'height':b,'height_derivative':float(m),'mapping_derivative':float(mapping),'target_source':float(target),'direction':w.tolist(),'inside_direction':v.tolist(),'front_height':float(f),'branch_condition':float(condition)}
  return [bp]
 grid=np.linspace(R,0,1025);save('solve-reservation.json',{'at':now(),'solves':1,'nodes':1025,'postsolve_same_polynomial_queries_reserved':4100,'current_ledger':ledger.copy(),'no_source_RGB':True})
 sol=solve_ivp(equation,(R,0),[0.],method='DOP853',rtol=1e-9,atol=1e-11,max_step=R/128,t_eval=grid)
 save('solver.json',{'success':bool(sol.success),'message':sol.message,'nfev':sol.nfev,'edge':'One-sided optical design limit, not a regular tangent ray.'});assert sol.success
 reserve({'design_nodes':1025});nodes=[equation(float(r),[float(b)],True) for r,b in zip(grid,sol.y[0])]
 rb=np.array([a['back_radius'] for a in nodes]);height=sol.y[0];m=np.array([a['height_derivative'] for a in nodes]);assert np.all(np.diff(rb)<0) and rb[-1]==0 and rb[0]==R and np.all(height[1:]>0) and height[0]==0 and m[-1]==0 and min(a['mapping_derivative'] for a in nodes)>0,'Single-valued positive regular back'
 radii=rb[::-1].copy();heights=height[::-1].copy();slopes=m[::-1].copy();profile=HermiteProfile(radii,heights,slopes)
 reserve({'profile_scalar_queries':2*1025});assert np.array_equal(profile.evaluate(radii),heights) and np.array_equal(profile.evaluate(radii,True),slopes),'Same-polynomial endpoint values'
 fr=lambda x:Fraction.from_float(float(x));H=Fraction(0);M=Fraction(0);minimum=None
 for j in range(1024):
  reserve({'bound_segments':1});dr=fr(radii[j+1])-fr(radii[j]);a,b=fr(heights[j]),fr(heights[j+1]);u,v=fr(slopes[j]),fr(slopes[j+1]);bern=[a,a+dr*u/3,b-dr*v/3,b]
  minimum=min(bern) if minimum is None else min(minimum,*bern);H=max(H,*bern);M=max(M,*[abs(3*(bern[i+1]-bern[i])/dr) for i in range(3)])
 assert minimum>=0,'Positive Bernstein certificate'
 def upper(x):
  a=float(x);return float(np.nextafter(a,np.inf)) if fr(a)<x else a
 Hmax=upper(H);Mmax=upper(M);save('back-profile.json',{'model':'Actual C1 cubic Hermite height, derivative from same polynomial','radius_nodes':radii.tolist(),'heights':heights.tolist(),'derivatives':slopes.tolist(),'maximum_height':Hmax,'slope_bound':Mmax,'center_derivative_exact_zero':bool(slopes[0]==0),'edge_height_exact_zero':bool(heights[-1]==0),'positive_certificate':'Exact rational Bernstein controls for intended polynomial, not an enclosure of all floating-point evaluations.'})
 reserve({'profile_scalar_queries':2*1025});Bval=profile.evaluate(rb);gradient=profile.evaluate(rb,True);normal=np.stack([-gradient,np.zeros(1025),-np.ones(1025)],-1);normal/=np.linalg.norm(normal,axis=1)[:,None];inside=np.array([a['inside_direction'] for a in nodes]);out,blocked,k=snell(inside,-normal,n,1.)
 assert not blocked.any();expected=np.array([a['direction'] for a in nodes]);errd=float(abs(out-expected).max());source=rb+(-D+Bval)*out[:,0]/out[:,2];errs=float(abs(source-np.array([a['target_source'] for a in nodes])).max());assert errd<1e-8 and errs<1e-8,'Same-height nodal Snell consistency'
 Fbound=.5*base.slope_bound/R;alpha=np.arctan(Fbound);delta=alpha-np.arcsin(np.sin(alpha)/n);beta=np.arctan(Mmax);arg=n*np.sin(beta+delta);theta=beta+np.arcsin(arg) if arg<1 else None
 escape=float(np.cos(theta)-Mmax*np.sin(theta)) if theta is not None else None
 bounds={'front_slope_bound':Fbound,'back_slope_bound':Mmax,'height_bound':Hmax,'D':D,'internal_back_margin_bound':float(np.cos(delta)-Mmax*np.sin(delta)),'internal_front_margin_bound':float(np.cos(delta)-Fbound*np.sin(delta)),'back_transmission_sine_bound':float(arg),'outgoing_no_reentry_bound':escape,'direct_front_escape_bound':float(np.cos(2*alpha)-Fbound*np.sin(2*alpha)),'scope':'Prospective sufficient scalar bounds only; no native forward tracing or source support certified.'}
 save('prospective-clearance.json',bounds);save('nodal-validation.json',{'nodes':1025,'max_direction_error':errd,'max_source_plane_error':errs,'edge_nodes_are_design_limits_not_regular_rays':True,'same_polynomial_height_and_gradient':True});save('design-nodes.json',{'nodes':nodes})
 result.update(status='ACTUAL_SEARCH_BACK_CONSTRUCTED_NO_FORWARD_IMAGE',maximum_height=Hmax,slope_bound=Mmax,minimum_radius_mapping_derivative=min(a['mapping_derivative'] for a in nodes),nodal_direction_error=errd,nodal_source_error=errs,source_map_prior_not_reference_truth=True,selected_state_changed=False)
except Exception as exc:result['status']='STOPPED_FIRST_INVARIANT';result['failure']=repr(exc)
finally:
 result['finished']=now();(O/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');(O/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n');print('FINAL',result['status'],result.get('failure'),ledger,flush=True)
