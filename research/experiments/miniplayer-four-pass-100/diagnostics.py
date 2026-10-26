"""Small saved-output diagnostics after replay; preserve unavailable samples."""
from pathlib import Path
import json,datetime,sys,hashlib,zipfile
import numpy as np
from PIL import Image
R=Path('/repo');O=Path(__file__).parent/sys.argv[1];recipe=json.loads((O/'final-recipe.json').read_text());F=json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels'];rows=[];ledger={'bitmap_pixels':0,'numeric_bytes':0,'sampled_pixels':0};caps={'bitmap_pixels':30000000,'numeric_bytes':100000000,'sampled_pixels':128};hashes={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def charge(k,n):assert ledger[k]+n<=caps[k];ledger[k]+=int(n)
def image(p):
 hashes[str(p.relative_to(R))]=sha(p);im=Image.open(p);charge('bitmap_pixels',im.width*im.height);return np.array(im)
def read(p,key):
 hashes[str(p.relative_to(R))]=sha(p)
 with zipfile.ZipFile(p) as z:
  with z.open(key+'.npy') as f:
   v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p,allow_pickle=False) as z:return z[key]
def finite(v):return [float(x) if np.isfinite(x) else None for x in v]
(O/'diagnostic-supplement-start.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'scope':'No replay repeated. Original four exact replays were saved before optional JSON diagnostics failed on unavailable values.'},indent=2)+'\n')
for m in ['expanded','compact']:
 work=R/f'.evidence-working/{m}-geometry-0{2 if m=="expanded" else 1}';center=np.array(json.loads((R/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
 if m=='compact':
  case=json.loads((work/'a/case.json').read_text());pr=json.loads((R/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];center=np.array(case['center'])+L*np.array([pr['shape_dx'],pr['shape_dy']])
 center+=np.array([-.5,0]);half=L*np.array([F['members'][m]['major_half'],F['geometry']['minor_half']])+np.array([1.5,0]);shadow=read(O/f'{m}-shadow{recipe["shadow_index"]}.npz','field')
 for r in ['a','b']:
  case=json.loads((work/r/'case.json').read_text());x0,y0,x1,y1=case['crop'];C=read(O/f'{m}-{r}-final.npz','complete');T=image(work/r/'target.png');S=image(work/r/'source.png');known=image(work/r/'known.png')>0
  points=[(int(round(center[0])),int(np.ceil(center[1]+half[1]+d)),'below center') for d in [.5,4,10,20]]
  points += [(int(round(x)),int(np.ceil(center[1]+half[1]+.5)),'same bottom row') for x in [center[0]-half[0],center[0]+half[0],x0+1,x1-2]]
  if m=='expanded':points += [(x,y,'yellow reference') for x in [1160,1280,1400] for y in [325,501]]
  for x,y,role in points:
   i,j=y-y0,x-x0
   if not(0<=i<C.shape[0] and 0<=j<C.shape[1]):continue
   charge('sampled_pixels',1);rows.append(dict(member=m,reference=r,x=x,y=y,role=role,target=T[y,x].tolist(),source=S[y,x].tolist() if known[y,x] else None,source_known=bool(known[y,x]),result=finite(C[i,j]*255),result_finite=bool(np.isfinite(C[i,j]).all()),unit_white_shadow=float(255*(1-recipe['shadow']['opacity']*shadow[2*i,2*j]))))
assert hashes=={k:sha(R/k) for k in hashes}
(O/'fixed-diagnostics.json').write_text(json.dumps({'records':rows,'ledger':ledger,'hashes':hashes,'scope':'Conditional mosaic before/after points; null marks unavailable data.'},indent=2)+'\n');print('DIAGNOSTIC SUPPLEMENT',ledger)
