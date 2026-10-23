from pathlib import Path
import json
import numpy as np
from PIL import Image
from geometric_optics import RadialCurvatureBack,HarmonicCircularBack
from geometric_playback import render_rows
from reproduce import CASES
D=Path('/evidence/extended/geometric-playback-inferred');source=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-source.png'),float)/255
p=json.loads(Path('/evidence/extended/playback-short-round/pass-03/replay-record.json').read_text())['recipe'];case={**CASES['media'],'crop':[1160,405,1192,406]};x0,y0,_,_=CASES['media']['crop'];rows=[]
for folder,surface in [(D,RadialCurvatureBack(**{k:json.loads((D/'geometry-checkpoint-FIRST.json').read_text())['surface'][k] for k in ['knots','curvature']})),(Path('/evidence/extended/geometric-playback-harmonic'),HarmonicCircularBack())]:
 C,b=render_rows(source,case,p,surface,1.5,2,0,1,True,True);old=np.load(folder/'complete.npy')[405-y0:406-y0,1160-x0:1192-x0]
 err=float(abs(C-old).max());assert err==0
 row=dict(folder=str(folder),pixels=32,actual_geometry_queries=512,max_complete_difference=err,bounds=b,scope='Partial public wrapper identity, actual prescribed surface; no new optical proposal/image/fit or full replay')
 (folder/'public-wrapper-partial-control.json').write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
print(json.dumps(rows))
