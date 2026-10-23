from pathlib import Path
import json,time
P=Path('/evidence/extended/playback-pipeline-01');src=(P/'refraction_grid.py').read_text().split('ledger=[];best=None')[0];src=src.replace("OUT=ROOT/'refraction-01'","OUT=ROOT/'refraction-01-second'")
exec(compile(src,str(P/'refraction_grid.py'),'exec'))
# Preserve original R1 absolute deadline, not a new35-minute budget.
DEADLINE=datetime.datetime.fromisoformat(json.loads((P/'refraction-01/result.json').read_text())['original_deadline_utc']).timestamp();gate()
if (OUT/'result.json').exists():raise RuntimeError('Completed second R1 cannot rerun')
s=surface(.01,.94);tiles,proof=qtiles(s,[('full',case['crop'])]);(OUT/'source-proof-FIRST.json').write_text(json.dumps(proof,indent=2)+'\n');C=render_tiles(tiles,[('full',case['crop'])])['full'];np.save(OUT/'candidate-complete.npy',C);np.savez(OUT/'candidate-surface.npz',nodes=s.knots,curvature=s.curvature)
result=dict(dc=.01,amplitude=.94,scores=scores(C,target[y0:y1,x0:x1],case),baseline_scores=scores(old,target[y0:y1,x0:x1],case),source=proof,full_native_candidates=1,reused_patch_trial=5,original_deadline=DEADLINE,wall_seconds=time.time()-START)
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
def pic(v):return Image.fromarray(np.uint8(np.rint(np.clip(v,0,1)*255)))
crop=Image.new('RGB',(1324,1632),'white');dr=ImageDraw.Draw(crop)
for i,(name,(a,b,c,d)) in enumerate(RECTS):
 for j,(v,label) in enumerate([(target[b:d,a:c],'Apple'),(old[b-y0:d-y0,a-x0:c-x0],'G05'),(C[b-y0:d-y0,a-x0:c-x0],'R1 second')]):crop.paste(pic(v).resize((440,480),Image.Resampling.NEAREST),(442*j,544*i+64));dr.text((442*j+5,544*i+20),name+' / '+label,fill='black')
crop.save(OUT/'crops.png');print(json.dumps(result),flush=True)
