"""Recover measurements only; no import of ray/shape/image-render code."""
import json,time,datetime
from pathlib import Path
import numpy as np
from PIL import Image
from reproduce import CASES,scores
D=Path('/evidence/extended/geometric-playback-harmonic');case=CASES['media'];x0,y0,x1,y1=case['crop'];C=np.load(D/'complete.npy');old=np.load(D/'historical-complete.npy');target=np.asarray(Image.open('/evidence/apple-matches/public-settled-replay/media-target.png'),np.float32)/255;ref=target[y0:y1,x0:x1];local={}
for name,(a,b,c,d) in [('bottom-left',[690,570,910,810]),('top-left',[690,290,910,530]),('upper-right-crossings',[1025,320,1245,560])]:
 region=np.s_[b-y0:d-y0,a-x0:c-x0];row=dict(box=[a,b,c,d])
 for label,im in [('historical',old[region]),('candidate',C[region])]:
  diff=(im-target[b:d,a:c])*255;luma=diff@np.array([.2126,.7152,.0722]);chroma=diff-diff.mean(-1)[...,None]
  row[label]=dict(RGB_RMSE=float(np.sqrt(np.mean(diff**2))),luma_RMSE=float(np.sqrt(np.mean(luma**2))),chroma_RMSE=float(np.sqrt(np.mean(chroma**2))),signed_RGB=diff.mean((0,1)).tolist())
 local[name]=row
result=dict(classification='USEFUL_NEGATIVE_NOT_ACCEPTED_VISIBLE_IMPROVEMENT',geometry=json.loads((D/'geometry-checkpoint-FIRST.json').read_text()),proof=json.loads((D/'source-proof-FIRST.json').read_text()),visible_composite_scores=scores(C,ref,case),historical_scores=scores(old.astype(np.float32),ref,case),local=local,completed_image_renders=1,fits=0,recovery=dict(new_rays=0,new_source_samples=0,new_image_renders=0,reason='Initial completed native image and previews saved, but historical float64 array failed OpenCV Sobel float32 score helper. Recover cached arrays; explicitly convert historical control to original float32 score helper dtype. Original saved arrays unchanged.',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()),scope='Unit raw transmission, no body grading/lighting/reflection/shadow/scattering; historical filtered icon color/alpha frozen nuisance. Exact bilinear differs from old quantized remap. Original source/masks/registration unchanged; historical official records remain authoritative.')
(D/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(geometry=result['geometry'],glass=result['visible_composite_scores']['all_glass'],local=local)))
