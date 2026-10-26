from pathlib import Path
import json,datetime,hashlib,zipfile,dataclasses
import numpy as np
from PIL import Image
from music_miniplayer_family import working_contour
from environment_radiance import decode_srgb
R=Path('/repo');O=Path(__file__).parent;P=json.loads((O/'forensic-plan.json').read_text());END=datetime.datetime.fromisoformat(P['deadline']);ledger=dict.fromkeys(P['caps'],0);first={}
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END
 assert ledger[k]+n<=P['caps'][k],(k,n);ledger[k]+=int(n)
def read(p,keys):
 first[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f);charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p) as z:return {k:z[k] for k in keys}
F=json.loads((O/'starting-family.json').read_text());L=F['length_unit_native_pixels'];records=[];patches=[]
for m in ['expanded','compact']:
 work=R/f'.evidence-working/{m}-geometry-0{2 if m=="expanded" else 1}';center=np.array(json.loads((R/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry']['center'])
 if m=='compact':
  p=json.loads((R/'reconstruction/studies/music-mini-compact-vector/review-round/pass-03.json').read_text())['parameters'];case=json.loads((work/'a/case.json').read_text());center=np.array(case['center'])+L*np.array([p['shape_dx'],p['shape_dy']])
 intended=center+[-.5,0];actual=center+[-1.,0];coord=dataclasses.replace(working_contour(m),counter=charge);A,B=coord.half;core=A-coord.original_radius;case=json.loads((work/'a/case.json').read_text());x0,y0,x1,y1=case['crop'];yy,xx=np.mgrid[y0:y1,x0:x1];alpha=read(R/f'research/experiments/miniplayer-four-pass-100/pass3/{m}-alpha32.npz',['alpha'])['alpha'][0];masks={}
 for role,ctr in [('intended',intended),('as_run_aliased',actual)]:
  x=xx-ctr[0];y=yy-ctr[1];charge('distance_points',x.size);sd=coord.boundary_distance(x,y)[0];zero=(sd>=-6)&(sd<=.5)
  for dx,dy in [(-.5,-.5),(-.5,.5),(.5,-.5),(.5,.5)]:
   X=x+dx;Y=y+dy;side=np.where(X>=0,1.,-1.);theta=(np.rad2deg(np.arctan2(-Y,X-side*core))-np.where(side<0,180.,0.)+180)%360-180;charge('angular_points',theta.size);zero&=(abs(X)>core)&(theta>=45)&(theta<=60)
  masks[role]=(zero,x,sd)
 for r in ['a','b']:
  casepath=work/r/'case.json';first[str(casepath.relative_to(R))]=hashlib.sha256(casepath.read_bytes()).hexdigest();case=json.loads(casepath.read_text());path=work/r/'target.png';h=hashlib.sha256(path.read_bytes()).hexdigest();assert h==case['source_sha256']['target.png'];first[str(path.relative_to(R))]=h;im=Image.open(path);charge('bitmap_pixels',im.width*im.height);T=np.asarray(im,dtype=np.float32)[y0:y1,x0:x1,:3]/255
  z=read(R/f'research/experiments/miniplayer-four-pass-100/pass3/{m}-{r}-final.npz',['complete','pre_foreground']);fg=np.zeros(T.shape[:2],bool)
  for layer in case['foreground_layers']:a,b,e,f=layer['box'];fg[b-y0:f-y0,a-x0:e-x0]=True
  for role,(mask,x,sd) in masks.items():
   for name,reg in [('upper-right',mask&(x>0)),('lower-left',mask&(x<0))]:
    charge('diagnostic_pixels',int(reg.sum()));assert reg.any();finite=np.isfinite(z['complete'][reg]).all(1)&np.isfinite(z['pre_foreground'][reg]).all(1);diff=z['complete'][reg][finite]-z['pre_foreground'][reg][finite]
    row=dict(member=m,reference=r,registration=role,region=name,pixels=int(reg.sum()),foreground_pixels=int((reg&fg).sum()),max_alpha=float(alpha[reg].max()),nonzero_alpha_pixels=int((alpha[reg]>0).sum()),maximum_completed_minus_pre=float(abs(diff).max()),mean_body_rgb=(np.mean(z['pre_foreground'][reg][finite],0)*255).tolist(),mean_target_rgb=(T[reg].mean(0)*255).tolist());records.append(row)
    if role=='as_run_aliased':assert row['max_alpha']==0 and row['foreground_pixels']==0 and row['maximum_completed_minus_pre']==0
  sd=masks['intended'][2]
  for xf in [-.6,-.3,0,.3,.6]:
   for yf in [-.5,.5]:
    X=int(round(intended[0]+xf*A));Y=int(round(intended[1]+yf*B));j,i=X-x0,Y-y0;sl=(slice(i-1,i+2),slice(j-1,j+2));charge('diagnostic_pixels',9);reason='foreground' if fg[sl].any() else 'rim' if not(sd[sl]<-10).all() else None
    row=dict(member=m,reference=r,x=X,y=Y,exclusion=reason)
    if reason is None:
     for name,a in [('target',T),('model',z['complete'])]:
      v=a[sl].reshape(-1,3).astype(float);row[name]=dict(rgb=(v.mean(0)*255).tolist(),linear_luminance=float(np.mean(decode_srgb(v)@np.array([.2126,.7152,.0722]))),encoded_chroma=float(np.mean(v.max(1)-v.min(1))))
    patches.append(row)
assert first=={k:hashlib.sha256((R/k).read_bytes()).hexdigest() for k in first}
save('forensic-result.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=records,patches=patches,ledger=ledger,hashes=first,confirmed_issue='The historical loader shares center/half arrays across references. In-place edits shift the effect center twice: -1 native pixel instead of -0.5. Changed-kernel source coordinates also receive the extra -0.5 shift. Correct copied arrays before new experiments; retain old results as-run.',optical_work=0));print('FORENSIC COMPLETE',records,ledger)
