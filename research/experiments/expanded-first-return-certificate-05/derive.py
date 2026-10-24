"""Exact coefficient arithmetic only; imports no optical or spline evaluator."""
from pathlib import Path
from fractions import Fraction as F
import datetime,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
p=json.loads((P/'protocol.json').read_text());end=datetime.datetime.fromisoformat(p['deadline'].replace('Z','+00:00'))
assert not (P/'result.json').exists();assert datetime.datetime.now(datetime.timezone.utc)<end
files=[ROOT/'research/experiments/expanded-spline-height-01/inference.json',ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json',ROOT/'research/experiments/expanded-outline-role-04/result.json',ROOT/'research/experiments/expanded-outline-role-04/protocol.json',ROOT/'reconstruction/spline_height_back.py',ROOT/'reconstruction/rounded_rectangle_back.py']
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
first={str(f.relative_to(ROOT)):sha(f) for f in files}
fit=json.loads(files[0].read_text());scene=json.loads(files[1].read_text())['geometry'];parent=json.loads(files[2].read_text());parent_protocol=json.loads(files[3].read_text())
c=[F(float(x)) for x in fit['best']['heights']];breaks=[F(float(x)) for x in fit['breaks']];R=F(float(scene['surface_radius']));half=[F(float(x)) for x in scene['surface_half']]
assert len(c)==11 and c[0]==c[1] and c[-1]==0 and min(c[:-1])>0
assert breaks[0]==0 and breaks[-1]==1 and all(a<b for a,b in zip(breaks,breaks[1:]))
assert 0<R<=min(half)
t=[breaks[0]]*3+breaks+[breaks[-1]]*3;assert len(t)==len(c)+4
first_derivative=[3*(c[i+1]-c[i])/(t[i+4]-t[i+1]) for i in range(len(c)-1)]
u=t[1:-1]
second_derivative=[2*(first_derivative[i+1]-first_derivative[i])/(u[i+3]-u[i+1]) for i in range(len(first_derivative)-1)]
assert first_derivative[0]==0
H=max(c);M_exact=max(map(abs,first_derivative))/R;K_exact=max(map(abs,second_derivative))/(R*R)
def up(q):
 scale=1<<40;return F((q.numerator*scale+q.denominator-1)//q.denominator,scale)
M=up(M_exact);K=up(K_exact);assert M>=M_exact and K>=K_exact and 0<M<1
rz_min=(1-M*M)/(1+M*M);rxy_squared_max=4*M*M/(1+M*M)**2
front_time_max=H/rz_min;clearance_factor=1-K*rxy_squared_max*front_time_max/2
# Until the footprint boundary, g'' >= -K*|r_xy|^2 and g'(0)=1.
# A positive factor excludes a back hit and an outside-footprint crossing.
passed=clearance_factor>0
margin=F(float(parent_protocol['numerical_cone_margin']));index=F(3,2)
critical_cosine_squared=1-1/(index*index)
former_cone_upper=M+margin
TIR_gap_squared=critical_cosine_squared-former_cone_upper**2
transfer=passed and TIR_gap_squared>0
new_count=parent['first_front_TIR_or_critical']+parent['uncertified_next_intersections'] if transfer else None

def rational(q):return dict(value=float(q),numerator=str(q.numerator),denominator=str(q.denominator))
result=dict(status='ANALYTIC_FIRST_RETURN_CERTIFICATE_PASS' if passed else 'SUFFICIENT_BOUND_INCONCLUSIVE',finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),degree=3,knots=[rational(x) for x in t],first_derivative_controls=[rational(x) for x in first_derivative],second_derivative_controls=[rational(x) for x in second_derivative],height_upper=rational(H),radius=rational(R),slope_exact=rational(M_exact),slope_upward=rational(M),gradient_lipschitz_exact=rational(K_exact),gradient_lipschitz_upward=rational(K),reflected_vertical_lower=rational(rz_min),reflected_lateral_squared_upper=rational(rxy_squared_max),front_time_upper=rational(front_time_max),clearance_factor_lower=rational(clearance_factor),first_return_front_certified=passed,former_cone_cosine_upper=rational(former_cone_upper),TIR_squared_gap_lower=rational(TIR_gap_squared),derived_transfer=dict(valid=transfer,previous_certified_front=parent['cone_certified_first_front_encounters'],previous_uncertified_next=parent['uncertified_next_intersections'],previous_measured_front_TIR=parent['first_front_TIR_or_critical'],predicted_total_front_TIR=new_count,as_run_parent_modified=False,new_trace_or_Fresnel_measurement=False,scope='Analytic intended-surface consequence; not an interval-verified floating-point propagation or radiance/image result.'),derived_scalar_entries=len(first_derivative)+len(second_derivative)+14,inputs=first,assumptions=['Cap-join width zero: Euclidean distance to fixed inner rectangle divided by radius.','Clamped cubic spline and exact center derivative zero.','Same surface supplies the gradient; primary front is flat and incidence vertical.','Regular positive-height back launch; exact crease excluded.','Hessian bound applies inside footprint, not across zero-extension boundary.','Rational certificate addresses the intended real B-spline; floating-point evaluation error is not globally interval verified.'],new_optical_evaluations=0,shared_edits=0)
assert result['derived_scalar_entries']<=p['caps']['derived_scalar_entries']
assert first=={str(f.relative_to(ROOT)):sha(f) for f in files};assert datetime.datetime.now(datetime.timezone.utc)<end
(P/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:result[k] for k in ['status','gradient_lipschitz_upward','front_time_upper','clearance_factor_lower','derived_transfer']}))
