import os,json,sys
from pathlib import Path
import numpy as np,cv2
os.umask(0o002);cv2.setNumThreads(1)
R=Path('/evidence/extended/helper-toolbar-work/more-close-round');B=R/'epoch02';D=B/'rim-width-pass02';sys.path.insert(0,str(R/'latest-circle-baseline/code'));from extended_fit import Study
s=Study(B/'inputs/a');z=np.load(B/'gray-pass01/candidate-native.npz');m=np.load(B/'baseline-arrays.npz');e=(z['material'].astype(float)-s.target_crop.astype(float))*255;out={}
for name,key in [('glass','glass_mask'),('rim','rim_mask'),('held','held_mask'),('interior','interior_mask'),('SSIM_safe','SSIM_safe_mask')]:
 mask=m[key];out[name]=dict(pixels=int(mask.sum()),signed_RGB_mean=e[mask].mean(0).tolist(),signed_neutral_mean=float(e[mask].mean()),RGB_RMSE=float(np.sqrt(np.mean(e[mask]**2))))
review=dict(stage='SAVED_RESIDUAL_MODEL_REVIEW_NO_FIT',residuals=out,findings=['Increasing rim amplitude and width improve squared RGB error but strict SSIM worsens; not evidence to waive SSIM or alter scoring masks.','Glyph residual now improves from a separate one-gray reconstruction adjustment; do not conflate with material/refraction identification.','Smooth locally estimated header remains unknown under control and does not identify refraction or ordinary blur; sourceupper3.785/posep95.463/AA and weight uncertainty retained.','Existing common neutral material bias could be considered only if supported by signed residuals and original nonlinear guards, not authorized here. No per-channel/background/crop coefficients or new operator proposed.'],body_renders=0,additional_optical_or_source_fits=0,source_or_mask_changes=0,new_epoch_count=1)
(D/'residual-model-review.json').write_text(json.dumps(review,indent=2)+'\n');print(json.dumps(review),flush=True)
