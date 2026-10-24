"""Infer a real back height from a physical source-plane correspondence prior."""
from pathlib import Path
import datetime,json,sys,hashlib
from fractions import Fraction
import numpy as np
from scipy.integrate import solve_ivp
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'reconstruction'));sys.path.insert(0,str(ROOT/'research/experiments/miniplayer-inverse-geometry-17'))
from geometric_optics import refract
from music_miniplayer_family import load_family,surface_for_member
from hermite_height_profile import HermiteProfile
P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));F=load_family();base=surface_for_member('expanded');R=base.radius;n=P['fixed']['index'];D=P['fixed']['background_distance']
ledger={k:0 for k in P['caps']}
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def charge(key,amount):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Original inverse-design deadline'
 assert ledger[key]+amount<=P['caps'][key],key
 ledger[key]+=int(amount)
 save('ledger.json',ledger)
assert not (OUT/'started.json').exists(),'One inverse solve only'
save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'family_sha256':hashlib.sha256((ROOT/'reconstruction/families/music-mini-player.json').read_bytes()).hexdigest()})
d2=base.profile.derivative(2)
def kinematics(r):
 charge('profile_scalar_queries',3)
 h=float(base.profile(r/R));hp=float(base.radial_derivative(r/R))/R;hpp=float(d2(r/R))/(R*R)
 f=P['fixed']['front_scale']*h;fp=P['fixed']['front_scale']*hp;fpp=P['fixed']['front_scale']*hpp
 front_normal=np.array([-fp,0.,1.]);front_normal/=np.linalg.norm(front_normal)
 back_normal=np.array([-hp,0.,-1.]);back_normal/=np.linalg.norm(back_normal)
 incident=np.array([0.,0.,-1.]);charge('shared_Snell_points',2)
 v,tir,_=refract(incident,front_normal,1.,n)
 old,old_tir,_=refract(incident,-back_normal,n,1.)
 assert not tir and not old_tir and v[2]<0 and old[2]<0
 target=r+(-D+h)*old[0]/old[2]
 alpha=np.arctan(fp);beta=np.arcsin(np.sin(alpha)/n);delta=alpha-beta
 k=v[0]/v[2]
 delta_prime=(1-np.cos(alpha)/(n*np.cos(beta)))*fpp/(1+fp*fp)
 kp=-(1+k*k)*delta_prime
 assert abs(k+np.tan(delta))<1e-12
 return f,fp,v,k,kp,target
checks=[]
for fraction in [.2,.4,.6,.8,.95]:
 r=R*fraction;eps=R*1e-6;center=kinematics(r);left=kinematics(r-eps);right=kinematics(r+eps)
 fd=(right[3]-left[3])/(2*eps);error=abs(fd-center[4]);assert error<5e-6
 checks.append({'input_radius':r,'k_derivative_error':float(error)})
save('checkpoint.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'same_front_derivative_controls':checks,'source_RGB_reads':0,'native_rays':0,'ledger':ledger})
events=[]
def equation(r,B,keep=False):
 charge('ode_rhs',1)
 f,fp,v,k,kp,target=kinematics(r);b=float(np.asarray(B).reshape(-1)[0]);rb=r-k*(b+f)
 target_direction=np.array([target-rb,0.,-D+b]);target_direction/=np.linalg.norm(target_direction)
 denominator=n*v[2]-target_direction[2]
 save('last-design-state.json', {'input_radius':float(r),'height':b,'back_radius':float(rb),'front_height':f,'target_source':float(target),'Snell_denominator':float(denominator)})
 assert denominator<0 and abs(denominator)>1e-8
 m=(n*v[0]-target_direction[0])/denominator
 condition=1+m*k;assert condition>1e-6,'Back-radius design branch is singular'
 derivative=m*(1-k*fp-kp*(b+f))/condition
 if keep:return {'input_radius':r,'back_radius':rb,'height':b,'height_derivative':m,'design_derivative':derivative,'mapping_derivative':1-k*(derivative+fp)-kp*(b+f),'target_source':target,'direction':target_direction.tolist(),'inside_direction':v.tolist(),'front_height':f,'branch_condition':condition}
 events.append({'r':float(r),'B':b,'back_radius':float(rb),'branch':float(condition)})
 return [derivative]
grid=np.linspace(R,0,P['caps']['design_nodes'])
solution=solve_ivp(equation,(R,0),[0.],method='DOP853',rtol=P['tolerances']['ODE_rtol'],atol=P['tolerances']['ODE_atol'],max_step=R*P['tolerances']['maximum_step_over_radius'],t_eval=grid)
save('solver.json',{'success':bool(solution.success),'message':solution.message,'nfev':solution.nfev,'edge_initialization':'One-sided optical limit defines boundary height; exact crease is not a transmitted ray.'})
assert solution.success
charge('design_nodes',len(grid))
nodes=[equation(float(r),[float(b)],True) for r,b in zip(grid,solution.y[0])]
rb=np.array([q['back_radius'] for q in nodes]);height=solution.y[0];m=np.array([q['height_derivative'] for q in nodes])
assert np.all(np.diff(rb)<0) and rb[-1]==0 and rb[0]==R,'Not a single-valued ordered back profile'
assert np.all(height[1:]>0) and height[0]==0 and m[-1]==0 and all(q['mapping_derivative']>0 for q in nodes)
rnodes=rb[::-1].copy();heights=height[::-1].copy();slopes=m[::-1].copy();actual=HermiteProfile(rnodes,heights,slopes)
assert np.array_equal(actual.evaluate(rnodes),heights)
assert np.array_equal(actual.evaluate(rnodes,True),slopes)
minimum=None;Hmax=Fraction(0);Mmax=Fraction(0)
fr=lambda x:Fraction.from_float(float(x))
for i in range(len(rnodes)-1):
 charge('polynomial_bound_segments',1)
 dr=fr(rnodes[i+1])-fr(rnodes[i]);a,b=fr(heights[i]),fr(heights[i+1]);u,v=fr(slopes[i]),fr(slopes[i+1])
 bern=[a,a+dr*u/3,b-dr*v/3,b]
 minimum=min(bern) if minimum is None else min(minimum,*bern)
 Hmax=max(Hmax,*bern)
 Mmax=max(Mmax,*[abs(3*(bern[j+1]-bern[j])/dr) for j in range(3)])
assert minimum>=0,'Actual Hermite surface lacks positive Bernstein certificate'
def upper(value):
 x=float(value)
 return float(np.nextafter(x,np.inf)) if fr(x)<value else x
save('back-profile.json',{'model':'Actual C1 cubic Hermite height; derivative from same polynomial','radius_nodes':rnodes.tolist(),'heights':heights.tolist(),'derivatives':slopes.tolist(),'maximum_height':upper(Hmax),'slope_bound':upper(Mmax),'positive_height_certificate':'Exact rational Bernstein controls of intended Hermite polynomial','center_derivative_exact_zero':bool(slopes[0]==0),'edge_height_exact_zero':bool(heights[-1]==0),'same_for_both_lengths':True})
save('design-nodes.json',{'nodes':nodes})
np.savetxt(OUT/'back-profile.csv',np.c_[rnodes,heights,slopes],delimiter=',',header='back_radius,physical_height,actual_height_derivative',comments='')
save('result.json',{'status':'INVERSE_BACK_HEIGHT_CONSTRUCTED_NO_FORWARD_RENDER','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'minimum_radius_mapping_derivative':min(q['mapping_derivative'] for q in nodes),'maximum_height':upper(Hmax),'slope_bound':upper(Mmax),'ODE_steps':solution.nfev,'ledger':ledger,'native_images':0,'physical_source_or_target_RGB_reads':0,'fits_to_RGB':0,'limits':'Nodal design consistency and intended-polynomial positivity/bounds only. Forward actual surface tracing, whole+guard source proof and native visual validation remain required. No residual warp or sampled-pixel correction.'})
print(json.dumps({'status':'CONSTRUCTED','H':upper(Hmax),'M':upper(Mmax),'ledger':ledger}),flush=True)
