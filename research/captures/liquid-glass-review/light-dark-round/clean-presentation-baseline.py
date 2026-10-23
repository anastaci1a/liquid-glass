"""PRIVATE zero-shadow presentation/supplemental guard, no optical/source fit."""
import os,json,sys,hashlib
from pathlib import Path
import numpy as np,cv2
from PIL import Image
R=Path('/evidence/extended/helper-toolbar-work/light-dark-round');O=R/'clean-presentation';sys.path.insert(0,str(R/'code'))
from reproduce import CASES,points
from render import case_geometry
cv2.setNumThreads(1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o002)
 if (O/'result.json').exists():print('Cleanbaseline complete,no repeat');return
 if O.exists():raise RuntimeError('Inspect partial baseline first')
 O.mkdir();rows=[]
 for name in ['regular-light','regular-dark']:
  case=CASES[name];x0,y0,x1,y1=case['crop'];H,W=y1-y0,x1-x0;L=min(case['half']);material=np.load(R/f'{name}-native-material.npy');source=np.asarray(Image.open(R/f'{name}-source.png').convert('RGB')).astype(float)/255;target=np.asarray(Image.open(R/f'{name}-target.png').convert('RGB')).astype(np.float32)/255;B=source[y0:y1,x0:x1];T=target[y0:y1,x0:x1]
  alpha=np.empty((H,W),float)
  for top in range(y0,y1,24):
   bottom=min(top+24,y1);yy,xx=np.mgrid[top:bottom:.25,x0:x1:.25];sd=case_geometry(case,xx-.375-case['center'][0],yy-.375-case['center'][1])[0];alpha[top-y0:bottom-y0]=(sd<=0).reshape(bottom-top,4,W,4).mean((1,3))
  xs,ys,x,y=points(case);sd=case_geometry(case,x,y)[0];ext=(sd>0)&(sd<.35*L);far=ext&(sd>.20*L);clean=material*alpha[...,None]+B*(1-alpha[...,None]);error=clean-T
  np.save(O/f'{name}-coverage.npy',alpha);np.save(O/f'{name}-baseline-complete.npy',clean);np.save(O/f'{name}-exterior-mask.npy',ext)
  Image.fromarray(np.rint(np.clip(clean,0,1)*255).astype(np.uint8)).save(O/f'{name}-zero-shadow-native.png');Image.fromarray(np.rint(np.clip(T,0,1)*255).astype(np.uint8)).save(O/f'{name}-target-native.png')
  def stat(mask):return dict(pixels=int(mask.sum()),source_mean_rgb_255=(B[mask].mean(0)*255).tolist(),target_mean_rgb_255=(T[mask].mean(0,dtype=np.float64)*255).tolist(),target_rgb_min_255=(T[mask].min(0)*255).tolist(),target_rgb_max_255=(T[mask].max(0)*255).tolist(),source_target_rmse=float(np.sqrt(np.mean((B[mask]-T[mask])**2))*255),exact_black_target_fraction=float(np.all(T[mask]==0,axis=1).mean()),target_nonzero_pixels=int(np.any(T[mask]!=0,axis=1).sum()))
  rows.append(dict(theme=name,source_domain='ExistingestimatedsourcePNG only; noobservedconfidence fabrication',coverage_subsamples_per_axis=4,zero_generated_shadow=True,compositor='material*true4x4coverage+EXISTINGsource*(1-coverage); NEVER compose/contact_context/targetresidual',supplemental_exterior=dict(mask='original0<sd<.35L',pixels=int(ext.sum()),rmse=float(np.sqrt(np.mean(error[ext]**2))*255),mask_sha256=sha(O/f'{name}-exterior-mask.npy')),exterior_background_semantic_stats=stat(ext),far_exterior_semantic_stats=stat(far),native_material_sha256=sha(R/f'{name}-native-material.npy'),declaration='SeparatePRIVATEpresentation/guardbaseline, NOT input/source/opticalgain or adoptedpublicshadow. Originalnativeglassmasks/metrics/recipes unchanged.'))
  print(name,json.dumps(rows[-1]),flush=True)
 (O/'result.json').write_text(json.dumps(dict(observations=rows,generated_shadow=0,source_or_optical_gain_claim=False,source_adoption=False,fit_performed=False,semantic_review_required=True),indent=2)+'\n')
if __name__=='__main__':main()
