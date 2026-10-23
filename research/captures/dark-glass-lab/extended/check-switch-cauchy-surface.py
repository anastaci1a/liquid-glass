import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import numpy as np,cv2
from switch_euclidean_surface import EuclideanSurfaceStudy
from switch_cauchy_surface import CauchySurfaceStudy
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'physical-euclidean-surface';p=json.loads((out/'coupling-settlement.json').read_text())['parameters'];rows=[]
for name in ['a','b']:
 s=CauchySurfaceStudy(root/'paired'/name);m=EuclideanSurfaceStudy(root/'paired'/name)
 x,y=np.meshgrid(np.linspace(-1.4,1.4,37),np.linspace(-.95,.95,29));x+=p['shape_dx'];y+=p['shape_dy'];a=s.field(x,y,p);b=m.field(x,y,p)
 assert all(np.array_equal(u,v) for u,v in zip(a,b));pc=copy.deepcopy(p);pc['cauchy_delta']=.03;ns=s.band_indices(pc);assert ns[0]<ns[1]<ns[2] and ns[1]==1.5
 C,J=s.field(x,y,pc);assert np.isfinite(C).all();assert np.array_equal(J,a[1])
 # Compare each spectral field to independently invoked monochromatic geometry.
 bounds=[]
 for n in ns:
  q=copy.deepcopy(pc);q['euclidean_surface']['n']=float(n);X,Y,_,_=m.geometry_field(x,y,q);bounds.append(dict(n=float(n),max_displacement=float(np.max(np.hypot(X-x,Y-y)))))
 rows.append(dict(observation=name,zero_delta_bit_exact=True,indices=ns.tolist(),bands=bounds))
with (out/'cauchy-invariants.json').open('x') as f:json.dump(dict(rows=rows,limits='Three bands, not spectral radiometry; inherited directional mixture is empirical. Tests of code consistency and valid rays, not Apple identification or score improvement.'),f,indent=2);f.write('\n')
print(json.dumps(rows),flush=True)
