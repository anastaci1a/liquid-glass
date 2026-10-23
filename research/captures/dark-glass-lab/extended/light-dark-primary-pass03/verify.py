"""Independent reconstruction of declared shared underlay, no optical re-fit."""
import os,sys,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from reproduce import CASES
from render import case_geometry
R=Path('/evidence/extended/helper-toolbar-work/light-dark-round');D=R/'offset-pass3';O=Path('/evidence/extended/light-dark-primary-pass03');os.umask(0o002)
recipe=json.loads((D/'candidate.json').read_text());p=recipe['parameters'];native=json.loads((R/'intake-result.json').read_text())['observations'];rows=[]
for i,name in enumerate(['regular-light','regular-dark']):
 c=CASES[name];x0,y0,x1,y1=c['crop'];L=min(c['half']);yy,xx=np.mgrid[y0:y1,x0:x1];x=xx.astype(np.float32)-c['center'][0];y=yy.astype(np.float32)-c['center'][1]
 shape=lambda a,b:case_geometry(c,a,b)[0]
 alpha=np.zeros(x.shape)
 for dy in [-.375,-.125,.125,.375]:
  for dx in [-.375,-.125,.125,.375]:alpha+=(shape(x+dx,y+dy)<=0)/16
 assert np.array_equal(alpha,np.load(R/f'clean-presentation/{name}-coverage.npy'))
 sd=shape(x,y);mask=(sd>0)&(sd<.35*L);assert np.array_equal(mask,np.load(R/f'clean-presentation/{name}-exterior-mask.npy'))
 source=np.asarray(Image.open(R/f'{name}-source.png').convert('RGB')).astype(float)/255;B=source[y0:y1,x0:x1];T=np.asarray(Image.open(R/f'{name}-target.png').convert('RGB')).astype(np.float32)[y0:y1,x0:x1]/255;M=np.load(R/f'{name}-native-material.npy')
 for field in recipe['input_hashes']:
  if field['theme']==name:assert hashlib.sha256((R/f'{name}-native-material.npy').read_bytes()).hexdigest()==field['material_sha256'];assert hashlib.sha256((R/f'{name}-source.png').read_bytes()).hexdigest()==field['source_sha256']
 K=p['opacityK']*np.exp(-.5*((np.maximum(shape(x,y-recipe['offsets_L']['K'][1]*L),0)/L)/np.float64(p['sigmaK_L']))**2)
 H=p['opacityH']*np.exp(-.5*((np.maximum(shape(x,y-recipe['offsets_L']['H'][1]*L),0)/L)/np.float64(p['sigmaH_L']))**2)
 bg=B*(1-K[...,None]);bg=bg+H[...,None]*(1-bg);full=M*alpha[...,None]+bg*(1-alpha[...,None]);saved=np.load(D/f'{name}-complete.npy')
 # Native float32 coordinate/distance staging and float64 parameters retained;
 # verify the declared physical field independently, without score tolerance.
 maxdiff=float(abs(saved-full).max());print('COMPOSITE',name,maxdiff,'argmax',np.unravel_index(np.argmax(abs(saved-full)),full.shape),'dtypes',full.dtype,saved.dtype,flush=True);assert maxdiff==0
 base=np.load(R/f'offset-neighborhood/{name}-complete.npy')
 metrics={}
 for key in ['train','held','all_glass','rim','interior','outer_rim']:
  m=np.load(R/f'{name}-native-masks.npz')[key];metrics[key]=bool(np.array_equal(full.astype(np.float32)[m],M[m]));assert metrics[key]
 rmse=lambda a,m:float(np.sqrt(np.mean(((a-T)[m]*255)**2)))
 old,new=rmse(base,mask),rmse(full,mask);assert new<old
 whole_before,whole_after=rmse(base,sd>0),rmse(full,sd>0);assert whole_after<whole_before
 rows.append(dict(theme=name,independent_composite_max_difference=maxdiff,original_scored_pixels_bit_exact=metrics,original_metrics=native[i]['native_scores'],supplemental_exterior={'before':old,'after':new,'pixels':int(mask.sum())},full_visible_exterior_advisory={'before':whole_before,'after':whole_after,'pixels':int((sd>0).sum())}))
(O/'verification.json').write_text(json.dumps(dict(accepted=True,visual_review=True,round_pass=3,scope='Generated exterior reconstruction ONLY. Original material/ray/AA/source unchanged; optical E ties, no refractive improvement claimed.',observations=rows,limits='Original independent theme materials and modeled/unobserved smooth/black inputs retained. Adding shared analytic underlay is model progress; removing target-derived display context gets no credit. Gaussian distance-falloff is empirical, not measured light transport. Black falloff width is at predeclared.7L upper bound; tail/source ambiguity and local far-band regressions remain.'),indent=2)+'\n');print('Accepted exterior-only second reconstruction pass',[(r['theme'],r['full_visible_exterior_advisory']) for r in rows],flush=True)
