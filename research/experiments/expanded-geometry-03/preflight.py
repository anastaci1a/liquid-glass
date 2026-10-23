"""Trace one shared native geometry, then certify both original sources."""
from pathlib import Path
import datetime,json
import cv2,numpy as np
from extended_fit import Study
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from geometric_optics import trace_flat_front_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02'
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline'])
assert not (OUT/'source-preflight.json').exists() and json.loads((OUT/'checkpoint.json').read_text())['status']=='PASS'
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];surface=RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius'],depth=.24,crown_depth=.2)
s=Study(WORK/'a');x0,y0,x1,y1=s.crop;yy,xx=np.mgrid[y0:y1:.5,x0:x1:.5];xx-=.25;yy-=.25
assert xx.size<=p['budgets']['full_shared_primary_rays']
q=trace_flat_front_orthographic(surface,(xx-scene['center'][0])/s.L,(yy-scene['center'][1])/s.L,1.5,2)
X=q['X']*s.L+scene['center'][0];Y=q['Y']*s.L+scene['center'][1]
np.savez_compressed(OUT/'native-paths.npz',X=X,Y=Y,inside=q['inside'],complete=q['complete'])
np.testing.assert_array_equal(q['inside'],np.load(WORK/'h1-a-paths.npz')['inside'])
rows=[];checks=0
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 case=Study(WORK/k);assert case.crop==s.crop and case.case['center']==s.case['center'] and case.case['half']==s.case['half'] and case.L==s.L
 masks=np.load(WORK/f'{k}-masks.npz');np.testing.assert_array_equal(case.valid,masks['glass'])
 np.testing.assert_array_equal(q['inside'],np.load(WORK/f'h1-{k}-paths.npz')['inside'])
 known=cv2.imread(str(WORK/k/'known.png'),0)>0;eroded=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 req=masks['glass']|masks['exterior']
 for layer in case.case['foreground_layers']:
  a,b,c,d=layer['box'];req[b-y0:d-y0,a-x0:c-x0]=True
 required=q['inside']|np.repeat(np.repeat(req,2,0),2,1);checks+=required.size;assert checks<=p['budgets']['source_audit_subrays']
 assert q['complete'][required].all() and np.isfinite(X[required]).all() and np.isfinite(Y[required]).all()
 a=np.floor(X).astype(int);b=np.floor(Y).astype(int);bounds=(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);base=np.zeros(a.shape,bool);lens=np.zeros(a.shape,bool);i,j=np.nonzero(bounds)
 for field,mask in [(base,known),(lens,eroded)]:field[i,j]=mask[b[i,j],a[i,j]]&mask[b[i,j]+1,a[i,j]]&mask[b[i,j],a[i,j]+1]&mask[b[i,j]+1,a[i,j]+1]
 support=np.where(q['inside'],lens,base);row=dict(reference=k,source_audit_subrays=required.size,whole=int(q['inside'].sum()),required_union=int(required.sum()),unsupported_required=int((required&~support).sum()),incomplete_required=int((required&~q['complete']).sum()),unsupported_unscored_only=int((~required&~support).sum()),source_radius=21,RGB_queries=0,coverage_exact=True)
 np.savez_compressed(OUT/f'{k}-support.npz',support=support,required=required);rows.append(row);print(json.dumps(row),flush=True)
status='PASS' if all(r['unsupported_required']==r['incomplete_required']==0 for r in rows) else 'STOP_UNSUPPORTED_REQUIRED_NO_RGB'
r=dict(status=status,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_primary_rays=xx.size,source_audit_subrays=checks,RGB_queries=0,native_images=0,references=rows,source_limit='Original confidence only; not hidden photographic truth.')
(OUT/'source-preflight.json').write_text(json.dumps(r,indent=2)+'\n')
if status!='PASS':raise RuntimeError('Unsupported required source; stop before RGB')
