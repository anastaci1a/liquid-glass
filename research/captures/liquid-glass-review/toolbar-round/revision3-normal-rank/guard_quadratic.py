"""Complete saved-image quadratic guard forms; no optical rendering/fitting."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.optimize import minimize

root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-normal-rank')
analysis = json.loads((root/'assessment.json').read_text())
intervals = json.loads((root/'guard-sensitivity.json').read_text())
native = np.load(root/'retained-native-central.npy', mmap_mode='r')
surrogate = np.load(root.parent/'agent-toolbar-revision3-derivative-reliability/surrogate.npy', mmap_mode='r')
proposal = root.parent/'agent-toolbar-response-trials/first-proposal'
alpha = np.load(proposal/'alpha.npy')
complete = np.load(proposal/'complete.npy')
T = np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png'), np.float32)[285:845, 475:1445]/255
masks = np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
fg = np.load('/tmp/agent-toolbar-evidence-package/derived-foreground.npz')
p = json.loads((proposal/'recipe.json').read_text())
transmission = alpha.copy()
for layer in p['foreground_layers']:
    transmission = transmission*(1-fg[layer['name']])
regions = {'glass': masks['glass'], 'exterior': masks['exterior']}
for layer in p['foreground_layers']:
    a, b, c, d = layer['box']
    m = np.zeros(alpha.shape, bool)
    m[b-285:d-285, a-475:c-475] = True
    regions[layer['name']] = m
order = intervals['order']
lo, hi = np.asarray(intervals['lower']), np.asarray(intervals['upper'])
scores = {'glass': 5.796156406402588, 'exterior': 11.466962522841486,
          'archivebox': 13.142080481292576, 'plus': 3.304110822040719}
forms, results = {}, []
for kind, J in [('original_native_central_h002', native), ('full_fraction_gradient_surrogate', surrogate)]:
    forms[kind] = {}
    for guard in order:
        m = regions[guard]
        columns = J[:, m].reshape(7, -1).astype(float)*255*.002
        if guard != 'glass':
            columns *= np.repeat(transmission[m], 3)[None]
        G = columns@columns.T/columns.shape[1]
        forms[kind][guard] = {'squared_RGB_guard_gram': G.tolist(),
                             'normalized_guard_gram': (G/(2*scores[guard])).tolist()}
for row in analysis['rows']:
    for subspace in ['all7', 'inner456']:
        indices = list(range(7)) if subspace == 'all7' else [4, 5, 6]
        n = len(indices)
        Q = np.asarray(row[subspace]['gram'])
        g = np.asarray(row['residual_gradient'])[indices]
        transform = np.concatenate([np.eye(n), -np.eye(n)], axis=1)
        A = np.concatenate([hi[:, indices], -lo[:, indices]], axis=1)
        guardG = np.stack([np.asarray(forms[row['derivative']][name]['normalized_guard_gram'])[np.ix_(indices, indices)] for name in order])
        def objective(z):
            x = transform@z
            return float(x@Q@x+g@x)
        def jac(z):
            return transform.T@(2*Q@(transform@z)+g)
        def guard(z):
            x = transform@z
            return A@z+np.einsum('i,kij,j->k', x, guardG, x)
        def guard_jac(z):
            return A+2*np.einsum('kij,j->ki', guardG, transform@z)@transform
        result = minimize(objective, np.zeros(2*n), jac=jac, bounds=[(0, 1)]*(2*n),
                          constraints=[{'type': 'ineq', 'fun': lambda z: 1-z.sum(), 'jac': lambda z: -np.ones(2*n)},
                                       {'type': 'ineq', 'fun': lambda z: -guard(z), 'jac': lambda z: -guard_jac(z)}],
                          method='SLSQP', options={'maxiter': 500, 'ftol': 1e-13})
        z = result.x
        # Independent strict witness, no numerical-zero truncation of solver vector.
        witness = np.zeros(2*n)
        witness[indices.index(4)] = 1
        results.append({'derivative': row['derivative'], 'cohort': row['cohort'], 'subspace': subspace,
                        'solver_success_NOT_native_acceptance': bool(result.success),
                        'guard_changes_with_quadratic': guard(z).tolist(),
                        'strict_machine_feasible': bool(z.min() >= 0 and z.sum() <= 1 and np.max(guard(z)) <= 0),
                        'quadratic_loss_decrease': -objective(z), 'required_loss_decrease': row['loss_at_this_diagnostic_weighting']*(1-.995**2),
                        'axis4_witness_guard_changes': guard(witness).tolist(),
                        'axis4_witness_strict_machine_feasible': bool(np.max(guard(witness)) <= 0),
                        'axis4_witness_loss_decrease': -objective(witness)})
(root/'guard-quadratic-review.json').write_text(json.dumps({'complete': True, 'guard_order': order, 'guard_forms': forms, 'results': results,
    'definition': 'Conservative score-gradient sensitivity envelopes plus PSD guard image-curvature term G/(2 baselineRMSE). Equivalent to local squared-RMSE constraints, not nonlinear native guard verification. Original glass/exterior/archive/plus only; rim stays in objective. No epsilon guard allowance, no new native renders/fits.'}, indent=2)+'\n')
print(json.dumps([r for r in results if r['cohort'] == 'all']), flush=True)
