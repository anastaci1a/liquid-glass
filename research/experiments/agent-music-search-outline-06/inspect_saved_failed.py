"""Saved target-plane count only; no renderer, optical or source imports."""
from pathlib import Path
import json,datetime,hashlib
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;B=P.parent/'agent-music-search-baseline-01';W=P.parents[2]/'.evidence-working/music-search-baseline-01'
assert not (P/'ceiling.json').exists()
g=.5193880051291454;b=.4473611800152188
# Positive binary64 multiply/add and four-sample sum/mean, then binary32 cast.
# Eight binary64 epsilons conservatively enclose the bounded arithmetic;
# one further binary32 successor encloses final rounding.
upper64=g+b+8*np.finfo(np.float64).eps
ceiling=float(np.nextafter(np.float32(upper64),np.float32(np.inf)))
rows=[];pixels=0
for k in ['a','b']:
 d=np.load(B/f'{k}-candidate.npz');m=np.load(B/f'{k}-masks.npz')
 target=np.asarray(Image.open(W/k/'target.png').convert('RGB').crop((1395,560,1635,795)),dtype=np.float32)/255
 pixels+=target.shape[0]*target.shape[1];assert pixels<=112800
 select=m['rim'].astype(bool)&(d['alpha']==1)
 v=target[select];above=v>ceiling
 rows.append(dict(reference=k,analyzed_native_pixels=target.shape[0]*target.shape[1],original_rim=int(m['rim'].sum()),fully_covered_original_rim=int(select.sum()),any_channel_above=int(above.any(1).sum()),all_channels_above=int(above.all(1).sum()),target_sha256=hashlib.sha256((W/k/'target.png').read_bytes()).hexdigest()))
(P/'ceiling.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),gain=g,bias=b,real_encoded_ceiling=g+b,binary64_rounding_enclosure=upper64,binary32_conservative_ceiling=ceiling,target_native_pixels=pixels,records=rows,interpretation='Conditional bounded encoded transmission ceiling on fully covered original rim pixels; not reflection identification, physical radiance, or a new mask.',optical_rays=0,heights=0,normals_directions_Fresnel=0,source_RGB_queries=0,fields_filters_composites_fits=0),indent=2)+'\n')
print((P/'ceiling.json').read_text())
