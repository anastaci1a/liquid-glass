"""Extract saved accepted native PNG panel only; no old renderer/source lookup."""
from pathlib import Path
from PIL import Image
import json,numpy as np,hashlib
P=Path('/evidence/extended/agent-pipeline-01');old=Path('/evidence/extended/expanded-mini-short-round/pass-03');out={}
for key in ['a','b']:
 c=json.loads((P/f'inputs/{key}/case.json').read_text());x0,y0,x1,y1=c['crop'];W=x1-x0;H=y1-y0;path=old/f'{key}-comparison.png';im=np.asarray(Image.open(path));assert im.shape[1]==2*W+2;caption=im.shape[0]-H;assert caption==82
 target=np.asarray(Image.open(P/f'inputs/{key}/target.png'))[y0:y1,x0:x1];assert np.array_equal(im[caption:,:W],target),'Saved Apple panel must be original native crop, no resize'
 hist=im[caption:,W+2:W*2+2].astype(np.float32)/255;np.save(P/f'historical-{key}-presentation.npy',hist);out[key]={'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'crop':[W+2,caption,2*W+2,caption+H],'Apple_panel_native_exact':True,'score_source':False,'limits':'8-bit saved accepted presentation only; inherited unscored context completion not active input. All historical native scores remain original JSON; never rescore this PNG.'}
(P/'historical-presentation-provenance.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
