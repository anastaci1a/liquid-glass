"""Bounded saved-state fade and interior-color audit; no new optics."""
from pathlib import Path
import json,datetime,importlib.util,zipfile,hashlib,traceback,dataclasses
import numpy as np
R=Path('/repo');O=Path(__file__).parent;P=json.loads((O/'plan.json').read_text());END=datetime.datetime.fromisoformat(P['first_intake_deadline']);caps=P['intake_caps'];ledger=dict.fromkeys(caps,0);first={}
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<END,'Intake deadline'
 assert ledger[k]+n<=caps[k],(k,n);ledger[k]+=int(n)
def read(p,keys):
 first[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
 with zipfile.ZipFile(p) as z:
  for k in keys:
   with z.open(k+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f);charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p) as z:return {k:z[k] for k in keys}
from music_miniplayer_family import working_contour,working_center,working_artwork_study
from outline_response import cap_strength
from environment_radiance import decode_srgb
spec=importlib.util.spec_from_file_location('audit_common',R/'research/experiments/miniplayer-middle-ground-99/material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=R/'research/experiments/miniplayer-four-pass-100/native-pass3'
save('intake-start.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=END.isoformat(),caps=caps,patches='3x3 at five fixed major fractions -0.6,-0.3,0,0.3,0.6 and minor fractions -0.5,+0.5; retain exclusions, no substitute patches',gaps='Whole-pixel corners in original 45..60 degree zero interval, within six native pixels of actual contour; exact named quarter-angle point controls',optical_work=0))
try:
 data=c.load_data(charge,first);records=[];patches=[];synthetic=[]
 for m in ['expanded','compact']:
  d=data[(m,'a')];s=d['s'];center=working_center(d['center']);coord=dataclasses.replace(working_contour(m),counter=charge);A,B=coord.half;Rcap=coord.original_radius;core=A-Rcap;cfg=c.F['material']['outline']['angular'];x0,y0,x1,y1=s.crop;yy,xx=np.mgrid[y0:y1,x0:x1];x=xx-center[0];y=yy-center[1]
  charge('distance_points',x.size);sd=coord.boundary_distance(x,y)[0];zero=np.ones(x.shape,bool)
  for dx,dy in [(-.5,-.5),(-.5,.5),(.5,-.5),(.5,.5)]:
   X=x+dx;Y=y+dy;side=np.where(X>=0,1.,-1.);theta=(np.rad2deg(np.arctan2(-Y,X-side*core))-np.where(side<0,180.,0.)+180)%360-180;charge('angular_points',theta.size);zero&=(abs(X)>core)&(theta>=45)&(theta<=60)
  zero&=(sd>=-6)&(sd<=.5);alpha=read(R/f'research/experiments/miniplayer-four-pass-100/pass3/{m}-alpha32.npz',['alpha'])['alpha'][0]
  angles=np.array([-60,-45,0,30,44,45,50,60,75,85],float)
  for side in [1,-1]:
   a=np.deg2rad(angles+(0 if side==1 else 180));X=side*core+Rcap*np.cos(a);Y=-Rcap*np.sin(a);charge('angular_points',len(X));v=cap_strength(X,Y,coord.half,Rcap,(0,0),cfg);assert v[5]==0 and v[6]==0 and v[7]==0;synthetic.append(dict(member=m,side=side,angles_degrees=(angles+(0 if side==1 else 180)).tolist(),strength=v.tolist()))
  for r in ['a','b']:
   d=data[(m,r)];s=d['s'];z=read(R/f'research/experiments/miniplayer-four-pass-100/pass3/{m}-{r}-final.npz',['complete','pre_foreground']);charge('composites',1);body=working_artwork_study(s).apply_foreground(z['pre_foreground'].copy())
   for name,region in [('upper-right',zero&(x>0)),('lower-left',zero&(x<0))]:
    charge('diagnostic_pixels',int(region.sum()));assert region.any();exact=np.array_equal(body[region],z['complete'][region],equal_nan=True);records.append(dict(member=m,reference=r,region=name,pixels=int(region.sum()),max_saved_alpha=float(alpha[region].max()),overlay_exactly_zero=exact,body_mean_rgb=(np.nanmean(body[region],axis=0)*255).tolist(),target_mean_rgb=(np.nanmean(s.target_crop[region],axis=0)*255).tolist()));assert exact and np.all(alpha[region]==0)
   fg=np.zeros(s.valid.shape,bool)
   for layer in s.case['foreground_layers']:
    a,b,e,f=layer['box'];fg[b-y0:f-y0,a-x0:e-x0]=True
   for xf in [-.6,-.3,0,.3,.6]:
    for yf in [-.5,.5]:
     X=int(round(center[0]+xf*A));Y=int(round(center[1]+yf*B));j,i=X-x0,Y-y0;sl=(slice(i-1,i+2),slice(j-1,j+2));charge('diagnostic_pixels',9);reason=None
     if fg[sl].any():reason='Original foreground guard intersects patch'
     elif not (sd[sl]<-10).all():reason='Not separated from rim'
     elif not np.isfinite(z['complete'][sl]).all():reason='Unavailable modeled pixels'
     row=dict(member=m,reference=r,x=X,y=Y,major_fraction=xf,minor_fraction=yf,exclusion=reason)
     if reason is None:
      for label,img in [('target',s.target_crop),('model',z['complete'])]:
       values=img[sl].reshape(-1,3).astype(float);row[label]=dict(mean_rgb=(values.mean(0)*255).tolist(),mean_linear_luminance=float(np.mean(decode_srgb(values)@np.array([.2126,.7152,.0722]))),mean_encoded_chroma=float(np.mean(values.max(1)-values.min(1))))
     patches.append(row)
 save('intake-result.json',dict(finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),gaps=records,point_controls=synthetic,interior_patches=patches,ledger=ledger,hashes=first,interpretation='Existing overlay is zero in the declared whole-pixel diagonal cohorts. Remaining visible brightness is in the body. Interior color patches are registered image comparisons, not isolated material measurements.'))
 assert first=={k:hashlib.sha256((R/k).read_bytes()).hexdigest() for k in first};print('INTAKE PASS',records,ledger)
except Exception as e:save('intake-failure.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
