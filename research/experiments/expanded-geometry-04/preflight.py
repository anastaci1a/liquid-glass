"""One native closed-solid path grid; both sources audited before RGB."""
from pathlib import Path
import datetime,json
import cv2,numpy as np
from extended_fit import Study
from rounded_rectangle_back import RoundedRectangleHarmonicBack
from parabolic_front_solid import ParabolicFrontHeightSolid
from geometric_optics import trace_closed_orthographic
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02'
p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);check=json.loads((OUT/'checkpoint.json').read_text());assert check['status']=='PASS' and not (OUT/'source-preflight.json').exists()
scene=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['geometry'];surface=ParabolicFrontHeightSolid(RoundedRectangleHarmonicBack(tuple(scene['surface_half']),scene['surface_radius']),.4)
surface.maximum_level_points=p['budgets']['total_new_level_points']-check['counts']['level_points']
s=Study(WORK/'a');x0,y0,x1,y1=s.crop;H,W=s.valid.shape;X=np.empty((2*H,2*W));Y=np.empty_like(X);inside=np.zeros(X.shape,bool);complete=np.zeros_like(inside);rays=0;max_bracket=0.;max_residual=0.;min_discriminant=1.
for top in range(0,H,8):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 bot=min(top+8,H);yy,xx=np.mgrid[y0+top:y0+bot:.5,x0:x1:.5];xx-=.25;yy-=.25;rays+=xx.size;assert rays<=p['budgets']['full_native_primary_rays']
 q=trace_closed_orthographic(surface,(xx-scene['center'][0])/s.L,(yy-scene['center'][1])/s.L,1.5,2,tolerance=1e-11,max_iterations=64)
 valid=q['inside']&q['complete']
 if valid.any():max_bracket=max(max_bracket,float(q['intersection_bracket'][valid].max()));max_residual=max(max_residual,float(abs(q['exit_level_residual'][valid]).max()));min_discriminant=min(min_discriminant,float(q['discriminant'][valid].min()))
 X[2*top:2*bot]=q['X']*s.L+scene['center'][0];Y[2*top:2*bot]=q['Y']*s.L+scene['center'][1];inside[2*top:2*bot]=q['inside'];complete[2*top:2*bot]=q['complete']
np.savez_compressed(OUT/'native-paths.npz',X=X,Y=Y,inside=inside,complete=complete)
np.testing.assert_array_equal(inside,np.load(WORK/'h1-a-paths.npz')['inside'])
rows=[];checks=0
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 case=Study(WORK/k);assert case.crop==s.crop and case.case['center']==s.case['center'] and case.case['half']==s.case['half'] and case.L==s.L
 masks=np.load(WORK/f'{k}-masks.npz');np.testing.assert_array_equal(case.valid,masks['glass']);np.testing.assert_array_equal(inside,np.load(WORK/f'h1-{k}-paths.npz')['inside'])
 known=cv2.imread(str(WORK/k/'known.png'),0)>0;eroded=cv2.erode(known.astype(np.uint8),np.ones((43,43),np.uint8),borderType=cv2.BORDER_CONSTANT,borderValue=0)>0
 req=masks['glass']|masks['exterior']
 for layer in case.case['foreground_layers']:
  a,b,c,d=layer['box'];req[b-y0:d-y0,a-x0:c-x0]=True
 required=inside|np.repeat(np.repeat(req,2,0),2,1);checks+=required.size;assert checks<=p['budgets']['source_audit_subrays']
 finite=np.isfinite(X)&np.isfinite(Y);a=np.floor(np.where(finite,X,-1)).astype(int);b=np.floor(np.where(finite,Y,-1)).astype(int);bounds=finite&(a>=0)&(b>=0)&(a+1<known.shape[1])&(b+1<known.shape[0]);base=np.zeros(a.shape,bool);lens=np.zeros(a.shape,bool);i,j=np.nonzero(bounds)
 for field,mask in [(base,known),(lens,eroded)]:field[i,j]=mask[b[i,j],a[i,j]]&mask[b[i,j]+1,a[i,j]]&mask[b[i,j],a[i,j]+1]&mask[b[i,j]+1,a[i,j]+1]
 support=np.where(inside,lens,base)&complete;row=dict(reference=k,source_audit_subrays=required.size,whole=int(inside.sum()),required_union=int(required.sum()),unsupported_required=int((required&~support).sum()),incomplete_required=int((required&~complete).sum()),unsupported_unscored_only=int((~required&~support).sum()),source_radius=21,RGB_queries=0,coverage_exact=True)
 np.savez_compressed(OUT/f'{k}-support.npz',support=support,required=required);rows.append(row);print(json.dumps(row),flush=True)
status='PASS' if all(r['unsupported_required']==r['incomplete_required']==0 for r in rows) else 'STOP_INCOMPLETE_OR_UNSUPPORTED_REQUIRED_NO_RGB'
r=dict(status=status,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_primary_rays=rays,level_points=surface.level_point_evaluations,checkpoint_level_points=check['counts']['level_points'],total_level_points=surface.level_point_evaluations+check['counts']['level_points'],height_evaluations_in_native_pass=surface.height_point_evaluations,maximum_intersection_bracket=max_bracket,maximum_exit_level_residual=max_residual,minimum_exit_discriminant=min_discriminant,source_audit_subrays=checks,RGB_queries=0,native_images=0,references=rows,source_limit='Original confidence only; not hidden photographic truth or reflected environment.')
(OUT/'source-preflight.json').write_text(json.dumps(r,indent=2)+'\n')
if status!='PASS':raise RuntimeError('Stop before RGB')
