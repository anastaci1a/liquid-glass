import json,time,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from geometric_render import render_rows
from geometric_optics import RadialCurvatureBack,HarmonicCircularBack
from harmonic_crowned_back import HarmonicCrownedBack
D=Path('/evidence/extended/playback-pipeline-01/shared-render-control');protocol=json.loads((D/'protocol-FIRST.json').read_text());start=protocol['started_unix'];rows=[];count=0
c=dict(center=[960,542],half=[245,245],crop=[1160,405,1192,406]);inv=Path('/evidence/extended/geometric-playback-inferred');params=json.loads((inv/'geometry-checkpoint-FIRST.json').read_text())['surface']
expected='ae20f4366287078794c6e84d70aff6e786400456264d88ffd832fd478d7b23f6'
cases=[('inferred-circle',RadialCurvatureBack(params['knots'],params['curvature']),c,Path('/evidence/apple-matches/public-settled-replay/media-source.png'),expected,inv/'complete.npy',(185,540)),('harmonic-circle',HarmonicCircularBack(),c,Path('/evidence/apple-matches/public-settled-replay/media-source.png'),expected,Path('/evidence/extended/geometric-playback-harmonic/complete.npy'),(185,540)),('harmonic-toolbar',HarmonicCrownedBack(),dict(center=[960,542],half=[392,170],crop=[650,450,682,451]),Path('/tmp/agent-toolbar-evidence-package/inputs/source.png'),'6c68d31ac994001701ae3763d67f494bca91d03fda950789dddf01cbb60ea21b',Path('/evidence/extended/geometric-toolbar-round/harmonic-05/material-0.15.npy'),(165,175))]
for name,surface,case,src,digest,old,(y,x) in cases:
 assert time.time()-start<120;assert hashlib.sha256(src.read_bytes()).hexdigest()==digest;source=np.asarray(Image.open(src),float)/255
 C,bounds=render_rows(source,case,{},surface,1.5,2,0,1,True,True);count+=C.shape[0]*C.shape[1]*16;assert count<=1536
 saved=np.load(old)[y:y+1,x:x+32];err=float(abs(C-saved.astype(np.float32)).max());assert err==0
 rows.append(dict(name=name,pixels=32,source_sha256=digest,original_array_dtype=str(saved.dtype),comparison_dtype='float32',maximum_difference_after_explicit_float32_cast=err,maximum_difference_against_original_precision=float(abs(C-saved).max()),source_bounds=bounds))
result=dict(protocol=protocol,controls=rows,actual_queries=count,wall_seconds=time.time()-start,full_candidate_images=0,new_scores=0,fits=0,conclusion='One unchanged projection/ray/source/AA function matches saved circle and toolbar patches. Explicit float32 comparison is software verification, not a score gate or optical-fidelity improvement.')
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
