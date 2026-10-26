"""Fixed outward shadow measurements from frozen inputs and final caches."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile
import numpy as np
from PIL import Image
R=Path('/repo');O=Path(__file__).parent/sys.argv[1];caps=dict(bitmap_pixels=25000000,numeric_bytes=20000000,samples=168);ledger=dict.fromkeys(caps,0);first={}
def charge(k,n):assert ledger[k]+n<=caps[k];ledger[k]+=int(n)
def bind(p):first[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
def bitmap(p):
 bind(p);im=Image.open(p);charge('bitmap_pixels',im.width*im.height);return np.asarray(im)
def cache(p):
 bind(p)
 with zipfile.ZipFile(p) as z:
  with z.open('complete.npy') as f:
   v=np.lib.format.read_magic(f);shape,_,dt=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f);charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p) as z:return z['complete']
(O/'shadow-profiles-start.json').write_text(json.dumps(dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),caps=caps,offsets_native=[1,3,6,12,20,32,48],positions='center and left/right apex x; above and below global extrema',scope='Conditional source-minus-target contrast; not an observed clean before/after pair. No new model evaluation.'),indent=2)+'\n')
F=json.loads((R/'reconstruction/families/music-mini-player-working.json').read_text());L=F['length_unit_native_pixels'];rows=[]
for m in ['expanded','compact']:
 work=R/f'.evidence-working/{m}-geometry-0{2 if m=="expanded" else 1}'
 center=np.array(json.loads((R/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
 if m=='compact':
  par=json.loads((R/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];case=json.loads((work/'a/case.json').read_text());center=np.array(case['center'])+L*np.array([par['shape_dx'],par['shape_dy']])
 center+=np.array([-.5,0]);half=np.array([F['members'][m]['major_half']*L+1.5,F['geometry']['minor_half']*L])
 for r in ['a','b']:
  cp=work/r/'case.json';bind(cp);case=json.loads(cp.read_text())
  for fn,h in case['source_sha256'].items():assert hashlib.sha256((work/r/fn).read_bytes()).hexdigest()==h
  source=bitmap(work/r/'source.png');target=bitmap(work/r/'target.png');known=bitmap(work/r/'known.png');C=cache(O/f'{m}-{r}-final.npz');x0,y0,x1,y1=case['crop']
  for position,x in [('center',center[0]),('left',center[0]-half[0]),('right',center[0]+half[0])]:
   x=int(round(x))
   for side,sign in [('above',-1),('below',1)]:
    for offset in [1,3,6,12,20,32,48]:
     y=int(round(center[1]+sign*(half[1]+offset)));charge('samples',1);ok=bool(known[y,x].all());inside=x0<=x<x1 and y0<=y<y1;result=C[y-y0,x-x0]*255 if inside else None
     rows.append(dict(member=m,reference=r,position=position,side=side,offset_native=offset,x=x,y=y,source_known=ok,source=source[y,x,:3].tolist() if ok else None,target=target[y,x,:3].tolist(),conditional_darkening=(source[y,x,:3].astype(float)-target[y,x,:3]).tolist() if ok else None,result=result.tolist() if result is not None and np.isfinite(result).all() else None))
assert first=={k:hashlib.sha256((R/k).read_bytes()).hexdigest() for k in first}
(O/'shadow-profiles.json').write_text(json.dumps(dict(rows=rows,ledger=ledger,first_last_hashes=first,interpretation='Positive conditional darkening means target is darker than modeled source. Unknown source is null. Texture, temporal registration and mosaic errors remain confounds; no physical opacity is inferred.'),indent=2)+'\n')
print('SHADOW PROFILES',ledger)
