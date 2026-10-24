"""Saved convex guard feasibility; no image arrays or optical evaluation."""
from pathlib import Path
from fractions import Fraction
import datetime
import hashlib
import json
import numpy as np
from scipy.optimize import minimize

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
source = ROOT / 'research/experiments/expanded-spline-material-01/forms.json'
p = json.loads((OUT / 'protocol.json').read_text())
deadline = datetime.datetime.fromisoformat(p['deadline_utc'].replace('Z', '+00:00'))
assert not (OUT / 'feasibility.json').exists(), 'No repeated solve'
forms = json.loads(source.read_text())
F = lambda x: Fraction(str(x))
a = next(f for f in forms if (f['reference'], f['cohort']) == ('a', 'jupiter.jpg'))
b = next(f for f in forms if (f['reference'], f['cohort']) == ('b', 'play.svg'))
weight = -F(a['v'][1]) / F(b['v'][1])
assert weight > 0
Q = [[F(a['H'][i][j]) + weight * F(b['H'][i][j]) for j in range(2)] for i in range(2)]
v = [F(a['v'][i]) + weight * F(b['v'][i]) for i in range(2)]
c = F(a['c']) + weight * F(b['c'])
assert Q[0][1] == Q[1][0] and Q[0][0] >= 0 and Q[1][1] >= 0
assert Q[0][0] * Q[1][1] - Q[0][1] ** 2 >= 0
lower = c - F('.02') * sum(abs(x) for x in v)
certificate = dict(forms=['a/jupiter.jpg', 'b/play.svg'], positive_weight=str(weight),
    positive_semidefinite_exact=True, canceled_bias_coefficient_exact=(v[1] == 0),
    exact_lower_bound=str(lower), lower_bound_float=float(lower),
    old_box_infeasible_exact=(lower > 0),
    scope='Exact rational arithmetic on saved decimal quadratic-model coefficients, including their existing model reserves. Not a global native or optical impossibility proof.')
assert lower > 0

H = np.asarray([f['H'] for f in forms]); V = np.asarray([f['v'] for f in forms])
C = np.asarray([f['c'] for f in forms])
assert np.all(np.linalg.eigvalsh(H) >= 0), 'Saved quadratics must be PSD'
active = np.any(H != 0, axis=(1, 2)) | np.any(V != 0, axis=1) | (C != 0)
# Dimensionless coordinates u: r=.125*u0, w=.001*u1.
B = np.array([[-.125, 0], [.125, .001]])
HQ = np.einsum('ai,nab,bj->nij', B, H, B)
VQ = V @ B
scale = np.maximum(np.sum(abs(HQ), axis=(1, 2)) + 2 * np.sum(abs(VQ), axis=1) + abs(C), 1e-12)
ledger = []; cache = {}; best = None

class BudgetStop(Exception):
    pass

def model(u):
    global best
    if datetime.datetime.now(datetime.timezone.utc) >= deadline:
        raise BudgetStop('Original task deadline')
    key = tuple(float(t) for t in u)
    if key in cache:
        return cache[key]
    if len(ledger) >= p['budgets']['model_evaluations']:
        raise BudgetStop('Model evaluation cap')
    delta = B @ u
    residual = np.einsum('i,nij,j->n', delta, H, delta) + 2 * V @ delta + C
    bound = bool(0 <= u[0] <= 1 and -1 <= u[1] <= 0 and 0 <= delta[1] <= .125)
    row = dict(evaluation=len(ledger) + 1, normalized_parameters=list(key),
        delta=delta.tolist(), residuals=residual.tolist(), parameter_feasible=bound,
        strictly_model_feasible=bool(bound and np.all(residual <= 0)),
        worst_scaled_residual=float(np.max(residual[active] / scale[active])))
    ledger.append(row); cache[key] = residual
    if row['strictly_model_feasible'] and (best is None or row['worst_scaled_residual'] < best['worst_scaled_residual']):
        best = row
    return residual

def constraint(z):
    residual = model(z[:2])
    return np.r_[z[2] - residual[active] / scale[active], (B @ z[:2])[1]]

def jacobian(z):
    grad = (2 * np.einsum('nij,j->ni', H, B @ z[:2]) + 2 * V) @ B
    return np.vstack([np.c_[-grad[active] / scale[active, None], np.ones(active.sum())],
                      np.array([.125, .001, 0.])])

initial = np.array([0., 0., np.max(model(np.zeros(2))[active] / scale[active])])
success = False; message = ''
try:
    answer = minimize(lambda z: z[2], initial, jac=lambda z: np.array([0., 0., 1.]),
        method='SLSQP', bounds=[(0., 1.), (-1., 0.), (-10., 10.)],
        constraints=[dict(type='ineq', fun=constraint, jac=jacobian)],
        options=dict(maxiter=64, ftol=1e-12))
    success = bool(answer.success); message = str(answer.message)
    model(answer.x[:2])
except BudgetStop as error:
    message = str(error)

result = dict(status='MODEL_FEASIBLE_NATIVE_GATE_OPEN' if best else 'NO_MODEL_FEASIBLE_POINT_NATIVE_GATE_CLOSED',
    finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    source=str(source.relative_to(ROOT)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    old_box_certificate=certificate, solver_success=success, solver_message=message,
    best=best, model_evaluations=len(ledger), ledger=ledger,
    rays=0, height_calls=0, source_queries=0, images=0, fits=1)
(OUT / 'feasibility.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
print(json.dumps({k: result[k] for k in ['status', 'model_evaluations', 'solver_success', 'solver_message', 'best', 'old_box_certificate']}), flush=True)
