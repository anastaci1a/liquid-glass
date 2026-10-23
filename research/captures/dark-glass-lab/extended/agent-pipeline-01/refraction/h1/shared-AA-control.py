"""Three32-pixel controls against saved H1; NOT a new full image."""
from pathlib import Path
import sys,json,hashlib,numpy as np,cv2
P=Path('/evidence/extended/agent-pipeline-01');O=P/'refraction/h1';sys.path.insert(0,str(P/'code'))
from expanded_surface import ExpandedHarmonicBack
from geometric_render import render_rows
G=json.loads((O/'geometry-checkpoint.json').read_text())['scene'];s=ExpandedHarmonicBack(tuple(G['surface_half']),G['surface_radius']);orig=json.loads((P/'inputs/a/case.json').read_text());source=cv2.imread(str(P/'inputs/a/source.png'))[:,:,::-1].astype(np.float32)/255;known=cv2.imread(str(P/'inputs/a/known.png'),0)>0;cached=np.load(O/'a-material.npy');out=[]
for x,y in [(950,414),(330,405),(1180,337)]:
 case={**orig,'center':G['center'],'crop':[x,y,x+32,y+1]}
 M,bounds,support=render_rows(source,case,{},s,1.5,2.,0,1,True,True,samples_per_axis=2,source_known=known,required_pixels=np.ones((1,32),bool),return_support=True)
 old=cached[y-orig['crop'][1]:y-orig['crop'][1]+1,x-orig['crop'][0]:x-orig['crop'][0]+32];out.append({'crop':case['crop'],'pixel_exact':bool(np.array_equal(M,old)),'maximum_difference':float(abs(M-old).max()),'support':bool(support.all())});assert np.array_equal(M,old)
result={'root_dependency_commit':'b4307df3','shared_render_sha256':hashlib.sha256((P/'code/geometric_render.py').read_bytes()).hexdigest(),'controls':out,'new_control_rays':384,'new_full_images':0,'no_optical_gain':True};(O/'shared-AA-control.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
