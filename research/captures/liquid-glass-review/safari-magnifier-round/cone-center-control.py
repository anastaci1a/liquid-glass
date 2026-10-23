"""Explain sourceconstant sensitivity of the saved-response cone; no rendering."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
R=Path('/evidence/extended/helper-toolbar-work/safari-magnifier-round/neutral-guard-cone');p=R/'review.json';v=json.loads(p.read_text());g=v['gradient_cases'][-1]['gradients'];names=[n for n in g if n!='E2'];A=np.array([g[n] for n in names]);A/=np.maximum(np.linalg.norm(A,axis=1)[:,None],1e-30);z=linprog(np.array(g['E2']),A_ub=A,b_ub=np.zeros(len(A)),bounds=[(-.002,.002)]*2,method='highs');q=z.x if z.success else np.zeros(2);derivatives={n:float(np.dot(d,q)) for n,d in g.items()};violations=[]
for c in v['gradient_cases']:
 for n,d in c['gradients'].items():
  change=float(np.dot(d,q))
  if n!='E2' and change>0:violations.append(dict(name=n,gradient_prediction=change,source_constant_rgb=c['source_constant_rgb'],bias_secant=c['bias_secant']))
v['center_constant_only_control']=dict(direction=q.tolist(),directional_derivatives=derivatives,violations_other_sourcecases=len(violations),worst_other_sourcecases=sorted(violations,key=lambda x:abs(x['gradient_prediction']),reverse=True)[:12],not_a_native_proposal=True,warning='Nominal constant-source cone has a direction; across sampledsourcevalues itfails. Do not mistake proxyrobustzero for rigorousnonexistence ofactualnative direction; missingexactgainbasis remainslimitation.')
v['conclusion']='NO supported sourcevariation-stable direction from retainedbases; robustproxy returnszero, notapass. Centerproxy feasible but violatesothersources. Actualnativegainbasis notsaved, no nativefit authorized. Need primary decision before exactbasisretention/calibration; continue assignedPLUSsource review.';p.write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v['center_constant_only_control']))
