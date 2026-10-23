import sys,json,copy
from pathlib import Path
sys.path[:0]=['/workspace/docs/liquid-glass/experiments/reconstruction','/evidence/extended']
import cv2,numpy as np
from switch_filter_space import FilterSpaceStudy
from switch_filter_cache import FilterSpaceCache
from switch_filter_space import decode
from render import shade
cv2.setNumThreads(1);root=Path('/evidence/extended/active-switch');out=root/'rev5-filter-space';old=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=copy.deepcopy(old['parameters']);co=np.array(old['material']);p.update(source_filter_space='bt709',output_filter_space='bt709');rows=[]
v=np.random.default_rng(222).normal(size=23);v/=np.linalg.norm(v)
for name in ['a','b']:
 s=FilterSpaceStudy(root/'paired'/name);cache=FilterSpaceCache(s,p)
 direct=s.render(p,co);cached=cache.render(co);error=float(np.max(abs(direct-cached)));assert error<2e-6
 analytic=np.stack([F@v for _,F in cache.material_channels(co)],-1);tests=[]
 for eps in [1e-3,3e-4,1e-4,5e-5]:
  finite=(cache.render(co+eps*v)-cache.render(co-eps*v))/(2*eps)
  # Rounded BT.709 knees are discontinuous; clipping is nondifferentiable.
  # Audit those crossings separately, never remove them from native scores.
  stages=[]
  for point in [co-eps*v,co+eps*v]:
   effective=cache.material_transform@point+cache.material_offset;core=cache.J[...,-1]
   gain=(1-core[...,None])*effective[:3]+core[...,None]*effective[-3:]
   raw=cache.C*gain+effective[3:6]+(cache.J[...,:-1]@effective[6:-3])[...,None]
   mean=np.clip(raw,0,1).reshape(cache.H,2,cache.W,2,3).mean((1,3)).astype(np.float32)
   linear=cv2.GaussianBlur(decode(mean,'bt709').astype(np.float32),(0,0),s.kernel_sigma(p,'post_sigma'))
   stages.append((raw,mean,linear))
  def crosses(a,b,k):return (np.minimum(a,b)<=k)&(np.maximum(a,b)>=k)
  r0,m0,l0=stages[0];r1,m1,l1=stages[1]
  bad=(crosses(r0,r1,0)|crosses(r0,r1,1)).reshape(cache.H,2,cache.W,2,3).any((1,3,4))
  bad|=crosses(m0,m1,.081).any(-1)
  radius=int(np.ceil(4*s.kernel_sigma(p,'post_sigma')))
  bad=cv2.dilate(bad.astype(np.uint8),np.ones((2*radius+1,2*radius+1),np.uint8)).astype(bool)
  bad|=crosses(l0,l1,.018).any(-1)
  relative=float(np.sqrt(np.mean((finite-analytic)**2))/max(np.sqrt(np.mean(analytic**2)),1e-12))
  smooth=float(np.sqrt(np.mean((finite[~bad]-analytic[~bad])**2))/max(np.sqrt(np.mean(analytic[~bad]**2)),1e-12))
  tests.append(dict(epsilon=eps,relative_RMS_error=relative,smooth_region_error=smooth,nonsmooth_output_pixels=int(bad.sum()),total_pixels=int(bad.size)))
  print(name,tests[-1],flush=True)
 assert all(t['smooth_region_error']<.01 for t in tests),tests
 rows.append(dict(observation=name,maximum_cache_difference=error,derivative_checks=tests));print(rows[-1],flush=True)
 del s,cache
with (out/'cache-verification.json').open('x') as f:json.dump(dict(rows=rows,limits='Continuous chain rule compared against finite native float32 differences; clipping and rounded transfer knees prevent global differentiability. Actual native scores decide acceptance.'),f,indent=2)
