from pathlib import Path
import json,time,datetime
P=Path('/evidence/extended/playback-pipeline-01');src=(P/'refraction_grid.py').read_text().split('ledger=[];best=None')[0];src=src.replace("OUT=ROOT/'refraction-01'","OUT=ROOT/'refraction-03'")
exec(compile(src,str(P/'refraction_grid.py'),'exec'))
from two_graph_control import TwoGraphCircle
from geometric_optics import trace_closed_orthographic
trace_flat_front_orthographic=trace_closed_orthographic
DEADLINE=min(START+45*60,HARD_END);back=RadialCurvatureBack(nodes,curv)
baseimages={n:old[b-y0:d-y0,a-x0:c-x0] for n,(a,b,c,d) in RECTS};base_loss,base_local=measure(baseimages);rows=[];best=None
for a in [.003,.006]:
 s=TwoGraphCircle(back,a);tiles,proof=qtiles(s,RECTS);(OUT/f'front-{a}-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');imgs=render_tiles(tiles,RECTS);loss,local=measure(imgs);row=dict(front_sag=a,feature_loss=loss,local=local,source_proof=proof);rows.append(row);np.savez(OUT/f'front-{a}-patches.npz',**imgs);(OUT/'trials.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'front_sag':a,'loss':loss,'base_loss':base_loss,'local':local}),flush=True)
 if best is None or loss<best[0]:best=(loss,a)
 del tiles
full=None
if best[0]<base_loss*.98:
 a=best[1];s=TwoGraphCircle(back,a);tiles,proof=qtiles(s,[('full',case['crop'])]);(OUT/'candidate-source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');C=render_tiles(tiles,[('full',case['crop'])])['full'];np.save(OUT/'candidate-complete.npy',C);full=dict(front_sag=a,scores=scores(C,target[y0:y1,x0:x1],case),baseline_scores=scores(old,target[y0:y1,x0:x1],case),source=proof)
 (OUT/'candidate.json').write_text(json.dumps(full,indent=2)+'\n')
 def pic(v):return Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)))
 crop=Image.new('RGB',(1324,1632),'white');dr=ImageDraw.Draw(crop)
 for i,(name,(aa,b,c,d)) in enumerate(RECTS):
  for j,(v,label) in enumerate([(target[b:d,aa:c],'Apple'),(old[b-y0:d-y0,aa-x0:c-x0],'G05'),(C[b-y0:d-y0,aa-x0:c-x0],'R3 curved-front')]):crop.paste(pic(v).resize((440,480),Image.Resampling.NEAREST),(442*j,544*i+64));dr.text((442*j+5,544*i+20),name+' / '+label,fill='black')
 crop.save(OUT/'crops.png')
result=dict(classification='PENDING_REVIEW' if full else 'USEFUL_NEGATIVE_NO_FULL_CANDIDATE',best=best,baseline_loss=base_loss,local_baseline=base_local,patch_evaluations=len(rows),full_native_candidates=int(full is not None),rays=sum(x['source_proof']['rays'] for x in rows),wall_seconds=time.time()-START,deadline=datetime.datetime.fromtimestamp(DEADLINE,datetime.timezone.utc).isoformat(),no_fit=True)
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
