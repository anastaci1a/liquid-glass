"""One exact cached compositor prerequisite; no optical queries or fitting."""
from pathlib import Path
import json,sys,datetime,time,hashlib,os
import numpy as np,cv2
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT/'reconstruction'))
from extended_fit import Study
from vector_foreground import coverage
os.umask(0o002);cv2.setNumThreads(1)
p=json.loads((P/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['checkpoint_deadline_utc'].replace('Z','+00:00')).timestamp();PRIMARY=ROOT.parent/'liquid-glass';CACHE=PRIMARY/'research/experiments/navigation-geometry-01';WORK=PRIMARY/'.evidence-working/navigation-geometry-01'
assert time.time()<deadline and not (P/'contract-started.json').exists()
(P/'contract-started.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
rows=[]
for key in ['a','b']:
 assert time.time()<deadline
 s=Study(WORK/key);old=np.load(CACHE/f'{key}-source-blur.npz');raw=np.load(CACHE/f'{key}-raw.npz');m=np.load(CACHE/f'{key}-masks.npz');assert not s.transmission_layers
 assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
 H,W=s.valid.shape;paint=np.zeros((H,W),bool);dependencies=np.zeros((H,W),bool);x0,y0,_,_=s.crop;layers=[]
 for layer in s.case['foreground_layers']:
  a,b,c,d=layer['box'];alpha=coverage(s.folder,layer);style=s.case.get('foreground_styles',{}).get(layer.get('style_key',layer['vector_asset']),{});alpha=alpha if 'response'in style else alpha*style.get('opacity',layer.get('opacity',1.));assert alpha.shape==(d-b,c-a)
  paint[b-y0:d-y0,a-x0:c-x0]|=alpha>0;dependencies[b-y0:d-y0,a-x0:c-x0]=True;layers.append({'asset':layer['vector_asset'],'box':layer['box'],'painted_pixels':int((alpha>0).sum()),'nonlinear_response':'response'in style})
 unsupported=int((paint&(raw['coverage']!=1)).sum());base={'case':key,'paint_pixels':int(paint.sum()),'style_dependency_pixels':int(dependencies.sum()),'paint_not_fully_covered':unsupported,'layers':layers,'new_rays':0,'new_RGB_queries':0}
 if unsupported:
  base['status']='STOP_CACHE_CANNOT_SUPPLY_EXACT_PAINTED_BACKING';rows.append(base);break
 # Unpainted completed pixels are already exact pre-foreground pixels. At every
 # painted pixel coverage=1, so saved lens_color is exactly integrated backing.
 # No foreground cache is subtracted or inverted.
 pre=old['complete'].copy();pre[paint]=old['material'][paint];assert np.isfinite(pre[dependencies]).all();actual=s.apply_foreground(pre.copy());finite=np.isfinite(old['complete']);same=np.array_equal(actual,old['complete'],equal_nan=True);delta=np.abs(actual[finite]-old['complete'][finite]);base.update(status='PASS_EXACT_CACHED_COMPOSITOR' if same else 'STOP_COMPOSITOR_NOT_EXACT',complete_exact=bool(same),max_difference=float(delta.max()),different_channels=int(np.count_nonzero(actual[finite]!=old['complete'][finite])),method='Reuse completed pixels only outside the union of actual vector coverage, where no foreground acts. Restore saved material on all painted pixels only after exact coverage-one proof. Apply the original ordered nonlinear compositor once. No foreground subtraction or fixed-opacity surrogate.');rows.append(base)
 np.savez_compressed(P/f'{key}-zero-control.npz',pre_foreground=pre,complete=actual,paint_mask=paint,style_dependencies=dependencies)
 if not same:break
result={'status':'PASS' if len(rows)==2 and all(r['status']=='PASS_EXACT_CACHED_COMPOSITOR' for r in rows) else 'INCOMPLETE_CACHE_COMPOSITOR_PREREQUISITE','rows':rows,'cached_zero_controls':sum('complete_exact'in r for r in rows),'new_rays':0,'new_RGB_queries':0,'new_fits':0,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(P/'contract-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
