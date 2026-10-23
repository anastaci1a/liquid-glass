"""Fixed cross-control colour prior, replaying exact sampled geometry."""
import datetime,json,time
import numpy as np
from native import ROOT,OUT,setup,save,metrics,preview
from material import cache,good,body_material,sample_incident,SIGMA
from geometric_render import incident_source_filter,coverage_blur
protocol=json.loads((OUT/'protocol.json').read_text());deadline=datetime.datetime.fromisoformat(protocol['stages'][2]['deadline']).timestamp()
if (OUT/'colour-result.json').exists():raise RuntimeError('Completed colour transfer cannot repeat')
def gate():
 if time.time()>deadline:raise RuntimeError('Colour stage deadline reached')
proof=json.loads((OUT/'blur-support-FIRST.json').read_text());assert all(r['unsupported_source_PSF_queries']==0 for r in proof['references'])
base=json.loads((OUT/'raw-result.json').read_text())['references']
unit={r['operator']:r['references'] for r in json.loads((OUT/'blur-result.json').read_text())['operators'] if 'references' in r}
prior=json.loads((ROOT/'reconstruction/studies/geometric-expanded-pipeline/summary.json').read_text())['material']
gain=prior['gain'];bias=prior['bias']
assert gain==protocol['stages'][2]['fixed_coefficients']['gain'] and bias==protocol['stages'][2]['fixed_coefficients']['bias']
states=[];queries=0
for k in ['a','b']:
 gate();s,c,surface,known,ext,required=setup(k);raw=cache(k);H,W=raw['coverage'].shape
 filtered,support,radius=incident_source_filter(s.source,known,SIGMA);assert radius==21
 source_samples,n=sample_incident(filtered,raw);queries+=n;assert queries<=1175792
 with np.load(OUT/f'{k}-blur-source.npz') as z:
  np.testing.assert_array_equal(source_samples.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32),z['pre_foreground'])
  np.testing.assert_array_equal(s.apply_foreground(z['pre_foreground'].copy()),z['complete'])
 states.append((k,s,raw,source_samples,ext))
save('colour-zero-controls.json',{'source_samples_reconstructed_to_saved_pre_foreground_exact':True,'original_foreground_replay_exact':True,'source_RGB_queries':queries,'new_rays':0,'reason':'The earlier PSF artifact retained pre-foreground pixels but not its individual filtered subray RGB; cached physical XY reconstruct them once for exact colour-before-AA evaluation.'})
trials=[];selected=None
for operator,factor in [('source',1.),('source',.5),('output',1.),('output',.5)]:
 gate();g=1+factor*(gain-1);b=factor*bias;rows=[]
 for (k,s,raw,source_samples,ext),baseline,unit_before in zip(states,base,unit[operator]):
  gate();H,W=raw['coverage'].shape;inside=raw['sample_inside']
  samples=(source_samples if operator=='source' else raw['sample_rgb']).copy()
  before=samples[inside];samples[inside]=g*before+b
  preclip=samples[inside];assert preclip.min()>=0 and preclip.max()<=1
  M=body_material(samples,inside,H,W)
  if operator=='source':pre=samples.reshape(H,2,W,2,3).mean((1,3)).astype(np.float32)
  else:
   M=coverage_blur(M,raw['coverage'],SIGMA);pre=(M*raw['coverage'][...,None]+raw['clear']).astype(np.float32)
  C=s.apply_foreground(pre.copy());z=metrics(s,M.astype(np.float32),C,ext)
  rows.append({'reference':k,'scores':z,'guards_against_raw':good(z,baseline['scores']),'colour_only_guards_against_unit_PSF':good(z,unit_before['scores']),'preclip_range':[float(preclip.min()),float(preclip.max())],'clipped_channels':0})
  np.savez_compressed(OUT/f'{k}-colour-{operator}-{factor:g}.npz',material=M,pre_foreground=pre,complete=C)
 trial={'operator':operator,'factor':factor,'gain':g,'bias':b,'references':rows};trials.append(trial);save('colour-ledger.json',trials)
 print(json.dumps({'operator':operator,'factor':factor,'E':[r['scores']['completed_image']['E'] for r in rows],'guards':[r['guards_against_raw'] for r in rows]}),flush=True)
 if all(all(r['guards_against_raw'].values()) for r in rows):selected=trial;break
result={'status':'PAIRED_MATERIAL_QUALIFIER_PENDING_VISUAL' if selected else 'NO_STRICT_PAIRED_MATERIAL_QUALIFIER','selected':selected,'pair_trials':len(trials),'fits':0,'new_rays':0,'source_RGB_queries':queries,'coefficients':'Fixed expanded-control common neutral response, with only declared half-step backtracks. No per-RGB/crop/reference coefficients.','operator_transfer':'Source-space placement changes the prior operator; output placement tests the original expanded material convention.','scope':'No geometric fidelity or complete-radiance acceptance is implied.'}
save('colour-result.json',result)
if selected:
 for k,s,raw,samples,ext in states:
  with np.load(OUT/f'{k}-colour-{selected["operator"]}-{selected["factor"]:g}.npz') as z:preview(s,z['complete'],f'{k}-colour-selected.png','Geometric material-transfer candidate')
