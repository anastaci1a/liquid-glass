"""Audit retained physical rays against the full incident PSF before RGB."""
import datetime,json
from pathlib import Path
import cv2,numpy as np
from extended_fit import Study
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02'
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['refraction_deadline'])
assert not (OUT/'source-preflight.json').exists()
rows=[];total=0
for h in ['h1','h2']:
 for k in ['a','b']:
  assert datetime.datetime.now(datetime.timezone.utc)<deadline
  s=Study(WORK/k);m=np.load(WORK/f'{k}-masks.npz');q=np.load(WORK/f'{h}-{k}-paths.npz');known=cv2.imread(str(WORK/k/'known.png'),0)>0
  np.testing.assert_array_equal(s.valid,m['glass']);np.testing.assert_array_equal(s.rim,m['rim']);np.testing.assert_array_equal(s.held,m['held'])
  req=m['glass']|m['exterior'];x0,y0,_,_=s.crop
  for l in s.case['foreground_layers']:
   a,b,c,d=l['box'];req[b-y0:d-y0,a-x0:c-x0]=True
  needed=q['inside']|np.repeat(np.repeat(req,2,0),2,1);total+=needed.size
  assert total<=p['budgets']['source_preflight_subrays_maximum']
  assert q['complete'][needed].all() and np.isfinite(q['X'][needed]).all() and np.isfinite(q['Y'][needed]).all()
  safe=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
  a=np.floor(q['X']).astype(int);b=np.floor(q['Y']).astype(int)
  bounds=(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);base=np.zeros(a.shape,bool);lens=np.zeros_like(base)
  i,j=np.nonzero(bounds)
  for field,mask in [(base,known),(lens,safe)]:field[i,j]=mask[b[i,j],a[i,j]]&mask[b[i,j]+1,a[i,j]]&mask[b[i,j],a[i,j]+1]&mask[b[i,j]+1,a[i,j]+1]
  support=np.where(q['inside'],lens,base)
  row=dict(hypothesis=h,reference=k,emitted_subrays=needed.size,whole=int(q['inside'].sum()),required_union=int(needed.sum()),unsupported_required=int((needed&~support).sum()),unsupported_whole=int((q['inside']&~support).sum()),unsupported_unscored_only=int((~needed&~support).sum()),source_kernel_radius=21,RGB_queries=0,mask_equality=True)
  rows.append(row);print(json.dumps(row),flush=True)
  np.savez_compressed(OUT/f'{h}-{k}-support.npz',support=support,required=needed)
result=dict(status='PASS' if all(r['unsupported_required']==0 for r in rows) else 'STOP_UNSUPPORTED_REQUIRED_NO_RGB',references=rows,emitted_subrays_checked=total,new_rays=0,RGB_queries=0,source_filter='Full43x43 incident kernel and all four bilinear texels for inside rays; original clear source outside',known_limit='Existing source confidence is not hidden photographic truth.',finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
(OUT/'source-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
if result['status']!='PASS':raise RuntimeError('Unsupported required source; no RGB proposal permitted')
