"""Sensitivity to recorded exposed-track color ranges, not an optical pass.

Frozen reference files/hashes/masks/recipes are unchanged. Only the in-memory
modeled track color is perturbed, within prior recorded componentwise5/95
percentiles. These are not joint confidence intervals or verified hidden RGB.
Reported scores are conditional sensitivity, never a new scoring epoch.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'/workspace/docs/liquid-glass/experiments/reconstruction')
import cv2,numpy as np
from extended_fit import Study
cv2.setNumThreads(1)
root=Path('/evidence/extended/active-switch');out=root/'rev5-source-uncertainty';out.mkdir(exist_ok=True)
base=json.loads((root/'rev4-ambient-review/candidate.json').read_text());p=base['parameters'];co=np.array(base['material']);rows=[]
for name in ['a','b']:
 s=Study(root/'paired'/name);source=s.source.copy();meta=s.case['background_estimate'];track=np.array(meta['track_color']);paper=np.array(meta['background_color']);low,high=np.array(meta['track_color_5_95']);observed=cv2.imread(str(s.folder/'observed.png'),cv2.IMREAD_GRAYSCALE)>0
 vector=track-paper;alpha=np.clip(np.sum((source-paper)*vector,axis=2)/np.sum(vector*vector),0,1);estimated=~observed
 # Fit fraction from the generated source, never from the distorted target.
 # Preserve its antialiasing residual and every directly observed pixel.
 trials=[]
 for label,color in [('baseline',track),('low',low),('half-low',(track+low)/2),('half-high',(track+high)/2),('high',high)]:
  altered=source+estimated[...,None]*alpha[...,None]*(color-track)
  assert np.array_equal(altered[observed],source[observed]);s.source=altered.astype(np.float32);s.cache.clear();im=s.render(p,co);m=s.scores(im,include_ssim=False)
  trials.append(dict(label=label,track_rgb_255=(color*255).tolist(),E=float(np.sqrt(m['loss'])),scores=m));print(name,label,trials[-1]['E'],flush=True)
 rows.append(dict(observation=name.upper(),trials=trials,source_file_sha256=s.case['source_sha256']['source.png'],direct_observed_pixels_preserved=True))
(out/'sensitivity.json').write_text(json.dumps(dict(method=__doc__,baseline='64b970e switch revision5',observations=rows,limits='The empirical percentiles contain measurement/encoding/lighting variation; varying all channels together is a stress test, not a joint uncertainty distribution. No input changes adopted and no score improvements counted.'),indent=2)+'\n')
