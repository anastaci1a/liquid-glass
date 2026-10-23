"""Queue36: saved residual inventory and analytic d geometry, no image render/fit."""
import json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import toolbar_candidate as model
from toolbar_scattering_covariance import transport_jacobian

cv2.setNumThreads(1)
root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-residual-modes')
root.mkdir(exist_ok=True)
prior = root.parent/'agent-toolbar-revision3-derivative-reliability'
proposal = root.parent/'agent-toolbar-response-trials/first-proposal'
case_recipe = json.loads((prior/'accepted-recipe.json').read_text())
C = np.load(proposal/'material.npy').astype(float)
full = np.load(proposal/'complete.npy')
alpha = np.load(proposal/'alpha.npy')
native = np.load(root.parent/'agent-toolbar-revision3-normal-rank/retained-native-central.npy', mmap_mode='r')
source = np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/source.png'), float)/255
T = np.asarray(Image.open('/tmp/agent-toolbar-evidence-package/inputs/target.png'), np.float32)[285:845, 475:1445]/255
masks = np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
cohorts = np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz')
fg = np.load('/tmp/agent-toolbar-evidence-package/derived-foreground.npz')


def write(name, value):
    (root/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


H, W = alpha.shape
yy, xx = np.mgrid[:H, :W]
_, nx, ny = model.boundary((xx+475-960)/170, (yy+285-542)/170, case_recipe)
gy, gx = np.gradient(C, axis=(0, 1))
normal_proxy = nx[..., None]*gx+ny[..., None]*gy
tangent_proxy = -ny[..., None]*gx+nx[..., None]*gy
laplace_proxy = np.gradient(gx, axis=1)+np.gradient(gy, axis=0)
# These output-image directions include material/PSF variation; not parameter derivatives.
proxies = {'output_normal_placement_PROXY': normal_proxy,
           'output_tangential_placement_PROXY': tangent_proxy,
           'ordinary_width_curvature_PROXY': laplace_proxy,
           'shared_neutral_offset_PROXY': np.ones_like(C)}
regions = {'glass': masks['glass'], 'rim': masks['rim']}
for name in ['observed_kernel_proxy', 'estimated_kernel_proxy', 'mixed_or_uncertain']:
    regions[name] = cohorts[name]
for name, box in {'upper': [650, 369, 1270, 435], 'd': [960, 450, 1120, 550], 'underside': [650, 650, 1270, 726]}.items():
    a, b, c, d = box
    m = np.zeros(alpha.shape, bool)
    m[b-285:d-285, a-475:c-475] = True
    regions[name] = m&masks['glass']


def direction_summary(v, desired):
    a, b = v.reshape(-1).astype(float), desired.reshape(-1).astype(float)
    aa, bb, ab = float(a@a), float(b@b), float(a@b)
    return {'direction_RMS_255': float(np.sqrt(aa/max(len(a), 1))),
            'cosine': ab/np.sqrt(aa*bb) if aa*bb else None,
            'single_span_projection_energy_fraction': ab*ab/(aa*bb) if aa*bb else None,
            'diagnostic_only_not_a_fitted_correction': True}


def energy(R):
    R = R.reshape(-1, 3).astype(float)*255
    neutral = R.sum(axis=1)/np.sqrt(3)
    chroma1 = (R[:, 0]-R[:, 1])/np.sqrt(2)
    chroma2 = (R[:, 0]+R[:, 1]-2*R[:, 2])/np.sqrt(6)
    total = float(np.mean(np.sum(R*R, axis=1)))
    return {'pixels': len(R), 'RGB_RMSE_diagnostic_255': float(np.sqrt(total/3)),
            'total_mean_squared_RGB_vector': total,
            'neutral_energy_fraction': float(np.mean(neutral*neutral)/total) if total else None,
            'chroma_energy_fraction': float(np.mean(chroma1*chroma1+chroma2*chroma2)/total) if total else None,
            'mean_signed_RGB_255': R.mean(axis=0).tolist(),
            'encoded_RGB_orthonormal_decomposition_NOT_radiometric_luminance': True}


inventory = []
for name, m in regions.items():
    desired = (T-C)[m]*255
    columns = native[:, m].reshape(7, -1).T.astype(float)*255
    G = columns.T@columns
    b = columns.T@desired.ravel()
    values, vectors = np.linalg.eigh(G)
    keep = values > max(values.max()*1e-12, 1e-24)
    representable = float(np.sum((vectors[:, keep].T@b)**2/values[keep])) if keep.any() else 0.
    residual_energy = float(desired.ravel()@desired.ravel())
    inventory.append({'region': name, 'residual': energy((C-T)[m]),
                      'normal7_local_span_rank': int(keep.sum()),
                      'normal7_unbounded_local_projection_energy_fraction_NOT_global_fit_bound': representable/residual_energy if residual_energy else None,
                      'source_cohorts': {k: int((m&cohorts[k]).sum()) for k in ['observed_kernel_proxy', 'estimated_kernel_proxy', 'mixed_or_uncertain']},
                      'proxy_directions': {n: direction_summary(v[m]*255, desired) for n, v in proxies.items()}})
write('inventory.json', {'complete': True, 'regions': inventory,
                         'limits': 'Retained-vector projections only; no new image correction/fit/render. Output normal/tangent/Laplacian directions mix optics, material, source/font/PSF and sampling, so are not identified physical operators. Full masks stay scored; cohorts/crops advisory.'})
transmission = alpha.copy()
for layer in case_recipe['foreground_layers']:
    transmission *= 1-fg[layer['name']]
protected = []
for name in ['exterior', 'archivebox', 'plus']:
    if name == 'exterior':
        m = masks['exterior']
    else:
        layer = next(q for q in case_recipe['foreground_layers'] if q['name'] == name)
        a, b, c, d = layer['box']
        m = np.zeros(alpha.shape, bool)
        m[b-285:d-285, a-475:c-475] = True
    J = native[:, m]*transmission[m][None, :, None]
    desired = (T-full)[m]*255
    columns = J.reshape(7, -1).T.astype(float)*255
    G = columns.T@columns
    b = columns.T@desired.ravel()
    values, vectors = np.linalg.eigh(G)
    keep = values > max(values.max()*1e-12, 1e-24)
    projection = float(np.sum((vectors[:, keep].T@b)**2/values[keep])) if keep.any() else 0
    protected.append({'region': name, 'complete_residual': energy((full-T)[m]),
                      'glass_normal_local_span_rank': int(keep.sum()),
                      'glass_normal_local_projection_energy_fraction': projection/float(desired.ravel()@desired.ravel()),
                      'limits': 'Foreground canonical-vector approximation, source and shadow uncertainties remain; projection does not authorize glyph/shadow/source changes.'})
write('protected-roles.json', protected)

# Analytic positional derivatives, distinct from quantized source-sampling derivatives.
dy, dx = np.mgrid[450:550, 960:1120]
x, y = (dx-960)/170, (dy-542)/170
J, flags = transport_jacobian(x, y, case_recipe)
X, Y = model.mapping(x, y, case_recipe)
det = np.linalg.det(J)
horizontal_stem = 1/J[..., 0, 0]
inverse_fixed_source_y = J[..., 1, 1]/det
hessians, convergence = [], []
for h in [.25, .125, .0625]:
    jxp = transport_jacobian(x+h/170, y, case_recipe)[0]
    jxm = transport_jacobian(x-h/170, y, case_recipe)[0]
    jyp = transport_jacobian(x, y+h/170, case_recipe)[0]
    jym = transport_jacobian(x, y-h/170, case_recipe)[0]
    Hess = np.stack([(jxp-jxm)/(2*h), (jyp-jym)/(2*h)], axis=-1)
    hessians.append(Hess)
    if len(hessians) > 1:
        difference = Hess-hessians[-2]
        convergence.append({'h_native_px': h, 'max_Hessian_change_per_native_px': float(abs(difference).max()),
                            'p99_Hessian_change': float(np.quantile(abs(difference), .99))})
Hess = hessians[-1]
np.savez(root/'d-map-derivatives.npz', J=J, Hessian=Hess, X_source=X*170+960, Y_source=Y*170+542,
         horizontal_stem_magnification=horizontal_stem, inverse_fixed_source_y=inverse_fixed_source_y,
         depth=flags['depth'], undefined_branch=flags['undefined_normal_branch'])


def stats(a):
    return {'min': float(np.min(a)), 'median': float(np.median(a)), 'max': float(np.max(a)),
            'p01_p99': np.quantile(a, [.01, .99]).tolist(), 'peak_to_peak': float(np.ptp(a))}


stem = (dx >= 1100)&(dx <= 1115)&(dy >= 445)&(dy <= 525)
geo = {'d_crop': [960, 450, 1120, 550], 'horizontal_vertical_source_stem_width_factor_1_over_Jxx': stats(horizontal_stem),
       'horizontal_inverse_map_fixed_source_y_factor_Jyy_over_det': stats(inverse_fixed_source_y),
       'Jxx': stats(J[..., 0, 0]), 'Jxy': stats(J[..., 0, 1]), 'Jyx': stats(J[..., 1, 0]), 'Jyy': stats(J[..., 1, 1]),
       'determinant': stats(det), 'coordinate_depth': stats(flags['depth']),
       'undefined_core_branch_count': int(flags['undefined_normal_branch'].sum()),
       'dJxx_dx_per_native_px': stats(Hess[..., 0, 0, 0]), 'dJxx_dy_per_native_px': stats(Hess[..., 0, 0, 1]),
       'Hessian_mixed_partial_disagreement': float(abs(Hess[..., :, 0, 1]-Hess[..., :, 1, 0]).max()),
       'analytic_Jacobian_spatial_difference_convergence': convergence,
       'known_d_right_stem_band_output': [1100, 445, 1116, 526],
       'stem_band_intersect_fixed_d_crop_width_factor': stats(horizontal_stem[stem]),
       'ordinary_source_sigma_native_px': 11., 'post_sigma_native_px': 1.25,
       'old_core13_support_width': .30,
       'old_core13_saturated_entire_d_crop': bool(np.all(flags['depth'] > .30)),
       'tangential_band_inactive_entire_d_crop': bool(np.all(flags['depth'] > case_recipe['parameters']['tangent_band'])),
       'limits': '1/Jxx maps the local NORMAL WIDTH of an intrinsically vertical source stem across a horizontal output scan; Jyy/det is inverse-map x response at fixed sourceY, a different metric. Full font contour/PSF and compression set apparent grayscale widths. Hessians are numerical spatial differences of analytic J, not rigorous global derivative bounds. Core undefined-normal branch retained/labeled, never removed from image scores.'}
write('d-geometry.json', geo)

# Independently identified font model23 remains an unadopted source alternative.
fontalpha = np.load(root.parent/'agent-toolbar-A-typography/selected-proposed-lastline-opacity-A.npy')
audit = json.loads(Path('/tmp/agent-toolbar-input-audit.json').read_text())
co = np.asarray(audit['registration']['page_field']['background_coefficients'])
yy, xx = np.mgrid[438:536, 1090:1128]
px, py = (xx-960)/960, (yy-540)/540
paper = np.clip(np.stack([px**i*py**j for i in range(5) for j in range(5-i)], axis=-1)@co, 1e-12, 1)
old_ink = np.clip(np.mean(1-source[438:536, 1090:1128]/paper, axis=-1), 0, 1)
new_ink = fontalpha[438:536, 1090:1128]
widths = []
for name, opacity in [('accepted_source_recovered_ink', old_ink), ('unadopted_independent_font23_opacity', new_ink)]:
    for threshold in [.2, .35, .5, .65, .8]:
        for y0, y1 in [(445, 463), (470, 510), (510, 526)]:
            values = []
            censored = 0
            for iy in range(y0-438, y1-438):
                row = opacity[iy]
                runs = []
                active = row >= threshold
                starts = np.flatnonzero(np.diff(np.r_[False, active, False].astype(int)) == 1)
                ends = np.flatnonzero(np.diff(np.r_[False, active, False].astype(int)) == -1)
                for a, b in zip(starts, ends):
                    if b <= 0 or a >= row.size:
                        continue
                    left = float(a)
                    right = float(b-1)
                    if a > 0 and row[a] != row[a-1]:
                        left = a-1+(threshold-row[a-1])/(row[a]-row[a-1])
                    if b < len(row) and row[b-1] != row[b]:
                        right = b-1+(row[b-1]-threshold)/(row[b-1]-row[b])
                    runs.append((left+1090, right+1090))
                if runs:
                    a, b = max(runs, key=lambda r: r[1])
                    censored += int(a <= 1090 or b >= 1127)
                    values.append(b-a)
            widths.append({'source': name, 'threshold': threshold, 'source_y_band': [y0, y1],
                           'rows_with_run': len(values), 'intrinsic_threshold_width_native_px': stats(np.asarray(values)) if values else None})
            widths[-1]['rows_censored_by_fixed_x_band'] = censored
write('source-stem-widths.json', {'rows': widths,
    'same_registered_known_d_only': True, 'source23_adopted': False,
    'limits': 'Diagnostic widths in source-opacity field only, no new font fit/source registration/render. Accepted ink recovered algebraically from fixed source/paper recipe. Font23 has a single independently fitted PSF, but neither field supplies exact original hidden-source RGB or per-position PSF. Threshold changes and rounded bowl/stem junction alter apparent width; no optical magnification estimated from these thresholds.'})
print('COMPLETE36', json.dumps(geo), flush=True)
