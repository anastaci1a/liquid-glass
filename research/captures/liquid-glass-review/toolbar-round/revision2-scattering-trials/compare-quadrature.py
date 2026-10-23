import json
from pathlib import Path
import numpy as np
root=Path('/evidence/extended/helper-toolbar-work/agent-toolbar-scattering-trials')
masks=np.load('/tmp/agent-toolbar-run/frozen-masks.npz');pairs=[];selected=None
for lower,upper in [(3,5),(5,7),(7,9)]:
    a=root/f'rho-{float(.02).hex()}-order-{lower}';b=root/f'rho-{float(.02).hex()}-order-{upper}'
    if not (b/'measurement.json').exists():break
    old=json.loads((a/'measurement.json').read_text());new=json.loads((b/'measurement.json').read_text());D=(np.load(b/'material.npy')-np.load(a/'material.npy'))*255
    rms={name:float(np.sqrt(np.mean(D[masks[name]]**2))) for name in ['glass','rim']};dv=abs(np.array(new['guard_after'])-np.array(old['guard_after']));dE=abs(new['E']-old['E']);passed=bool(max(rms.values())<=.01 and dE<=.001 and dv.max()<=.001)
    pairs.append({'lower_order':lower,'upper_order':upper,'material_RGB_RMS_difference_255':rms,'E_abs_difference':dE,'original_five_score_abs_differences':dv.tolist(),'passed_predeclared_numerical_control':passed})
    if passed:selected=upper;break
result={'pairs':pairs,'selected_order':selected,'selection_uses_lowest_E':False,'controls_are_not_optical_gains':True,'calibration_supported':selected is not None,'all_predeclared_orders_completed':bool(pairs and pairs[-1]['upper_order']==9)}
(root/'quadrature-comparison.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
