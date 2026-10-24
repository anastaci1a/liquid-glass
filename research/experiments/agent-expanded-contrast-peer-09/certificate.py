"""Check saved-model certificate and the one declared point; no solve."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
R=Path('/research/liquid-glass');O=Path('/research/agent-navigation-spline-223/research/experiments/agent-expanded-contrast-peer-09')
p=R/'research/experiments/expanded-contrast-guard-02';claim=json.loads((p/'feasibility.json').read_text());file=R/claim['source'];assert hashlib.sha256(file.read_bytes()).hexdigest()==claim['source_sha256'];forms=json.loads(file.read_text());f=lambda x:F(str(x))
a=next(v for v in forms if (v['reference'],v['cohort'])==('a','jupiter.jpg'));b=next(v for v in forms if (v['reference'],v['cohort'])==('b','play.svg'))
w=-f(a['v'][1])/f(b['v'][1]);Q=[[f(a['H'][i][j])+w*f(b['H'][i][j]) for j in range(2)] for i in range(2)];v=[f(a['v'][i])+w*f(b['v'][i]) for i in range(2)];c=f(a['c'])+w*f(b['c']);lower=c-2*F('0.01')*sum(abs(x) for x in v)
assert w>0 and v[1]==0 and Q[0][1]==Q[1][0] and Q[0][0]>=0 and Q[1][1]>=0 and Q[0][0]*Q[1][1]>=Q[0][1]**2 and lower>0
assert str(lower)==claim['old_box_certificate']['exact_lower_bound'] and str(w)==claim['old_box_certificate']['positive_weight']
x=list(map(f,claim['best']['delta']));rr=[]
for z in forms:
 value=sum(x[i]*f(z['H'][i][j])*x[j] for i in range(2) for j in range(2))+2*sum(f(z['v'][i])*x[i] for i in range(2))+f(z['c']);rr.append(dict(reference=z['reference'],cohort=z['cohort'],exact_nonpositive=value<=0,residual=float(value)))
assert all(z['exact_nonpositive'] for z in rr)
(O/'certificate-review.json').write_text(json.dumps(dict(status='PASS_SAVED_MODEL_SCOPE_ONLY',forms_sha256=claim['source_sha256'],positive_weight=str(w),exact_lower_bound=str(lower),fixed_point_residuals=rr,solves=0,alternative_points=0,limitation='Exact on saved decimal model with its existing reserves; not native global infeasibility or optical impossibility.'),indent=2)+'\n')
print('MODEL_CERTIFICATE_PASS')
