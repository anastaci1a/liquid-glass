"""Three prescribed offset-only pairs after accepted pass2; no optical renders or repeated fit."""
import os,sys,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
R=Path('/evidence/extended/helper-toolbar-work/light-dark-round');sys.path.insert(0,str(R));import importlib.util
spec=importlib.util.spec_from_file_location('generated_exterior',R/'generated-exterior.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
from render import case_geometry
from reproduce import CASES,scores
O=R/'offset-pass3';os.umask(0o002)
if O.exists():raise RuntimeError('Inspect existing outputs; no repeat')
O.mkdir();rows=g.load();recipe=json.loads((R/'generated-exterior/recipe.json').read_text());p=np.array(list(recipe['parameters'].values()),dtype=np.float64);history=[];accepted=None
for r in rows:
 r['accepted']=np.load(R/f"offset-neighborhood/{r['name']}-complete.npy");r['fullmask']=r['sd']>0;r['accepted_scores']=scores(r['M'],r['T'],CASES[r['name']])
 for key in ['mask','fullmask']:
  r[key+'_baseline']=float(np.sqrt(np.mean(((r['accepted']-r['T'])[r[key]]*255)**2)))
 assert r['fullmask'].sum()==171369
for s in [1.2,1.15,1.05]:
 trial=[];outputs=[]
 for r in rows:
  c=CASES[r['name']];L=min(c['half']);rr=dict(r);rr['dK']=np.maximum(case_geometry(c,r['x'],r['y']-.06*s*L)[0]/L,0);rr['dH']=np.maximum(case_geometry(c,r['x'],r['y']+.4*s*L)[0]/L,0)
  out,B,K,H=g.evaluate(rr,p);sc=scores(out.astype(np.float32),r['T'],c);errs={key:float(np.sqrt(np.mean(((out-r['T'])[r[key]]*255)**2))) for key in ['mask','fullmask']};guard=all(errs[key]<=r[key+'_baseline'] for key in errs) and sc==r['accepted_scores']
  trial.append(dict(theme=r['name'],supplemental_baseline=r['mask_baseline'],supplemental_candidate=errs['mask'],full_visible_baseline=r['fullmask_baseline'],full_visible_candidate=errs['fullmask'],all_original_scores_exact=sc==r['accepted_scores'],guards=guard));outputs.append(out)
 qualifier=all(t['guards'] for t in trial) and any(t['supplemental_candidate']<t['supplemental_baseline'] or t['full_visible_candidate']<t['full_visible_baseline'] for t in trial)
 history.append(dict(s=s,observations=trial,qualifier=qualifier));(O/'trials.json').write_text(json.dumps(history,indent=2)+'\n');print(s,qualifier,[(t['supplemental_candidate'],t['full_visible_candidate']) for t in trial],flush=True)
 if qualifier:
  accepted=s
  for r,out in zip(rows,outputs):
   np.save(O/f"{r['name']}-complete.npy",out)
   ims=[Image.fromarray(np.rint(np.clip(a,0,1)*255).astype(np.uint8)).resize((720,391),Image.Resampling.LANCZOS) for a in [r['T'],r['accepted'],out]];sheet=Image.new('RGB',(2160,455),'white');d=ImageDraw.Draw(sheet)
   for i,(im,label) in enumerate(zip(ims,['Apple','Accepted pass2','Offset candidate'])):d.text((i*720+12,24),label,fill='black');sheet.paste(im,(i*720,64))
   sheet.save(O/f"{r['name']}-comparison.png")
  candidate=dict(recipe);candidate['offset_multiplier']=s;candidate['offsets_L']={'K':[0,.06*s],'H':[0,-.4*s]};(O/'candidate.json').write_text(json.dumps(candidate,indent=2)+'\n');break
(O/'result.json').write_text(json.dumps(dict(qualifier=accepted is not None,accepted=False,count=2,scope='EXTERIOR-ONLY/Eoptical tie',trials=len(history),s=accepted,optical_renders=0,source_unchanged=True,trial_history=history),indent=2)+'\n')
