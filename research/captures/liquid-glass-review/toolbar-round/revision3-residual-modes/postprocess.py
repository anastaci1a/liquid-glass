"""Reproduce36 saved-grid supplemental geometry/projection summaries only."""
import json
from pathlib import Path
import numpy as np
from toolbar_scattering_covariance import transport_jacobian

r = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-residual-modes')
p = json.loads(Path('/tmp/agent-toolbar-code/accepted-toolbar-revision3.json').read_text())
z = np.load(r/'d-map-derivatives.npz')
yy, xx = np.mgrid[450:550, 960:1120]
x, y = (xx-960)/170, (yy-542)/170
fine, h = z['Hessian'], .125
coarse = np.stack([(transport_jacobian(x+h/170, y, p)[0]-transport_jacobian(x-h/170, y, p)[0])/(2*h),
                   (transport_jacobian(x, y+h/170, p)[0]-transport_jacobian(x, y-h/170, p)[0])/(2*h)], axis=-1)
err = np.max(abs(fine-coarse), axis=(-3, -2, -1))
ind = np.unravel_index(np.argmax(err), err.shape)
stem = (xx >= 1100)&(xx <= 1115)&(yy >= 450)&(yy <= 525)
upperstem = stem&(yy < 463)
numeric = {'purpose': 'Investigate nonuniform Hessian convergence noticed in36, not new optical/native derivative probes',
           'global_max_change_location_xy': [int(xx[ind]), int(yy[ind])],
           'global_max_change': float(err[ind]), 'depth_at_global_max': float(z['depth'][ind]),
           'undefined_branch_at_global_max': bool(z['undefined_branch'][ind]),
           'stem_band_max_Hessian_change': float(err[stem].max()),
           'upper_stem_max_Hessian_change': float(err[upperstem].max()),
           'stem_Jxx_y_Hessian_max_abs_perpx': float(abs(fine[..., 0, 0, 1][stem]).max()),
           'upper_stem_Jxx_y_Hessian_max_abs_perpx': float(abs(fine[..., 0, 0, 1][upperstem]).max()),
           'limits': 'Global max does NOT converge monotonically near inherited deep-core branch. Do not claim uniform/global Hessian accuracy or rigorous bound. Actual stem-domain convergence is separately measured; no score pixels removed or epoch changed.'}
J, H = z['J'], z['Hessian']
slope = -J[..., 0, 1]/J[..., 0, 0]
curve = -(H[..., 0, 0, 0]*slope*slope+2*H[..., 0, 0, 1]*slope+H[..., 0, 1, 1])/J[..., 0, 0]
width = -(H[..., 0, 0, 0]*slope+H[..., 0, 0, 1])/J[..., 0, 0]**2
def stats(a):
    return {'min': float(a.min()), 'median': float(np.median(a)), 'max': float(a.max()),
            'p01_p99': np.quantile(a, [.01, .99]).tolist()}
edges = {'implicit_source_vertical_edge_output_slope_dxdy': stats(slope[stem]),
         'implicit_source_vertical_edge_x_second_derivative_per_native_px': stats(curve[stem]),
         'horizontal_width_factor_derivative_along_edge_per_native_px': stats(width[stem]),
         'formulas': {'slope': 'q=-Jxy/Jxx', 'curvature': 'x_second=-(Fxx*q*q+2*Fxy*q+Fyy)/Jxx',
                      'width_derivative': 'd(1/Jxx)/dy_along_edge=-(Fxx*q+Fxy)/(Jxx^2)'},
         'limits': 'Evaluated on fixed registered d stem band, not a newly fitted/inverted glyph edge. Assumes intrinsically vertical source edge and geometric width, omits font contour/PSF/contrast. Numerical Hessian convergence verified on stem band, not globally near core.'}
assessment = json.loads((r.parent/'agent-toolbar-revision3-normal-rank/assessment.json').read_text())
projection = []
for row in assessment['rows']:
    if row['derivative'] != 'original_native_central_h002':
        continue
    G, g, loss = np.array(row['all7']['gram']), np.array(row['residual_gradient']), row['loss_at_this_diagnostic_weighting']
    value = float(g@np.linalg.solve(G, g)/4)
    projection.append({'cohort': row['cohort'], 'normal7_unbounded_local_projection_energy_fraction': value/loss,
                       'local_projected_loss_decrease': value, 'loss': loss, 'not_global_native_fit_bound': True})
for name, value in [('hessian-numerical-review.json', numeric), ('d-stem-edge-geometry.json', edges),
                    ('weighted-normal-projection.json', projection)]:
    (r/name).write_text(json.dumps(value, indent=2)+'\n')
