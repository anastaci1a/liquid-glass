"""Actual-normal partial Fresnel ledger, never an outline RGB renderer."""
from pathlib import Path
import datetime
import hashlib
import json
import numpy as np
from PIL import Image
from geometric_optics import fresnel_components, reflect_direction

OUT = Path(__file__).resolve().parent; ROOT = OUT.parents[2]
P = ROOT / 'research/experiments/expanded-spline-observation-01'
WORK = ROOT / '.evidence-working/expanded-geometry-02'
DECISION = ROOT / 'research/experiments/expanded-contrast-guard-02/primary-decision.json'
p = json.loads((OUT / 'protocol.json').read_text())
deadline = datetime.datetime.fromisoformat(p['deadline_utc'].replace('Z', '+00:00'))
assert not (OUT / 'result.json').exists(), 'No repeated audit'
assert datetime.datetime.now(datetime.timezone.utc) < deadline
q = np.load(P / 'native-paths.npz'); inside = q['inside']
normal = q['outward_normal'][inside]
N = len(normal); assert N <= p['budgets']['cached_back_interface_points']
assert q['complete'][inside].all() and np.isfinite(normal).all()
assert np.max(abs(np.linalg.norm(normal, axis=-1)-1)) < 1e-12
assert (normal[:,2] < 0).all()
M = json.loads((ROOT / 'research/experiments/expanded-spline-height-01/inference.json').read_text())['best']['slope_bound']
front_sp = fresnel_components(1., 1., 1.5)
assert np.max(abs(front_sp-.04)) < 1e-15
front_R = float(front_sp.mean()); front_T = 1-front_R
back_sp = fresnel_components(-normal[:,2], 1.5, 1.)
assert np.all((back_sp >= 0)&(back_sp < 1))
incident = np.zeros_like(normal); incident[:,2] = -1
reflected = reflect_direction(incident, normal)
assert N <= p['budgets']['specular_direction_evaluations']
assert (reflected[:,2] > 0).all()
# With the global height Lipschitz bound, positive clearance rate proves the
# reflected segment cannot meet the back again before the flat front.
cone = reflected[:,2] - M*np.linalg.norm(reflected[:,:2],axis=-1)
certified = cone > p['numerical_cone_margin']
K = int(certified.sum())
assert N+K+1 <= p['budgets']['total_fresnel_interface_evaluations']
return_sp = fresnel_components(reflected[certified,2], 1.5, 1.)
primary = front_T*(1-back_sp.mean(axis=-1))
first_front_exit = np.zeros(N)
remaining = front_T*back_sp.mean(axis=-1)
# The original front is normal incidence, so its s/p factors agree. At the
# back and following flat-front encounter both incidence planes coincide.
# Keep their separate polarized powers rather than multiplying averages.
first_front_exit[certified] = front_T*np.mean(back_sp[certified]*(1-return_sp),axis=-1)
remaining[certified] = front_T*np.mean(back_sp[certified]*return_sp,axis=-1)
power_error = float(np.max(abs(front_R+primary+first_front_exit+remaining-1)))
assert power_error < 2e-15

def stats(value):
    return dict(min=float(np.min(value)),median=float(np.median(value)),
                p95=float(np.quantile(value,.95)),max=float(np.max(value)))

decision = json.loads(DECISION.read_text())
cap = decision['material']['gain'] + decision['material']['bias']
# A conservative representable float32 upper enclosure, not a score tolerance.
cap32 = float(np.nextafter(np.float32(cap),np.float32(np.inf)))
H,W = q['inside'].shape[0]//2,q['inside'].shape[1]//2
coverage = inside.reshape(H,2,W,2).mean((1,3))
rows = []
for key in ['a','b']:
    assert datetime.datetime.now(datetime.timezone.utc) < deadline
    case = json.loads((WORK/key/'case.json').read_text())
    target = np.asarray(Image.open(WORK/key/'target.png').convert('RGB'),np.float32)/255
    x0,y0,x1,y1 = case['crop']; target=target[y0:y1,x0:x1]
    masks = np.load(WORK/f'{key}-masks.npz')
    rim = masks['rim'] & (coverage == 1)
    exceeds = target[rim] > cap32
    rows.append(dict(reference=key,fully_covered_original_rim_pixels=int(rim.sum()),
        any_channel_above_coded_cap=int(exceeds.any(axis=1).sum()),
        all_channels_above_coded_cap=int(exceeds.all(axis=1).sum()),
        maximum_channel_excess_levels=float(np.max(target[rim]-cap32)*255),
        scope='Conditional on current geometry coverage and bounded encoded source; not physical alpha or a unique lighting explanation.'))

result = dict(status='PARTIAL_POWER_AND_CODE_ROLE_AUDIT_NO_RGB',
    finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    cached_back_interface_points=N,specular_direction_evaluations=N,
    fresnel_interface_evaluations=N+K+1,cone_certified_first_front_encounters=K,
    uncertified_next_intersections=N-K,
    first_front_TIR_or_critical=int(np.all(return_sp==1,axis=1).sum()),
    front_reflection=front_R,back_reflection=stats(back_sp.mean(axis=-1)),
    primary_power=stats(primary),first_front_exit_power=stats(first_front_exit),
    retained_internal_or_unresolved_power=stats(remaining),power_sum_max_error=power_error,
    selected_slope_bound=M,numerical_cone_margin=p['numerical_cone_margin'],
    coded_transmission_cap_real=cap,conservative_float32_cap=cap32,code_ceiling=rows,
    new_intersection_solves=0,new_height_evaluations=0,source_RGB_queries=0,
    candidate_composites=0,parameter_fits=0,
    unresolved='Every front-environment contribution and all remaining internal/unresolved power are retained as unknown; none is assigned RGB.',
    inputs=[dict(path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest())
            for f in [P/'native-paths.npz',DECISION,ROOT/'reconstruction/geometric_optics.py']])
(OUT/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result),flush=True)
