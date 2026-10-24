"""Exact intended-polynomial convexity decision; no optical module is imported."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,datetime,math
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;P=json.loads((OUT/'protocol.json').read_text());END=datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));ledger={k:0 for k in P['caps']}
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END and ledger[k]+n<=P['caps'][k];ledger[k]+=n;save('ledger.json',ledger)
def exact(x):return {'numerator':str(x.numerator),'denominator':str(x.denominator),'approximate':float(x)}
def value(c,t):return c[0]*(1-t)**3+3*c[1]*t*(1-t)**2+3*c[2]*t*t*(1-t)+c[3]*t**3
assert not (OUT/'started.json').exists();save('started.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat()});data=(ROOT/P['source']).read_bytes();digest=hashlib.sha256(data).hexdigest();assert digest==P['source_sha256'];model=json.loads(data);r=list(map(Q.from_float,model['radius_nodes']));h=list(map(Q.from_float,model['heights']));m=list(map(Q.from_float,model['derivatives']));intervals=[];positive=[];maximum_first=None;maximum_abs_second=Q(0)
for i in range(len(r)-1):
 charge('polynomial_intervals',1);d=r[i+1]-r[i];assert d>0;c=[h[i],h[i]+d*m[i]/3,h[i+1]-d*m[i+1]/3,h[i+1]];q=[3*(c[j+1]-c[j])/d for j in range(3)];assert value(c,Q(0))==h[i] and value(c,Q(1))==h[i+1] and q[0]==m[i] and q[2]==m[i+1];left=2*(q[1]-q[0])/d;right=2*(q[2]-q[1])/d;maximum_abs_second=max(maximum_abs_second,abs(left),abs(right));candidates=[q[0],q[2]];A=q[0]-2*q[1]+q[2]
 if A<0:
  t=(q[0]-q[1])/A
  if 0<t<1:candidates.append(q[0]*(1-t)**2+2*q[1]*t*(1-t)+q[2]*t*t)
 first=max(candidates);maximum_first=first if maximum_first is None else max(maximum_first,first);intervals.append({'interval':i,'radius_start':float(r[i]),'radius_end':float(r[i+1]),'maximum_first_derivative':float(first),'second_derivative_left':float(left),'second_derivative_right':float(right),'concave':max(left,right)<=0})
 if max(left,right)>0:positive.append((max(left,right),i,c,left,right))
 if i==7:
  now=datetime.datetime.now(datetime.timezone.utc);assert now<datetime.datetime.fromisoformat(P['checkpoint_deadline'].replace('Z','+00:00'));save('checkpoint.json',{'at':now.isoformat(),'first_eight_exact_endpoint_controls':True,'source_hash_exact':True});print('CHECKPOINT '+now.isoformat()+' exact endpoint algebra PASS',flush=True)
witnesses=[]
for _,i,c,left,right in sorted(positive,reverse=True)[:3]:
 if left>0 and right>0:t=Q(1,2)
 elif left>0:t=left/(left-right)/2
 else:t=(1+(-left)/(right-left))/2
 e=min(t,1-t)/2;assert e>0;charge('exact_witness_values',3);a=value(c,t-e);mid=value(c,t);b=value(c,t+e);gap=(a+b)/2-mid;assert gap>0;dr=r[i+1]-r[i];witnesses.append({'interval':i,'left_radius':exact(r[i]+dr*(t-e)),'middle_radius':exact(r[i]+dr*t),'right_radius':exact(r[i]+dr*(t+e)),'back_height_left':exact(a),'back_height_middle':exact(mid),'back_height_right':exact(b),'chord_below_actual_lower_boundary':exact(gap),'interpretation':'At straight body x=0,y=(minor_half-radius)+r,z=-B(r), both endpoints lie on the actual back. The midpoint lies below the actual back by this positive gap; therefore the closed solid is nonconvex.'})
last=hashlib.sha256((ROOT/P['source']).read_bytes()).hexdigest();assert last==digest;save('intervals.json',{'records':intervals});save('witnesses.json',{'records':witnesses});upper=float(maximum_abs_second)
if Q.from_float(upper)<maximum_abs_second:upper=math.nextafter(upper,math.inf)
save('result.json',{'status':'NONCONVEX_SOLID_WITNESS' if witnesses else 'CONCAVE_RADIAL_BACK_CERTIFICATE','finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'profile_sha256':digest,'first_last_source_match':True,'intervals':len(intervals),'positive_second_derivative_intervals':len(positive),'maximum_first_derivative':exact(maximum_first),'radial_profile_second_derivative_absolute_bound':upper,'bound_scope':'Inside profile domain only; zero extension has a derivative crease at projected silhouette. No universal outer gradient-Lipschitz certificate asserted.','solid_convex':not bool(witnesses) and maximum_first<=0,'convex_event_solver_authorized':not bool(witnesses) and maximum_first<=0,'ledger':ledger,'primary_tracer_invalidated':False,'claim':'Intended real polynomial, not physical Apple geometry or a floating-point interval enclosure. Current primary Lipschitz tracer does not assume convexity.'});print(json.dumps({'positive_intervals':len(positive),'witnesses':len(witnesses),'radial_second_bound':upper,'maximum_first':float(maximum_first),'ledger':ledger}),flush=True)
