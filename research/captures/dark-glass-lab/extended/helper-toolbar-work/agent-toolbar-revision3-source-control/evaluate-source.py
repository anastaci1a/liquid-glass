"""ONE public-path accepted3/source23 native source control; never optical progress."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys

root = Path('/evidence/extended/helper-toolbar-work/agent-toolbar-revision3-source-control')
sys.path.insert(0, str(root/'public-code'))
import numpy as np
import cv2
from PIL import Image
from tensor_replay import composite
from progress_gate import error, evaluate

cv2.setNumThreads(1)
pkg = Path('/tmp/agent-toolbar-evidence-package')
inputs = root/'inputs'
inputs.mkdir(exist_ok=True)
oldrecipe = json.loads((root/'accepted-revision3-recipe.json').read_text())
verification = json.loads((root/'accepted-revision3-verification.json').read_text())
assert verification['gate']['accepted'] and verification['candidate']['observations']['A']['glass']['rmse'] == 5.796156406402588
source23 = root.parent/'agent-toolbar-A-typography/input-proposal/source-typography-proposed.png'
assert source23.exists()
newsha = '1b64c31b4e24273d753efe13b43ef60e0ae0ad860a0a78826cc02be5be55fd21'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(source23) == newsha
for name, sourcepath in [('source.png', source23), ('target.png', pkg/'inputs/target.png')]:
    destination = inputs/name
    if destination.exists():
        assert destination.read_bytes() == sourcepath.read_bytes()
    else:
        shutil.copy2(sourcepath, destination)
for layer in oldrecipe['foreground_layers']:
    sourcepath = pkg/'inputs'/layer['asset']
    assert sha(sourcepath) == layer['sha256']
    destination = inputs/layer['asset']
    if destination.exists():
        assert sha(destination) == layer['sha256']
    else:
        shutil.copy2(sourcepath, destination)
p = copy.deepcopy(oldrecipe)
p['source_sha256']['source.png'] = newsha
control = copy.deepcopy(p)
control['source_sha256'] = oldrecipe['source_sha256']
assert control == oldrecipe
assert p['source_sha256']['target.png'] == '5bb59714854d0bd019d689b3e8c444dd82b057d6abdc9275ca88a8295692bbf8'
for name, digest in p['source_sha256'].items():
    assert sha(inputs/name) == digest
write = lambda path, value: path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
write(root/'source-control-recipe.json', p)
maskpath = Path('/tmp/agent-toolbar-run/frozen-masks.npz')
assert sha(maskpath) == 'da7d9dec1b557f91321e9ed5aaef5a4416371cbd5657b83e2ff6fccb86b0aa53'
source = np.asarray(Image.open(inputs/'source.png'), float)/255
target = np.asarray(Image.open(inputs/'target.png'), np.float32)/255
assert source.shape == target.shape == (1080, 1920, 3)
masks = np.load(maskpath)
codehash = {f.name: sha(f) for f in (root/'public-code').glob('*.py')}
signature = hashlib.sha256(json.dumps({'recipe': p, 'code': codehash, 'mask': sha(maskpath)}, sort_keys=True).encode()).hexdigest()
progresspath = root/'progress.json'
state = json.loads(progresspath.read_text()) if progresspath.exists() else {'signature': signature, 'render_attempts': 0, 'complete': False}
assert state['signature'] == signature
if state.get('complete'):
    print('COMPLETE41 immutable completed result; no rerender', flush=True)
    raise SystemExit(0)
saved = [root/f'{n}.npy' for n in ['complete', 'material', 'alpha']]
if all(f.exists() for f in saved):
    complete, material, alpha = [np.load(f) for f in saved]
elif state['render_attempts']:
    raise RuntimeError('A prior render was started; inspect partials before any recovery. No automatic duplicate.')
else:
    state['render_attempts'] = 1
    state['phase'] = 'public tensor_replay.composite→crowned_tensor.render native4xAA scale1'
    write(progresspath, state)
    print('BEGIN41 ONE public native source-control render', flush=True)
    complete, material, alpha = composite(source, p['case'], p, inputs, scale=1)
    for f, a in zip(saved, [complete, material, alpha]):
        np.save(f, a)
    state['phase'] = 'render_saved_before_scoring_or_epoch_gate'
    write(progresspath, state)

primary = Path('/evidence/extended/toolbar-response-primary-review')
old_material = np.load(primary/'material.npy')
old_complete = np.load(primary/'complete.npy')
old_alpha = np.load(primary/'alpha.npy')
assert np.array_equal(old_alpha, alpha)
case = p['case']
x0, y0, x1, y1 = case['crop']
T = target[y0:y1, x0:x1]


def measure(C, full):
    scores = {}
    for name in ['glass', 'rim']:
        d = (C-T)[masks[name]]*255
        scores[name] = {'rmse': float(np.sqrt(np.mean(d*d))), 'pixels': int(masks[name].sum())}
    scores['shadow'] = float(np.sqrt(np.mean(((full-T)[masks['exterior']]*255)**2)))
    foreground = {}
    for layer in p['foreground_layers']:
        a, b, c, d = layer['box']
        foreground[layer['name']] = float(np.sqrt(np.mean((full[b-y0:d-y0, a-x0:c-x0]-T[b-y0:d-y0, a-x0:c-x0])**2))*255)
    return scores, foreground


new, newfg = measure(material, complete)
old, oldfg = measure(old_material, old_complete)
assert old == verification['candidate']['observations']['A']
for name in oldfg:
    assert abs(oldfg[name]-verification['foreground'][name]['after']) < 1e-12
epoch = hashlib.sha256(json.dumps({'old_accepted_epoch': verification['epoch'], 'private_source_control_only': True,
                                   'inputs': p['source_sha256'], 'mask': sha(maskpath)}, sort_keys=True).encode()).hexdigest()
newstate = {'epoch': epoch, 'observations': {'A': new}}
try:
    unexpected = evaluate(verification['candidate'], newstate, visual_review=False, replay_verified=False, source_support_verified=False)
except ValueError as exc:
    cross_gate = {'accepted': False, 'expected_cross_input_epoch_refusal': True, 'reason': str(exc)}
else:
    raise RuntimeError('Cross-input gate MUST refuse mismatch: '+str(unexpected))
report = {'source_control_only': True, 'accepted_baseline_revision': 3,
          'original_accepted_epoch_UNCHANGED': verification['epoch'], 'private_input_control_digest_NOT_adopted_epoch': epoch,
          'new_source_sha256': newsha, 'only_recipe_change': 'source_sha256.source.png',
          'original_target_and_canonical_SVG_hashes_unchanged': True, 'mask_sha256': sha(maskpath), 'coverage_exact': True,
          'old3_primary_cached_scores': old, 'old3_primary_cached_foreground': oldfg, 'old3_E': error(old),
          'new_input_current3_scores': new, 'new_input_current3_foreground': newfg, 'new_input_current3_E': error(new),
          'cross_input_progress_gate': cross_gate, 'new_native_source_control_renders': 1, 'old3_rerenders': 0,
          'old2_rerenders': 0, 'new_native_fits': 0, 'new_HQ_replays': 0, 'new_source_adoptions': 0,
          'new_accepted_passes': 0, 'public_code_sha256': codehash,
          'limits': 'Independent font23input estimate, not recovered hiddenRGB/ink. Source-only response change is NOT optical gain. Original source/epoch/count3 stay fixed pending lead decision;4kdelivery40 NOT included.'}
write(root/'source-control-measurement.json', report)
Image.fromarray(np.uint8(np.rint(np.clip(complete, 0, 1)*255))).save(root/'native-source-control-preview.png')
state['complete'] = True
state['phase'] = 'complete_separate_source_control_no_adoption'
write(progresspath, state)
print('COMPLETE41', json.dumps({k: v for k, v in report.items() if k != 'public_code_sha256'}), flush=True)
