from pathlib import Path
import sys,json,datetime,ast
import numpy as np,cv2
O=Path(__file__).parent;ROOT=Path('/research/liquid-glass');D=ROOT/'research/experiments/miniplayer-inverse-forward-18';CAND=ROOT/'research/experiments/miniplayer-incident-material-20';BASE=ROOT/'research/experiments/miniplayer-interface-power-19';P=json.loads((O/'protocol.json').read_text());ledger={'cached_composites':0,'Study_constructors':0,'score_calls':0,'metric_gaussians':0,'metric_erosions':0,'cached_annular_direction_evaluations':0,'mask_points':0};records=[]
def gate():assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat(P['deadline'].replace('Z','+00:00'))
def charge(k,n):
 gate();assert ledger[k]+n<=P['caps'][k];ledger[k]+=int(n)
 if k=='score_calls':
  charge('metric_gaussians',5*n);charge('metric_erosions',n)
assert not (O/'replay-started.json').exists();(O/'replay-started.json').write_text(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat()})+'\n')
try:
 sys.path.insert(0,str(ROOT/'reconstruction'));from extended_fit import Study
 from geometric_render import neutral_color_response
 from environment_radiance import annular_environment,decode_srgb,encode_srgb
 cv2.setNumThreads(1);proto=json.loads((D/'protocol.json').read_text())
 tree=ast.parse((ROOT/'research/experiments/miniplayer-outline-light-07/render.py').read_text());definition=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='score'];exec(compile(ast.Module(body=definition,type_ignores=[]),'frozen-score','exec'))
 for member in ['expanded','compact']:
  q=np.load(D/f'{member}-paths.npz',allow_pickle=False);inside=q['inside'];charge('cached_annular_direction_evaluations',int(inside.sum()));unit=q['front_reflection_power'][inside]*annular_environment(q['front_reflection_direction'][inside])
  work=ROOT/('.evidence-working/expanded-geometry-02' if member=='expanded' else '.evidence-working/compact-geometry-01')
  for ref in ['a','b']:
   charge('Study_constructors',1);s=Study(work/ref);H,W=s.valid.shape;charge('mask_points',H*W)
   m=np.load(work/f'{ref}-masks.npz' if member=='expanded' else ROOT/f'research/experiments/compact-geometry-01/{ref}-masks.npz',allow_pickle=False);assert np.array_equal(s.valid,m['glass']) and np.array_equal(s.rim,m['rim']) and np.array_equal(s.held,m['held'])
   old=json.loads((CAND/f'{member}-{ref}-factor0.5-metrics.json').read_text());raw=np.load(D/f'{member}-{ref}-light4.npz',allow_pickle=False)['raw_source'];values=raw.copy();values[inside]=neutral_color_response(raw[inside],gain=old['gain'],bias=old['bias'])
   cov=np.load(D/f'{member}-{ref}-light4.npz',allow_pickle=False)['coverage'];frozen=np.load(ROOT/f'research/experiments/compact-geometry-01/{ref}-raw.npz',allow_pickle=False)['coverage'] if member=='compact' else cov;partial=m['glass']&(frozen<1)
   for amp in [4]:
    gate();changed=values.copy();encoded=encode_srgb(q['primary_power'][inside,None]*decode_srgb(values[inside])+amp*unit[:,None]);changed[inside]=np.clip(encoded,0,1);pre=changed.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32);charge('cached_composites',1);C=s.apply_foreground(pre.copy());saved=np.load(CAND/f'{member}-{ref}-factor0.5.npz',allow_pickle=False);assert np.array_equal(pre,saved['pre_foreground'],equal_nan=True) and np.array_equal(C,saved['complete'],equal_nan=True),'Cached image discrepancy'
    scores=score(s,C,m,partial,proto['fixed_crops'][member]);assert scores==old['scores'],'Score discrepancy'
    records.append({'member':member,'reference':ref,'amplitude':amp,'pre_foreground_exact':True,'complete_exact':True,'all_scores_exact':True,'E':scores['E'],'SSIM':scores['ssim'],'partial':scores['partial'],'failed_original_guards':[k for k,v in old['selected_guards'].items() if not v], 'failed_held_guards':[k for k,v in old['held_guards'].items() if not v]})
    print('REPLAY_EXACT',member,ref,amp,flush=True)
 status='PASS_FOUR_CACHED_COMPOSITES_WITH_LIMITS'
except Exception as e:status='STOPPED_FIRST_DISCREPANCY';failure=repr(e)
(O/'replay-result.json').write_text(json.dumps({'status':status,'failure':locals().get('failure'),'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'ledger':ledger,'new_rays_heights_source_queries_fields_Fresnel_fits':0},indent=2)+'\n');print('FINAL',status,locals().get('failure'),flush=True)
