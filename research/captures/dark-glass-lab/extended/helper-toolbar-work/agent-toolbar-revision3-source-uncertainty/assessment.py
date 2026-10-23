"""Queue37: held-out measured mismatch, NOT a hidden-source confidence interval."""
import json
from pathlib import Path
import numpy as np

root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-source-uncertainty')
root.mkdir(exist_ok=True)
fontroot = root.parent/'agent-toolbar-A-typography'
report = json.loads((fontroot/'feasibility.json').read_text())
selected = report['selected']
observed = np.load(fontroot/'observed-opacity.npz')['ink']
predicted = np.load(fontroot/'0-predicted-lastline-opacity.npy')
assert report['selected_by_TRAIN_only_index'] == 0
protocol = json.loads((fontroot/'protocol.json').read_text())
a, b, c, d = protocol['geometry_boxes']['heldout_world_around_us']['box']
P, O = predicted[b:d, a:c].astype(float), observed[b:d, a:c].astype(float)
error = P-O
gy, gx = np.gradient(predicted.astype(float))
gx, gy = gx[b:d, a:c], gy[b:d, a:c]
slope = np.hypot(gx, gy)
edge = (P >= .2)&(P <= .8)&(slope >= .05)
vertical = edge&(abs(gx) >= 2*abs(gy))
horizontal = edge&(abs(gy) >= 2*abs(gx))
yy, xx = np.mgrid[b:d, a:c]
# Exact inherited720->A similarity, used for coordinate labels only; no new registration.
M = np.array([[.9578697054607762, .00018082755364204328, 40.514486622923656],
              [-.00018082755364204328, .9578697054607762, 210.46202215716735]])
ax = M[0, 0]*xx+M[0, 1]*yy+M[0, 2]
ay = M[1, 0]*xx+M[1, 1]*yy+M[1, 2]
scale = float(np.hypot(M[0, 0], M[1, 0]))
upperstem = vertical&(ax >= 1100)&(ax <= 1118)&(ay >= 445)&(ay <= 463)


def stats(v):
    return {'n': int(v.size), 'mean': float(np.mean(v)), 'median': float(np.median(v)),
            'RMS': float(np.sqrt(np.mean(v*v))),
            'absolute_p50_p90_p95_p99': np.quantile(abs(v), [.5, .9, .95, .99]).tolist()}


rows = []
for name, mask in [('all_heldout', np.ones(P.shape, bool)), ('all_edges', edge),
                   ('vertical_source_edges', vertical), ('horizontal_source_edges', horizontal),
                   ('known_d_upper_vertical_stem', upperstem)]:
    row = {'region': name, 'opacity_mismatch': stats(error[mask])}
    if name != 'all_heldout':
        equiv = error[mask]/slope[mask]
        row['slope_opacity_per_raw720_px'] = stats(slope[mask])
        row['signed_edge_equivalent_mismatch_raw720_px_NOT_observed_displacement'] = stats(equiv)
        row['signed_edge_equivalent_mismatch_registeredA_px_NOT_confidence_interval'] = stats(equiv*scale)
    rows.append(row)
blocks = []
for top in range(0, P.shape[0], 16):
    for left in range(0, P.shape[1], 16):
        sl = (slice(top, top+16), slice(left, left+16))
        m = vertical[sl]
        if m.sum() < 4:
            continue
        v = error[sl][m]/slope[sl][m]*scale
        blocks.append({'raw720_block_origin': [a+left, b+top], 'pixels': int(m.sum()),
                       'mean_edge_equivalent_mismatch_A_px': float(v.mean()),
                       'RMS_edge_equivalent_mismatch_A_px': float(np.sqrt(np.mean(v*v)))})
write = lambda name, value: (root/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
write('heldout-edge-discrepancy.json', {'complete': True, 'rows': rows, 'vertical_edge_blocks16px': blocks,
    'original23_heldout_crop_render_opacity_RMSE': selected['heldout_world_run_opacity_RMSE'],
    'cached_full_line_heldout_opacity_RMSE': float(np.sqrt(np.mean(error*error))),
    'cache_full_line_vs_original_crop_boundary_difference_in_RMSE': float(np.sqrt(np.mean(error*error))-selected['heldout_world_run_opacity_RMSE']),
    'registration_scale': scale,
    'limits': 'Measured held-out mismatch on visible720 known text, conditional on the selected font/one global PSF/the-only pose. e/gradient is an edge-equivalent error diagnostic, NOT a measured displacement or random confidence interval. Correlated font/PSF/photometry/shape residuals do not average away as independent pixels. No unknown ink observed, no new fit/raster/registration.'})

widths = json.loads((root.parent/'agent-toolbar-revision3-residual-modes/source-stem-widths.json').read_text())['rows']
def width_row(name):
    return next(r for r in widths if r['source'] == name and r['threshold'] == .5 and r['source_y_band'] == [445, 463])
old, alternative = width_row('accepted_source_recovered_ink'), width_row('unadopted_independent_font23_opacity')
oldmedian = old['intrinsic_threshold_width_native_px']['median']
newmedian = alternative['intrinsic_threshold_width_native_px']['median']
geo = json.loads((root.parent/'agent-toolbar-revision3-residual-modes/d-geometry.json').read_text())
variation = geo['stem_band_intersect_fixed_d_crop_width_factor']['peak_to_peak']
predicted_change = oldmedian*variation
sigma_raw = selected['train_parameters'][3]
sigma_A = sigma_raw*scale
details = {'accepted_source_clean_upper_stem_median_width_px': oldmedian,
           'independent_UNADOPTED_font23_upper_stem_median_width_px': newmedian,
           'measured_model_difference_px_NOT_truth_uncertainty_interval': oldmedian-newmedian,
           'accepted_source_upper_stem_width_peak_to_peak_px': old['intrinsic_threshold_width_native_px']['peak_to_peak'],
           'current_map_stem_width_factor_peak_to_peak': variation,
           'current_map_implied_10px_stem_width_change_px': predicted_change,
           'model_difference_over_current_map_change': abs(oldmedian-newmedian)/predicted_change,
           'oldsource_stem_row_variation_over_current_map_change': old['intrinsic_threshold_width_native_px']['peak_to_peak']/predicted_change,
           'font23_intrinsic_PSF_sigma_raw720_px': sigma_raw,
           'font23_intrinsic_PSF_sigma_registeredA_px': sigma_A,
           'accepted_ordinary_blur_sigma_A_px': 11.,
           'gaussian_sigma_combination_if_independent_stationary_Gaussians': float(np.hypot(11, sigma_A)),
           'sigma_combination_is_assumption_not_recovered_LiquidGlass_PSF': True,
           'original_font_fit_termination': selected['train_message'],
           'original_font_fit_optimality': selected['train_optimality'],
           'original_fd_probe_steps_raw720_pose_scale_sigma_opacity': [.125, .125, .0008, .05, .004],
           'no_saved_parameter_covariance_or_registration_covariance': True,
           'numerical_probe_sizes_are_NOT_uncertainty_bounds': True,
           'relative_absolute_width_scale_precision_needed_to_resolve_current_map_variation': variation,
           'limits': 'A constant similarity maps straight lines to straight lines and common scale cancels relative width ratios; lack of registration covariance alone does not manufacture curvature. These registration precision numbers concern absolute widths/correspondence. Nonuniform font contour/PSF/photometry errors can affect width variation. Stronger optical curvature remains plausible, not identified in sign/amplitude by current data. Hidden-source uncertainty is unbounded by this visible-text scatter.'}
write('feature-uncertainty-budget.json', details)
print('COMPLETE37', json.dumps({'edge_regions': rows, 'budget': details}), flush=True)
