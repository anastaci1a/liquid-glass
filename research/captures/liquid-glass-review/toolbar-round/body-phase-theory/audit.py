"""Queue42 pure-geometry controls/rank. No source/target/image renderer loaded."""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import brentq
import toolbar_body_phase as phase
import toolbar_candidate as baseline
import toolbar_core_strain as priorcore
import toolbar_phase_tail as priorbump

root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-body-phase-theory')
root.mkdir(exist_ok=True)
p = json.loads((root.parent/'agent-toolbar-revision3-source-control/accepted-revision3-recipe.json').read_text())
half, soft = p['shape']['half'], p['footprint_softness']
a, L = max(half), min(half)
modulehash = hashlib.sha256(Path(phase.__file__).read_bytes()).hexdigest()
write = lambda name, value: (root/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
done = root/'complete.json'
if done.exists():
    assert json.loads(done.read_text())['module_sha256'] == modulehash
    print('COMPLETE42 existing controls; no repeated analysis', flush=True)
    raise SystemExit(0)
rng = np.random.default_rng(42)
x, y = rng.uniform(-1.1*a, 1.1*a, 2048), rng.uniform(-1.1*L, 1.1*L, 2048)
F = lambda x, y, **kw: np.stack(phase.addition(x, y, half, soft, **kw), axis=-1)
P = lambda x, y, **kw: phase.potential(x, y, half, soft, **kw)
_, _, T, gx, gy, e = phase.geometry(x, y, half, soft)
z = e[0]*x+e[1]*y
u = np.clip(1-np.sqrt(T), 0, 1)
factor = np.divide(140*u**3*(1-u)**3, 4*np.sqrt(T), out=np.zeros_like(T), where=T > 0)
reference = -z[:, None]*phase.s7(u)[:, None]*e+z[:, None]**2*factor[:, None]*np.stack([gx, gy], axis=-1)
algebra_error = float(abs(reference-F(x, y)).max())
assert algebra_error < 1e-12
invariants = {'algebra_direct_chain_rule_vs_division_free_max_error': algebra_error,
              'zero_amplitude_exact': bool(np.array_equal(F(x, y, amplitude=0), np.zeros((len(x), 2)))),
              'center_potential_exact': float(P(0., 0.)), 'center_added_map': F(0., 0.).tolist()}
assert invariants['zero_amplitude_exact'] and invariants['center_potential_exact'] == 0 and np.array_equal(F(0., 0.), [0, 0])
base = F(x, y)
for scale in [.5, 2.3]:
    scaled = np.stack(phase.addition(x*scale, y*scale, np.asarray(half)*scale, soft), axis=-1)
    error = float(abs(scaled-base*scale).max())
    potential_error = float(abs(phase.potential(x*scale, y*scale, np.asarray(half)*scale, soft)-P(x, y)*scale**2).max())
    assert error < 1e-11 and potential_error < 1e-11
    invariants[f'scale_{scale}'] = {'field_max_error': error, 'potential_max_error': potential_error}
for sx, sy in [(-1, 1), (1, -1), (-1, -1)]:
    error = float(abs(F(sx*x, sy*y)-base*np.array([sx, sy])).max())
    assert error < 1e-12
    invariants[f'mirror_{sx}_{sy}'] = error
rotated = np.stack(phase.addition(-y, x, half[::-1], soft), axis=-1)
rotation_error = float(abs(rotated-np.stack([-base[:, 1], base[:, 0]], axis=-1)).max())
assert rotation_error < 1e-12
invariants['rotation90_max_error'] = rotation_error
try:
    phase.addition(x, y, [1, 1], soft)
except ValueError:
    invariants['automatic_equal_axes_rejected'] = True
else:
    raise AssertionError('Circle must not receive an undeclared majoraxis')
circle = np.stack(phase.addition(x, y, [1, 1], soft, circle=True, axis=[1, 0]), axis=-1)
circle_rotated = np.stack(phase.addition(-y, x, [1, 1], soft, circle=True, axis=[0, 1]), axis=-1)
assert np.max(abs(circle_rotated-np.stack([-circle[:, 1], circle[:, 0]], axis=-1))) < 1e-12
cx = float(phase.potential(.4, 0., [1, 1], soft, circle=True, axis=[1, 0]))
cy = float(phase.potential(0., .4, [1, 1], soft, circle=True, axis=[1, 0]))
assert cx > 0 and cy == 0
invariants['circle_explicit_axis_anisotropic'] = {'Psi_x': cx, 'Psi_y': cy, 'rotates_covariantly_only_with_axis': True}
write('invariants.json', invariants)

differences = []
for h in [1e-4*L, 5e-5*L, 2.5e-5*L]:
    gradient = np.stack([(P(x+h, y)-P(x-h, y))/(2*h), (P(x, y+h)-P(x, y-h))/(2*h)], axis=-1)
    curl = (F(x+h, y)[:, 1]-F(x-h, y)[:, 1])/(2*h)-(F(x, y+h)[:, 0]-F(x, y-h)[:, 0])/(2*h)
    differences.append({'h': h, 'potential_FD_gradient_max_error': float(abs(gradient+base).max()),
                        'added_curl_max': float(abs(curl).max()), 'added_curl_RMS': float(np.sqrt(np.mean(curl*curl)))})
assert differences[-1]['potential_FD_gradient_max_error'] < 1e-6
assert differences[-1]['added_curl_max'] < 1e-5
write('finite-differences.json', {'points': len(x), 'seed': 42, 'rows': differences,
                                  'limits': 'Sampled floating controls, not a global numerical error/curl bound. Exact gradient/C3regularity supplies conservative-field proof; inherited totalmap remains empirical.'})

angles = np.linspace(0, 2*np.pi, 129)[:-1]
boundary = []
for theta in angles:
    c, s = np.cos(theta), np.sin(theta)
    ray = lambda t: float(phase.geometry(t*c, t*s, half, soft)[2])-1
    radius = brentq(ray, 0, np.hypot(a, L)*1.001, xtol=5e-15)
    boundary.append([radius*c, radius*s])
boundary = np.asarray(boundary)
boundary_rows = []
for eps in [.04, .02, .01, .005, .0025]:
    points = boundary*(1-eps)
    value = P(points[:, 0], points[:, 1])
    delta = F(points[:, 0], points[:, 1])
    boundary_rows.append({'radial_fraction_inside': eps, 'max_abs_potential': float(abs(value).max()),
                          'max_added_field': float(np.linalg.norm(delta, axis=-1).max())})
write('boundary-center.json', {'boundary_T_residual': float(abs(phase.geometry(boundary[:, 0], boundary[:, 1], half, soft)[2]-1).max()),
                             'boundary_max_added_field': float(abs(F(boundary[:, 0], boundary[:, 1])).max()),
                             'boundary_rows': boundary_rows,
                             'center_proof': 'See model.md fractional-power/Glaeser argument; division-free value alone is not regularity proof.',
                             'source_or_target_sampled': False})


def rank_fields(x, y, label):
    T, gx, gy = phase.geometry(x, y, half, soft)[2:5]
    inside = T <= 1
    x, y, T, gx, gy = x[inside], y[inside], T[inside], gx[inside], gy[inside]
    depth = L*(1-np.sqrt(T))
    norm = np.hypot(gx, gy)
    nx = np.divide(gx, norm, out=np.zeros_like(gx), where=norm > 1e-14)
    ny = np.divide(gy, norm, out=np.zeros_like(gy), where=norm > 1e-14)
    gd = np.stack([np.divide(-L*gx, 2*np.sqrt(T), out=np.zeros_like(T), where=T > 0),
                   np.divide(-L*gy, 2*np.sqrt(T), out=np.zeros_like(T), where=T > 0)], axis=-1)
    names, fields = ['affine_core_x', 'affine_core_y'], [np.stack([-x, np.zeros_like(x)], axis=-1), np.stack([np.zeros_like(y), -y], axis=-1)]
    basis = BSpline.design_matrix(np.clip(depth/p['shape']['radius'], 0, 1), baseline.KNOTS, 3).toarray()[:, :7]
    for k in range(7):
        names.append(f'normal_{k}')
        fields.append(-L*basis[:, k, None]*np.stack([nx, ny], axis=-1))
    for band, exponent, name in [(p['parameters']['tangent_band'], 4, 'current_tangent'), (.6299800744984626, 6.228297245226836, 'prior_wider_onset_best')]:
        u = np.clip(depth/band, 0, 1)
        W = (1-u)**exponent*(1+exponent*u)
        tau = -ny*x+nx*y
        fields.append(W[:, None]*tau[:, None]*np.stack([ny, -nx], axis=-1))
        names.append(name)
    def falloff(band, exponent):
        u = np.clip(depth/band, 0, 1)
        return (1-u)**exponent*(1+exponent*u), -exponent*(exponent+1)*u*(1-u)**(exponent-1)/band
    W, D = falloff(.55, 7.)
    W0, D0 = falloff(p['parameters']['tangent_band'], 4.)
    K, Kd = .19*W-p['parameters']['tangent']*W0, .19*D-p['parameters']['tangent']*D0
    fields.append(np.stack([-x*K, np.zeros_like(x)], axis=-1)-.5*x[:, None]**2*Kd[:, None]*gd)
    names.append('prior_coupled_wide_start_band055_m7')
    old = copy.deepcopy(p)
    old['core_strain'] = {'amplitude': 1., 'width': .30*L}
    fields.append(np.stack(priorcore.addition(x, y, old), axis=-1))
    names.append('prior_core_potential030')
    for band in [.65, .8, 1.]:
        old = copy.deepcopy(p)
        old['phase_tail'] = {'strength': 1., 'band': band}
        fields.append(np.stack(priorbump.perturbation(x, y, old), axis=-1))
        names.append(f'prior_compact_bump_{band}')
    columns = np.stack(fields).reshape(len(fields), -1).T
    norms = np.sqrt(np.mean(columns*columns, axis=0))
    active = norms > 0
    zero_names = [name for name, yes in zip(names, active) if not yes]
    oldB = columns[:, active]/norms[active]
    new = F(x, y).ravel()
    newnorm = np.sqrt(np.mean(new*new))
    coeff, _, rank, old_s = np.linalg.lstsq(oldB, new, rcond=1e-10)
    fraction = float(np.sum((new-oldB@coeff)**2)/np.sum(new*new))
    augmented = np.concatenate([oldB, (new/newnorm)[:, None]], axis=1)
    singular = np.linalg.svd(augmented/np.sqrt(len(new)), compute_uv=False)
    cosines = (oldB.T@new)/len(new)/newnorm
    return {'region': label, 'geometry_points': len(x), 'zero_fields_not_orthogonality_evidence': zero_names,
            'old_active_fields': [n for n, a in zip(names, active) if a], 'old_rank': int(rank),
            'old_normalized_singular_values': (old_s/np.sqrt(len(new))).tolist(),
            'augmented_normalized_singular_values': singular.tolist(),
            'augmented_rank_relative_threshold_1e_minus10': int(np.sum(singular > singular[0]*1e-10)),
            'new_geometry_field_unexplained_energy_fraction': fraction,
            'pairwise_cosines': dict(zip([n for n, a in zip(names, active) if a], cosines.tolist())),
            'new_unit_field_max_norm': float(np.linalg.norm(F(x, y), axis=-1).max()),
            'limits': 'Uniform geometric vector-field metric, NOT native image/target/residual fit; rank novelty does not identify optics or predict score. No fitted coefficients applied or proposed.'}


grids, bound = [], phase.displacement_bound(half, soft)
for W, H in [(256, 128), (512, 256)]:
    yy, xx = np.mgrid[:H, :W]
    x = -a+(xx+.5)*2*a/W
    y = -L+(yy+.5)*2*L/H
    value = rank_fields(x.ravel(), y.ravel(), f'uniform_geometry_{W}x{H}')
    assert value['new_unit_field_max_norm'] <= bound['unit_displacement_bound']
    grids.append(value)
    write('rank-and-bound.json', {'complete': False, 'analytic_bound': bound, 'regions': grids})
yy, xx = np.mgrid[450:550, 960:1120]
grids.append(rank_fields(((xx+.5-960)/170).ravel(), ((yy+.5-542)/170).ravel(), 'fixed_d_geometry_only'))
write('rank-and-bound.json', {'complete': True, 'analytic_bound': bound, 'regions': grids,
                             'dense_grid_is_NOT_global_bound_proof': True, 'new_native_renders_or_fits': 0})
write('complete.json', {'complete': True, 'module_sha256': modulehash, 'new_native_renders': 0,
                        'new_native_fits': 0, 'new_accepted_passes': 0, 'calibration_authorized': False})
print('COMPLETE42', json.dumps({'invariants': invariants, 'differences': differences, 'bound': bound,
                              'rank': [{k: v for k, v in row.items() if k in ['region', 'old_rank', 'augmented_rank_relative_threshold_1e_minus10', 'new_geometry_field_unexplained_energy_fraction', 'new_unit_field_max_norm']} for row in grids]}), flush=True)
