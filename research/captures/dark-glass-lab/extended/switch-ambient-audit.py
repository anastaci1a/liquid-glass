"""Verify candidate response scope and sufficient grayscale monotonicity."""
import sys,json,copy,argparse
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import numpy as np,cv2
from extended_fit import Study
from material_context import affine,mean_source,LUMA
cv2.setNumThreads(1)
ap=argparse.ArgumentParser();ap.add_argument('candidate',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
r=json.loads(a.candidate.read_text());p=r['parameters'];co=np.array(r['material']);rows=[]
for name in ['a','b']:
 s=Study(Path('/evidence/extended/active-switch/paired')/name);q=copy.deepcopy(p);q.pop('ambient_rim_response',None)
 y,x=np.mgrid[-.95:.95:37j,-1.4:1.4:51j]
 before=s.geometry_field(x,y,q);after=s.geometry_field(x,y,p)
 assert all(np.array_equal(b,c) for b,c in zip(before,after))
 T,offset=affine(s,p);mu=mean_source(s,p)
 expected=np.zeros(23);expected[[6,9,12]]=(float(mu@LUMA)-.5)*np.array(p['ambient_rim_response'])
 assert np.allclose(offset,expected,rtol=0,atol=1e-14)
 # For uniform achromatic inputs, context contraction stays fixed. Positive
 # material gains, nonnegative response and nonnegative radial bases suffice:
 # d(raw)/dg = gamma*g^(gamma-1)*gain + sum(response_i*basis_i) >= 0.
 # Clipping, averaging, Gaussian filtering and reflection weights in[0,1]
 # preserve this monotonicity. This is NOT a guarantee for arbitrary changing
 # colored/spatial backgrounds or a claim of measured Apple adaptation.
 grayscale_gain=np.array([float(co[:3]@LUMA),float(co[-3:]@LUMA)])
 sufficient=bool(np.all(grayscale_gain>=0) and p['gamma']>0 and np.all(np.array(p['ambient_rim_response'])>=0))
 rows.append(dict(observation=name.upper(),source_mean_rgb=mu.tolist(),source_encoded_luma=float(mu@LUMA),offset_neutral_terms=offset[[6,9,12]].tolist(),geometry_and_lighting_basis_unchanged=True,uniform_grayscale_monotonicity_sufficient=sufficient,grayscale_rim_core_gains=grayscale_gain.tolist()))
a.output.write_text(json.dumps(dict(observations=rows,method=__doc__,scope='Source-mean-derived empirical neutral lighting, fixed geometry/transmission. Two measured contexts; no physical interpretation or broad colored-background monotonicity claim.',grayscale_proof='For uniform grayscale g: gamma*g^(gamma-1)*gain + sum(response_i*nonnegative_radial_basis_i) >= 0; clipping, positive filtering and convex reflection preserve order.'),indent=2)+'\n');print(json.dumps(rows),flush=True)
