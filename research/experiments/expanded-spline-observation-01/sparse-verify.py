"""Independent cached-coordinate interpolation checks; no repeated tracing."""
from pathlib import Path
import datetime,json,hashlib
import cv2,numpy as np
from scipy.ndimage import map_coordinates
from extended_fit import Study
from geometric_render import incident_source_filter
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);r=json.loads((OUT/'result.json').read_text());assert not (OUT/'sparse-verification.json').exists();q=np.load(OUT/'native-paths.npz');queries=0;rows=[]
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 s=Study(WORK/k);assert not s.transmission_layers;z=np.load(OUT/f'{k}-candidate.npz');m=np.load(WORK/f'{k}-masks.npz')['glass'];ids=np.flatnonzero(m);selected=ids[np.linspace(0,len(ids)-1,12,dtype=int)];rr,cc=np.unravel_index(selected,m.shape);X=np.stack([q['X'][2*rr+iy,2*cc+ix] for iy in range(2) for ix in range(2)],1);Y=np.stack([q['Y'][2*rr+iy,2*cc+ix] for iy in range(2) for ix in range(2)],1);inside=np.stack([q['inside'][2*rr+iy,2*cc+ix] for iy in range(2) for ix in range(2)],1);raw=np.stack([z['sample_before_response'][2*rr+iy,2*cc+ix] for iy in range(2) for ix in range(2)],1);known=cv2.imread(str(WORK/k/'known.png'),0)>0;filtered,_,radius=incident_source_filter(s.source,known,6.75);assert radius==21;check=np.empty_like(raw)
 for flag,source in [(inside,filtered),(~inside,s.source)]:
  for channel in range(3):check[...,channel][flag]=map_coordinates(source[...,channel],[Y[flag],X[flag]],order=1,mode='constant',cval=np.nan,prefilter=False,output=np.float64)
 queries+=X.size;assert r['source_RGB_queries']+queries<=p['budgets']['source_RGB_queries'];sample_error=float(np.max(abs(check-raw)));assert sample_error<2e-15
 graded=np.where(inside[...,None],np.clip(.701980827595718*check+.22423217000784113,0,1),check);body=graded.mean(1).astype(np.float32);actual=z['pre_foreground'][rr,cc];pixel_error=float(np.max(abs(body-actual)));assert pixel_error<=2e-7;np.testing.assert_array_equal(actual,z['complete'][rr,cc]);rows.append(dict(reference=k,native_pixels=12,source_queries=int(X.size),sample_max_error=sample_error,integrated_float32_max_error=pixel_error,foreground_disjoint_glass_complete_exact=True))
files=['reconstruction/spline_height_back.py','reconstruction/geometric_optics.py','reconstruction/geometric_render.py','reconstruction/extended_fit.py',str((OUT/'preflight.py').relative_to(ROOT)),str((OUT/'observe.py').relative_to(ROOT))];result=dict(status='PASS_SPARSE_INDEPENDENT_SAMPLING_CONTROLS',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),records=rows,new_rays=0,new_height_calls=0,new_full_images=0,new_source_queries=queries,cumulative_source_RGB_queries=r['source_RGB_queries']+queries,declared_query_cap=p['budgets']['source_RGB_queries'],code_SHA256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files});(OUT/'sparse-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
