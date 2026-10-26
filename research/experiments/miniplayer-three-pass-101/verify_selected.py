"""Verify the public selected family against retained scientific outputs."""
from pathlib import Path
import sys,json,datetime,hashlib,zipfile,importlib.util,traceback
import numpy as np
R=Path('/repo');B=Path(__file__).parent;P=B/sys.argv[1];O=B/'selected-verification';assert not O.exists();O.mkdir()
recipe=json.loads((P/'final-recipe.json').read_text());N=B/recipe['native'];deadline=datetime.datetime.fromisoformat(json.loads((B/'final-verification-plan.json').read_text())['deadline'])
caps=dict(Studies=4,mask_points=1121600,numeric_bytes=3000000000,bitmap_pixels=50000000,fixture_rays=32,height_points=1000000,environment_points=2243200,composites=8);ledger=dict.fromkeys(caps,0);first={}
def save(n,v):(O/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def charge(k,n):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline;assert ledger[k]+n<=caps[k],(k,n);ledger[k]+=int(n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p,keys):
 first[str(p.relative_to(R))]=sha(p)
 with zipfile.ZipFile(p) as z:
  for key in keys:
   with z.open(key+'.npy') as f:
    v=np.lib.format.read_magic(f);shape,_,dt=np.lib.format.read_array_header_1_0(f) if v==(1,0) else np.lib.format.read_array_header_2_0(f);charge('numeric_bytes',int(np.prod(shape))*dt.itemsize)
 with np.load(p) as z:return {k:z[k] for k in keys}
save('start.json',dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),deadline=deadline.isoformat(),caps=caps,selected_pass=sys.argv[1],scope='32 actual factory fixture rays and four cached compositions; no new source query, filter or parameter trial'))
try:
 from music_miniplayer_family import load_working_family,working_surface_pair,working_composite,working_center,working_contour
 from raised_front_optics import trace_raised_front_orthographic
 from environment_radiance import annular_environment
 spec=importlib.util.spec_from_file_location('selected_common',B/'material_common.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);c.NATIVE=N
 F=load_working_family()
 for f in [Path(__file__),R/'reconstruction/music_miniplayer_family.py',R/'reconstruction/families/music-mini-player-working.json',R/F['geometry']['back_profile'],R/'reconstruction/miniplayer_refinement_effects.py',R/'reconstruction/miniplayer_color_refinement.py',R/'reconstruction/shoulder_core_coordinate.py',R/'reconstruction/raised_front_optics.py']:first[str(f.relative_to(R))]=sha(f)
 data=c.load_data(charge,first);records=[];geometry=[]
 for member in ['expanded','compact']:
  contour=working_contour(member);assert contour.half==(F['members'][member]['major_half']*c.L,F['geometry']['minor_half']*c.L)
  for reference in ['a','b']:assert np.array_equal(working_center(data[(member,reference)]['center']),data[(member,reference)]['center']+[-.5,0])
 for m in ['expanded','compact']:
  keys=['inside','front','back','front_normal','outward_normal','exit_direction','X','Y','primary_power','front_reflection_power','front_reflection_direction'];q=read(N/f'{m}-paths.npz',keys);I=q['inside'];ids=np.flatnonzero(I);ids=ids[np.linspace(0,len(ids)-1,16,dtype=int)];points=q['front'].reshape(-1,3)[ids]
  back,front=working_surface_pair(m);charge('fixture_rays',len(ids));trial=trace_raised_front_orthographic(back,points[:,0],points[:,1],1.,F['optics']['index'],F['optics']['background_distance'],lambda label,n:charge('height_points',n),front_surface=front)
  assert trial['complete'].all();errors={}
  for key in ['front','back','front_normal','outward_normal','exit_direction','X','Y','primary_power']:
   original=q[key].reshape((-1,)+q[key].shape[2:])[ids];errors[key]=float(np.max(abs(trial[key]-original)));assert errors[key]<1e-9,(key,errors[key])
  geometry.append(dict(member=m,errors=errors,rays=len(ids)));charge('environment_points',int(I.sum()));light=4*q['front_reflection_power'][I]*annular_environment(q['front_reflection_direction'][I])
  order=max(x['order'] for x in json.loads((P/'integration.json').read_text()) if x['member']==m);alpha=read(P/f'{m}-alpha{order}.npz',['alpha'])['alpha'][recipe['outline_index']];shadow=read(P/f'{m}-shadow{recipe["shadow_index"]}.npz',['field'])['field']
  for r in ['a','b']:
   d=data[(m,r)];raw=d['z']['raw_source'] if recipe['sigma']==6.075 else read(P/f'{m}-{r}-blur{recipe["sigma"]}-samples.npz',['raw_source'])['raw_source'];charge('composites',2)
   actual=working_composite(d['s'],raw,I,d['z']['supported'],q['primary_power'],light,alpha,shadow);saved=read(P/f'{m}-{r}-final.npz',['complete','pre_foreground'])
   errors={k:float(np.nanmax(abs(actual[k]-saved[k]))) for k in saved};assert all(np.array_equal(actual[k],saved[k],equal_nan=True) for k in saved);records.append(dict(member=m,reference=r,exact=True,errors=errors))
 assert first=={f:sha(R/f) for f in first};save('result.json',dict(passed=True,geometry=geometry,compositions=records,ledger=ledger,first_last_hashes=first,finished=datetime.datetime.now(datetime.timezone.utc).isoformat()));print('SELECTED FACTORY PASS',geometry,records)
except Exception as e:save('failure.json',dict(error=repr(e),traceback=traceback.format_exc(),ledger=ledger));raise
