"""One material-opacity direction for the existing transport-vector role."""
from pathlib import Path
import datetime,json,copy
import numpy as np
from extended_fit import Study
from vector_foreground import coverage
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02';BASE=ROOT/'research/experiments/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'result.json').exists()
def score(s,C,m):
 r=s.scores(C);r['E']=float(np.sqrt(r['loss']));e=(C-s.target_crop)*255;r['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));r['foreground_artwork_MSE']={};x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  x,y,x1,y1=layer['box'];name=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));r['foreground_artwork_MSE'][name]=float(np.mean(e[y-y0:y1-y0,x-x0:x1-x0]**2))
 return r
def guards(r,b):
 g={n:r[n]['rmse']<=b[n]['rmse'] for n in ['glass','rim','held','interior']};g.update({n:r[n]<=b[n] for n in ['E','exterior_RMSE']});g['ssim']=r['ssim']>=b['ssim'];g.update({n:r['foreground_artwork_MSE'][n]<=v for n,v in b['foreground_artwork_MSE'].items()});return g
contexts={};numer=0.;denom=0.;controls=[]
for k in ['a','b']:
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 s=Study(WORK/k);z=np.load(BASE/f'h1-{k}.npz');M=z['pre_foreground'];C=z['complete'];np.testing.assert_array_equal(s.apply_foreground(M.copy()),C);m=np.load(WORK/f'{k}-masks.npz');x0,y0,_,_=s.crop;sections=[]
 for layer in s.case['foreground_layers']:
  if layer.get('vector_asset') not in ['play.svg','forward.svg']:continue
  assert layer.get('opacity',1)==1
  a,b,c,d=layer['box'];alpha=coverage(s.folder,layer,1);yy,xx=np.mgrid[b:d,a:c];core=alpha>.95;train=core&((xx//8+yy//8)%2==0);held=core&~train;assert train.any() and held.any();body=M[b-y0:d-y0,a-x0:c-x0];ink=C[b-y0:d-y0,a-x0:c-x0];T=s.target_crop[b-y0:d-y0,a-x0:c-x0];D=(ink-body).astype(float);Y=(T-body).astype(float);numer+=float(np.mean(D[train]*Y[train]));denom+=float(np.mean(D[train]**2));sections.append((layer['vector_asset'],(a,b,c,d),train,held));controls.append(dict(reference=k,role=layer['vector_asset'],train=int(train.sum()),held=int(held.sum()),original_core_RMSE=float(np.sqrt(np.mean(((ink-T)[held]*255)**2)))))
 assert len(sections)==2;contexts[k]=(s,m,M,C.copy(),sections,score(s,C,m),copy.deepcopy(s.case.get('foreground_styles',{})))
raw=numer/denom;opacity=float(np.clip(raw,0,1));proposal=dict(raw_common_opacity=raw,bounded_opacity=opacity,controls=controls);(OUT/'proposal.json').write_text(json.dumps(proposal,indent=2)+'\n');ledger=[];selected=None
for trial,factor in enumerate([1.,.5] if opacity<1 else []):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 op=1+factor*(opacity-1);rows=[]
 for k,(s,m,M,C0,sections,old,styles) in contexts.items():
  s.case['foreground_styles']=copy.deepcopy(styles)
  for role,box,train,held in sections:s.case['foreground_styles'][role]={'opacity':op}
  C=s.apply_foreground(M.copy());r=score(s,C,m);g=guards(r,old);held_results=[];x0,y0,_,_=s.crop
  for role,(a,b,c,d),train,held in sections:
   err=(C-s.target_crop)[b-y0:d-y0,a-x0:c-x0]*255;held_results.append(dict(role=role,held_core_RMSE=float(np.sqrt(np.mean(err[held]**2)))))
  np.savez_compressed(OUT/f'trial{trial}-{k}.npz',complete=C);rows.append(dict(reference=k,scores=r,guards=g,advisory_held_core=held_results))
 rec=dict(trial=trial,factor=factor,opacity=op,records=rows,paired_qualifier=all(all(r['guards'].values()) for r in rows));ledger.append(rec)
 if rec['paired_qualifier']:selected=rec;break
result=dict(status='ZERO_BOUNDED_CHANGE' if opacity==1 else ('STRICT_PAIRED_COMPONENT_QUALIFIER' if selected else 'NO_STRICT_QUALIFIER'),proposal=proposal,selected=selected,ledger=ledger,new_rays=0,source_queries=0,fits=1,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat());(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],proposal=proposal,failed=[[[n for n,v in r['guards'].items() if not v] for r in z['records']] for z in ledger])),flush=True)
