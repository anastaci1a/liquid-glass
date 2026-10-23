import os,sys,json
from pathlib import Path
import numpy as np
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction');from extended_fit import Study
from publish import pair
ROOT=Path('/evidence/extended/helper-toolbar-work/active-slider-round');D=ROOT/'pass08-ambient-neutral/shared-nullspace';OUT=Path('/evidence/extended/active-slider-primary-pass03');os.umask(0o002)
for i,n in enumerate(['a','b']):
 s=Study(ROOT/n);full=np.load(D/f'ref{i}-complete.npy');pair(np.rint(s.target_crop*255).astype(np.uint8),np.rint(np.clip(full,0,1)*255).astype(np.uint8),('Apple source','Reconstruction')).save(OUT/f'{n}-comparison.png')
