"""One fixed accepted native-material HQ evaluation; shadow candidates reuse it."""
from pathlib import Path
import sys,json,time
import cv2,numpy as np
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
from extended_fit import Study
from source_support import masks,kernel_safe,confidence_at
cv2.setNumThreads(1)
R=Path('/evidence/extended/safari-plus-source-round');O=Path('/evidence/extended/safari-plus-shadow-round/hq-body');assert not(O/'material.npy').exists();s=Study(R/'b-proposed');r=json.loads((R/'transfer-recipe.json').read_text());p=r['parameters'];scale=8;t=time.time();M=s.render(p,np.asarray(r['material']),scale);np.save(O/'material.npy',M);np.save(O/'alpha.npy',s.shape_coverage(p,scale));print('HQ material persisted',M.shape,time.time()-t,flush=True)
defd,obs=masks(s);safe,k=kernel_safe(defd,s,p);counts={'whole':0,'all_scored':0,'post_footprint':0,'whole_bad':0,'all_scored_bad':0,'post_footprint_bad':0};bounds=[1e9,1e9,-1e9,-1e9];margin=4
for row,bottom,W,x,y in s.raster_tiles(scale):
 X,Y,d,J=s.geometry_field(x,y,p);rx=(X*s.L+s.case['center'][0]).astype('float32');ry=(Y*s.L+s.case['center'][1]).astype('float32');sd=s.shape(x,y,p)[-1][0];q=confidence_at(safe,rx,ry)
 # Original scored regions evaluated at corresponding emitted OUTPUT ray coordinates; no mask expansion for scoring.
 nx=np.clip(np.floor(x*s.L+s.case['center'][0]-s.crop[0]+.5).astype(int),0,s.valid.shape[1]-1);ny=np.clip(np.floor(y*s.L+s.case['center'][1]-s.crop[1]+.5).astype(int),0,s.valid.shape[0]-1)
 groups={'whole':sd<=0,'all_scored':s.valid[ny,nx],'post_footprint':sd<=margin/s.L}
 for name,m in groups.items():counts[name]+=int(m.sum());counts[name+'_bad']+=int((q[m]<.999999).sum())
 m=groups['post_footprint']|groups['all_scored']
 if m.any():bounds=[min(bounds[0],float(rx[m].min())),min(bounds[1],float(ry[m].min())),max(bounds[2],float(rx[m].max())),max(bounds[3],float(ry[m].max()))]
assert not any(counts[n] for n in ['whole_bad','all_scored_bad','post_footprint_bad'])
report={'scale':scale,'raster':list(M.shape[:2][::-1]),'sampling':'2x2 per OUTPUT pixel; source normalized map/filter widths frozen','render_seconds':time.time()-t,'counts':counts,'source_bounds':bounds,'finite_source_gaussian_radius':k,'postblur_footprint_native':margin,'hidden_observed_fraction':0,'limits':'Mathematical affine-domain definedness only; no recovered RGB, infinite-Gaussian or physical-optics proof','source_recipe':str(R/'transfer-recipe.json'),'no_new_pass':True};(O/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
