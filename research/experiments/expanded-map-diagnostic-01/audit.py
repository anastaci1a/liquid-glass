"""Empirical map diagnostics only; no material, ray tracing or RGB sampling."""
from pathlib import Path
import datetime,json
import cv2,numpy as np
from extended_fit import Study
from map_compatibility_audit import sample_map
from surface_compatibility import inverse_gradient
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline'])
assert not (OUT/'result.json').exists()
s=Study(WORK/'a');recipe=json.loads((ROOT/'reconstruction/studies/music-mini-expanded-vector/review-round/pass-03.json').read_text())['parameters'];scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];count=0
# Any accidental texture lookup is an error, even though geometry_field needs none.
def forbidden(*args,**kwargs):raise RuntimeError('RGB lookup prohibited in map diagnostic')
cv2.remap=forbidden;s.sample_field=forbidden
x0,y0,x1,y1=s.crop;H,W=s.valid.shape;empX=np.empty((2*H,2*W));empY=np.empty_like(empX)
def field(x,y):
 global count
 count+=np.broadcast_arrays(x,y)[0].size;assert count<=p['budgets']['empirical_field_points'];assert datetime.datetime.now(datetime.timezone.utc)<deadline
 X,Y,_,_=s.geometry_field(x,y,recipe);assert np.isfinite(X).all() and np.isfinite(Y).all();return X,Y
for top in range(0,H,8):
 bot=min(top+8,H);yy,xx=np.mgrid[y0+top:y0+bot:.5,x0:x1:.5];xx-=.25;yy-=.25
 X,Y=field((xx-s.case['center'][0])/s.L,(yy-s.case['center'][1])/s.L);empX[2*top:2*bot]=X*s.L+s.case['center'][0];empY[2*top:2*bot]=Y*s.L+s.case['center'][1]
yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];xx-=.25;yy-=.25;gx=(xx-scene['center'][0])/s.L;gy=(yy-scene['center'][1])/s.L
base=np.load(WORK/'h1-a-paths.npz');m=np.load(WORK/'a-masks.npz');glass=np.repeat(np.repeat(m['glass'],2,0),2,1);rim=np.repeat(np.repeat(m['rim'],2,0),2,1)
cohorts=dict(glass=glass,rim=rim,interior=glass&~rim,left_cap=base['inside']&(gx<-scene['surface_half'][0]+scene['surface_radius']),right_cap=base['inside']&(gx>scene['surface_half'][0]-scene['surface_radius']))
comparisons=[]
files=[('H1',WORK/'h1-a-paths.npz'),('closer',WORK/'h2-a-paths.npz'),('redistributed',ROOT/'research/experiments/expanded-geometry-03/native-paths.npz'),('curved-front',ROOT/'research/experiments/expanded-geometry-04/native-paths.npz')]
for name,file in files:
 q=np.load(file);assert q['X'].shape==empX.shape;np.testing.assert_array_equal(q['inside'],base['inside']);regions={}
 for region,mask in cohorts.items():
  d=np.stack([q['X'][mask]-empX[mask],q['Y'][mask]-empY[mask]],-1);regions[region]=dict(subrays=int(mask.sum()),map_vector_RMS_native_pixels=float(np.sqrt(np.mean(np.sum(d*d,-1)))))
 comparisons.append(dict(model=name,regions=regions))
# The vertical native column lies inside the long flat core: use its actual
# frozen source displacements, not a newly invented target-normal field.
col=int(np.argmin(abs(xx[0]-scene['center'][0])));rho=(gy[:,col]-(scene['surface_half'][1]-scene['surface_radius']))/scene['surface_radius'];use=(rho>0)&(rho<1)
v=np.stack([(empX[:,col]-xx[:,col])/s.L,(empY[:,col]-yy[:,col])/s.L],-1);admitted=(np.linalg.norm(v,axis=-1)<2*np.sqrt(1.5**2-1))&use;minimum=np.full(v.shape,np.nan);minimum[admitted]=inverse_gradient(v[admitted],np.full(admitted.sum(),2.),1.5)
profile=dict(rho=rho[use].tolist(),diagnostic_displacement_over_L=v[use].tolist(),H1_displacement_over_L=np.stack([(base['X'][:,col]-xx[:,col])/s.L,(base['Y'][:,col]-yy[:,col])/s.L],-1)[use].tolist(),minimum_flat_front_slope_at_maximum_clearance=np.linalg.norm(minimum[use],axis=-1).tolist(),native_column_offset_px=float(xx[0,col]-scene['center'][0]))
# Correct unknown-height compatibility, not a raw-curl or no-fold rejection.
a=scene['surface_half'][0];b=scene['surface_half'][1];cx,cy=np.meshgrid(np.linspace(-.97*a,.97*a,65),np.linspace(-.97*b,.97*b,33));vx=cx+recipe['shape_dx'];vy=cy+recipe['shape_dy'];sd=s.shape(vx,vy,recipe)[-1][0];inside=sd<-.002
compat=sample_map(lambda x,y:np.stack(field(x,y),-1)-np.stack([x,y],-1),vx,vy,inside)
np.savez_compressed(OUT/'historical-diagnostic-map.npz',X=empX,Y=empY)
r=dict(status='DIAGNOSTIC_NOT_RENDERER_OR_GEOMETRIC_TRUTH',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),empirical_field_points=count,new_geometric_rays=0,RGB_queries=0,fits=0,native_images=0,comparisons=comparisons,profile=profile,compatibility=compat,limits=['Historical fitted field contains empirical normal/tangent corrections; it is not an automatically realizable solid.','Map-vector closeness is not a bound on attainable image error.','Near-zero or step-sensitive compatibility quantities remain unresolved.'])
def safe(value):
 if isinstance(value,dict):return {k:safe(v) for k,v in value.items()}
 if isinstance(value,list):return [safe(v) for v in value]
 return None if isinstance(value,float) and not np.isfinite(value) else value
(OUT/'result.json').write_text(json.dumps(safe(r),indent=2,allow_nan=False)+'\n');print(json.dumps({k:r[k] for k in ['status','empirical_field_points','compatibility','comparisons']},allow_nan=True))
