"""Frozen source/geometry; existing shadow changes only the clear contribution."""
from pathlib import Path
import datetime,json
import numpy as np
from extended_fit import Study
from extended_shadow import shadow
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;WORK=ROOT/'.evidence-working/expanded-geometry-02';BASE=ROOT/'research/experiments/expanded-geometry-02';p=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(p['deadline']);assert not (OUT/'result.json').exists()
def score(s,C,m):
 r=s.scores(C);r['E']=float(np.sqrt(r['loss']));e=(C-s.target_crop)*255;r['exterior_RMSE']=float(np.sqrt(np.mean(e[m['exterior']]**2)));r['foreground_artwork_MSE']={};x0,y0,_,_=s.crop
 for layer in s.case['foreground_layers']:
  x,y,x1,y1=layer['box'];name=layer.get('style_key',layer.get('vector_asset',layer.get('artwork_asset')));r['foreground_artwork_MSE'][name]=float(np.mean(e[y-y0:y1-y0,x-x0:x1-x0]**2))
 return r
def guards(r,b):
 g={n:r[n]['rmse']<=b[n]['rmse'] for n in ['glass','rim','held','interior']};g.update({n:r[n]<=b[n] for n in ['E','exterior_RMSE']});g['ssim']=r['ssim']>=b['ssim'];g.update({n:r['foreground_artwork_MSE'][n]<=v for n,v in b['foreground_artwork_MSE'].items()});return g
hist=json.loads((ROOT/'research/captures/dark-glass-lab/extended/agent-pipeline-01/historical-pass03.json').read_text())['parameters'];contexts={};zeros=[]
for k in ['a','b']:
 s=Study(WORK/k);base=np.load(BASE/f'h1-{k}.npz');q=np.load(WORK/f'h1-{k}-paths.npz');m=np.load(WORK/f'{k}-masks.npz');H,W=s.valid.shape;inside=q['inside'];clear=np.where(inside[...,None],0,base['sample_before_response']).reshape(H,2,W,2,3).mean((1,3));full=inside.reshape(H,2,W,2).all((1,3));unit=shadow(s,{**hist,'shadow':{**p['shadow'],'opacity':1.}},s.x,s.y);assert (unit>=0).all() and (unit<=1).all()
 M=base['pre_foreground'];zero=(M.astype(float)-0*unit[...,None]*clear).astype(np.float32);np.testing.assert_array_equal(zero,M);np.testing.assert_array_equal(s.apply_foreground(zero.copy()),base['complete']);zeros.append(dict(reference=k,material_and_complete_exact=True,partial_original_glass_pixels=int((m['glass']&~full).sum())));contexts[k]=(s,m,M,base['complete'].copy(),clear,unit,full,score(s,base['complete'],m))
ledger=[];selected=None
for trial,opacity in enumerate(p['settings']):
 assert datetime.datetime.now(datetime.timezone.utc)<deadline
 rows=[]
 for k,(s,m,M,C0,clear,unit,full,old) in contexts.items():
  candidate=(M.astype(float)-opacity*unit[...,None]*clear).astype(np.float32);np.testing.assert_array_equal(candidate[full],M[full]);C=s.apply_foreground(candidate.copy());r=score(s,C,m);g=guards(r,old);np.savez_compressed(OUT/f'trial{trial}-{k}.npz',pre_foreground=candidate,complete=C);rows.append(dict(reference=k,scores=r,guards=g,fully_covered_pixels_exact=True));
 row=dict(trial=trial,opacity=opacity,records=rows,paired_qualifier=all(all(r['guards'].values()) for r in rows));ledger.append(row);print(json.dumps(dict(trial=trial,paired_qualifier=row['paired_qualifier'],E=[r['scores']['E'] for r in rows],failed=[[n for n,v in r['guards'].items() if not v] for r in rows])),flush=True)
 if row['paired_qualifier']:selected=row;break
(OUT/'result.json').write_text(json.dumps(dict(status='STRICT_PAIRED_COMPONENT_QUALIFIER' if selected else 'NO_STRICT_QUALIFIER',selected=selected,zero_controls=zeros,baseline={k:v[-1] for k,v in contexts.items()},ledger=ledger,new_rays=0,source_queries=0,fits=0,finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat()),indent=2)+'\n')
