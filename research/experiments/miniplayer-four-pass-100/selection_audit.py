"""Training-mask audit of completed candidate rankings; no rerendering."""
from pathlib import Path
import json,datetime,zipfile,hashlib
import numpy as np
from PIL import Image
R=Path('/repo');O=Path(__file__).parent;ledger={'numeric_bytes':0,'bitmap_pixels':0,'reduced_channels':0};caps={'numeric_bytes':600000000,'bitmap_pixels':10000000,'reduced_channels':200000000};first={}
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):assert ledger[k]+n<=caps[k],(k,n);ledger[k]+=int(n)
def read(p,keys):
 first[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with zipfile.ZipFile(p) as z:
  for key in keys:
   with z.open(key+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=(np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f));charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p,allow_pickle=False) as z:return {k:z[k] for k in keys}
def rms(C,T,mask):
 charge('reduced_channels',int(mask.sum())*3);assert np.isfinite(C[mask]).all();return float(np.sqrt(np.mean(((C[mask]-T[mask])*255)**2)))
save('selection-audit-start.json',{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'caps':caps,'scope':'Read saved outputs only. Audit excludes original held pixels from ranking; original exploratory full-mask choices remain unchanged.'})
data={}
for m in ['expanded','compact']:
 for r in ['a','b']:
  work=R/f'.evidence-working/{m}-geometry-0{2 if m=="expanded" else 1}';case=json.loads((work/r/'case.json').read_text());x0,y0,x1,y1=case['crop'];im=Image.open(work/r/'target.png');charge('bitmap_pixels',im.width*im.height);T=np.asarray(im,dtype=np.float32)[y0:y1,x0:x1]/255
  mp=work/f'{r}-masks.npz' if m=='expanded' else R/f'research/experiments/compact-geometry-01/{r}-masks.npz';z=read(mp,['glass','rim','held','exterior']);masks={k:z[v]&~z['held'] for k,v in [('blur','glass'),('color','glass'),('outline','rim'),('shadow','exterior')]};art=np.zeros(T.shape[:2],bool)
  for layer in case['foreground_layers']:
   if layer['mode']=='artwork':a,b,c,d=layer['box'];art[b-y0:d-y0,a-x0:c-x0]=True
  assert not (art&z['held']).any();masks['artwork']=art
  baseline=read(R/f'research/experiments/miniplayer-middle-ground-99/peak-brightness/{m}-{r}-floor0.24.npz',['complete'])['complete'];den={k:rms(baseline,T,mask) for k,mask in masks.items()};data[(m,r)]=(T,masks,den)
records=[]
for p in ['pass1','pass2']:
 Q=O/p;choices=json.loads((Q/'choices.json').read_text())
 for stage,choice in choices.items():
  candidates=list(choice.get('mean_errors',choice.get('mean_normalized_errors')).keys());scores={}
  for label in candidates:
   values=[]
   for (m,r),(T,masks,den) in data.items():
    C=read(Q/f'{m}-{r}-{label}.npz',['complete'])['complete'];values.append(rms(C,T,masks[stage])/den[stage])
   scores[label]=float(np.mean(values))
  winner=min(scores,key=scores.get);records.append(dict(pass_name=p,stage=stage,original_choice=choice['chosen'],training_only_choice=winner,choices_match=winner==choice['chosen'],normalized_training_errors=scores))
assert first=={k:hashlib.sha256((R/k).read_bytes()).hexdigest() for k in first}
save('selection-audit.json',{'records':records,'ledger':ledger,'hashes':first,'limitation':'Earlier fixed-set rankings inspected full-mask error, including held pixels. They are exploratory and are not held-out validation. Subsequent optimization and ranking must use training masks explicitly. This audit does not retroactively alter their procedure.','new_renders':0});print(json.dumps(records,indent=2))
