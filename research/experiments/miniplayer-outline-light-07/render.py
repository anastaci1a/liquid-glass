"""Two fixed, hypothetical scene lights; no edge matte or optical refit."""
from pathlib import Path
import sys, json, datetime, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'reconstruction'))
from extended_fit import Study
from geometric_render import neutral_color_response
from environment_radiance import certified_first_return, decode_srgb, encode_srgb

P = json.loads((OUT/'protocol.json').read_text())
END = datetime.datetime.fromisoformat(P['deadline'].replace('Z', '+00:00'))
F = json.loads((ROOT/'reconstruction/families/music-mini-player.json').read_text())
ledger = {k: 0 for k in P['caps']}

def save(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')

def gate():
    assert datetime.datetime.now(datetime.timezone.utc) < END, 'Original deadline'

def charge(key, amount):
    gate()
    assert ledger[key]+amount <= P['caps'][key], key
    ledger[key] += int(amount)
    save('ledger.json', ledger)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert not (OUT/'started.json').exists(), 'One declared run only'
save('started.json', {'at': datetime.datetime.now(datetime.timezone.utc).isoformat()})
bindings = [ROOT/'reconstruction/families/music-mini-player.json',
            ROOT/'reconstruction/environment_radiance.py', ROOT/'reconstruction/geometric_optics.py',
            ROOT/'research/experiments/expanded-first-return-certificate-05/result.json']
first = {str(p.relative_to(ROOT)): sha(p) for p in bindings}
save('first-hashes.json', first)

# Small algebraic controls: equal-index reflection is zero; on-axis emitter dark.
fixtures = np.array([[0., 0., -1.], [.1, 0., -1.], [0., .5, -1.], [.67, 0., -1.]])
fixtures /= np.linalg.norm(fixtures, axis=1)[:, None]
for index in [1., 1.5]:
    charge('reflected_direction_points', 4); charge('snell_interface_points', 4)
    charge('fresnel_interface_points', 9); charge('environment_direction_queries', 5)
    q = certified_first_return(fixtures, index)
    assert np.array_equal(q['unit_emitter_radiance'], np.zeros(4)) if index == 1 else q['unit_emitter_radiance'][0] == 0
    assert q['closure_max_error'] < 2e-14
assert np.max(abs(encode_srgb(decode_srgb(np.linspace(0, 1, 1001)))-np.linspace(0, 1, 1001))) < 1e-14

def score(s, C, masks, frozen_partial, crops):
    charge('score_calls', 1)
    z = s.scores(C); z['E'] = float(np.sqrt(z['loss']))
    err = (C-s.target_crop)*255
    z['exterior'] = float(np.sqrt(np.mean(err[masks['exterior']]**2)))
    z['partial'] = {'pixels': int(frozen_partial.sum()), 'RMSE': float(np.sqrt(np.mean(err[frozen_partial]**2)))}
    x0, y0, _, _ = s.crop
    z['foreground'] = {}
    for layer in s.case['foreground_layers']:
        a, b, c, d = layer['box']
        name = layer.get('style_key', layer.get('vector_asset', layer.get('artwork_asset')))
        tile = err[b-y0:d-y0, a-x0:c-x0]
        z['foreground'][name] = float(np.mean(tile**2))
    z['crops'] = {}
    for name, (a, b, c, d) in crops.items():
        tile = err[b-y0:d-y0, a-x0:c-x0]
        z['crops'][name] = {'RGB_RMSE': float(np.sqrt(np.mean(tile**2))),
                            'luma_signed': float(np.mean(tile @ np.array([.2126, .7152, .0722])))}
    return z

def display(C):
    good = np.isfinite(C).all(axis=-1)
    yy, xx = np.indices(good.shape)
    return np.where(good[..., None], C, np.where(((xx//6+yy//6)%2)[..., None], .72, .9))

def to_image(C):
    return Image.fromarray(np.uint8(np.rint(np.clip(display(C), 0, 1)*255)))

def images(prefix, s, baseline, candidate, crops, amplitude):
    H, W = s.valid.shape; width = min(W, 1080); height = round(H*width/W)
    canvas = Image.new('RGB', (2*width+2, height+64), 'white')
    draw = ImageDraw.Draw(canvas); font = ImageFont.load_default(size=17)
    for i, (v, label) in enumerate([(s.target_crop, 'Apple reference'), (candidate, f'Conditional first-return light; radiance {amplitude}')]):
        canvas.paste(to_image(v).resize((width, height), Image.Resampling.LANCZOS), (i*(width+2), 64))
        draw.text((i*(width+2)+8, 20), label, fill='black', font=font)
    canvas.save(OUT/f'{prefix}-comparison.png')
    x0, y0, _, _ = s.crop; rows = []; maxwidth = 0
    for name, (a, b, c, d) in crops.items():
        w, h = 2*(c-a), 2*(d-b)
        row = Image.new('RGB', (3*w+4, h+32), 'white'); draw = ImageDraw.Draw(row)
        for i, (v, label) in enumerate([(s.target_crop, 'Reference'), (baseline, 'Selected baseline'), (candidate, 'Conditional first return')]):
            cut = v[b-y0:d-y0, a-x0:c-x0]
            row.paste(to_image(cut).resize((w, h), Image.Resampling.NEAREST), (i*(w+2), 32))
            draw.text((i*(w+2)+3, 5), f'{name}: {label}', fill='black', font=font)
        rows.append(row); maxwidth = max(maxwidth, row.width)
    sheet = Image.new('RGB', (maxwidth, sum(row.height for row in rows)+8*(len(rows)-1)), 'white')
    y = 0
    for row in rows:
        sheet.paste(row, (0, y)); y += row.height+8
    sheet.save(OUT/f'{prefix}-crops.png')

records = []
for member in ['expanded', 'compact']:
    gate()
    if member == 'expanded':
        base = ROOT/'research/experiments/expanded-contrast-guard-02'
        rawbase = ROOT/'research/experiments/expanded-spline-observation-01'
        pathfile = rawbase/'native-paths.npz'
        work = ROOT/'.evidence-working/expanded-geometry-02'
        proof = rawbase/'source-preflight.json'
    else:
        base = rawbase = ROOT/'research/experiments/miniplayer-shared-transfer-06'
        pathfile = base/'compact-paths.npz'
        work = ROOT/'.evidence-working/compact-geometry-01'
        proof = base/'source-proof-FIRST.json'
    bindings += [pathfile, proof]
    assert json.loads(proof.read_text())['status'] in ['PASS', 'PASS_BOTH_BEFORE_RGB']
    q = np.load(pathfile); inside = q['inside']; normal = q['outward_normal'][inside]; N = len(normal)
    assert q['complete'][inside].all() and np.max(abs(np.linalg.norm(normal, axis=-1)-1)) < 1e-12
    # The same family certificate depends only on shared profile/minor/radius,
    # not major length; both footprints are convex offsets of inner rectangles.
    charge('reflected_direction_points', N); charge('snell_interface_points', N)
    charge('fresnel_interface_points', 2*N+1); charge('environment_direction_queries', N+1)
    branch = certified_first_return(normal, F['optics']['index'])
    back = q['back'][inside]; time_to_front = -back[:, 2]/branch['reflected_direction'][:, 2]
    assert (time_to_front > 0).all()
    front = back+time_to_front[:, None]*branch['reflected_direction']
    assert np.max(abs(front[:, 2])) < 1e-13
    np.savez_compressed(OUT/f'{member}-first-return.npz', **{k: v for k, v in branch.items() if isinstance(v, np.ndarray)}, front=front, back=back)
    save(f'{member}-branch.json', {'inside_points': N, 'closure_error': branch['closure_max_error'],
         'blocked_first_front_exits': int(branch['blocked'].sum()), 'next_front_time_max': float(time_to_front.max()),
         'unit_emitter_max': float(branch['unit_emitter_radiance'].max()),
         'tail_max': float(branch['retained_tail'].max()), 'event_certificate': 'expanded-first-return-certificate-05; same profile and convex footprint',
         'new_intersections': 0, 'new_heights': 0, 'source_proof': str(proof.relative_to(ROOT)), 'source_proof_sha256': sha(proof)})
    for k in ['a', 'b']:
        gate()
        charge('Study_constructor_pixels', 1360*250 if member == 'expanded' else 920*240)
        s = Study(work/k); masks = np.load(work/f'{k}-masks.npz') if member == 'expanded' else np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-masks.npz')
        source = rawbase/f'{k}-candidate.npz' if member == 'expanded' else rawbase/f'compact-{k}-candidate.npz'
        acceptedfile = base/f'{k}-candidate.npz' if member == 'expanded' else source
        bindings += [source, acceptedfile, work/k/'case.json']
        z = np.load(source); accepted = np.load(acceptedfile); raw = z['sample_before_response']; coverage = accepted['coverage']
        H, W = s.valid.shape; values = raw.copy()
        values[inside] = neutral_color_response(raw[inside], gain=F['material']['gain'], bias=F['material']['bias'])
        pre0 = values.reshape(H, 2, W, 2, 3).mean((1, 3)).astype(np.float32)
        charge('identity_composites', 1); C0 = s.apply_foreground(pre0.copy())
        assert np.array_equal(pre0, accepted['pre_foreground'], equal_nan=True)
        assert np.array_equal(C0, accepted['complete'], equal_nan=True)
        if member == 'expanded':
            partial = masks['glass'] & (coverage < 1)
        else:
            frozen = np.load(ROOT/f'research/experiments/compact-geometry-01/{k}-raw.npz')
            partial = masks['glass'] & (frozen['coverage'] < 1)
        crops = P['fixed_crops'][member]
        before = score(s, C0, masks, partial, crops)
        save(f'{member}-{k}-identity.json', {'pre_foreground_exact': True, 'complete_exact': True, 'baseline_scores': before})
        save('checkpoint.json', {'at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'last_identity': f'{member}-{k}', 'identity_exact': True, 'first_return_valid': True, 'ledger': ledger})
        base_linear = decode_srgb(values[inside])
        for amplitude in [1., 4.]:
            gate()
            light = amplitude*branch['unit_emitter_radiance'][:, None]
            linear = base_linear+light
            encoded = encode_srgb(linear)
            # Finite-display saturation is explicit and measured, not a hidden
            # Fresnel/geometry correction. Retained tail is not assigned RGB.
            clips = int((encoded > 1).sum())
            changed = values.copy(); changed[inside] = np.clip(encoded, 0, 1)
            pre = changed.reshape(H, 2, W, 2, 3).mean((1, 3)).astype(np.float32)
            charge('candidate_composites', 1); C = s.apply_foreground(pre.copy())
            now = score(s, C, masks, partial, crops)
            guards = {name: now[name]['rmse'] <= before[name]['rmse'] for name in ['glass', 'rim', 'held', 'interior']}
            guards.update(E=now['E'] <= before['E'], SSIM=now['ssim'] >= before['ssim'], exterior=now['exterior'] <= before['exterior'], partial=now['partial']['RMSE'] <= before['partial']['RMSE'])
            guards.update({name: value <= before['foreground'][name] for name, value in now['foreground'].items()})
            prefix = f'{member}-{k}-light{int(amplitude)}'
            np.savez_compressed(OUT/f'{prefix}.npz', pre_foreground=pre, complete=C, coverage=coverage)
            images(prefix, s, C0, C, crops, int(amplitude))
            # A mathematical radiance interval at every retained sample; this
            # upper error bar is not a rendered/assigned tail contribution.
            upper = encode_srgb(linear+max(1., amplitude)*branch['retained_tail'][:, None])
            row = {'member': member, 'reference': k, 'amplitude': amplitude, 'scores': now, 'baseline': before,
                   'guards': guards, 'all_original_and_partial_guards_pass': all(guards.values()), 'clipped_channels': clips,
                   'encoded_tail_interval_max_levels': float(np.max(np.clip(upper, 0, 1)-np.clip(encoded, 0, 1))*255),
                   'conditional_first_return_only': True, 'environment_observed': False, 'source_queries': 0}
            records.append(row); save(prefix+'-metrics.json', row)
            print(json.dumps({'member': member, 'ref': k, 'light': amplitude, 'E': now['E'], 'baseline_E': before['E'], 'guards': guards}), flush=True)
            gate()

save('result.json', {'status': 'CONDITIONAL_LIGHT_DIAGNOSTICS_COMPLETE_NOT_FULL_RADIANCE',
     'finished': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'records': records, 'ledger': ledger,
     'family_changed': False, 'source_or_mask_changed': False, 'adopted': False,
     'uncertainty': 'Unobserved hypothetical emitter, approximate response calibration, retained later-event radiance interval; no full scene or fidelity claim.'})
save('last-hashes.json', {str(p.relative_to(ROOT)): sha(p) for p in bindings})
assert all(sha(ROOT/k) == v for k, v in first.items())
