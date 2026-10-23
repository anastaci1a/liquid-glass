"""Geometric exact-support audit; no source/target sampling or optical render."""
import json
from pathlib import Path
import cv2
import numpy as np
from scipy.interpolate import BSpline
import toolbar_candidate as model

cv2.setNumThreads(1)
root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-normal-rank')
p = json.loads(Path('/tmp/agent-toolbar-code/accepted-toolbar-revision3.json').read_text())
case = p['case']
x0, y0, x1, y1 = case['crop']
H, W, L = y1-y0, x1-x0, min(case['half'])
support = np.zeros((7, H, W), bool)
for top in range(0, H, 8):
    bot = min(top+8, H)
    yy, xx = np.mgrid[top*4:bot*4, :W*4]
    x = (x0+(xx+.5)/4-.5-case['center'][0])/L
    y = (y0+(yy+.5)/4-.5-case['center'][1])/L
    sd, _, _ = model.boundary(x, y, p)
    b = BSpline.design_matrix(np.clip(-sd/p['shape']['radius'], 0, 1).ravel(), model.KNOTS, 3).toarray()[:, :7].reshape((*x.shape, 7))
    active = (b != 0)&(sd[..., None] <= 0)
    for k in range(7):
        support[k, top:bot] = active[..., k].reshape(bot-top, 4, W, 4).any((1, 3))
impulse = np.zeros((65, 65), np.float32)
impulse[32, 32] = 1
kernel = cv2.GaussianBlur(impulse, (0, 0), p['post_sigma']*L)
iy, ix = np.nonzero(kernel)
radius = int(max(abs(iy-32).max(), abs(ix-32).max()))
assert radius < 32
alpha = np.load('/evidence/extended/helper-toolbar-work/agent-toolbar-response-trials/first-proposal/alpha.npy')
masks = np.load('/tmp/agent-toolbar-run/frozen-masks.npz')
regions = {'exterior': masks['exterior']}
for layer in p['foreground_layers']:
    a, b, c, d = layer['box']
    mask = np.zeros((H, W), bool)
    mask[b-y0:d-y0, a-x0:c-x0] = True
    regions[layer['name']] = mask
rows = []
for k in range(7):
    # Square dilation conservatively includes all actual separable-kernel taps.
    expanded = cv2.dilate(support[k].astype(np.uint8), np.ones((2*radius+1, 2*radius+1), np.uint8)).astype(bool)&(alpha > 0)
    rows.append({'coefficient': k, 'raw_active_output_pixels': int(support[k].sum()),
                 'guard_potentially_affected_pixels': {name: int((expanded&mask).sum()) for name, mask in regions.items()},
                 'exact_disjoint_support_guards': [name for name, mask in regions.items() if not (expanded&mask).any()]})
result = {'gaussian_actual_impulse_nonzero_radius_native_px': radius,
          'sigma': p['post_sigma']*L, 'support': rows,
          'limits': 'Fixed discrete native grid/spline basis; conservative square postfilter support includes all actual Gaussian taps. Zero overlap proves unchanged complete color under coefficient changes with frozen geometry/material/coverage/glyph/shadow, independently of unknown source. Nonzero overlap does NOT establish a nonzero photometric derivative. No source or target sampled.'}
(root/'exact-support.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
