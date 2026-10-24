from pathlib import Path
import json,datetime
import numpy as np
from PIL import Image
O=Path(__file__).parent;ROOT=O.parents[2];B=O.parent/'agent-music-search-baseline-01';WORK=ROOT/'.evidence-working/music-search-baseline-01';P=json.loads((O/'protocol.json').read_text());assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'));crops=json.loads((B/'RGB-started.json').read_text())['fixed_original_frame_crops'];count=0
for k in ['a','b']:
 c=json.loads((WORK/k/'case.json').read_text());x0,y0,x1,y1=c['crop'];target=np.asarray(Image.open(WORK/k/'target.png').convert('RGB')).astype(np.float32)/255;target=target[y0:y1,x0:x1];C=np.load(O/f'{k}-candidate.npz',allow_pickle=False)['complete'];out={};luma=np.array([.2126,.7152,.0722])
 for name,(a,b,cc,d) in crops.items():
  e=(C[b-y0:d-y0,a-x0:cc-x0].astype(float)-target[b-y0:d-y0,a-x0:cc-x0].astype(float))*255;count+=e.shape[0]*e.shape[1];e=e[np.isfinite(e).all(2)];Y=e@luma;ch=e-Y[:,None];out[name]={'bounds':[a,b,cc,d],'RGB_RMSE':float(np.sqrt(np.mean(e*e))),'luma_RMSE':float(np.sqrt(np.mean(Y*Y))),'chroma_RMSE':float(np.sqrt(np.mean(ch*ch))),'signed_RGB':e.mean(0).tolist()}
 (O/f'{k}-fixed-crops.json').write_text(json.dumps(out,indent=2)+'\n')
(O/'diagnostic-correction.json').write_text(json.dumps({'initial_issue':'As-run observe.local omitted return out, leaving fixed_crops null. Original metrics preserved. This saved-array-only supplement provides the four unchanged fixed crop metrics per case.','candidate_or_score_repeats':0,'saved_crop_pixel_reductions':count,'decoded_target_pixels':2*target.shape[0]*target.shape[1],'source_queries':0,'at':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
print('SAVED_CROP_SUPPLEMENT',count)
