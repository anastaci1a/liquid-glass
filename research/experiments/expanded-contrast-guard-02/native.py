"""One actual cached-sample pair, gated by saved-form feasibility."""
from pathlib import Path
import datetime
import hashlib
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from extended_fit import Study
from geometric_render import neutral_color_response

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SPLINE = ROOT / 'research/experiments/expanded-spline-observation-01'
BASE = ROOT / 'research/experiments/expanded-geometry-02'
WORK = ROOT / '.evidence-working/expanded-geometry-02'
p = json.loads((OUT / 'protocol.json').read_text())
deadline = datetime.datetime.fromisoformat(p['deadline_utc'].replace('Z', '+00:00'))
fit = json.loads((OUT / 'feasibility.json').read_text())
assert fit['best'] is not None and fit['best']['strictly_model_feasible']
assert json.loads((SPLINE / 'source-preflight.json').read_text())['status'] == 'PASS'
assert not (OUT / 'native-start.json').exists(), 'One native attempt only'
(OUT / 'native-start.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat())) + '\n')
delta = np.asarray(fit['best']['delta'])
g0 = p['parameters']['original_gain']; b0 = p['parameters']['original_bias']
g, b = g0 + delta[0], b0 + delta[1]
cv2.setNumThreads(1)
inside = np.load(SPLINE / 'native-paths.npz')['inside']
rows = []; identities = 0; candidates = 0

def gate():
    assert datetime.datetime.now(datetime.timezone.utc) < deadline, 'Original deadline'

def integrate(raw, gain, bias, H, W):
    response, preclip = neutral_color_response(raw, gain=gain, bias=bias, return_preclip=True)
    values = np.where(inside[..., None], response, raw)
    pre = values.reshape(H, 2, W, 2, 3).mean((1, 3)).astype(np.float32)
    return pre, preclip

def scores(s, C, masks):
    z = s.scores(C); z['E'] = float(np.sqrt(z['loss']))
    err = (C - s.target_crop) * 255
    z['exterior_RMSE'] = float(np.sqrt(np.mean(err[masks['exterior']] ** 2)))
    z['foreground_artwork_MSE'] = {}
    x0, y0, _, _ = s.crop
    for layer in s.case['foreground_layers']:
        a, bb, c, d = layer['box']
        tile = err[bb-y0:d-y0, a-x0:c-x0]
        assert np.isfinite(tile).all()
        name = layer.get('style_key', layer.get('vector_asset', layer.get('artwork_asset')))
        z['foreground_artwork_MSE'][name] = float(np.mean(tile * tile))
    return z

for key in ['a', 'b']:
    gate()
    s = Study(WORK / key)
    assert not s.transmission_layers and not s.case.get('foreground_styles')
    z = np.load(SPLINE / f'{key}-candidate.npz')
    old = np.load(BASE / f'h1-{key}.npz')['complete']
    masks = np.load(WORK / f'{key}-masks.npz')
    raw = z['sample_before_response']; H, W = s.valid.shape
    pre0, _ = integrate(raw, g0, b0, H, W)
    np.testing.assert_array_equal(pre0, z['pre_foreground'])
    zero = s.apply_foreground(pre0.copy()); identities += 1
    np.testing.assert_array_equal(zero, z['complete'])
    gate()
    pre, preclip = integrate(raw, g, b, H, W)
    assert np.isfinite(preclip[inside]).all()
    clips = [int((preclip[inside] < 0).sum()), int((preclip[inside] > 1).sum())]
    assert clips == [0, 0]
    C = s.apply_foreground(pre.copy()); candidates += 1
    now, before = scores(s, C, masks), scores(s, old, masks)
    guards = {name: now[name]['rmse'] <= before[name]['rmse'] for name in ['glass', 'rim', 'held', 'interior']}
    guards.update(E=now['E'] <= before['E'], ssim=now['ssim'] >= before['ssim'],
                  exterior=now['exterior_RMSE'] <= before['exterior_RMSE'])
    guards.update({name: value <= before['foreground_artwork_MSE'][name]
                   for name, value in now['foreground_artwork_MSE'].items()})
    cohorts = {name: masks[name] for name in ['glass', 'rim', 'held', 'exterior']}
    cohorts['interior'] = masks['glass'] & ~masks['rim']
    x0, y0, _, _ = s.crop
    for layer in s.case['foreground_layers']:
        a, bb, c, d = layer['box']; mask = np.zeros((H, W), bool)
        mask[bb-y0:d-y0, a-x0:c-x0] = True
        cohorts[layer.get('style_key', layer.get('vector_asset', layer.get('artwork_asset')))] = mask
    err = (C.astype(float) - s.target_crop.astype(float)) * 255
    olderr = (old.astype(float) - s.target_crop.astype(float)) * 255
    double = {name: bool(np.mean(err[mask] ** 2) <= np.mean(olderr[mask] ** 2))
              for name, mask in cohorts.items()}
    partial = masks['glass'] & (z['coverage'] < 1)
    partial_review = dict(pixels=int(partial.sum()),
        baseline_RMSE=float(np.sqrt(np.mean(olderr[partial] ** 2))),
        candidate_RMSE=float(np.sqrt(np.mean(err[partial] ** 2))),
        scope='Advisory local disclosure; no new post hoc guard or mask change.')
    np.savez_compressed(OUT / f'{key}-candidate.npz', pre_foreground=pre, complete=C, coverage=z['coverage'])
    valid = np.isfinite(C).all(2); yy, xx = np.indices(valid.shape)
    view = np.where(valid[..., None], C, np.where(((xx//6 + yy//6) % 2)[..., None], .72, .9))
    width = 1080; height = round(H * width / W)
    canvas = Image.new('RGB', (2*width + 2, height + 64), 'white')
    canvas.paste(Image.fromarray(np.uint8(np.rint(s.target_crop * 255))).resize((width, height), Image.Resampling.LANCZOS), (0, 64))
    canvas.paste(Image.fromarray(np.uint8(np.rint(np.clip(view, 0, 1)*255))).resize((width, height), Image.Resampling.LANCZOS), (width+2, 64))
    draw = ImageDraw.Draw(canvas); font = ImageFont.load_default(size=18)
    draw.text((12, 20), 'Apple reference', fill='black', font=font)
    draw.text((width+14, 20), 'Fixed spline; one shared contrast response', fill='black', font=font)
    canvas.save(OUT / f'{key}-comparison.png')
    row = dict(reference=key, scores=now, baseline_scores=before,
        original_guards=guards, float64_residual_guards=double,
        partial_boundary_advisory=partial_review, identity_exact=True,
        clip_counts=clips, preclip_range=[float(preclip[inside].min()), float(preclip[inside].max())],
        all_pass=all(guards.values()) and all(double.values()))
    rows.append(row)
    (OUT / f'{key}-measurement.json').write_text(json.dumps(row, indent=2, allow_nan=False) + '\n')
    print(json.dumps(row), flush=True)
    gate()

inputs = [SPLINE / 'native-paths.npz', SPLINE / 'source-preflight.json',
          SPLINE / 'a-candidate.npz', SPLINE / 'b-candidate.npz']
result = dict(status='STRICT_PAIRED_NUMERIC_CANDIDATE' if all(r['all_pass'] for r in rows) else 'REJECTED_NATIVE_PAIR',
    finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    gain=float(g), bias=float(b), delta=delta.tolist(), records=rows,
    identity_composites=identities, candidate_composites=candidates,
    rays=0, height_calls=0, source_queries=0, optical_filters=0,
    inputs=[dict(path=str(f.relative_to(ROOT)), sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in inputs])
(OUT / 'native-result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
print(result['status'], flush=True)
