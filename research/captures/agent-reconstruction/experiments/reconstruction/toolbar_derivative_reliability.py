"""Queue33: native finite-step diagnostics, never an optical fit or sampler change.

The full-fraction source gradient is a SURROGATE for the quantized lookup.
Native cv2.remap alone supplies actual directional responses. No optimizer.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.interpolate import BSpline

import toolbar_candidate as model
from toolbar_sampling_precision import bilinear, quantized_coordinates


STEPS = (0.000125, 0.0005, 0.002)


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--recipe', required=True)
    args = parser.parse_args()
    cv2.setNumThreads(1)
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    p = json.loads(Path(args.recipe).read_text())
    pkg = Path('/tmp/agent-toolbar-evidence-package')
    source = np.asarray(Image.open(pkg/'inputs/source.png'), float)/255
    for filename, digest in p['source_sha256'].items():
        assert hashlib.sha256((pkg/'inputs'/filename).read_bytes()).hexdigest() == digest
    case = p['case']
    L = min(case['half'])
    x0, y0, x1, y1 = case['crop']
    H, W = y1-y0, x1-x0
    co = np.asarray(p['material'])
    gamma = p['intensity_response']['gamma']
    assert gamma == 1.0456395525912732
    original = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/first-proposal')
    reference = np.load(original/'material.npy')
    alpha = np.load(original/'alpha.npy')
    old_recipe = json.loads((original/'recipe.json').read_text())
    assert old_recipe == p
    atlasroot = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-covariance/native-atlas')
    atlas = {k: np.load(atlasroot/f'{k}.npy', mmap_mode='r') for k in ['sx', 'sy', 'inside']}
    blur = cv2.GaussianBlur(source, (0, 0), p['source_sigma']*L)
    cases = [(k, h, sign) for k in range(7) for h in STEPS for sign in [-1, 1]]
    signature = hashlib.sha256(Path(__file__).read_bytes()+Path(args.recipe).read_bytes()).hexdigest()
    statepath = root/'progress.json'
    if statepath.exists():
        state = json.loads(statepath.read_text())
        assert state['signature'] == signature
        if state.get('complete'):
            print('COMPLETE33 existing immutable result; no rerun', flush=True)
            return
        start = state['next_top']
    else:
        state = {'signature': signature, 'next_top': 0, 'complete': False,
                 'cases': cases, 'native_fits': 0, 'new_optical_passes': 0}
        start = 0
        write(statepath, state)
    def cached(name, shape):
        path = root/f'{name}.npy'
        return np.lib.format.open_memmap(path, mode='r+' if path.exists() else 'w+',
                                       dtype=np.float32, shape=shape)
    native = cached('native-raw', (len(cases)+1, H, W, 3))
    derivative = cached('surrogate-raw', (7, H, W, 3))
    # Deterministic source-only sample: all cohorts represented, no target selection.
    cohorts = np.load('/tmp/agent-toolbar-revision2-identifiability/support-cohorts.npz')
    eligible = np.flatnonzero(atlas['inside'])
    sampled = eligible[np.linspace(0, len(eligible)-1, 32768, dtype=int)]
    sample_y, sample_x = np.unravel_index(sampled, atlas['inside'].shape)
    sample_path = root/'ray-diagnostics.npz'
    if sample_path.exists():
        saved = dict(np.load(sample_path))
    else:
        saved = {'indices': sampled, 'sx': np.full(len(sampled), np.nan),
                 'sy': np.full(len(sampled), np.nan),
                 'jacobian': np.full((len(sampled), 7, 2), np.nan),
                 'cohort_observed': cohorts['observed_kernel_proxy'][sample_y//4, sample_x//4],
                 'cohort_estimated': cohorts['estimated_kernel_proxy'][sample_y//4, sample_x//4]}
    for top in range(start, H, 8):
        bot = min(top+8, H)
        yy, xx = np.mgrid[top*4:bot*4, :W*4]
        x = (x0+(xx+.5)/4-.5-case['center'][0])/L
        y = (y0+(yy+.5)/4-.5-case['center'][1])/L
        sd, nx, ny = model.boundary(x, y, p)
        inside = sd <= 0
        assert np.array_equal(inside, atlas['inside'][top*4:bot*4].astype(bool))
        basis = BSpline.design_matrix(np.clip(-sd/p['shape']['radius'], 0, 1).ravel(), model.KNOTS, 3).toarray()[:, :7].reshape((*x.shape, 7))
        # Shape is frozen. Normal-map coefficient dependence is exactly affine.
        dx = -L*min(p['shape']['half'])*basis*nx[..., None]*inside[..., None]
        dy = -L*min(p['shape']['half'])*basis*ny[..., None]*inside[..., None]
        sx64 = atlas['sx'][top*4:bot*4]
        sy64 = atlas['sy'][top*4:bot*4]
        sx, sy = sx64.astype(np.float32), sy64.astype(np.float32)
        u = np.clip(-sd/p['blur_transition'], 0, 1)
        mix = (u**3*(u*(6*u-15)+10))[..., None]
        light = model.lighting(x, y, p)
        core = light[..., -1, None]
        gain = (1-core)*co[:3]+core*co[-3:]
        offset = co[3:6]+(light[..., :-1]@co[6:-3])[..., None]
        sh = (bot-top, 4, W, 4)
        weight = inside.reshape(sh).sum((1, 3))
        assert np.array_equal(weight/16, alpha[top:bot])
        def reduce(C):
            return (C*inside[..., None]).reshape((*sh, 3)).sum((1, 3))/np.maximum(weight, 1)[..., None]
        def sample(sx, sy):
            clear = cv2.remap(source, sx, sy, cv2.INTER_LINEAR)
            blurred = cv2.remap(blur, sx, sy, cv2.INTER_LINEAR)
            return clear+(blurred-clear)*mix
        C = sample(sx, sy)
        # Multiplication/addition order matches render.shade for exact zero control.
        value = np.maximum(C, 0)**gamma
        raw = value*gain+co[3:6]+(light[..., :-1]@co[6:-3])[..., None]
        native[0, top:bot] = reduce(np.clip(raw, 0, 1))
        _, gx0, gy0 = bilinear(source, sx, sy, gradient=True)
        _, gx1, gy1 = bilinear(blur, sx, sy, gradient=True)
        gx = gx0+(gx1-gx0)*mix
        gy = gy0+(gy1-gy0)*mix
        # Surrogate uses native mixed intensity for current response/clip factors.
        factor = gamma*np.maximum(C, 0)**(gamma-1)*gain*((raw > 0)&(raw < 1))
        for k in range(7):
            derivative[k, top:bot] = reduce((gx*dx[..., k, None]+gy*dy[..., k, None])*factor)
        for i, (k, h, sign) in enumerate(cases, 1):
            a = (sx64+sign*h*dx[..., k]).astype(np.float32)
            b = (sy64+sign*h*dy[..., k]).astype(np.float32)
            Q = np.maximum(sample(a, b), 0)**gamma
            # Existing shade ordering, no material reoptimization.
            shaded = np.clip(Q*gain+co[3:6]+(light[..., :-1]@co[6:-3])[..., None], 0, 1)
            native[i, top:bot] = reduce(shaded)
        take = (sample_y >= top*4)&(sample_y < bot*4)
        iy, ix = sample_y[take]-top*4, sample_x[take]
        saved['sx'][take] = sx64[iy, ix]
        saved['sy'][take] = sy64[iy, ix]
        saved['jacobian'][take, :, 0] = dx[iy, ix]
        saved['jacobian'][take, :, 1] = dy[iy, ix]
        native.flush()
        derivative.flush()
        np.savez(sample_path, **saved)
        state['next_top'] = bot
        write(statepath, state)
        print('STRIP33', bot, H, flush=True)
    sigma = p['post_sigma']*L
    denominator = np.maximum(cv2.GaussianBlur(alpha, (0, 0), sigma), 1e-12)
    def post(C):
        return cv2.GaussianBlur(C*alpha[..., None], (0, 0), sigma)/denominator[..., None]
    zero = post(native[0])
    difference = float(abs(zero-reference).max())
    write(root/'zero-control.json', {'material_max_difference': difference, 'exact': difference == 0,
                                   'accepted_revision': 3, 'gamma': gamma})
    assert difference == 0, 'Native zero path must match accepted revision3 EXACTLY'
    D = np.stack([post(d) for d in derivative])
    np.save(root/'surrogate.npy', D)
    # The source coordinate map is algebraically affine in these fixed coefficients.
    # Float64 reassociation can still alter ties; verify representative direct maps.
    iy, ix = sample_y[:4096], sample_x[:4096]
    x = (x0+(ix+.5)/4-.5-case['center'][0])/L
    y = (y0+(iy+.5)/4-.5-case['center'][1])/L
    import copy
    coordinate_checks = []
    for k in range(7):
        for sign in [-1, 1]:
            q = copy.deepcopy(p)
            q['parameters']['coefficients'][k] += sign*STEPS[-1]
            X, Y = model.mapping(x, y, q)
            a = (saved['sx'][:4096]+sign*STEPS[-1]*saved['jacobian'][:4096, k, 0]).astype(np.float32)
            b = (saved['sy'][:4096]+sign*STEPS[-1]*saved['jacobian'][:4096, k, 1]).astype(np.float32)
            coordinate_checks.append({'coefficient': k, 'sign': sign,
                                      'float32_map_exact': bool(np.array_equal(a, (X*L+case['center'][0]).astype(np.float32)) and np.array_equal(b, (Y*L+case['center'][1]).astype(np.float32)))})
    write(root/'map-coordinate-controls.json', coordinate_checks)
    assert all(r['float32_map_exact'] for r in coordinate_checks)
    masks = np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
    target = np.asarray(Image.open(pkg/'inputs/target.png'), np.float32)[y0:y1, x0:x1]/255
    B = source[y0:y1, x0:x1]
    shadow = model.gaussian_coverage_shadow(case, p)
    foreground = np.load(pkg/'derived-foreground.npz')
    fg_transmission = np.ones((H, W, 1))
    def complete(C):
        full = C*alpha[..., None]+B*(1-shadow[..., None])*(1-alpha[..., None])
        for layer in p['foreground_layers']:
            a = foreground[layer['name']][..., None]
            full = full*(1-a)+np.asarray(layer['color'])*a
        return full
    for layer in p['foreground_layers']:
        fg_transmission *= 1-foreground[layer['name']][..., None]
    whole = complete(zero)
    fullD = D*alpha[None, ..., None]*fg_transmission[None]
    def score(C):
        out = {}
        for name in ['glass', 'rim']:
            out[name] = float(np.sqrt(np.mean(((C-target)[masks[name]]*255)**2)))
        full = complete(C)
        out['exterior'] = float(np.sqrt(np.mean(((full-target)[masks['exterior']]*255)**2)))
        for layer in p['foreground_layers']:
            a, b, c, d = layer['box']
            out[layer['name']] = float(np.sqrt(np.mean(((full-target)[b-y0:d-y0, a-x0:c-x0]*255)**2)))
        out['E'] = float(np.sqrt(.7*out['glass']**2+.3*out['rim']**2))
        return out
    baseline_scores = score(zero)
    def derivative_scores(C, DC, full, DF):
        out = {}
        for name in ['glass', 'rim']:
            out[name] = float(np.mean((C-target)[masks[name]]*DC[masks[name]])*255**2/baseline_scores[name])
        out['exterior'] = float(np.mean((full-target)[masks['exterior']]*DF[masks['exterior']])*255**2/baseline_scores['exterior'])
        for layer in p['foreground_layers']:
            a, b, c, d = layer['box']
            sl = (slice(b-y0, d-y0), slice(a-x0, c-x0))
            out[layer['name']] = float(np.mean((full-target)[sl]*DF[sl])*255**2/baseline_scores[layer['name']])
        out['E'] = (.7*baseline_scores['glass']*out['glass']+.3*baseline_scores['rim']*out['rim'])/baseline_scores['E']
        return out
    coordinate_rows, rows = [], []
    sx = saved['sx'].astype(np.float32).reshape(-1, 1)
    sy = saved['sy'].astype(np.float32).reshape(-1, 1)
    qx, qy = quantized_coordinates(sx, sy)
    for k in range(7):
        predicted_scores = derivative_scores(zero, D[k], whole, fullD[k])
        for h in STEPS:
            index = cases.index((k, h, -1))+1
            minus, plus = post(native[index]), post(native[index+1])
            actual = (plus-minus)/(2*h)
            row = {'coefficient': k, 'step': h, 'surrogate_guard_derivatives': predicted_scores,
                   'minus_original_native': score(minus), 'plus_original_native': score(plus), 'cohorts': {}}
            for name in ['all', 'observed_kernel_proxy', 'estimated_kernel_proxy', 'mixed_or_uncertain']:
                mm = cohorts[name]
                a, b = actual[mm].ravel().astype(float), D[k][mm].ravel().astype(float)
                denominator_norm = np.linalg.norm(a)*np.linalg.norm(b)
                row['cohorts'][name] = {'pixels': int(mm.sum()), 'actual_central_RMS_255_per_coefficient': float(np.sqrt(np.mean(a*a))*255),
                                        'surrogate_RMS_255_per_coefficient': float(np.sqrt(np.mean(b*b))*255),
                                        'cosine': float(a@b/denominator_norm) if denominator_norm else None,
                                        'relative_RMS_error': float(np.linalg.norm(a-b)/np.linalg.norm(a)) if np.linalg.norm(a) else None,
                                        'forward_vs_backward_relative_RMS': float(np.linalg.norm((plus-zero)[mm]-(zero-minus)[mm])/max(np.linalg.norm((plus-minus)[mm])/2, 1e-30))}
            row['actual_central_guard_derivatives'] = {name: (row['plus_original_native'][name]-row['minus_original_native'][name])/(2*h) for name in baseline_scores}
            rows.append(row)
            delta = saved['jacobian'][:, k]*h
            moved = np.stack([saved['sx'], saved['sy']], axis=-1)+delta
            a, b = moved[:, 0].astype(np.float32)[:, None], moved[:, 1].astype(np.float32)[:, None]
            ax, by = quantized_coordinates(a, b)
            active = np.linalg.norm(saved['jacobian'][:, k], axis=1) > 0
            cr = {'coefficient': k, 'step': h, 'active_rays': int(active.sum()), 'all_rays': len(active),
                  'displacement_native_px_quantiles': np.quantile(np.linalg.norm(delta[active], axis=1), [0, .5, .9, .99, 1]).tolist(),
                  'integer_cell_crossing_fraction_active': float(np.mean(((np.floor(a[:, 0]) != np.floor(sx[:, 0])) | (np.floor(b[:, 0]) != np.floor(sy[:, 0])))[active])),
                  'table_cell_crossing_fraction_active': float(np.mean(((ax[:, 0] != qx[:, 0]) | (by[:, 0] != qy[:, 0]))[active]))}
            coordinate_rows.append(cr)
            write(root/'directional-comparison.json', {'complete': False, 'baseline_scores': baseline_scores, 'rows': rows})
    write(root/'coordinate-steps.json', coordinate_rows)
    write(root/'directional-comparison.json', {'complete': True, 'accepted_revision': 3, 'baseline_scores': baseline_scores,
                                            'rows': rows, 'new_native_evaluations': 43, 'new_native_fits': 0,
                                            'limitations': 'Full-fraction gradients are a surrogate, NOT derivatives of cv2 table lookup. Native coefficient perturbations are reliability diagnostics, NOT proposed/accepted fits. Source proxy cohorts are not truth. No source, sampler, epoch or accepted count change.'})
    state['complete'] = True
    write(statepath, state)
    print('COMPLETE33', baseline_scores, flush=True)


if __name__ == '__main__':
    main()
