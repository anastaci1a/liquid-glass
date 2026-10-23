"""Queue35: retained-image quadratic/rank review; no native render or fit."""
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy.optimize import minimize

cv2.setNumThreads(1)
root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-normal-rank')
root.mkdir(exist_ok=True)
prior = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-derivative-reliability')
metadata = json.loads((prior/'directional-comparison.json').read_text())
assert metadata['complete'] and metadata['accepted_revision'] == 3
recipe = json.loads((prior/'accepted-recipe.json').read_text())
sigma = recipe['post_sigma']*170
alpha = np.load('/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/first-proposal/alpha.npy')
C = np.load('/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/first-proposal/material.npy')
T = np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png'), np.float32)[285:845, 475:1445]/255
masks = np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
cohorts = np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz')
raw = np.load(prior/'native-raw.npy', mmap_mode='r')
surrogate = np.load(prior/'surrogate.npy', mmap_mode='r')
denom = np.maximum(cv2.GaussianBlur(alpha, (0, 0), sigma), 1e-12)


def write(name, value):
    (root/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def post(A):
    return cv2.GaussianBlur(A*alpha[..., None], (0, 0), sigma)/denom[..., None]


native_path = root/'retained-native-central.npy'
if native_path.exists():
    native = np.load(native_path, mmap_mode='r')
else:
    native = np.stack([(post(raw[1+6*k+5])-post(raw[1+6*k+4]))/.004 for k in range(7)])
    np.save(native_path, native)


def forms(J, selected):
    G, g, loss = np.zeros((7, 7)), np.zeros(7), 0.
    for mask, weight in [(selected, .7), (masks['rim'], .3)]:
        columns = J[:, mask].reshape(7, -1).T.astype(float)*255*.002
        residual = (C-T)[mask].reshape(-1).astype(float)*255
        G += weight*(columns.T@columns)/len(residual)
        g += weight*2*(columns.T@residual)/len(residual)
        loss += weight*(residual@residual)/len(residual)
    return G, g, loss


def spectrum(G, indices):
    B = G[np.ix_(indices, indices)]
    values = np.sqrt(np.maximum(np.linalg.eigvalsh(B), 0))[::-1]
    norms = np.sqrt(np.maximum(np.diag(B), 0))
    corr = B/np.maximum(norms[:, None]*norms[None, :], 1e-300)
    singular = np.sqrt(np.maximum(np.linalg.eigvalsh(corr), 0))[::-1]
    return {'gram': B.tolist(), 'singular_values': values.tolist(),
            'condition': float(values[0]/values[-1]) if values[-1] else None,
            'column_norms': norms.tolist(), 'column_normalized_singular_values': singular.tolist(),
            'column_normalized_condition': float(singular[0]/singular[-1]) if singular[-1] else None}


guards = ['glass', 'exterior', 'archivebox', 'plus']
guard_lo, guard_hi = [], []
for guard in guards:
    lows, highs = [], []
    for k in range(7):
        rows = [r for r in metadata['rows'] if r['coefficient'] == k]
        observed = [r['actual_central_guard_derivatives'][guard] for r in rows]
        observed.append(rows[0]['surrogate_guard_derivatives'][guard])
        lows.append(min(observed)*.002)
        highs.append(max(observed)*.002)
    guard_lo.append(lows)
    guard_hi.append(highs)
guard_lo, guard_hi = np.array(guard_lo), np.array(guard_hi)
write('guard-sensitivity.json', {'order': guards, 'dimensionless_scales': [.002]*7,
                              'lower': guard_lo.tolist(), 'upper': guard_hi.tolist(),
                              'definition': 'Conservative envelope across three saved native central score differences plus surrogate guard gradient. Not a rigorous interval bound. No epsilon guard relaxation. Rim is reported in33, NOT an extra standalone guard.'})


def assess(G, g, loss, indices):
    Q, b = G[np.ix_(indices, indices)], g[indices]
    lo, hi = guard_lo[:, indices], guard_hi[:, indices]
    n = len(indices)
    # z=[positive,negative], x=positive-negative. Convex hull of validated axis steps.
    transform = np.concatenate([np.eye(n), -np.eye(n)], axis=1)
    robust = np.concatenate([hi, -lo], axis=1)
    def objective(z):
        x = transform@z
        return float(x@Q@x+b@x)
    def gradient(z):
        return transform.T@(2*Q@(transform@z)+b)
    result = minimize(objective, np.zeros(2*n), jac=gradient, bounds=[(0, 1)]*(2*n),
                      constraints=[{'type': 'ineq', 'fun': lambda z: 1-z.sum(), 'jac': lambda z: -np.ones(2*n)},
                                   {'type': 'ineq', 'fun': lambda z: -robust@z, 'jac': lambda z: -robust}],
                      method='SLSQP', options={'maxiter': 500, 'ftol': 1e-13})
    z = result.x
    native_delta = transform@z*.002
    feasible = bool(z.min() >= 0 and z.sum() <= 1 and np.max(robust@z) <= 0)
    return {'indices': indices, 'solver': 'SLSQP one zero start, local convex PSD quadratic assessment only',
            'solver_success': bool(result.success), 'message': result.message,
            'strict_machine_linear_constraints_satisfied_NOT_native_guard_acceptance': feasible,
            'largest_signed_linear_guard_residual_no_epsilon': float(np.max(robust@z)),
            'split_sum': float(z.sum()), 'coefficient_delta_DIAGNOSTIC_ONLY': native_delta.tolist(),
            'robust_linear_guard_changes': (robust@z).tolist(),
            'local_quadratic_loss_decrease': -objective(z),
            'required_loss_decrease': loss*(1-.995**2),
            'unguarded_linear_upper_bound_on_local_quadratic_loss_decrease_L1': float(abs(b).max()),
            'unguarded_linear_upper_bound_BOX': float(abs(b).sum()),
            'predicted_E_relative_reduction_DIAGNOSTIC_ONLY': float(1-np.sqrt(max(loss+objective(z), 0)/loss)),
            'not_global_image_fit_bound': True}


rows = []
for kind, J in [('original_native_central_h002', native), ('full_fraction_gradient_surrogate', surrogate)]:
    for cohort in ['all', 'observed_kernel_proxy', 'estimated_kernel_proxy', 'mixed_or_uncertain']:
        selected = cohorts[cohort]
        G, g, loss = forms(J, selected)
        row = {'derivative': kind, 'cohort': cohort, 'cohort_pixels': int(selected.sum()),
               'source_subset_is_diagnostic_not_scoring_mask': True,
               'rim_uses_original_full_mask': True, 'loss_at_this_diagnostic_weighting': loss,
               'residual_gradient': g.tolist(), 'all7': spectrum(G, list(range(7))),
               'inner456': spectrum(G, [4, 5, 6]),
               'guarded_all7': assess(G, g, loss, list(range(7))),
               'guarded_inner456': assess(G, g, loss, [4, 5, 6])}
        # Exact coordinate-axis witness already rendered in33, not a new proposal.
        row['already_tested_axis4_witness'] = {
            'dimensionless_direction': [0, 0, 0, 0, 1, 0, 0],
            'worst_linear_guard_changes': guard_hi[:, 4].tolist(),
            'strict_machine_linear_constraints_satisfied': bool(np.max(guard_hi[:, 4]) <= 0),
            'local_quadratic_loss_decrease': float(-G[4, 4]-g[4]),
            'not_a_new_native_proposal': True}
        rows.append(row)
        write('assessment.json', {'complete': False, 'rows': rows})
        print('ASSESSED35', kind, cohort, row['guarded_all7']['local_quadratic_loss_decrease'], flush=True)
write('assessment.json', {'complete': True, 'rows': rows,
                         'trust_region': 'sum abs(delta_coefficient/.002)<=1; conservative convex hull of tested AXIS steps, joint nonlinear reliability still unverified',
                         'dimensionless_scales': [.002]*7, 'new_native_renders': 0, 'new_native_fits': 0,
                         'accepted_revision': 3, 'new_accepted_passes': 0,
                         'limits': 'Closed low-dimensional quadratic diagnostics only; source proxy cohorts are not hidden-source truth. Local PSD linear upper bounds apply to the local quadratic ONLY, not actual nonlinear fit. SLSQP tolerance never relaxes native guards. No proposed native direction merely from solver success.'})
